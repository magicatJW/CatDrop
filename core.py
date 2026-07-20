from __future__ import annotations

import re
import secrets
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


NEW_IMAGE_EXTENSIONS = {".jfif", ".heif", ".avif", ".ico"}

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv",
    ".jpg", ".jpeg", ".jfif", ".png", ".gif", ".bmp", ".webp",
    ".tif", ".tiff", ".heic", ".heif", ".avif", ".ico",
}

LEGACY_ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS - NEW_IMAGE_EXTENSIONS


def parse_enabled_extensions(value: str) -> set[str]:
    """將設定值限制在程式已知白名單內；空值代表沿用完整白名單。"""
    if not value.strip():
        return set(ALLOWED_EXTENSIONS)
    requested = {item.strip().lower() for item in value.split(",") if item.strip()}
    return requested & ALLOWED_EXTENSIONS


def serialize_enabled_extensions(extensions: set[str]) -> str:
    """以穩定順序保存已啟用的副檔名。"""
    return ",".join(sorted(extensions & ALLOWED_EXTENSIONS))


def setting_is_enabled(database: "Database", key: str, default: bool = True) -> bool:
    """將 SQLite 文字設定轉為布林值。"""
    fallback = "1" if default else "0"
    return database.get_setting(key, fallback) == "1"


def sort_upload_rows(rows: list[sqlite3.Row], column: str, descending: bool) -> list[sqlite3.Row]:
    """依控制台欄位使用原始資料排序，避免以格式化後文字誤排大小或日期。"""
    key_functions = {
        "status": lambda row: (int(row["processed"]), int(row["id"])),
        "user": lambda row: (str(row["user_name"]).casefold(), int(row["id"])),
        "name": lambda row: (str(row["original_name"]).casefold(), int(row["id"])),
        "size": lambda row: (int(row["size_bytes"]), int(row["id"])),
        "time": lambda row: (str(row["uploaded_at"]), int(row["id"])),
    }
    key_function = key_functions.get(column, key_functions["time"])
    return sorted(rows, key=key_function, reverse=descending)


def safe_name(value: str, fallback: str = "未命名") -> str:
    """清除 Windows 禁用字元與路徑控制字元。"""
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", value.strip())
    value = value.rstrip(". ")
    if value.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        value = f"_{value}"
    return value[:80] or fallback


def unique_filename(original: str) -> str:
    """產生不含使用者路徑的唯一檔名。"""
    clean = safe_name(Path(original).name, "file")
    stem = Path(clean).stem[:100] or "file"
    suffix = Path(clean).suffix.lower()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{stem}_{stamp}_{secrets.token_hex(2)}{suffix}"


def file_signature_matches(extension: str, head: bytes) -> bool:
    """以常見檔頭阻擋只改副檔名的明顯偽裝檔案。"""
    extension = extension.lower()

    def has_iso_brand(data: bytes, brands: set[bytes]) -> bool:
        """檢查 ISO Base Media File Format 的主要與相容品牌。"""
        if len(data) < 12 or data[4:8] != b"ftyp":
            return False
        return any(data[offset:offset + 4] in brands for offset in range(8, len(data) - 3, 4))

    signatures = {
        ".pdf": lambda b: b.startswith(b"%PDF-"),
        ".doc": lambda b: b.startswith(bytes.fromhex("D0CF11E0A1B11AE1")),
        ".xls": lambda b: b.startswith(bytes.fromhex("D0CF11E0A1B11AE1")),
        ".docx": lambda b: b.startswith(b"PK"),
        ".xlsx": lambda b: b.startswith(b"PK"),
        ".jpg": lambda b: b.startswith(b"\xff\xd8\xff"),
        ".jpeg": lambda b: b.startswith(b"\xff\xd8\xff"),
        ".jfif": lambda b: b.startswith(b"\xff\xd8\xff"),
        ".png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
        ".gif": lambda b: b.startswith((b"GIF87a", b"GIF89a")),
        ".bmp": lambda b: b.startswith(b"BM"),
        ".webp": lambda b: len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WEBP",
        ".tif": lambda b: b.startswith((b"II*\x00", b"MM\x00*")),
        ".tiff": lambda b: b.startswith((b"II*\x00", b"MM\x00*")),
        ".heic": lambda b: has_iso_brand(b, {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"}),
        ".heif": lambda b: has_iso_brand(b, {b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"mif1", b"msf1"}),
        ".avif": lambda b: has_iso_brand(b, {b"avif", b"avis"}),
        ".ico": lambda b: b.startswith(b"\x00\x00\x01\x00"),
    }
    if extension == ".csv":
        return b"\x00" not in head
    check = signatures.get(extension)
    return bool(check and check(head))


@dataclass(frozen=True)
class UploadRecord:
    id: int
    user_name: str
    original_name: str
    stored_name: str
    size_bytes: int
    uploaded_at: str
    processed: int


class Database:
    """封裝 SQLite 紀錄與設定存取。"""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    stored_name TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    processed INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def get_setting(self, key: str, default: str) -> str:
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return str(row["value"]) if row else default

    def set_setting(self, key: str, value: str) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def add_upload(self, user_name: str, original_name: str, stored_name: str, stored_path: str, size_bytes: int) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO uploads(user_name, original_name, stored_name, stored_path, size_bytes, uploaded_at) VALUES(?, ?, ?, ?, ?, ?)",
                (user_name, original_name, stored_name, stored_path, size_bytes, datetime.now().isoformat(timespec="seconds")),
            )

    def list_uploads(self, search: str = "", days: int | None = None) -> list[sqlite3.Row]:
        with closing(self._connect()) as connection, connection:
            clauses: list[str] = []
            parameters: list[object] = []
            if search:
                clauses.append("(user_name LIKE ? OR original_name LIKE ?)")
                parameters.extend((f"%{search}%", f"%{search}%"))
            if days is not None:
                clauses.append("uploaded_at >= datetime('now', 'localtime', ?)")
                parameters.append(f"-{days} days")
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            return connection.execute(f"SELECT * FROM uploads{where} ORDER BY id DESC", parameters).fetchall()

    def mark_processed(self, record_ids: list[int]) -> None:
        if not record_ids:
            return
        placeholders = ",".join("?" for _ in record_ids)
        with closing(self._connect()) as connection, connection:
            connection.execute(f"UPDATE uploads SET processed = 1 WHERE id IN ({placeholders})", record_ids)

    def unprocessed_count(self) -> int:
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT COUNT(*) AS total FROM uploads WHERE processed = 0").fetchone()
        return int(row["total"])

    def delete_records(self, record_ids: list[int]) -> None:
        """刪除已由操作人員明確確認的上傳紀錄。"""
        if not record_ids:
            return
        placeholders = ",".join("?" for _ in record_ids)
        with closing(self._connect()) as connection, connection:
            connection.execute(f"DELETE FROM uploads WHERE id IN ({placeholders})", record_ids)
