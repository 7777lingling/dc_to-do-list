# 待辦事項清單應用程式

一個美觀、簡約、柔和的待辦事項管理應用程式。

## 功能特色

- ✨ 美觀的用戶界面設計
- 📝 新增、編輯、刪除待辦事項
- ✅ 勾選完成/未完成狀態
- 📊 即時統計資訊
- 💾 自動儲存功能
- 🎨 柔和色彩主題
- 📱 響應式設計
- 🔔 Discord 通知功能

## 安裝與使用

### 方法一：直接下載使用（推薦）
1. 下載 `待辦事項清單.exe`
2. 直接點擊執行即可使用
3. 首次運行時會自動設定必要的檔案
4. 依照提示設定 Discord webhook（可選）

### 方法二：從原始碼運行
1. 確保已安裝 Python 3.7+
2. 安裝依賴：`pip install -r requirements.txt`
3. 運行應用程式：`python todo_app.py`

### 方法三：自行打包
1. 安裝 PyInstaller：`pip install pyinstaller`
2. 生成圖示：`python create_icon.py`
3. 運行打包腳本：`python build_exe.py`
4. 在 `dist` 資料夾中找到 `待辦事項清單.exe`

## 使用說明

1. **新增待辦事項**：在輸入框中輸入內容，按 Enter 或點擊「新增」按鈕
2. **標記完成**：點擊項目前的勾選框
3. **刪除項目**：點擊項目右側的 × 按鈕
4. **設定提醒**：點擊項目右側的鈴鐺圖示
5. **編輯項目**：雙擊項目文字
6. **Discord 通知**：
   - 在 Discord 中建立 Webhook（[教學](https://support.discord.com/hc/zh-tw/articles/228383668-%E4%BD%BF%E7%94%A8%E7%B6%B2%E7%B5%A1%E9%89%A4%E6%89%8B-Webhooks-)）
   - 在應用程式中設定 Webhook URL
   - 為待辦事項設定提醒時間

## 檔案說明

```
待辦事項清單/
├── 待辦事項清單.exe    # 主程式（唯一需要的檔案）
├── todos.json         # 待辦事項資料（自動生成）
└── config.json       # 設定檔（自動生成）
```

## 技術特色

- 使用 tkinter 建立原生桌面應用程式
- JSON 格式儲存資料
- 多執行緒自動儲存
- 響應式滾動設計
- 柔和色彩主題
- Discord Webhook 整合

## 注意事項

- 程式會自動在運行目錄創建必要的設定檔
- 每個安裝都是獨立的，資料不會互相影響
- Discord 通知功能需要設定 Webhook URL 