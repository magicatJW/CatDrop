from __future__ import annotations

import csv
import ctypes
import http.client
import ipaddress
import logging
import os
import socket
import sys
import threading
import tkinter as tk
import webbrowser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse

import qrcode

from core import ALLOWED_EXTENSIONS, LEGACY_ALLOWED_EXTENSIONS, Database, parse_enabled_extensions, serialize_enabled_extensions, setting_is_enabled, sort_upload_rows
from server import UploadServer
from ui_text import text


# 單檔 EXE 執行時，程式資源位於暫存目錄，使用者資料則固定放在 EXE 旁。
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
DATA_DIR = APP_DIR / "data"
QR_DIR = APP_DIR / "qrcodes"
LOG_DIR = APP_DIR / "logs"
DEFAULT_STORAGE = APP_DIR / "received_files"
HOST = "0.0.0.0"
PORT = 8080
APP_NAME = "CatDrop"
PRIVATE_IPV4_NETWORKS = tuple(ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


class LanUrlError(RuntimeError):
    """包含固定錯誤碼的區網網址檢查錯誤。"""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def is_usable_lan_ipv4(value: str) -> bool:
    """只接受可供一般私人區網使用的 RFC 1918 IPv4 位址。"""
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return address.version == 4 and any(address in network for network in PRIVATE_IPV4_NETWORKS)


def discover_lan_ipv4_candidates() -> list[str]:
    """依預設路由與主機網卡順序收集可用的私人 IPv4 候選。"""
    candidates: list[str] = []

    def add(value: str) -> None:
        if is_usable_lan_ipv4(value) and value not in candidates:
            candidates.append(value)

    for target in (("192.0.2.1", 80), ("198.51.100.1", 80)):
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(target)
            add(str(probe.getsockname()[0]))
        except OSError:
            pass
        finally:
            probe.close()
    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET, socket.SOCK_STREAM):
            add(str(item[4][0]))
    except OSError:
        pass
    return candidates


def detect_lan_ip() -> str:
    """偵測目前可用的區網位址，離線或失敗時回退至本機位址。"""
    candidates = discover_lan_ipv4_candidates()
    return candidates[0] if candidates else "127.0.0.1"


def probe_lan_service(address: str, port: int, timeout: float = 0.8) -> bool:
    """確認目前 HTTP 首頁可透過指定區網位址回應。"""
    connection = http.client.HTTPConnection(address, port, timeout=timeout)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        response.read(1)
        return response.status == 200
    except OSError:
        return False
    finally:
        connection.close()


def resolve_lan_url(current_url: str, port: int = PORT) -> tuple[str, str, bool]:
    """驗證目前網址並嘗試其他網卡，自動修復為可回應的區網網址。"""
    candidates = discover_lan_ipv4_candidates()
    try:
        current_host = str(urlparse(current_url).hostname or "")
    except ValueError:
        current_host = ""
    if is_usable_lan_ipv4(current_host) and current_host not in candidates:
        candidates.insert(0, current_host)
    if not candidates:
        raise LanUrlError("CD-NET-001", "找不到可用的私人區網 IPv4 位址。")
    for address in candidates:
        if probe_lan_service(address, port):
            url = f"http://{address}:{port}"
            return address, url, url != current_url
    raise LanUrlError("CD-NET-002", "已找到私人區網位址，但 CatDrop 首頁無法透過該位址回應。")


IP_ADDRESS = detect_lan_ip()
SITE_URL = f"http://{IP_ADDRESS}:{PORT}"
_INSTANCE_MUTEX = None
LOGGER = logging.getLogger("catdrop")


def configure_logging() -> Path:
    """建立輪替式應用程式日誌，避免長期執行無限制占用空間。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "catdrop.log"
    if not LOGGER.handlers:
        handler = RotatingFileHandler(log_path, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)
        LOGGER.propagate = False
    return log_path


def show_fatal_error(error: BaseException, log_path: Path) -> None:
    """嘗試以視窗顯示致命錯誤；視窗不可用時仍保留日誌證據。"""
    try:
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("CatDrop 無法啟動", f"{error}\n\n錯誤紀錄：{log_path}")
        error_root.destroy()
    except Exception:
        return


def acquire_single_instance() -> bool:
    """使用 Windows 命名 Mutex，避免同一後台重複啟動。"""
    global _INSTANCE_MUTEX
    if os.name != "nt":
        return True
    _INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\CatDropControlPanel")
    return bool(_INSTANCE_MUTEX) and ctypes.windll.kernel32.GetLastError() != 183


def prepare_qrcode(site_url: str, ip_address: str, output_dir: Path | None = None) -> Path:
    """驗證區網網址後離線產生對應裝置的 QR Code。"""
    parsed = urlparse(site_url)
    if parsed.scheme != "http" or parsed.hostname != ip_address or not is_usable_lan_ipv4(ip_address):
        raise LanUrlError("CD-NET-003", "區網網址格式或位址不正確。")
    target_dir = output_dir or QR_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"website_{ip_address}.png"
    qrcode.make(site_url).save(target)
    return target


def startup_shortcut_path() -> Path:
    """取得目前使用者的 Windows 啟動資料夾捷徑位置。"""
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    return appdata / "Microsoft/Windows/Start Menu/Programs/Startup/CatDrop.cmd"


class ControlPanel(tk.Tk):
    """提供服務控制、上傳歸檔、排序、多選與設定管理。"""

    def __init__(self) -> None:
        super().__init__()
        self.geometry("1120x700")
        self.minsize(920, 580)
        self.database = Database(DATA_DIR / "uploads.db")
        self._initialize_settings()
        self.language = self.database.get_setting("ui_language", "zh")
        if self.language not in {"zh", "en"}:
            self.language = "zh"
        self.sort_column = "time"
        self.sort_descending = True
        self.ip_address = IP_ADDRESS
        self.site_url = SITE_URL
        self.http_server: UploadServer | None = None
        self.server_thread: threading.Thread | None = None
        self.settings_window: tk.Toplevel | None = None
        self._drag_anchor: str | None = None
        self._build_ui()
        self._start_server()
        self.refresh_records()
        self.after(2000, self._poll)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _initialize_settings(self) -> None:
        """補上新版本設定預設值，不覆蓋既有使用者設定。"""
        defaults = {
            "storage_path": str(DEFAULT_STORAGE),
            "max_file_mb": "100",
            "ui_language": "zh",
            "enabled_extensions": serialize_enabled_extensions(set(ALLOWED_EXTENSIONS)),
            "allow_all_file_types": "0",
            "upload_enabled": "1",
            "show_upload_toggle": "1",
        }
        for key, value in defaults.items():
            if not self.database.get_setting(key, ""):
                self.database.set_setting(key, value)
        enabled_value = self.database.get_setting("enabled_extensions", "")
        if parse_enabled_extensions(enabled_value) == LEGACY_ALLOWED_EXTENSIONS:
            # 只升級未自訂的舊版完整白名單，避免覆蓋使用者刻意取消的格式。
            self.database.set_setting("enabled_extensions", serialize_enabled_extensions(set(ALLOWED_EXTENSIONS)))

    def _t(self, key: str, **values: object) -> str:
        """取得目前控制台語言的介面文字。"""
        return text(self.language, key, **values)

    def report_callback_exception(self, exception_type, exception, traceback_object) -> None:
        """記錄 Tkinter 回呼中的未預期錯誤並告知日誌位置。"""
        LOGGER.error("介面操作發生未預期錯誤", exc_info=(exception_type, exception, traceback_object))
        messagebox.showerror("CatDrop 發生錯誤", f"{exception}\n\n詳細資訊已寫入：{LOG_DIR / 'catdrop.log'}")

    def _build_ui(self) -> None:
        """建立目前語言的控制台，設定儲存後可安全重建。"""
        self.title(self._t("window_title"))
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Microsoft JhengHei UI", 18, "bold"))
        style.configure("Notice.TLabel", foreground="#b24d1d", font=("Microsoft JhengHei UI", 11, "bold"))
        style.configure("Open.TButton", foreground="#146c43")
        style.configure("Paused.TButton", foreground="#9a302d")

        self.main_container = ttk.Frame(self, padding=18)
        self.main_container.pack(fill="both", expand=True)
        header = ttk.Frame(self.main_container)
        header.pack(fill="x")
        ttk.Label(header, text=self._t("panel_title"), style="Title.TLabel").pack(side="left")
        ttk.Button(header, text=self._t("settings"), command=self._open_settings).pack(side="right")
        if setting_is_enabled(self.database, "show_upload_toggle"):
            self.upload_toggle_button = ttk.Button(header, command=self._toggle_upload_enabled)
            self.upload_toggle_button.pack(side="right", padx=8)
            self._update_upload_toggle_button()
        else:
            self.upload_toggle_button = None
        self.status_label = ttk.Label(header, text=self._t("server_starting"))
        self.status_label.pack(side="right", padx=(0, 8))

        info = ttk.LabelFrame(self.main_container, text=self._t("connection_info"), padding=12)
        info.pack(fill="x", pady=(14, 10))
        self.lan_url_label = ttk.Label(info, text=self._t("lan_url", url=self.site_url))
        self.lan_url_label.pack(side="left")
        ttk.Button(info, text=self._t("open_site"), command=lambda: webbrowser.open(self.site_url)).pack(side="right")
        ttk.Button(info, text=self._t("open_qr"), command=lambda: self._open_path(QR_DIR)).pack(side="right", padx=8)
        self.generate_qr_button = ttk.Button(info, text=self._t("generate_qr"), command=self._generate_qrcode)
        self.generate_qr_button.pack(side="right")
        self.copy_url_button = ttk.Button(info, text=self._t("copy_url"), command=self._copy_site_url)
        self.copy_url_button.pack(side="right", padx=8)

        toolbar = ttk.Frame(self.main_container)
        toolbar.pack(fill="x", pady=(4, 8))
        self.notice_label = ttk.Label(toolbar, text="", style="Notice.TLabel")
        self.notice_label.pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.search_var, width=24).pack(side="right")
        ttk.Button(toolbar, text=self._t("search"), command=self.refresh_records).pack(side="right", padx=5)
        self.date_filter_var = tk.StringVar(value=self._t("date_all"))
        self.date_filter = ttk.Combobox(toolbar, textvariable=self.date_filter_var, values=self._date_labels(), state="readonly", width=14)
        self.date_filter.pack(side="right", padx=5)
        self.date_filter.bind("<<ComboboxSelected>>", lambda _event: self.refresh_records())
        ttk.Button(toolbar, text=self._t("export"), command=self._export_records).pack(side="right", padx=5)
        ttk.Button(toolbar, text=self._t("delete"), command=self._delete_selected).pack(side="right", padx=5)
        ttk.Button(toolbar, text=self._t("open_file"), command=self._open_selected).pack(side="right", padx=5)
        ttk.Button(toolbar, text=self._t("mark_processed"), command=self._mark_processed).pack(side="right", padx=5)
        ttk.Button(toolbar, text=self._t("select_all"), command=self._select_all).pack(side="right", padx=5)

        columns = ("status", "user", "name", "size", "time")
        table = ttk.Frame(self.main_container)
        table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="extended")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("user", width=150)
        self.tree.column("name", width=410)
        self.tree.column("size", width=110, anchor="e")
        self.tree.column("time", width=180)
        self._update_sort_headings()
        self.tree.bind("<ButtonPress-1>", self._begin_drag_selection, add="+")
        self.tree.bind("<B1-Motion>", self._drag_select, add="+")
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _rebuild_ui(self) -> None:
        """語言或按鈕顯示設定變更後，保留篩選與選取狀態重建介面。"""
        search = self.search_var.get() if hasattr(self, "search_var") else ""
        days = self._selected_days() if hasattr(self, "date_filter_var") else None
        selected = set(self.tree.selection()) if hasattr(self, "tree") else set()
        self.main_container.destroy()
        self._build_ui()
        self.search_var.set(search)
        self.date_filter_var.set(self._date_label_for_days(days))
        if self.http_server:
            self.status_label.config(text=self._t("server_running", port=PORT))
        self.refresh_records()
        for item in selected:
            if self.tree.exists(item):
                self.tree.selection_add(item)

    def _date_labels(self) -> tuple[str, str, str, str]:
        """回傳目前語言的日期篩選選項。"""
        return (self._t("date_all"), self._t("date_today"), self._t("date_7"), self._t("date_30"))

    def _date_label_for_days(self, days: int | None) -> str:
        """將查詢天數轉為目前語言的選項文字。"""
        return {1: self._t("date_today"), 7: self._t("date_7"), 30: self._t("date_30")}.get(days, self._t("date_all"))

    def _start_server(self) -> None:
        try:
            self.http_server = UploadServer((HOST, PORT), self.database, RESOURCE_DIR)
            self.server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            self.server_thread.start()
            self.status_label.config(text=self._t("server_running", port=PORT))
            LOGGER.info("HTTP 服務已啟動：%s", self.site_url)
        except OSError as error:
            LOGGER.exception("HTTP 服務啟動失敗")
            self.status_label.config(text=self._t("server_failed"))
            messagebox.showerror(self._t("server_error_title"), self._t("server_error", port=PORT, error=error))

    def _sort_by(self, column: str) -> None:
        """點擊同一欄位時切換升降冪，切換欄位時先使用升冪。"""
        if self.sort_column == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = column
            self.sort_descending = False
        self._update_sort_headings()
        self.refresh_records()

    def _update_sort_headings(self) -> None:
        """更新可點擊欄位標題與目前排序方向。"""
        labels = {
            "status": self._t("column_status"),
            "user": self._t("column_source"),
            "name": self._t("column_name"),
            "size": self._t("column_size"),
            "time": self._t("column_time"),
        }
        for column, label in labels.items():
            arrow = " ▼" if self.sort_descending else " ▲"
            heading = label + arrow if column == self.sort_column else label
            self.tree.heading(column, text=heading, command=lambda selected=column: self._sort_by(selected))

    def refresh_records(self) -> None:
        selected = set(self.tree.selection())
        self.tree.delete(*self.tree.get_children())
        rows = self.database.list_uploads(self.search_var.get().strip(), self._selected_days())
        for row in sort_upload_rows(rows, self.sort_column, self.sort_descending):
            size = f"{row['size_bytes'] / 1048576:.2f} MB" if row["size_bytes"] >= 1048576 else f"{max(1, row['size_bytes'] // 1024)} KB"
            status = self._t("status_processed") if row["processed"] else self._t("status_new")
            self.tree.insert("", "end", iid=str(row["id"]), values=(status, row["user_name"], row["original_name"], size, row["uploaded_at"].replace("T", " ")))
        for item in selected:
            if self.tree.exists(item):
                self.tree.selection_add(item)
        count = self.database.unprocessed_count()
        self.notice_label.config(text=self._t("notice_new", count=count) if count else self._t("notice_none"))

    def _begin_drag_selection(self, event) -> None:
        """記住滑鼠拖曳起點，僅在資料列區域啟用範圍選取。"""
        if self.tree.identify_region(event.x, event.y) != "cell":
            self._drag_anchor = None
            return
        self._drag_anchor = self.tree.identify_row(event.y) or None

    def _drag_select(self, event) -> None:
        """按住滑鼠拖曳時選取起點與目前資料列之間的所有檔案。"""
        current = self.tree.identify_row(event.y)
        if not self._drag_anchor or not current:
            return
        rows = list(self.tree.get_children())
        try:
            start = rows.index(self._drag_anchor)
            end = rows.index(current)
        except ValueError:
            return
        low, high = sorted((start, end))
        self.tree.selection_set(rows[low:high + 1])

    def _select_all(self) -> None:
        """選取目前篩選結果內的全部檔案紀錄。"""
        self.tree.selection_set(self.tree.get_children())

    def _poll(self) -> None:
        self.refresh_records()
        self.after(2000, self._poll)

    def _upload_enabled(self) -> bool:
        """取得目前是否開放檔案上傳。"""
        return setting_is_enabled(self.database, "upload_enabled")

    def _toggle_upload_enabled(self) -> None:
        """由控制台右上角切換接收狀態，HTTP 網頁服務保持運作。"""
        enabled = not self._upload_enabled()
        self.database.set_setting("upload_enabled", "1" if enabled else "0")
        LOGGER.info("檔案接收狀態切換為：%s", "開放" if enabled else "暫停")
        self._update_upload_toggle_button()

    def _update_upload_toggle_button(self) -> None:
        """同步控制台接收狀態按鈕文字與樣式。"""
        if not self.upload_toggle_button:
            return
        enabled = self._upload_enabled()
        self.upload_toggle_button.config(text=self._t("accept_open") if enabled else self._t("accept_paused"), style="Open.TButton" if enabled else "Paused.TButton")

    def _open_settings(self) -> None:
        """開啟單一設定視窗，避免同時寫入互相衝突的設定。"""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
        window = tk.Toplevel(self)
        self.settings_window = window
        window.geometry("760x760")
        window.minsize(680, 680)
        window.transient(self)
        window.language_var = tk.StringVar(value=self.language)
        window.storage_var = tk.StringVar(value=self.database.get_setting("storage_path", str(DEFAULT_STORAGE)))
        window.max_mb_var = tk.StringVar(value=self.database.get_setting("max_file_mb", "100"))
        window.startup_var = tk.BooleanVar(value=startup_shortcut_path().exists())
        enabled_extensions = parse_enabled_extensions(self.database.get_setting("enabled_extensions", ""))
        window.extension_vars = {extension: tk.BooleanVar(value=extension in enabled_extensions) for extension in sorted(ALLOWED_EXTENSIONS)}
        window.allow_all_file_types_var = tk.BooleanVar(value=setting_is_enabled(self.database, "allow_all_file_types", default=False))
        window.upload_enabled_var = tk.BooleanVar(value=self._upload_enabled())
        window.show_toggle_var = tk.BooleanVar(value=setting_is_enabled(self.database, "show_upload_toggle"))
        window.protocol("WM_DELETE_WINDOW", self._close_settings)
        self._render_settings(window)
        window.grab_set()

    def _render_settings(self, window: tk.Toplevel) -> None:
        """依設定視窗選定的語言重建內容，尚未按儲存前不修改資料庫。"""
        language = window.language_var.get()
        local_text = lambda key, **values: text(language, key, **values)
        window.title(local_text("settings_title"))
        for child in window.winfo_children():
            child.destroy()
        content = ttk.Frame(window, padding=18)
        content.pack(fill="both", expand=True)

        language_frame = ttk.LabelFrame(content, text=local_text("language"), padding=12)
        language_frame.pack(fill="x", pady=(0, 10))
        ttk.Radiobutton(language_frame, text=local_text("chinese"), variable=window.language_var, value="zh", command=lambda: window.after_idle(lambda: self._render_settings(window))).pack(side="left")
        ttk.Radiobutton(language_frame, text=local_text("english"), variable=window.language_var, value="en", command=lambda: window.after_idle(lambda: self._render_settings(window))).pack(side="left", padx=18)

        general = ttk.LabelFrame(content, text=local_text("settings"), padding=12)
        general.pack(fill="x", pady=(0, 10))
        ttk.Label(general, text=local_text("storage_path")).grid(row=0, column=0, sticky="w")
        ttk.Entry(general, textvariable=window.storage_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(general, text=local_text("choose"), command=lambda: self._choose_storage_for_settings(window, language)).grid(row=0, column=2)
        ttk.Label(general, text=local_text("max_file_mb")).grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(general, from_=1, to=2048, textvariable=window.max_mb_var, width=10).grid(row=1, column=1, sticky="w", padx=8, pady=(10, 0))
        ttk.Checkbutton(general, text=local_text("startup"), variable=window.startup_var).grid(row=2, column=1, sticky="w", padx=8, pady=(10, 0))
        general.columnconfigure(1, weight=1)

        extensions = ttk.LabelFrame(content, text=local_text("allowed_types"), padding=12)
        extensions.pack(fill="x", pady=(0, 10))
        ttk.Checkbutton(
            extensions,
            text=local_text("allow_all_file_types"),
            variable=window.allow_all_file_types_var,
            command=lambda: self._update_settings_extension_state(window),
        ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 5))
        ttk.Label(extensions, text=local_text("allow_all_warning"), wraplength=680).grid(row=1, column=0, columnspan=5, sticky="w", pady=(0, 8))
        window.extension_checkbuttons = []
        for index, extension in enumerate(sorted(ALLOWED_EXTENSIONS)):
            checkbutton = ttk.Checkbutton(extensions, text=extension[1:].upper(), variable=window.extension_vars[extension])
            checkbutton.grid(row=index // 5 + 2, column=index % 5, sticky="w", padx=(0, 18), pady=3)
            window.extension_checkbuttons.append(checkbutton)
        self._update_settings_extension_state(window)

        upload = ttk.LabelFrame(content, text=local_text("upload_state"), padding=12)
        upload.pack(fill="x", pady=(0, 10))
        window.upload_open_radio = ttk.Radiobutton(upload, text=local_text("upload_open"), variable=window.upload_enabled_var, value=True)
        window.upload_open_radio.grid(row=0, column=0, sticky="w")
        window.upload_pause_radio = ttk.Radiobutton(upload, text=local_text("upload_pause"), variable=window.upload_enabled_var, value=False)
        window.upload_pause_radio.grid(row=0, column=1, sticky="w", padx=18)
        ttk.Checkbutton(upload, text=local_text("show_toggle"), variable=window.show_toggle_var, command=lambda: self._update_settings_upload_state(window)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))
        window.locked_label = ttk.Label(upload, text=local_text("state_locked"))
        window.locked_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self._update_settings_upload_state(window)

        actions = ttk.Frame(content)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text=local_text("cancel"), command=self._close_settings).pack(side="right")
        ttk.Button(actions, text=local_text("save"), command=lambda: self._save_settings(window)).pack(side="right", padx=8)

    def _update_settings_upload_state(self, window: tk.Toplevel) -> None:
        """控制台按鈕顯示時鎖定設定頁面的接收狀態選項。"""
        locked = window.show_toggle_var.get()
        state = "disabled" if locked else "normal"
        window.upload_open_radio.config(state=state)
        window.upload_pause_radio.config(state=state)
        window.locked_label.grid() if locked else window.locked_label.grid_remove()

    def _update_settings_extension_state(self, window: tk.Toplevel) -> None:
        """全格式模式啟用時鎖定個別格式，避免設定意義互相衝突。"""
        state = "disabled" if window.allow_all_file_types_var.get() else "normal"
        for checkbutton in window.extension_checkbuttons:
            checkbutton.config(state=state)

    def _choose_storage_for_settings(self, window: tk.Toplevel, language: str) -> None:
        """在設定頁面選擇接收檔案儲存資料夾。"""
        selected = filedialog.askdirectory(initialdir=window.storage_var.get(), title=text(language, "choose_storage"))
        if selected:
            window.storage_var.set(selected)

    def _save_settings(self, window: tk.Toplevel) -> None:
        """驗證並一次保存設定，失敗時不留下部分更新。"""
        language = window.language_var.get()
        local_text = lambda key, **values: text(language, key, **values)
        try:
            max_mb = int(window.max_mb_var.get())
            if not 1 <= max_mb <= 2048:
                raise ValueError
        except ValueError:
            messagebox.showerror(local_text("setting_error"), local_text("max_error"), parent=window)
            return
        selected_extensions = {extension for extension, variable in window.extension_vars.items() if variable.get()}
        if not window.allow_all_file_types_var.get() and not selected_extensions:
            messagebox.showerror(local_text("setting_error"), local_text("extension_error"), parent=window)
            return
        storage = Path(window.storage_var.get()).expanduser()
        try:
            storage.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            messagebox.showerror(local_text("setting_error"), local_text("storage_error", error=error), parent=window)
            return
        try:
            self._set_startup(window.startup_var.get())
        except OSError as error:
            messagebox.showerror(local_text("startup_error_title"), local_text("startup_error", error=error), parent=window)
            return

        self.database.set_setting("storage_path", str(storage.resolve()))
        self.database.set_setting("max_file_mb", str(max_mb))
        self.database.set_setting("ui_language", language)
        self.database.set_setting("enabled_extensions", serialize_enabled_extensions(selected_extensions))
        self.database.set_setting("allow_all_file_types", "1" if window.allow_all_file_types_var.get() else "0")
        self.database.set_setting("show_upload_toggle", "1" if window.show_toggle_var.get() else "0")
        if not window.show_toggle_var.get():
            self.database.set_setting("upload_enabled", "1" if window.upload_enabled_var.get() else "0")
        self.language = language
        LOGGER.info("控制台設定已更新")
        self._close_settings()
        self._rebuild_ui()
        messagebox.showinfo(self._t("saved_title"), self._t("saved"), parent=self)

    def _close_settings(self) -> None:
        """關閉設定視窗並釋放模態控制。"""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.grab_release()
            self.settings_window.destroy()
        self.settings_window = None

    def _set_startup(self, enabled: bool) -> None:
        """依設定建立或移除目前使用者的 Windows 登入啟動命令。"""
        shortcut = startup_shortcut_path()
        if enabled:
            shortcut.parent.mkdir(parents=True, exist_ok=True)
            launcher = Path(sys.executable) if getattr(sys, "frozen", False) else APP_DIR / "start.bat"
            shortcut.write_text(f'@echo off\r\nstart "" "{launcher}"\r\n', encoding="utf-8")
        elif shortcut.exists():
            shortcut.unlink()

    def _refresh_lan_url(self) -> bool:
        """重新驗證區網網址，必要時改用能回應 CatDrop 的其他網卡位址。"""
        try:
            address, site_url, repaired = resolve_lan_url(self.site_url, PORT)
        except LanUrlError as error:
            LOGGER.error("區網網址自動修復失敗 [%s] %s", error.code, error.detail)
            messagebox.showerror(
                self._t("lan_error_title"),
                self._t("lan_error", code=error.code, detail=error.detail),
                parent=self,
            )
            return False
        self.ip_address = address
        self.site_url = site_url
        self.lan_url_label.config(text=self._t("lan_url", url=self.site_url))
        if repaired:
            LOGGER.info("區網網址已自動修復：%s", self.site_url)
        return True

    def _generate_qrcode(self) -> None:
        """確認區網網址可用後產生 QR Code，避免建立無法連線的圖碼。"""
        if not self._refresh_lan_url():
            return
        try:
            target = prepare_qrcode(self.site_url, self.ip_address)
        except LanUrlError as error:
            LOGGER.error("QR Code 網址驗證失敗 [%s] %s", error.code, error.detail)
            messagebox.showerror(self._t("lan_error_title"), self._t("lan_error", code=error.code, detail=error.detail), parent=self)
            return
        except Exception as error:
            code = "CD-QR-001"
            LOGGER.exception("QR Code 寫入失敗 [%s]", code)
            messagebox.showerror(self._t("qr_error_title"), self._t("qr_error", code=code, detail=error), parent=self)
            return
        messagebox.showinfo(self._t("qr_ready_title"), self._t("qr_ready", path=target), parent=self)

    def _copy_site_url(self) -> None:
        """將目前控制台顯示的網址複製到 Windows 剪貼簿。"""
        if not self._refresh_lan_url():
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self.site_url)
            self.update_idletasks()
        except tk.TclError as error:
            code = "CD-CLIP-001"
            LOGGER.exception("複製區網網址失敗 [%s]", code)
            messagebox.showerror(self._t("copy_error_title"), self._t("copy_error", code=code, detail=error), parent=self)
            return
        messagebox.showinfo(self._t("copied_title"), self._t("copied", url=self.site_url), parent=self)

    def _mark_processed(self) -> None:
        record_ids = [int(item) for item in self.tree.selection()]
        if not record_ids:
            messagebox.showinfo(self._t("not_selected"), self._t("select_to_process"))
            return
        self.database.mark_processed(record_ids)
        self.refresh_records()

    def _open_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(self._t("not_selected"), self._t("select_to_open"))
            return
        rows = {str(row["id"]): row for row in self.database.list_uploads()}
        failed: list[str] = []
        for item in selection:
            row = rows.get(item)
            if not row:
                continue
            stored_path = Path(row["stored_path"])
            try:
                if stored_path.is_file():
                    os.startfile(stored_path)
                else:
                    failed.append(row["original_name"])
            except OSError:
                failed.append(row["original_name"])
        if failed:
            messagebox.showerror(self._t("missing_title"), self._t("missing_files", files="\n".join(failed[:10])))

    def _delete_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(self._t("not_selected"), self._t("select_to_delete"))
            return
        if not messagebox.askyesno(self._t("confirm_delete_title"), self._t("confirm_delete", count=len(selection))):
            return
        rows = {str(row["id"]): row for row in self.database.list_uploads()}
        failed: list[str] = []
        deleted_ids: list[int] = []
        for item in selection:
            row = rows.get(item)
            if not row:
                continue
            try:
                path = Path(row["stored_path"])
                if path.exists():
                    path.unlink()
                deleted_ids.append(int(item))
            except OSError:
                failed.append(row["original_name"])
        self.database.delete_records(deleted_ids)
        self.refresh_records()
        if failed:
            messagebox.showerror(self._t("delete_failed_title"), self._t("delete_failed", files="\n".join(failed[:10])))

    def _selected_days(self) -> int | None:
        """將中英文日期選項轉為 SQLite 查詢天數，允許語言切換時保留條件。"""
        labels = {
            text("zh", "date_today"): 1,
            text("zh", "date_7"): 7,
            text("zh", "date_30"): 30,
            text("en", "date_today"): 1,
            text("en", "date_7"): 7,
            text("en", "date_30"): 30,
        }
        return labels.get(self.date_filter_var.get())

    def _open_path(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(path)

    def _export_records(self) -> None:
        target = filedialog.asksaveasfilename(title=self._t("export_title"), defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not target:
            return
        with open(target, "w", newline="", encoding="utf-8-sig") as output:
            writer = csv.writer(output)
            writer.writerow([self._t("column_status"), self._t("column_source"), self._t("column_name"), self._t("column_stored"), self._t("column_size_bytes"), self._t("column_time"), self._t("storage_path")])
            rows = self.database.list_uploads(self.search_var.get().strip(), self._selected_days())
            for row in sort_upload_rows(rows, self.sort_column, self.sort_descending):
                status = self._t("status_processed") if row["processed"] else self._t("status_new")
                writer.writerow([status, row["user_name"], row["original_name"], row["stored_name"], row["size_bytes"], row["uploaded_at"], row["stored_path"]])
        messagebox.showinfo(self._t("export_done_title"), self._t("export_done"))

    def _on_close(self) -> None:
        if self.settings_window:
            self._close_settings()
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
            LOGGER.info("HTTP 服務已停止")
        self.destroy()


if __name__ == "__main__":
    current_log = configure_logging()
    try:
        LOGGER.info("CatDrop 啟動，Python=%s，目錄=%s", sys.version.split()[0], APP_DIR)
        if not acquire_single_instance():
            duplicate_root = tk.Tk()
            duplicate_root.withdraw()
            messagebox.showinfo("程式已在執行", "CatDrop 後台已經啟動。")
            duplicate_root.destroy()
            raise SystemExit(0)
        ControlPanel().mainloop()
    except SystemExit:
        raise
    except BaseException as error:
        LOGGER.exception("CatDrop 發生未處理的致命錯誤")
        show_fatal_error(error, current_log)
        raise
