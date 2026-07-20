const translations = {
  zh: { eyebrow: "私人區網傳檔", title: "傳送檔案到主要電腦", subtitle: "請保持裝置與主要電腦連接至相同的私人網路。", nameLabel: "來源名稱", namePlaceholder: "例如：我的手機", remember: "在這台裝置記住來源名稱", choose: "選擇檔案", chooseHint: "可一次選取多個檔案", remove: "移除", removeFile: "移除 {name}", upload: "開始上傳", confirmUpload: "確認從「{name}」傳送 {count} 個檔案？", supportedTitle: "支援的檔案類型", allTypes: "全格式支援", size: "單一檔案上限：{size} MB", uploading: "上傳中，請勿關閉頁面", success: "已成功上傳 {count} 個檔案", partial: "成功 {accepted} 個，失敗 {failed} 個", failed: "上傳失敗，請檢查檔案後重試。", noName: "請輸入來源名稱。", noFiles: "請選擇至少一個檔案。", paused: "CatDrop 目前暫停接收檔案，請等待主要電腦重新開放。", configFailed: "無法取得 CatDrop 狀態，請稍後重新整理頁面。" },
  en: { eyebrow: "PRIVATE LAN FILE TRANSFER", title: "Send files to your main computer", subtitle: "Keep this device and the main computer connected to the same private network.", nameLabel: "Source name", namePlaceholder: "For example: My phone", remember: "Remember the source name on this device", choose: "Choose files", chooseHint: "You can select multiple files", remove: "Remove", removeFile: "Remove {name}", upload: "Upload files", confirmUpload: "Send {count} file(s) from “{name}”?", supportedTitle: "Supported file types", allTypes: "All file types", size: "Maximum size per file: {size} MB", uploading: "Uploading. Please keep this page open.", success: "Successfully uploaded {count} file(s)", partial: "{accepted} succeeded, {failed} failed", failed: "Upload failed. Check the files and try again.", noName: "Enter a source name.", noFiles: "Choose at least one file.", paused: "CatDrop is currently paused. Wait for the main computer to resume receiving files.", configFailed: "CatDrop status is unavailable. Refresh this page later." }
};
const state = { language: "zh", languageInitialized: false, files: [], maxFileMb: 100, extensions: [], allowAllFileTypes: false, uploadEnabled: true };
const form = document.querySelector("#uploadForm");
const nameInput = document.querySelector("#name");
const rememberInput = document.querySelector("#remember");
const fileInput = document.querySelector("#files");
const dropZone = document.querySelector("#dropZone");
const fileList = document.querySelector("#fileList");
const submitButton = document.querySelector("#submitButton");
const message = document.querySelector("#message");
const uploadStatus = document.querySelector("#uploadStatus");

// 所有畫面文字與控制狀態都由目前設定重新渲染，避免前後端狀態不一致。
function text(key, values = {}) { return Object.entries(values).reduce((result, [name, value]) => result.replace(`{${name}}`, value), translations[state.language][key]); }
function renderLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-Hant" : "en";
  document.querySelectorAll("[data-i18n]").forEach(node => { node.textContent = text(node.dataset.i18n); });
  document.querySelectorAll("[data-placeholder]").forEach(node => { node.placeholder = text(node.dataset.placeholder); });
  document.querySelector("#languageButton").textContent = state.language === "zh" ? "EN" : "中文";
  document.querySelector("#sizeHint").textContent = text("size", { size: state.maxFileMb });
  document.querySelector("#supportedExtensions").textContent = state.allowAllFileTypes ? text("allTypes") : state.extensions.map(extension => extension.slice(1).toUpperCase()).join(" · ");
  uploadStatus.textContent = text("paused");
  renderFiles();
  applyUploadState();
}
function readableSize(bytes) { return bytes < 1048576 ? `${Math.ceil(bytes / 1024)} KB` : `${(bytes / 1048576).toFixed(1)} MB`; }
function renderFiles() {
  fileList.replaceChildren(...state.files.map((file, index) => {
    const row = document.createElement("div"); row.className = "file-item";
    const details = document.createElement("div"); details.className = "file-details";
    const name = document.createElement("span"); name.textContent = file.name;
    const size = document.createElement("span"); size.textContent = readableSize(file.size);
    const remove = document.createElement("button"); remove.type = "button"; remove.className = "remove-file";
    remove.textContent = text("remove"); remove.setAttribute("aria-label", text("removeFile", { name: file.name }));
    remove.addEventListener("click", () => { state.files.splice(index, 1); renderFiles(); message.textContent = ""; });
    details.append(name, size); row.append(details, remove); return row;
  }));
  submitButton.disabled = state.files.length === 0 || !state.uploadEnabled;
}
function applyUploadState() {
  fileInput.disabled = !state.uploadEnabled;
  dropZone.classList.toggle("disabled", !state.uploadEnabled);
  dropZone.setAttribute("aria-disabled", String(!state.uploadEnabled));
  uploadStatus.hidden = state.uploadEnabled;
  submitButton.disabled = state.files.length === 0 || !state.uploadEnabled;
}
// 白名單模式會在前後端驗證格式；全格式模式由使用者明確承擔較寬鬆的安全邊界。
function selectFiles(files) {
  if (!state.uploadEnabled) return;
  state.files = Array.from(files).filter(file => state.allowAllFileTypes || state.extensions.includes(`.${file.name.split(".").pop().toLowerCase()}`));
  renderFiles(); message.textContent = "";
}
fileInput.addEventListener("change", () => selectFiles(fileInput.files));
["dragenter", "dragover"].forEach(eventName => dropZone.addEventListener(eventName, event => { event.preventDefault(); if (state.uploadEnabled) dropZone.classList.add("drag"); }));
["dragleave", "drop"].forEach(eventName => dropZone.addEventListener(eventName, event => { event.preventDefault(); dropZone.classList.remove("drag"); }));
dropZone.addEventListener("drop", event => selectFiles(event.dataTransfer.files));
document.querySelector("#languageButton").addEventListener("click", () => { state.language = state.language === "zh" ? "en" : "zh"; state.languageInitialized = true; renderLanguage(); });

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (!state.uploadEnabled) { showMessage(text("paused"), "error"); return; }
  const userName = nameInput.value.trim();
  if (!userName) { showMessage(text("noName"), "error"); return; }
  if (!state.files.length) { showMessage(text("noFiles"), "error"); return; }
  if (!window.confirm(text("confirmUpload", { name: userName, count: state.files.length }))) return;
  if (rememberInput.checked) localStorage.setItem("uploadUserName", userName); else localStorage.removeItem("uploadUserName");
  submitButton.disabled = true; document.querySelector("#progressWrap").hidden = false; showMessage(text("uploading"), "");
  let accepted = 0;
  for (let index = 0; index < state.files.length; index += 1) {
    const file = state.files[index];
    const result = await uploadOneFile(userName, file, progress => {
      const overall = Math.round(((index + progress / 100) / state.files.length) * 100);
      setProgress(overall);
    });
    if (result.ok) accepted += 1;
    if (result.paused) { state.uploadEnabled = false; applyUploadState(); break; }
  }
  const failed = state.files.length - accepted;
  if (failed === 0) { showMessage(text("success", { count: accepted }), "success"); state.files = []; fileInput.value = ""; renderFiles(); }
  else showMessage(state.uploadEnabled ? text("partial", { accepted, failed }) : text("paused"), "error");
  submitButton.disabled = state.files.length === 0 || !state.uploadEnabled;
  setTimeout(() => { document.querySelector("#progressWrap").hidden = true; setProgress(0); }, 900);
});
function uploadOneFile(userName, file, onProgress) {
  return new Promise(resolve => {
    const data = new FormData(); data.append("name", userName); data.append("files", file);
    const request = new XMLHttpRequest(); request.open("POST", "/api/upload");
    request.upload.addEventListener("progress", progress => { if (progress.lengthComputable) onProgress(progress.loaded / progress.total * 100); });
    request.addEventListener("load", () => { try { const response = JSON.parse(request.responseText); resolve({ ok: request.status === 200 && response.accepted === 1, paused: request.status === 503 }); } catch { resolve({ ok: false, paused: false }); } });
    request.addEventListener("error", () => resolve({ ok: false, paused: false }));
    request.send(data);
  });
}
function setProgress(value) { document.querySelector("#progressBar").style.width = `${value}%`; document.querySelector("#progressText").textContent = `${value}%`; }
function showMessage(value, type) { message.textContent = value; message.className = `message ${type}`; }
async function loadConfig() {
  // 定期讀取設定，讓支援格式、語言與暫停狀態不需重新整理即可同步。
  try {
    const response = await fetch("/api/config", { cache: "no-store" });
    if (!response.ok) throw new Error("config unavailable");
    const config = await response.json();
    state.maxFileMb = config.maxFileMb;
    state.extensions = config.extensions;
    state.allowAllFileTypes = config.allowAllFileTypes;
    state.uploadEnabled = config.uploadEnabled;
    fileInput.accept = state.allowAllFileTypes ? "" : state.extensions.join(",");
    if (!state.languageInitialized) { state.language = config.defaultLanguage; state.languageInitialized = true; }
    renderLanguage();
  } catch {
    showMessage(text("configFailed"), "error");
  }
}

const rememberedName = localStorage.getItem("uploadUserName");
if (rememberedName) { nameInput.value = rememberedName; rememberInput.checked = true; }
renderLanguage();
loadConfig();
setInterval(loadConfig, 3000);
