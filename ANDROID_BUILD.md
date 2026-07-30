# Android APK 打包流程紀錄

本文件記錄此專案目前轉成 Android App 的打包流程、已成功完成的步驟，以及後續安裝 APK 的方式。

## 目前狀態

已完成：

- 已新增 Android / Kivy 版入口程式：`android_app.py`
- 已新增 Buildozer 預設入口：`main.py`
- 已新增 Android 打包設定：`buildozer.spec`
- 已新增 Android 依賴清單：`requirements_android.txt`
- 已在 Ubuntu / WSL 中安裝 Buildozer
- 已解決 `cython` 指令找不到的問題
- `buildozer android debug` 已開始下載 `python-for-android`

目前打包流程已進入真正的 Android build 階段。

## 專案檔案

```text
android_app.py               # Android / Kivy 手機版 UI
main.py                      # Buildozer 預設啟動檔
buildozer.spec               # APK 打包設定
requirements_android.txt     # Android 版 Python 依賴
storage.py                   # JSON 讀寫邏輯
```

## Android 版目前功能

- 新增任務
- 編輯任務
- 刪除任務
- 勾選完成 / 取消完成
- `completed` 與 `status` 自動同步
- 使用與桌面版相近的任務 JSON 欄位

注意：Android 版目前會把 `todos.json` 存在手機 App 私有資料目錄，不會自動與 Windows 桌面版同步。

## Ubuntu / WSL 打包流程

進入專案目錄：

```bash
cd /mnt/e/vscode/schedule
```

更新套件清單：

```bash
sudo apt update
```

安裝 Android 打包需要的系統套件：

```bash
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev
```

Ubuntu 24.04 會限制直接用 `pip install --user` 安裝系統環境套件，因此使用 `pipx` 安裝 Buildozer：

```bash
sudo apt install -y pipx python3-venv python3-full
pipx ensurepath
source ~/.profile
pipx install buildozer
```

確認 Buildozer 已安裝：

```bash
buildozer --version
```

目前成功結果：

```text
Buildozer 1.6.0
```

## Cython 問題與解法

執行：

```bash
buildozer android debug
```

曾遇到：

```text
Cython (cython) not found, please install it.
```

先將 Cython 注入 Buildozer 的 pipx 虛擬環境：

```bash
pipx inject buildozer "cython<3.0"
```

確認版本：

```bash
pipx runpip buildozer show cython
```

目前成功結果：

```text
Name: Cython
Version: 0.29.37
```

但 Buildozer 會用外部命令尋找 `cython`，所以還需要建立 symlink：

```bash
ln -sf ~/.local/share/pipx/venvs/buildozer/bin/cython ~/.local/bin/cython
export PATH="$HOME/.local/bin:$PATH"
which cython
cython --version
```

目前成功結果：

```text
/home/ling/.local/bin/cython
```

之後再執行：

```bash
buildozer android debug
```

目前成功進度：

```text
# Search for Cython (cython)
#  -> found at /home/ling/.local/bin/cython
# Search for Java compiler (javac)
#  -> found at /usr/bin/javac
# Search for Java keytool (keytool)
#  -> found at /usr/bin/keytool
# Install platform
# Run 'git clone -b master --single-branch https://github.com/kivy/python-for-android.git python-for-android' ...
# Cwd /mnt/e/vscode/schedule/.buildozer/android/platform
Cloning into 'python-for-android'...
```

這代表已進入真正的 Android 打包流程。

## Ubuntu 24.04 PEP 668 問題

若 Buildozer 下載完 `python-for-android` 後出現：

```text
ERROR: Can not perform a '--user' install.
note: If you believe this is a mistake ... --break-system-packages
```

原因是 Ubuntu 24.04 啟用了 PEP 668，Buildozer 內部執行：

```text
/usr/bin/python3 -m pip install --user ...
```

會被系統 Python 擋下。

建議用環境變數允許 Buildozer 這次打包流程使用 pip：

```bash
cd /mnt/e/vscode/schedule
export PIP_BREAK_SYSTEM_PACKAGES=1
buildozer android debug
```

也可以只套用在單次指令：

```bash
cd /mnt/e/vscode/schedule
PIP_BREAK_SYSTEM_PACKAGES=1 buildozer android debug
```

如果前一次 Buildozer 暫存已經壞掉，可以清掉後重跑：

```bash
cd /mnt/e/vscode/schedule
rm -rf .buildozer
PIP_BREAK_SYSTEM_PACKAGES=1 buildozer android debug
```

注意指令要完整貼上，不要分成 `buildozer an` 和 `droid debug` 兩段。

## APK 輸出位置

打包成功後 APK 會輸出到：

```bash
/mnt/e/vscode/schedule/bin/
```

在 Windows 中對應：

```text
E:\vscode\schedule\bin
```

可能看到的檔名類似：

```text
schedule-0.1.0-arm64-v8a-debug.apk
```

## 安裝到 Android 手機

1. 將 APK 傳到 Android 手機。
2. 在手機上開啟 APK。
3. 若系統提示不允許未知來源 App，允許該檔案管理器或瀏覽器安裝未知來源。
4. 安裝完成後，手機上會出現 `Schedule` App。

## 注意事項

- 目前產生的是 debug APK，適合自己測試，不適合正式上架。
- 第一次 `buildozer android debug` 會下載 Android SDK、NDK、Gradle 與 Python-for-Android，可能需要很久。
- 若中途失敗，請保留 `ERROR:` 或 `Exception` 前後約 30 行錯誤訊息。
- Android 版目前沒有與桌面版自動同步資料。
- Android 原生通知與背景執行限制尚未完整處理。
