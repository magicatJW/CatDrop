from __future__ import annotations

import argparse
import importlib
import platform
import socket
import sqlite3
import sys
import tempfile
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
REQUIRED_FILES = (
    "app.py",
    "core.py",
    "server.py",
    "ui_text.py",
    "web/index.html",
    "web/app.js",
    "web/styles.css",
)


@dataclass(frozen=True)
class CheckResult:
    """保存單一檢查項目的層級、名稱與說明。"""

    level: str
    name: str
    detail: str


def detect_lan_ip() -> str:
    """偵測目前路由使用的 IPv4 位址，失敗時回退本機位址。"""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 80))
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def check_python() -> CheckResult:
    """確認 Python 版本符合專案最低需求。"""
    version = platform.python_version()
    if sys.version_info < (3, 11):
        return CheckResult("FAIL", "Python", f"需要 Python 3.11 以上，目前為 {version}")
    return CheckResult("PASS", "Python", f"{version} · {sys.executable}")


def check_dependencies() -> list[CheckResult]:
    """確認執行與打包所需模組可匯入。"""
    results: list[CheckResult] = []
    modules = (("tkinter", "Tkinter"), ("qrcode", "qrcode"), ("PIL", "Pillow"))
    for module_name, label in modules:
        try:
            importlib.import_module(module_name)
            results.append(CheckResult("PASS", label, "可正常匯入"))
        except Exception as error:
            results.append(CheckResult("FAIL", label, f"無法匯入：{error}"))
    return results


def check_resources() -> list[CheckResult]:
    """確認執行時必要程式與網頁檔案存在。"""
    results: list[CheckResult] = []
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        level = "PASS" if path.is_file() else "FAIL"
        detail = "存在" if path.is_file() else "缺少必要檔案"
        results.append(CheckResult(level, relative, detail))
    return results


def check_write_and_sqlite() -> list[CheckResult]:
    """在專案根目錄驗證寫入權限與 SQLite 基本操作。"""
    try:
        with tempfile.TemporaryDirectory(prefix=".catdrop-check-", dir=ROOT) as directory:
            test_dir = Path(directory)
            marker = test_dir / "write-test.txt"
            marker.write_text("CatDrop 自檢", encoding="utf-8")
            database_path = test_dir / "diagnostic.db"
            with closing(sqlite3.connect(database_path)) as connection, connection:
                connection.execute("CREATE TABLE check_result(value TEXT NOT NULL)")
                connection.execute("INSERT INTO check_result(value) VALUES(?)", ("通過",))
                value = connection.execute("SELECT value FROM check_result").fetchone()[0]
            if marker.read_text(encoding="utf-8") != "CatDrop 自檢" or value != "通過":
                raise RuntimeError("寫入後讀回的內容不一致")
        return [
            CheckResult("PASS", "寫入權限", str(ROOT)),
            CheckResult("PASS", "SQLite", "建立、寫入與讀取正常"),
        ]
    except Exception as error:
        return [CheckResult("FAIL", "寫入／SQLite", str(error))]


def check_port(port: int = 8080) -> CheckResult:
    """確認 HTTP 服務預定通訊埠目前可供繫結。"""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        listener.bind(("0.0.0.0", port))
        return CheckResult("PASS", f"TCP {port}", "目前可用")
    except OSError as error:
        return CheckResult("FAIL", f"TCP {port}", f"無法使用：{error}")
    finally:
        listener.close()


def check_network() -> CheckResult:
    """顯示偵測到的網址，並標示只能本機使用的回退狀態。"""
    address = detect_lan_ip()
    if address == "127.0.0.1":
        return CheckResult("WARN", "區網位址", "僅偵測到 127.0.0.1，其他裝置目前無法連線")
    return CheckResult("PASS", "區網位址", f"http://{address}:8080")


def run_checks(quick: bool = False) -> list[CheckResult]:
    """執行快速啟動檢查或完整環境檢查。"""
    results = [check_python(), *check_dependencies(), *check_resources(), check_network()]
    if not quick:
        results.extend(check_write_and_sqlite())
        results.append(check_port())
    return results


def render_report(results: list[CheckResult], quick: bool) -> str:
    """產生可直接附加到錯誤回報的純文字診斷報告。"""
    lines = [
        "CatDrop Diagnostic Report",
        f"Time: {datetime.now().isoformat(timespec='seconds')}",
        f"Mode: {'quick' if quick else 'full'}",
        f"OS: {platform.platform()}",
        f"Project: {ROOT}",
        "",
    ]
    lines.extend(f"[{result.level}] {result.name}: {result.detail}" for result in results)
    return "\n".join(lines) + "\n"


def save_report(report: str) -> Path | None:
    """保存最新診斷報告；若根目錄無法寫入則只輸出到終端。"""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        target = LOG_DIR / "diagnostic-latest.txt"
        target.write_text(report, encoding="utf-8")
        return target
    except OSError:
        return None


def main() -> int:
    """執行命令列自檢並以結束碼回報是否存在失敗項目。"""
    parser = argparse.ArgumentParser(description="CatDrop 環境與執行條件自檢")
    parser.add_argument("--quick", action="store_true", help="只執行啟動前必要檢查")
    args = parser.parse_args()
    results = run_checks(quick=args.quick)
    report = render_report(results, args.quick)
    print(report, end="")
    saved = save_report(report)
    print(f"Report: {saved}" if saved else "Report: 無法寫入 logs 資料夾")
    return 1 if any(result.level == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
