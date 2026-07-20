import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from core import Database
from server import UploadServer


class ServerTests(unittest.TestCase):
    """以實際 HTTP 請求驗證首頁、設定與 PDF 上傳。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "web").mkdir()
        (self.root / "web/index.html").write_text("首頁", encoding="utf-8")
        self.database = Database(self.root / "data.db")
        self.database.set_setting("storage_path", str(self.root / "uploads"))
        self.database.set_setting("max_file_mb", "100")
        self.database.set_setting("enabled_extensions", ".pdf")
        self.database.set_setting("allow_all_file_types", "0")
        self.database.set_setting("upload_enabled", "1")
        self.database.set_setting("ui_language", "en")
        self.server = UploadServer(("127.0.0.1", 0), self.database, self.root)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.assertFalse(self.thread.is_alive())
        self.temp.cleanup()

    def upload_pdf(self, source_name, filename, payload=b"%PDF-1.7\n%%EOF"):
        """建立實際 multipart 請求，供上傳邊界測試共用。"""
        boundary = "----catdrop-test-boundary"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{source_name}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{filename}\"\r\nContent-Type: application/pdf\r\n\r\n"
        ).encode("utf-8") + payload + f"\r\n--{boundary}--\r\n".encode()
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        connection.request("POST", "/api/upload", body, {"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))})
        response = connection.getresponse()
        return response.status, json.loads(response.read())

    def test_home_and_config(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        connection.request("GET", "/")
        self.assertEqual(connection.getresponse().status, 200)
        connection.request("GET", "/api/config")
        response = connection.getresponse()
        self.assertEqual(response.status, 200)
        config = json.loads(response.read())
        self.assertEqual(config["maxFileMb"], 100)
        self.assertEqual(config["extensions"], [".pdf"])
        self.assertFalse(config["allowAllFileTypes"])
        self.assertTrue(config["uploadEnabled"])
        self.assertEqual(config["defaultLanguage"], "en")

    def test_pdf_upload(self):
        status, result = self.upload_pdf("我的手機", "test.pdf")
        self.assertEqual(status, 200)
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(self.database.unprocessed_count(), 1)
        record = self.database.list_uploads()[0]
        self.assertEqual(record["user_name"], "我的手機")
        self.assertTrue((self.root / "uploads" / "我的手機").is_dir())

    def test_duplicate_name_does_not_overwrite(self):
        first_status, _ = self.upload_pdf("平板", "重複檔案.pdf", b"%PDF-1.7\nfirst")
        second_status, _ = self.upload_pdf("平板", "重複檔案.pdf", b"%PDF-1.7\nsecond")
        self.assertEqual((first_status, second_status), (200, 200))
        records = self.database.list_uploads()
        self.assertEqual(len(records), 2)
        stored_paths = [Path(row["stored_path"]) for row in records]
        self.assertEqual(len({path.name for path in stored_paths}), 2)
        self.assertEqual({path.read_bytes() for path in stored_paths}, {b"%PDF-1.7\nfirst", b"%PDF-1.7\nsecond"})

    def test_path_cleanup_stays_inside_storage(self):
        status, result = self.upload_pdf("../../私人/手機", "../../報告.pdf")
        self.assertEqual(status, 200)
        self.assertEqual(result["accepted"], 1)
        record = self.database.list_uploads()[0]
        storage_root = (self.root / "uploads").resolve()
        stored_path = Path(record["stored_path"]).resolve()
        self.assertEqual(stored_path.parent.parent, storage_root)
        self.assertNotIn("..", stored_path.relative_to(storage_root).parts)

    def test_utf8_traditional_chinese_filename(self):
        status, result = self.upload_pdf("主要手機", "繁中測試檔案.pdf")
        self.assertEqual(status, 200)
        self.assertEqual(result["accepted"], 1)
        record = self.database.list_uploads()[0]
        self.assertEqual(record["original_name"], "繁中測試檔案.pdf")
        self.assertTrue(Path(record["stored_path"]).is_file())

    def test_paused_upload_is_rejected_without_writing(self):
        self.database.set_setting("upload_enabled", "0")
        status, result = self.upload_pdf("手機", "paused.pdf")
        self.assertEqual(status, 503)
        self.assertFalse(result["ok"])
        self.assertEqual(self.database.unprocessed_count(), 0)

    def test_disabled_file_type_is_rejected(self):
        self.database.set_setting("enabled_extensions", ".png")
        status, result = self.upload_pdf("手機", "disabled.pdf")
        self.assertEqual(status, 200)
        self.assertEqual(result["accepted"], 0)
        self.assertEqual(self.database.unprocessed_count(), 0)

    def test_all_file_types_mode_accepts_unlisted_payload(self):
        """全格式模式應接受任意副檔名，同時保留一般儲存與紀錄流程。"""
        self.database.set_setting("allow_all_file_types", "1")
        status, result = self.upload_pdf("手機", "封存資料.bin", b"\x00\x01" + "任意內容".encode("utf-8"))
        self.assertEqual(status, 200)
        self.assertEqual(result["accepted"], 1)
        record = self.database.list_uploads()[0]
        self.assertEqual(record["original_name"], "封存資料.bin")
        self.assertTrue(Path(record["stored_path"]).is_file())

        no_extension_status, no_extension_result = self.upload_pdf("手機", "README", "無副檔名".encode("utf-8"))
        self.assertEqual(no_extension_status, 200)
        self.assertEqual(no_extension_result["accepted"], 1)

        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        connection.request("GET", "/api/config")
        config = json.loads(connection.getresponse().read())
        self.assertTrue(config["allowAllFileTypes"])


if __name__ == "__main__":
    unittest.main()
