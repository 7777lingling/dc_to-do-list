import json
import os
import sys

CONFIG_FILE = "config.json"
CONFIG_EXAMPLE_FILE = "config.example.json"
TODOS_FILE = "todos.json"

# Directory where the package lives (read-only in bundled exe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_data_dir() -> str:
    """Return a directory for writable app data.

    - When running as a PyInstaller frozen exe, prefer a per-user AppData folder on Windows
      (or the user's home directory on other platforms).
    - When running from source, keep using the package directory so behavior is unchanged.
    """
    if getattr(sys, "frozen", False):
        # Running as bundled exe — use APPDATA on Windows, XDG or home on others
        if os.name == "nt":
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
        else:
            base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
        data_dir = os.path.join(base, "Schedule")
    else:
        data_dir = BASE_DIR
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def resolve_path(filename: str) -> str:
    """Resolve a filename to a writable path for runtime data files.

    Example: when frozen this will point to "%APPDATA%/Schedule/config.json" so the
    executable can persist changes across runs.
    """
    return os.path.join(get_data_dir(), filename)


def load_config(config_path: str | None = None, default_webhook: str = "YOUR_WEBHOOK_URL_HERE") -> dict:
    path = config_path or resolve_path(CONFIG_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                config = json.load(handle)
            if isinstance(config, dict):
                return config
        except Exception:
            return {"discord_webhook_url": default_webhook}
    return {"discord_webhook_url": default_webhook}


def save_config(config: dict, config_path: str | None = None) -> None:
    path = config_path or resolve_path(CONFIG_FILE)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=4)


def load_todos(path: str | None = None) -> list:
    target_path = path or resolve_path(TODOS_FILE)
    if not os.path.exists(target_path):
        return []
    try:
        with open(target_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        return []
    return []


def save_todos(todos: list, path: str | None = None) -> None:
    target_path = path or resolve_path(TODOS_FILE)
    with open(target_path, "w", encoding="utf-8") as handle:
        json.dump(todos, handle, ensure_ascii=False, indent=2)


def mask_webhook_url(url: str | None) -> str:
    if not url or not str(url).strip():
        return "未設定"
    if "YOUR_WEBHOOK_URL_HERE" in url or "your-webhook" in url:
        return "範例值"
    return "已設定（已遮罩）"
