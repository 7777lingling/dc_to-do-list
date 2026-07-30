import json
import threading
import time
from datetime import datetime

import requests
from plyer import notification


def _clean_image_url(url: str | None) -> str:
    if not url:
        return ""
    cleaned = str(url).strip().strip("<>")
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    return ""


class NotificationService:
    def __init__(self, app, webhook_url: str):
        self.app = app
        self.webhook_url = webhook_url
        self._stop_event = threading.Event()

    def start(self):
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _run_loop(self):
        while not self._stop_event.is_set():
            self._check_notifications()
            time.sleep(10)

    def _check_notifications(self):
        current_time = datetime.now()
        for todo in list(self.app.todos):
            if todo.get('completed') or not todo.get('notification'):
                continue
            try:
                notification_data = json.loads(todo['notification'])
                notification_time = datetime.fromisoformat(notification_data['time'])
            except Exception:
                continue

            time_diff = (notification_time - current_time).total_seconds()
            if time_diff <= 0:
                self._send_notification(todo, notification_data, current_time)

    def _send_notification(self, todo: dict, notification_data: dict, current_time: datetime) -> None:
        template = notification_data.get('template', "🔔 待辦事項提醒\n📝 {content}")
        notification_type = notification_data.get('type', 'discord')
        creator = notification_data.get('creator', '用戶')
        variables = {
            'content': todo.get('title', '無標題'),
            'time': current_time.strftime('%Y/%m/%d %H:%M'),
            'creator': creator,
        }
        message = template.format(**variables)

        if notification_type == 'discord' and self.webhook_url:
            payload = {"content": message}
            image_url = _clean_image_url(notification_data.get('image_url'))
            if image_url:
                payload['embeds'] = [{
                    "color": 0x4F46E5,
                    "image": {"url": image_url}
                }]
            elif notification_data.get('image_url'):
                print(f"忽略無效圖片 URL: {notification_data.get('image_url')}")
            try:
                response = requests.post(self.webhook_url, json=payload, timeout=10)
                if response.status_code >= 400:
                    print(f"Discord 通知失敗: {response.status_code} {response.text}")
            except Exception as exc:
                print(f"Discord 通知錯誤: {exc}")
        else:
            notification.notify(title='待辦事項提醒', message=message, timeout=10)

        todo['notification'] = None
        self.app.save_todos()
        self.app.render_todos()
