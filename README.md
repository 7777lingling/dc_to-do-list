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

## 安裝與使用

### 方法一：直接運行 Python 檔案
1. 確保已安裝 Python 3.7+
2. 安裝依賴：`pip install -r requirements.txt`
3. 運行應用程式：`python todo_app.py`

### 方法二：打包成 EXE 檔案
1. 安裝 PyInstaller：`pip install pyinstaller`
2. 安裝 Pillow（用於生成圖示）：`pip install pillow`
3. 生成圖示：`python create_icon.py`
4. 運行打包腳本：`python build_exe.py`
5. 在 `dist` 資料夾中找到可執行檔案

## 使用說明

1. **新增待辦事項**：在輸入框中輸入內容，按 Enter 或點擊「新增」按鈕
2. **標記完成**：點擊項目前的勾選框
3. **刪除項目**：點擊項目右側的 × 按鈕
4. **自動儲存**：應用程式會自動儲存您的待辦事項

## 檔案結構

```
schedule/
├── todo_app.py          # 主程式
├── build_exe.py         # 打包腳本
├── create_icon.py       # 圖示生成腳本
├── requirements.txt     # 依賴清單
├── todos.json          # 待辦事項資料（自動生成）
└── README.md           # 說明文件
```

## 技術特色

- 使用 tkinter 建立原生桌面應用程式
- JSON 格式儲存資料
- 多執行緒自動儲存
- 響應式滾動設計
- 柔和色彩主題

## 快速開始

```bash
# 直接運行
python todo_app.py

# 或打包成 exe
pip install pyinstaller pillow
python create_icon.py
python build_exe.py
``` 