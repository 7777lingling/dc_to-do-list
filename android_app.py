from datetime import datetime
import uuid

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from storage import load_todos, save_todos


CATEGORIES = ["學習", "工作", "生活", "其他"]
PRIORITY_LEVELS = ["低", "中", "高"]
STATUS_OPTIONS = ["未開始", "進行中", "已完成"]

COLORS = {
    "background": "#F8FAFC",
    "surface": "#EEF4FF",
    "card": "#FFFFFF",
    "primary": "#4F46E5",
    "success": "#22C55E",
    "danger": "#EF4444",
    "text": "#1F2937",
    "muted": "#6B7280",
}


def sync_todo_completion_state(todo):
    if todo.get("status") == "已完成":
        todo["completed"] = True
    if todo.get("completed"):
        todo["status"] = "已完成"
        if not todo.get("completion_time"):
            todo["completion_time"] = datetime.now().isoformat()
    elif todo.get("status") == "已完成":
        todo["status"] = "未開始"
    if not todo.get("completed"):
        todo.pop("completion_time", None)


class TaskCard(BoxLayout):
    todo = DictProperty({})

    def __init__(self, app, todo, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.todo = todo
        self.orientation = "vertical"
        self.spacing = dp(8)
        self.padding = [dp(14), dp(12), dp(14), dp(12)]
        self.size_hint_y = None
        self.height = dp(150)

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36), spacing=dp(8))
        check_text = "✓" if todo.get("completed") else "○"
        self.check_button = Button(
            text=check_text,
            size_hint_x=None,
            width=dp(44),
            background_color=self._hex(COLORS["success"] if todo.get("completed") else COLORS["surface"]),
            color=self._hex("#FFFFFF" if todo.get("completed") else COLORS["muted"]),
        )
        self.check_button.bind(on_release=lambda *_: self.app.toggle_todo(todo["id"]))

        title = Label(
            text=todo.get("title", "無標題"),
            halign="left",
            valign="middle",
            color=self._hex(COLORS["text"]),
            bold=True,
        )
        title.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        delete_button = Button(
            text="刪除",
            size_hint_x=None,
            width=dp(64),
            background_color=self._hex(COLORS["danger"]),
            color=self._hex("#FFFFFF"),
        )
        delete_button.bind(on_release=lambda *_: self.app.delete_todo(todo["id"]))

        top.add_widget(self.check_button)
        top.add_widget(title)
        top.add_widget(delete_button)

        meta = Label(
            text=f"{todo.get('category', '其他')}   {todo.get('status', '未開始')}   {todo.get('priority', '中')}優先",
            halign="left",
            valign="middle",
            color=self._hex(COLORS["primary"]),
            size_hint_y=None,
            height=dp(28),
        )
        meta.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        content = Label(
            text=todo.get("content") or "未填寫說明",
            halign="left",
            valign="top",
            color=self._hex(COLORS["muted"]),
        )
        content.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        edit_button = Button(
            text="編輯",
            size_hint_y=None,
            height=dp(36),
            background_color=self._hex(COLORS["surface"]),
            color=self._hex(COLORS["text"]),
        )
        edit_button.bind(on_release=lambda *_: self.app.open_editor(todo))

        self.add_widget(top)
        self.add_widget(meta)
        self.add_widget(content)
        self.add_widget(edit_button)

    @staticmethod
    def _hex(value):
        value = value.lstrip("#")
        return [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1]


class TodoEditor(Popup):
    def __init__(self, app, todo=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.todo = todo
        self.title = "編輯任務" if todo else "新增任務"
        self.size_hint = (0.92, 0.86)

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        self.title_input = TextInput(text=(todo or {}).get("title", ""), hint_text="標題", multiline=False)
        self.content_input = TextInput(text=(todo or {}).get("content", ""), hint_text="內容", size_hint_y=None, height=dp(110))
        self.category_input = Spinner(text=(todo or {}).get("category", CATEGORIES[0]), values=CATEGORIES)
        self.priority_input = Spinner(text=(todo or {}).get("priority", PRIORITY_LEVELS[1]), values=PRIORITY_LEVELS)
        self.status_input = Spinner(text=(todo or {}).get("status", STATUS_OPTIONS[0]), values=STATUS_OPTIONS)

        layout.add_widget(self.title_input)
        layout.add_widget(self.content_input)
        layout.add_widget(self.category_input)
        layout.add_widget(self.priority_input)
        layout.add_widget(self.status_input)

        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        cancel = Button(text="取消")
        cancel.bind(on_release=lambda *_: self.dismiss())
        save = Button(text="保存", background_color=TaskCard._hex(COLORS["primary"]), color=TaskCard._hex("#FFFFFF"))
        save.bind(on_release=self.save)
        actions.add_widget(cancel)
        actions.add_widget(save)
        layout.add_widget(actions)
        self.content = layout

    def save(self, *_):
        data = {
            "title": self.title_input.text.strip() or "無標題",
            "content": self.content_input.text.strip(),
            "start_date": (self.todo or {}).get("start_date", datetime.now().date().isoformat()),
            "category": self.category_input.text or "其他",
            "priority": self.priority_input.text or "中",
            "status": self.status_input.text or "未開始",
            "notification": (self.todo or {}).get("notification"),
            "completion_history": list((self.todo or {}).get("completion_history", [])),
        }
        sync_todo_completion_state(data)
        if self.todo:
            self.app.update_todo(self.todo["id"], data)
        else:
            self.app.create_todo(data)
        self.dismiss()


class AndroidTodoApp(App):
    def build(self):
        self.todos_path = self.user_data_dir + "/todos.json"
        self.todos = load_todos(self.todos_path)
        for todo in self.todos:
            sync_todo_completion_state(todo)
        self.save_todos()

        root = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(16))
        root.canvas.before.clear()

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(88), spacing=dp(4))
        title = Label(text="Schedule", halign="left", font_size="22sp", bold=True, color=TaskCard._hex(COLORS["text"]))
        title.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        self.summary = Label(text="", halign="left", color=TaskCard._hex(COLORS["muted"]))
        self.summary.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        header.add_widget(title)
        header.add_widget(self.summary)

        action_bar = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self.quick_input = TextInput(hint_text="輸入新任務", multiline=False)
        add_button = Button(text="新增", size_hint_x=None, width=dp(86), background_color=TaskCard._hex(COLORS["primary"]), color=TaskCard._hex("#FFFFFF"))
        add_button.bind(on_release=lambda *_: self.add_quick_todo())
        action_bar.add_widget(self.quick_input)
        action_bar.add_widget(add_button)

        self.list_layout = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.list_layout)

        root.add_widget(header)
        root.add_widget(action_bar)
        root.add_widget(scroll)
        self.refresh()
        return root

    def save_todos(self):
        save_todos(self.todos, self.todos_path)

    def refresh(self):
        self.list_layout.clear_widgets()
        total = len(self.todos)
        completed = len([todo for todo in self.todos if todo.get("completed")])
        rate = int((completed / total) * 100) if total else 0
        self.summary.text = f"完成率 {rate}%   任務 {completed}/{total}"
        for todo in self.todos:
            self.list_layout.add_widget(TaskCard(self, todo))

    def add_quick_todo(self):
        title = self.quick_input.text.strip()
        if not title:
            return
        self.create_todo({
            "title": title,
            "content": "",
            "start_date": datetime.now().date().isoformat(),
            "category": CATEGORIES[0],
            "priority": PRIORITY_LEVELS[1],
            "status": STATUS_OPTIONS[0],
            "notification": None,
            "completion_history": [],
        })
        self.quick_input.text = ""

    def open_editor(self, todo=None):
        TodoEditor(self, todo).open()

    def create_todo(self, todo_data):
        todo_data["id"] = str(uuid.uuid4())
        todo_data["text"] = todo_data.get("title", "無標題")
        sync_todo_completion_state(todo_data)
        self.todos.append(todo_data)
        self.save_todos()
        self.refresh()

    def update_todo(self, todo_id, todo_data):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo.update(todo_data)
                todo["text"] = todo_data.get("title", todo.get("text", "無標題"))
                sync_todo_completion_state(todo)
                break
        self.save_todos()
        self.refresh()

    def delete_todo(self, todo_id):
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        self.save_todos()
        self.refresh()

    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo.get("completed")
                if todo["completed"]:
                    todo["status"] = "已完成"
                elif todo.get("status") == "已完成":
                    todo["status"] = "未開始"
                sync_todo_completion_state(todo)
                break
        self.save_todos()
        self.refresh()


if __name__ == "__main__":
    AndroidTodoApp().run()
