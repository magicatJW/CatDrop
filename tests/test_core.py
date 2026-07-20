import tempfile
import unittest
from pathlib import Path

from core import Database, file_signature_matches, parse_enabled_extensions, safe_name, serialize_enabled_extensions, setting_is_enabled, sort_upload_rows, unique_filename


class CoreTests(unittest.TestCase):
    """驗證檔名安全、檔頭白名單與人工處理狀態。"""

    def test_safe_name_removes_path_characters(self):
        self.assertEqual(safe_name("../王/小明"), ".._王_小明")
        self.assertFalse("/" in safe_name("甲/乙"))

    def test_reserved_windows_name_is_prefixed(self):
        self.assertEqual(safe_name("CON"), "_CON")

    def test_unique_filename_keeps_extension(self):
        result = unique_filename("../../報價單.PDF")
        self.assertTrue(result.endswith(".pdf"))
        self.assertNotIn("/", result)

    def test_signatures(self):
        self.assertTrue(file_signature_matches(".pdf", b"%PDF-1.7"))
        self.assertTrue(file_signature_matches(".png", b"\x89PNG\r\n\x1a\n"))
        self.assertTrue(file_signature_matches(".csv", "姓名,金額".encode("utf-8")))
        self.assertTrue(file_signature_matches(".jfif", b"\xff\xd8\xff\xe0"))
        self.assertTrue(file_signature_matches(".ico", b"\x00\x00\x01\x00"))
        self.assertTrue(file_signature_matches(".avif", b"\x00\x00\x00\x18ftypavif\x00\x00\x00\x00avif"))
        self.assertTrue(file_signature_matches(".heif", b"\x00\x00\x00\x18ftypmif1\x00\x00\x00\x00heic"))
        self.assertFalse(file_signature_matches(".pdf", b"not a pdf"))
        self.assertFalse(file_signature_matches(".avif", b"\x00\x00\x00\x18ftypmif1\x00\x00\x00\x00heic"))

    def test_database_processed_flow(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "test.db")
            database.add_upload("王小明", "a.pdf", "stored.pdf", "x/stored.pdf", 123)
            self.assertEqual(database.unprocessed_count(), 1)
            record_id = int(database.list_uploads()[0]["id"])
            database.mark_processed([record_id])
            self.assertEqual(database.unprocessed_count(), 0)

    def test_enabled_extensions_are_limited_to_allowlist(self):
        self.assertEqual(parse_enabled_extensions(".pdf,.png,.exe"), {".pdf", ".png"})
        self.assertIn(".docx", parse_enabled_extensions(""))
        self.assertTrue({".avif", ".heif", ".jfif", ".ico"}.issubset(parse_enabled_extensions("")))
        self.assertEqual(serialize_enabled_extensions({".png", ".pdf", ".exe"}), ".pdf,.png")

    def test_boolean_setting_uses_explicit_database_value(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "test.db")
            self.assertTrue(setting_is_enabled(database, "upload_enabled"))
            database.set_setting("upload_enabled", "0")
            self.assertFalse(setting_is_enabled(database, "upload_enabled"))

    def test_upload_rows_sort_by_raw_status_and_size(self):
        rows = [
            {"id": 1, "processed": 1, "user_name": "B", "original_name": "b.pdf", "size_bytes": 20, "uploaded_at": "2026-01-01T10:00:00"},
            {"id": 2, "processed": 0, "user_name": "A", "original_name": "a.pdf", "size_bytes": 100, "uploaded_at": "2026-01-02T10:00:00"},
        ]
        self.assertEqual([row["id"] for row in sort_upload_rows(rows, "status", False)], [2, 1])
        self.assertEqual([row["id"] for row in sort_upload_rows(rows, "size", True)], [2, 1])


if __name__ == "__main__":
    unittest.main()
