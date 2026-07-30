# 待辦事項清單桌面應用程式

這是一個使用 Python `tkinter` 開發的桌面待辦事項管理工具。專案提供任務新增、編輯、完成狀態管理、提醒通知、Discord Webhook 通知，以及 JSON / Markdown 匯出功能，適合用來管理個人工作、學習與生活任務。

目前介面已重新整理為偏 Windows 11 Fluent Design 的低飽和生產力工具風格，重點是清楚的資訊層級、舒適留白、卡片式任務列表與一致的表單元件。

## 專案概覽

- 應用型態：Windows 桌面 GUI 應用程式
- 主要語言：Python
- 主要介面框架：tkinter、ttk、tkcalendar
- 資料儲存：本機 JSON 檔案
- 通知方式：Discord Webhook 或系統通知
- 匯出格式：JSON、Markdown
- 打包方式：PyInstaller
- 介面風格：低飽和冷色系、卡片式任務列表、集中式 `ttk.Style`
- Android 版本：提供 Kivy 入口程式與 Buildozer 打包設定

## 主要功能

- 任務管理：新增、編輯、刪除待辦事項。
- 任務欄位：支援標題、內容、分類、優先級、進度、開始日期。
- 完成管理：可切換完成狀態，並保留完成心得或紀錄。
- 提醒設定：可為單一任務設定提醒時間、提醒內容模板、設定人與圖片 URL。
- 通知整合：支援 Discord Webhook 與本機系統通知。
- 匯出工具：可依任務、分類、狀態、優先級、日期與手動勾選範圍匯出。
- 匯出預覽：匯出前可即時預覽 JSON 或 Markdown 內容。
- 設定管理：Webhook 設定儲存在 `config.json`，並提供 `config.example.json` 範例。
- 圖示與打包：包含圖示產生與 PyInstaller 打包腳本。

## 介面設計

新版 UI 將主畫面拆成三個主要區塊：

```text
Header
  顯示 Schedule 標題、今天日期、完成率、今日任務數

搜尋與操作列
  左側為搜尋 / 快速輸入欄位，右側為「新增」與「匯出」按鈕

任務列表
  每筆任務以白色卡片呈現，包含完成狀態、標題、分類、進度、優先級、開始日期、提醒與刪除操作
```

視覺設計使用低飽和冷色系：

- 背景：`#F8FAFC`
- 主背景：`#EEF4FF`
- 卡片：`#FFFFFF`
- 主要色：`#4F46E5`
- Hover：`#6366F1`
- 成功：`#22C55E`
- 警告：`#F59E0B`
- 危險：`#EF4444`
- 主要文字：`#1F2937`
- 次要文字：`#6B7280`
- Border：`#E5E7EB`
- Divider：`#F1F5F9`

介面樣式集中在 `todo_app.py` 的 `setup_style()`，並搭配 `UI_COLORS`、字體常數與間距常數管理，避免樣式分散在各個元件中。

## 安裝與執行

### 1. 使用原始碼執行

請先確認已安裝 Python 3.10 或以上版本。

```bash
pip install -r requirements.txt
python todo_app.py
```

也可以在 Windows 直接執行：

```bat
run.bat
```

### 2. 設定 Discord Webhook

第一次執行時，若尚未建立 `config.json` 或 Webhook 尚未設定，應用程式會開啟設定視窗。

設定檔格式如下：

```json
{
  "discord_webhook_url": "https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"
}
```

如果不需要 Discord 通知，可以保留預設值，並在任務提醒中選擇系統通知。

### 3. 打包成執行檔

安裝 PyInstaller 後執行：

```bash
pip install pyinstaller
python build_exe.py
```

打包完成後，執行檔會輸出到 `dist/` 目錄。

注意：打包後的單一 exe 檔案會將程式資源封裝或解到臨時位置，通常無法直接把可變資料寫回到 exe 檔內。因此程式會把使用者設定與資料（例如 `config.json`、`todos.json`）儲存在使用者可寫的資料目錄。Windows 平台預設路徑為 `%APPDATA%/Schedule`，以確保資料能在更新或覆蓋執行檔時保留。

### 4. Android 版

專案另外提供 `android_app.py` 作為 Android 版入口，並用 `main.py` 作為 Buildozer 預設啟動檔。Android 版使用 Kivy 製作手機介面，保留待辦事項的主要 JSON 欄位與完成狀態同步規則。

本機測試 Android 版介面：

```bash
pip install -r requirements_android.txt
python android_app.py
```

打包 APK 建議在 WSL 或 Linux 環境使用 Buildozer：

```bash
pip install buildozer
buildozer android debug
```

產出的 APK 會在 `bin/` 目錄。首次打包會下載 Android SDK、NDK、Gradle 與 Python-for-Android，時間會比較久。

## 專案結構

```text
schedule/
├── todo_app.py                  # 主程式與 tkinter GUI
├── android_app.py               # Android / Kivy 版入口程式
├── storage.py                   # config.json / todos.json 讀寫邏輯
├── notify.py                    # Discord 與系統通知服務
├── export.py                    # JSON / Markdown 匯出服務
├── create_icon.py               # 產生應用程式圖示
├── build_exe.py                 # PyInstaller 打包腳本
├── run.bat                      # Windows 啟動批次檔
├── requirements.txt             # Python 套件依賴
├── requirements_android.txt     # Android / Kivy 版依賴
├── buildozer.spec               # Android APK 打包設定
├── ANDROID_BUILD.md             # Android 打包流程紀錄
├── config.example.json          # Discord Webhook 設定範例
├── todos.json                   # 待辦事項資料檔
├── tests/
│   └── test_export_and_completion.py
├── output/                      # Markdown 匯出輸出目錄
├── icon.png
├── icon.ico
└── 待辦事項清單.spec
```

## 資料格式

待辦事項儲存在 `todos.json`，每筆任務大致包含下列欄位：

```json
{
  "id": "uuid",
  "title": "任務標題",
  "content": "任務內容",
  "start_date": "2026-07-30",
  "category": "學習",
  "priority": "中",
  "status": "進行中",
  "completed": false,
  "notification": null,
  "completion_history": []
}
```

提醒設定會以 JSON 字串儲存在任務的 `notification` 欄位中，包含提醒時間、通知模板、通知方式、設定人與圖片 URL。

## 測試

目前測試集中在匯出功能與欄位選擇行為：

```bash
python -m unittest discover -s tests
```

測試檔案位於 `tests/test_export_and_completion.py`。

## 技術分析

此專案採用單機檔案型架構，主程式 `todo_app.py` 負責 GUI、視窗流程與使用者互動；`storage.py`、`notify.py`、`export.py` 則拆出儲存、通知與匯出邏輯，讓核心功能比單一檔案更容易測試與維護。

UI 層目前主要集中在 `SearchApp`、`TodoItem`、`TaskEditorWindow`、`ExportWindow` 與 `ConfigWindow`。主畫面的資料讀寫、通知發送、匯出流程仍維持既有服務與 callback，介面重排不改變任務資料格式或 JSON 儲存方式。

Android 版 UI 集中在 `android_app.py`。它是獨立入口，不會取代 Windows 桌面版；手機端會使用 Android App 私有資料目錄保存 `todos.json`，不會自動與 Windows 桌面版同步。

目前資料以 JSON 檔直接保存，優點是部署簡單、不需資料庫；限制是多人同步、資料衝突與大量資料查詢能力較弱。若未來要擴充成長期使用工具，可考慮加入資料備份、匯入功能、欄位驗證、通知失敗重試，以及更完整的單元測試。

## UI 維護原則

- 新增或調整顏色時，優先修改 `UI_COLORS`。
- 新增 ttk 元件樣式時，優先放在 `setup_style()`。
- 盡量保留任務資料結構、method name、callback 與 event binding。
- UI 調整應集中在視窗與元件排版，不直接改動 `storage.py`、`notify.py`、`export.py` 的商業邏輯。

## 注意事項

- `config.json` 可能包含 Discord Webhook，建議不要提交到公開版本庫。
- `todos.json` 是本機任務資料，若要保留任務紀錄請定期備份。
- 執行通知功能時，應用程式需要保持開啟。
- 若匯出 Markdown 或 JSON，請確認選擇的輸出路徑有寫入權限。
