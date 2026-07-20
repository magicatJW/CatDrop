import unittest

from ui_text import TEXTS, text


class UiTextTests(unittest.TestCase):
    """驗證控制台兩種語言都有必要狀態文字。"""

    def test_chinese_and_english_status_text(self):
        self.assertEqual(text("zh", "accept_paused"), "已暫停")
        self.assertEqual(text("en", "accept_paused"), "Paused")

    def test_unknown_language_falls_back_to_chinese(self):
        self.assertEqual(text("unknown", "settings"), "設定")

    def test_both_languages_have_the_same_keys(self):
        self.assertEqual(set(TEXTS["zh"]), set(TEXTS["en"]))

    def test_all_file_types_warning_is_explicit(self):
        self.assertIn("略過檔案內容特徵驗證", text("zh", "allow_all_warning"))
        self.assertIn("without file-signature validation", text("en", "allow_all_warning"))


if __name__ == "__main__":
    unittest.main()
