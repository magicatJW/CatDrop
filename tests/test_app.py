import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import app
from core import ALLOWED_EXTENSIONS, LEGACY_ALLOWED_EXTENSIONS, Database, parse_enabled_extensions, serialize_enabled_extensions


class AppRuntimeTests(unittest.TestCase):
    """驗證應用程式網址偵測與錯誤日誌基礎流程。"""

    def test_detect_lan_ip_returns_ipv4_text(self):
        address = app.detect_lan_ip()
        parts = address.split(".")
        self.assertEqual(len(parts), 4)
        self.assertTrue(all(part.isdigit() and 0 <= int(part) <= 255 for part in parts))

    def test_lan_address_validation_only_accepts_private_ipv4(self):
        self.assertTrue(app.is_usable_lan_ipv4("192.168.1.20"))
        self.assertTrue(app.is_usable_lan_ipv4("172.16.10.5"))
        self.assertFalse(app.is_usable_lan_ipv4("127.0.0.1"))
        self.assertFalse(app.is_usable_lan_ipv4("8.8.8.8"))
        self.assertFalse(app.is_usable_lan_ipv4("not-an-ip"))

    def test_resolve_lan_url_repairs_stale_address_and_has_error_code(self):
        with mock.patch.object(app, "discover_lan_ipv4_candidates", return_value=["192.168.1.20"]), mock.patch.object(app, "probe_lan_service", return_value=True):
            address, url, repaired = app.resolve_lan_url("http://127.0.0.1:8080")
        self.assertEqual(address, "192.168.1.20")
        self.assertEqual(url, "http://192.168.1.20:8080")
        self.assertTrue(repaired)

        with mock.patch.object(app, "discover_lan_ipv4_candidates", return_value=[]):
            with self.assertRaises(app.LanUrlError) as context:
                app.resolve_lan_url("http://127.0.0.1:8080")
        self.assertEqual(context.exception.code, "CD-NET-001")

    def test_prepare_qrcode_rejects_loopback_and_writes_verified_url(self):
        with tempfile.TemporaryDirectory() as directory:
            image = mock.Mock()
            with mock.patch.object(app.qrcode, "make", return_value=image) as make:
                target = app.prepare_qrcode("http://192.168.1.20:8080", "192.168.1.20", Path(directory))
            make.assert_called_once_with("http://192.168.1.20:8080")
            image.save.assert_called_once_with(target)
            self.assertEqual(target.name, "website_192.168.1.20.png")
            with self.assertRaises(app.LanUrlError) as context:
                app.prepare_qrcode("http://127.0.0.1:8080", "127.0.0.1", Path(directory))
            self.assertEqual(context.exception.code, "CD-NET-003")

    def test_copy_site_url_updates_clipboard(self):
        panel = SimpleNamespace(
            site_url="http://192.168.1.20:8080",
            clipboard_clear=mock.Mock(),
            clipboard_append=mock.Mock(),
            update_idletasks=mock.Mock(),
            _refresh_lan_url=mock.Mock(return_value=True),
            _t=lambda key, **values: key,
        )
        with mock.patch.object(app.messagebox, "showinfo"):
            app.ControlPanel._copy_site_url(panel)
        panel.clipboard_clear.assert_called_once_with()
        panel._refresh_lan_url.assert_called_once_with()
        panel.clipboard_append.assert_called_once_with("http://192.168.1.20:8080")
        panel.update_idletasks.assert_called_once_with()

    def test_qrcode_write_failure_reports_fixed_error_code(self):
        panel = SimpleNamespace(
            site_url="http://192.168.1.20:8080",
            ip_address="192.168.1.20",
            _refresh_lan_url=mock.Mock(return_value=True),
            _t=lambda key, **values: str(values.get("code", key)),
        )
        with mock.patch.object(app, "prepare_qrcode", side_effect=RuntimeError("write failed")), mock.patch.object(app.LOGGER, "exception"), mock.patch.object(app.messagebox, "showerror") as showerror:
            app.ControlPanel._generate_qrcode(panel)
        self.assertIn("CD-QR-001", showerror.call_args.args)

    def test_rotating_log_is_created(self):
        original_log_dir = app.LOG_DIR
        original_handlers = list(app.LOGGER.handlers)
        try:
            for handler in original_handlers:
                app.LOGGER.removeHandler(handler)
            with tempfile.TemporaryDirectory() as directory:
                app.LOG_DIR = Path(directory)
                log_path = app.configure_logging()
                app.LOGGER.error("測試錯誤紀錄")
                for handler in app.LOGGER.handlers:
                    handler.flush()
                self.assertTrue(log_path.is_file())
                self.assertIn("測試錯誤紀錄", log_path.read_text(encoding="utf-8"))
                for handler in list(app.LOGGER.handlers):
                    handler.close()
                    app.LOGGER.removeHandler(handler)
        finally:
            for handler in list(app.LOGGER.handlers):
                handler.close()
                app.LOGGER.removeHandler(handler)
            for handler in original_handlers:
                app.LOGGER.addHandler(handler)
            app.LOG_DIR = original_log_dir

    def test_legacy_full_allowlist_is_upgraded_without_overwriting_custom_selection(self):
        """舊版完整白名單應加入新格式，使用者自訂子集合則保持不變。"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy_database = Database(root / "legacy.db")
            legacy_database.set_setting("enabled_extensions", serialize_enabled_extensions(LEGACY_ALLOWED_EXTENSIONS))
            app.ControlPanel._initialize_settings(SimpleNamespace(database=legacy_database))
            self.assertEqual(parse_enabled_extensions(legacy_database.get_setting("enabled_extensions", "")), ALLOWED_EXTENSIONS)

            custom_database = Database(root / "custom.db")
            custom_database.set_setting("enabled_extensions", ".pdf,.png")
            app.ControlPanel._initialize_settings(SimpleNamespace(database=custom_database))
            self.assertEqual(custom_database.get_setting("enabled_extensions", ""), ".pdf,.png")


if __name__ == "__main__":
    unittest.main()
