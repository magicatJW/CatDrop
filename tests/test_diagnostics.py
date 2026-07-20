import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import diagnostics


class DiagnosticsTests(unittest.TestCase):
    """驗證診斷結果格式、必要資源與失敗判定。"""

    def test_required_resources_exist(self):
        results = diagnostics.check_resources()
        self.assertTrue(results)
        self.assertFalse(any(result.level == "FAIL" for result in results))

    def test_report_contains_environment_and_results(self):
        results = [diagnostics.CheckResult("PASS", "測試項目", "正常")]
        report = diagnostics.render_report(results, quick=True)
        self.assertIn("CatDrop Diagnostic Report", report)
        self.assertIn("[PASS] 測試項目: 正常", report)
        self.assertIn("Mode: quick", report)

    def test_main_returns_failure_exit_code(self):
        failure = diagnostics.CheckResult("FAIL", "測試項目", "故意失敗")
        with mock.patch.object(diagnostics, "run_checks", return_value=[failure]), mock.patch.object(diagnostics, "save_report", return_value=None), mock.patch("sys.argv", ["diagnostics.py"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(diagnostics.main(), 1)


if __name__ == "__main__":
    unittest.main()
