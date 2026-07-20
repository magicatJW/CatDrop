from __future__ import annotations

import json
import logging
import shutil
from email.parser import BytesParser
from email.policy import default
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from core import Database, file_signature_matches, parse_enabled_extensions, safe_name, setting_is_enabled, unique_filename


MAX_FORM_OVERHEAD = 2 * 1024 * 1024
LOGGER = logging.getLogger("catdrop.server")


class UploadServer(ThreadingHTTPServer):
    """保存服務共用物件，供每個請求處理器使用。"""

    daemon_threads = True

    def __init__(self, address: tuple[str, int], database: Database, project_dir: Path):
        super().__init__(address, UploadHandler)
        self.database = database
        self.project_dir = project_dir


class UploadHandler(BaseHTTPRequestHandler):
    server: UploadServer

    def log_message(self, format: str, *args: object) -> None:
        # 後台 UI 已顯示服務狀態，不在終端輸出裝置請求資訊。
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_file(self.server.project_dir / "web" / "index.html", "text/html; charset=utf-8")
        elif path == "/styles.css":
            self._send_file(self.server.project_dir / "web" / "styles.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self._send_file(self.server.project_dir / "web" / "app.js", "application/javascript; charset=utf-8")
        elif path == "/api/config":
            max_mb = int(self.server.database.get_setting("max_file_mb", "100"))
            extensions = parse_enabled_extensions(self.server.database.get_setting("enabled_extensions", ""))
            language = self.server.database.get_setting("ui_language", "zh")
            self._json({
                "maxFileMb": max_mb,
                "extensions": sorted(extensions),
                "allowAllFileTypes": setting_is_enabled(self.server.database, "allow_all_file_types", default=False),
                "uploadEnabled": setting_is_enabled(self.server.database, "upload_enabled"),
                "defaultLanguage": language if language in {"zh", "en"} else "zh",
            })
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/upload":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not setting_is_enabled(self.server.database, "upload_enabled"):
            self._json({"ok": False, "error": "目前暫停接收檔案。"}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        try:
            self._handle_upload()
        except ValueError as error:
            self._json({"ok": False, "error": str(error)}, HTTPStatus.BAD_REQUEST)
        except Exception:
            LOGGER.exception("處理檔案上傳時發生未預期錯誤")
            self._json({"ok": False, "error": "伺服器處理失敗，請稍後重試。"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_upload(self) -> None:
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            raise ValueError("上傳格式不正確。")
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("無效的資料大小。") from error
        max_mb = int(self.server.database.get_setting("max_file_mb", "100"))
        enabled_extensions = parse_enabled_extensions(self.server.database.get_setting("enabled_extensions", ""))
        allow_all_file_types = setting_is_enabled(self.server.database, "allow_all_file_types", default=False)
        if content_length <= 0 or content_length > max_mb * 1024 * 1024 + MAX_FORM_OVERHEAD:
            raise ValueError(f"單次請求不可超過約 {max_mb} MB；請分批上傳。")

        body = self.rfile.read(content_length)
        message = BytesParser(policy=default).parsebytes(
            b"Content-Type: " + content_type.encode("ascii", "ignore") + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
        )
        name_part = None
        file_parts = []
        for part in message.iter_parts():
            field_name = part.get_param("name", header="content-disposition")
            if field_name == "name":
                # FormData 的文字欄位通常未附 charset，必須明確以 UTF-8 解碼繁體中文來源名稱。
                try:
                    name_part = (part.get_payload(decode=True) or b"").decode("utf-8").strip()
                except UnicodeDecodeError as error:
                    raise ValueError("來源名稱編碼不正確，請重新輸入。") from error
            elif field_name == "files" and part.get_filename():
                file_parts.append(part)
        user_name = safe_name(str(name_part or ""), "")
        if not user_name:
            raise ValueError("請輸入來源名稱。")
        if not file_parts:
            raise ValueError("請選擇至少一個檔案。")

        storage_root = Path(self.server.database.get_setting("storage_path", str(self.server.project_dir / "received_files")))
        user_dir = storage_root / user_name
        user_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for part in file_parts:
            original_name = Path(str(part.get_filename())).name
            extension = Path(original_name).suffix.lower()
            if not allow_all_file_types and extension not in enabled_extensions:
                results.append({"name": original_name, "ok": False, "error": "不支援的檔案類型"})
                continue
            payload = part.get_payload(decode=True) or b""
            if len(payload) > max_mb * 1024 * 1024:
                results.append({"name": original_name, "ok": False, "error": f"超過 {max_mb} MB"})
                continue
            if not allow_all_file_types and not file_signature_matches(extension, payload[:64]):
                results.append({"name": original_name, "ok": False, "error": "檔案內容與副檔名不符"})
                continue
            stored_name = unique_filename(original_name)
            target = user_dir / stored_name
            with target.open("xb") as output:
                output.write(payload)
            self.server.database.add_upload(user_name, original_name, stored_name, str(target), len(payload))
            results.append({"name": original_name, "ok": True})
        accepted = sum(1 for item in results if item["ok"])
        self._json({"ok": accepted > 0, "accepted": accepted, "total": len(results), "results": results})

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        with path.open("rb") as source:
            shutil.copyfileobj(source, self.wfile)

    def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)
