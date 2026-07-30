import json
import os

CONFIG_FILE = "config.json"
CONFIG_EXAMPLE_FILE = "config.example.json"
TODOS_FILE = "todos.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resolve_path(filename: str) -> str:
    return os.path.join(BASE_DIR, filename)


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
