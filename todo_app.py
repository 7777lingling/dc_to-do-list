import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, time as dt_time
import uuid
from tkcalendar import DateEntry
import os

from export import ExportService
from notify import NotificationService
from storage import (
    CONFIG_FILE,
    CONFIG_EXAMPLE_FILE,
    load_config as load_storage_config,
    save_config as save_storage_config,
    load_todos as load_storage_todos,
    save_todos as save_storage_todos,
    mask_webhook_url,
    resolve_path,
)

# 配置文件路徑
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"  # 預設值
CATEGORIES = ["學習", "工作", "生活", "其他"]
PRIORITY_LEVELS = ["低", "中", "高"]
STATUS_OPTIONS = ["未開始", "進行中", "已完成"]

UI_COLORS = {
    "background": "#F8FAFC",
    "background_soft": "#EEF4FF",
    "card": "#FFFFFF",
    "primary": "#4F46E5",
    "primary_hover": "#6366F1",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "divider": "#F1F5F9",
}

FONT_FAMILY = "Microsoft JhengHei UI"
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13)
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 10)

PAD_WINDOW = 24
PAD_SECTION = 16
PAD_CONTROL = 10


def setup_style(root=None):
    """集中管理 tkinter / ttk 視覺樣式。"""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", font=FONT_BODY, background=UI_COLORS["background"], foreground=UI_COLORS["text"])
    style.configure("TFrame", background=UI_COLORS["background"])
    style.configure("Surface.TFrame", background=UI_COLORS["background_soft"])
    style.configure("Card.TFrame", background=UI_COLORS["card"], relief="flat")
    style.configure("TLabel", background=UI_COLORS["background"], foreground=UI_COLORS["text"])
    style.configure("Muted.TLabel", background=UI_COLORS["background"], foreground=UI_COLORS["muted"], font=FONT_SMALL)
    style.configure("Title.TLabel", background=UI_COLORS["background"], foreground=UI_COLORS["text"], font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=UI_COLORS["background"], foreground=UI_COLORS["muted"], font=FONT_SUBTITLE)
    style.configure("HeaderTitle.TLabel", background=UI_COLORS["card"], foreground=UI_COLORS["text"], font=FONT_TITLE)
    style.configure("HeaderSubtitle.TLabel", background=UI_COLORS["card"], foreground=UI_COLORS["muted"], font=FONT_SUBTITLE)
    style.configure("SurfaceSubtitle.TLabel", background=UI_COLORS["background_soft"], foreground=UI_COLORS["muted"], font=FONT_SUBTITLE)
    style.configure("SurfaceMuted.TLabel", background=UI_COLORS["background_soft"], foreground=UI_COLORS["muted"], font=FONT_SMALL)
    style.configure("Card.TLabel", background=UI_COLORS["card"], foreground=UI_COLORS["text"], font=FONT_BODY)
    style.configure("CardMuted.TLabel", background=UI_COLORS["card"], foreground=UI_COLORS["muted"], font=FONT_SMALL)
    style.configure("HeaderMetric.TLabel", background=UI_COLORS["card"], foreground=UI_COLORS["muted"], font=FONT_SMALL)
    style.configure("HeaderValue.TLabel", background=UI_COLORS["card"], foreground=UI_COLORS["text"], font=(FONT_FAMILY, 16, "bold"))

    style.configure("TButton", font=FONT_BODY_BOLD, padding=(14, 8), borderwidth=1, relief="flat")
    style.map("TButton", background=[("active", UI_COLORS["divider"])], foreground=[("active", UI_COLORS["text"])])
    style.configure("Primary.TButton", background=UI_COLORS["primary"], foreground="#FFFFFF", bordercolor=UI_COLORS["primary"])
    style.map("Primary.TButton", background=[("active", UI_COLORS["primary_hover"])], foreground=[("active", "#FFFFFF")])
    style.configure("Secondary.TButton", background=UI_COLORS["card"], foreground=UI_COLORS["text"], bordercolor=UI_COLORS["border"])
    style.map("Secondary.TButton", background=[("active", UI_COLORS["divider"])])
    style.configure("Danger.TButton", background=UI_COLORS["danger"], foreground="#FFFFFF", bordercolor=UI_COLORS["danger"])
    style.map("Danger.TButton", background=[("active", "#DC2626")], foreground=[("active", "#FFFFFF")])
    style.configure("Success.TButton", background=UI_COLORS["success"], foreground="#FFFFFF", bordercolor=UI_COLORS["success"])
    style.map("Success.TButton", background=[("active", "#16A34A")], foreground=[("active", "#FFFFFF")])

    style.configure("TEntry", fieldbackground=UI_COLORS["card"], foreground=UI_COLORS["text"], bordercolor=UI_COLORS["border"], lightcolor=UI_COLORS["border"], darkcolor=UI_COLORS["border"], padding=(10, 8))
    style.configure("TCombobox", fieldbackground=UI_COLORS["card"], foreground=UI_COLORS["text"], bordercolor=UI_COLORS["border"], lightcolor=UI_COLORS["border"], darkcolor=UI_COLORS["border"], padding=(8, 6))
    style.configure("TLabelframe", background=UI_COLORS["background"], bordercolor=UI_COLORS["border"], relief="solid")
    style.configure("TLabelframe.Label", background=UI_COLORS["background"], foreground=UI_COLORS["text"], font=FONT_BODY_BOLD)
    style.configure("Treeview", background=UI_COLORS["card"], fieldbackground=UI_COLORS["card"], foreground=UI_COLORS["text"], bordercolor=UI_COLORS["border"], rowheight=32, font=FONT_BODY)
    style.configure("Treeview.Heading", background=UI_COLORS["divider"], foreground=UI_COLORS["text"], font=FONT_BODY_BOLD)
    style.configure("TNotebook", background=UI_COLORS["background"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), font=FONT_BODY)
    return style

# 加載配置
def load_config():
    global DISCORD_WEBHOOK_URL
    config = load_storage_config()
    DISCORD_WEBHOOK_URL = config.get('discord_webhook_url', DISCORD_WEBHOOK_URL)
    if not os.path.exists(CONFIG_FILE) and os.path.exists(resolve_path(CONFIG_EXAMPLE_FILE)):
        save_config(load_storage_config(config_path=resolve_path(CONFIG_EXAMPLE_FILE)))

# 保存配置
def save_config(config):
    try:
        save_storage_config(config)
    except Exception as e:
        print(f"保存配置文件時發生錯誤: {e}")

class GradientFrame(tk.Canvas):
    # 預設顏色組
    COLOR_SCHEMES = {
        "theme1": {
            "start": UI_COLORS["background"],
            "end": UI_COLORS["background_soft"]
        },
        "theme2": {
            "start": UI_COLORS["background"],
            "end": UI_COLORS["background_soft"]
        }
    }
    
    def __init__(self, parent, theme="theme1", **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.set_theme(theme)
        self.bind("<Configure>", self._draw_gradient)
    
    def set_theme(self, theme):
        """設置顏色主題"""
        if theme in self.COLOR_SCHEMES:
            self._color1 = self.COLOR_SCHEMES[theme]["start"]
            self._color2 = self.COLOR_SCHEMES[theme]["end"]
            self._draw_gradient()
        
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 0 or height <= 0:
            return
        
        # 創建漸層效果
        limit = max(width, 1)
        (r1, g1, b1) = self.winfo_rgb(self._color1)
        (r2, g2, b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit
        
        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            self.create_line(i, 0, i, height, tags=("gradient",), fill=color)
        
        self.lower("gradient")

class NotificationWindow(tk.Toplevel):
    def __init__(self, parent, todo_id, current_notification=None, app=None, callback=None):
        super().__init__(parent)
        self.title("設定通知")
        self.todo_id = todo_id
        self.app = app
        self.callback = callback
        
        # 設定視窗大小和位置
        self.geometry("480x640")  # 增加一點高度來容納新的輸入欄位
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=UI_COLORS["background"])
        
        # 創建主框架
        main_frame = ttk.Frame(self, padding=PAD_WINDOW)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="通知設定", style="Title.TLabel").pack(anchor='w', pady=(0, 4))
        ttk.Label(main_frame, text="設定提醒時間與通知內容。", style="Subtitle.TLabel").pack(anchor='w', pady=(0, PAD_SECTION))
        
        # 創建日期選擇器
        ttk.Label(main_frame, text="選擇日期").pack(anchor='w', pady=(0, 5))
        self.date_picker = DateEntry(
            main_frame,
            width=20,
            background=UI_COLORS["primary"],
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd'
        )
        self.date_picker.pack(fill='x', pady=(0, 15))
        
        # 創建時間選擇器
        ttk.Label(main_frame, text="選擇時間").pack(anchor='w', pady=(0, 5))
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill='x', pady=(0, 15))
        
        self.hour_spinbox = ttk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            width=5,
            format="%02.0f"
        )
        self.hour_spinbox.pack(side='left', padx=(0, 5))
        
        ttk.Label(time_frame, text=":").pack(side='left', padx=5)
        
        self.minute_spinbox = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=5,
            format="%02.0f"
        )
        self.minute_spinbox.pack(side='left', padx=(5, 0))
        
        # 創建設定人輸入欄位
        ttk.Label(main_frame, text="設定人").pack(anchor='w', pady=(0, 5))
        self.creator_entry = ttk.Entry(main_frame)
        self.creator_entry.pack(fill='x', pady=(0, 15))
        self.creator_entry.insert(0, "用戶")  # 預設值
        
        # 創建通知內容編輯區
        ttk.Label(main_frame, text="通知內容").pack(anchor='w', pady=(0, 5))
        self.content_text = tk.Text(
            main_frame,
            height=5,
            wrap='word',
            font=FONT_BODY,
            bg=UI_COLORS["card"],
            fg=UI_COLORS["text"],
            insertbackground=UI_COLORS["text"],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=UI_COLORS["border"],
            highlightcolor=UI_COLORS["primary"]
        )
        self.content_text.pack(fill='x', pady=(0, 15))
        
        # 添加圖片 URL 輸入
        ttk.Label(main_frame, text="圖片 URL（可選）").pack(anchor='w', pady=(0, 5))
        self.image_url_entry = ttk.Entry(main_frame)
        self.image_url_entry.pack(fill='x', pady=(0, 15))

        # 通知類型選擇
        ttk.Label(main_frame, text="通知方式").pack(anchor='w', pady=(0, 5))
        self.notify_type = tk.StringVar(value='discord')
        notify_frame = ttk.Frame(main_frame)
        notify_frame.pack(fill='x', pady=(0, 15))
        ttk.Radiobutton(notify_frame, text='Discord', variable=self.notify_type, value='discord').pack(side='left', padx=(0, 10))
        ttk.Radiobutton(notify_frame, text='系統通知', variable=self.notify_type, value='system').pack(side='left')
        
        # 創建變數選擇區
        ttk.Label(main_frame, text="可用變數").pack(anchor='w', pady=(0, 5))
        variables_frame = ttk.Frame(main_frame)
        variables_frame.pack(fill='x', pady=(0, 15))
        
        variables = [
            ("事項內容", "{content}"),
            ("提醒時間", "{time}"),
            ("設定人", "{creator}")
        ]
        
        for label, var in variables:
            btn = ttk.Button(
                variables_frame,
                text=label,
                command=lambda v=var: self.insert_variable(v),
                style="Secondary.TButton"
            )
            btn.pack(side='left', padx=5)
        
        # 創建按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy,
            style="Secondary.TButton"
        ).pack(side='right', padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="確定",
            command=self.save_notification,
            style="Primary.TButton"
        ).pack(side='right')
        
        # 設定預設值
        self.set_default_values()
        if current_notification:
            self.load_current_notification(current_notification)
        else:
            # 設定預設的通知內容模板
            default_template = (
                "🔔 待辦事項提醒\n"
                "📝 {content}\n"
                "👤 設定人：{creator}\n"
                "⏰ 提醒時間：{time}"
            )
            self.content_text.insert('1.0', default_template)
        
        self.center_window()
    
    def set_default_values(self):
        """設定預設的日期和時間"""
        now = datetime.now()
        self.date_picker.set_date(now)
        self.hour_spinbox.set(now.hour)
        self.minute_spinbox.set(now.minute)
    
    def load_current_notification(self, notification_str):
        """載入現有的通知設定"""
        try:
            notification_data = json.loads(notification_str)
            notification_time = datetime.fromisoformat(notification_data['time'])
            self.date_picker.set_date(notification_time.date())
            self.hour_spinbox.set(f"{notification_time.hour:02d}")
            self.minute_spinbox.set(f"{notification_time.minute:02d}")
            
            if 'template' in notification_data:
                self.content_text.delete('1.0', 'end')
                self.content_text.insert('1.0', notification_data['template'])
            
            if 'image_url' in notification_data:
                self.image_url_entry.insert(0, notification_data['image_url'])
            
            if 'creator' in notification_data:
                self.creator_entry.delete(0, 'end')
                self.creator_entry.insert(0, notification_data['creator'])
            if 'type' in notification_data:
                self.notify_type.set(notification_data['type'])
        except Exception as e:
            print(f"載入通知設定時發生錯誤: {e}")
    
    def insert_variable(self, variable):
        """插入變數到文本框"""
        self.content_text.insert('insert', variable)
    
    def save_notification(self):
        try:
            # 獲取日期和時間
            date = self.date_picker.get_date()
            hour = int(self.hour_spinbox.get())
            minute = int(self.minute_spinbox.get())
            
            # 組合日期時間
            notification_time = datetime.combine(date, dt_time(hour, minute))
            
            # 獲取通知內容模板、圖片URL和設定人
            content_template = self.content_text.get('1.0', 'end-1c')
            image_url = self.image_url_entry.get().strip()
            creator = self.creator_entry.get().strip() or "用戶"  # 如果沒有輸入，使用預設值
            
            # 保存通知設定
            notification_data = {
                'time': notification_time.isoformat(),
                'template': content_template,
                'type': self.notify_type.get(),
                'creator': creator
            }
            
            # 如果有設定圖片 URL，則添加到通知數據中
            if image_url:
                notification_data['image_url'] = image_url
            
            if self.callback:
                self.callback(self.todo_id, json.dumps(notification_data))
            else:
                self.app.update_notification(self.todo_id, json.dumps(notification_data))
            self.destroy()
        except Exception as e:
            messagebox.showerror("錯誤", f"保存通知設定時發生錯誤：{e}")
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class TodoItem:
    def __init__(self, canvas, y, todo, delete_callback, toggle_callback, notification_callback, edit_callback):
        self.canvas = canvas
        self.y = y
        self.todo = todo
        self.delete_callback = delete_callback
        self.toggle_callback = toggle_callback
        self.notification_callback = notification_callback
        self.edit_callback = edit_callback
        
        self.completed = todo['completed']
        
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = canvas.winfo_reqwidth()
        if canvas_width <= 1:
            canvas_width = 640

        self.item_ids = []
        self.card_tag = f"task-card-{todo['id']}"
        card_x = 12
        card_y = y
        card_width = max(canvas_width - 24, 320)
        card_height = 118

        self.card_id = self._create_round_rect(
            card_x,
            card_y,
            card_x + card_width,
            card_y + card_height,
            12,
            fill=UI_COLORS["card"],
            outline=UI_COLORS["border"],
            width=1,
            tags=(self.card_tag,)
        )
        self.item_ids.append(self.card_id)

        left_x = card_x + 18
        text_x = left_x + 36
        top_y = card_y + 18
        detail_text = todo.get('content', '') or '未填寫說明'
        start_text = todo.get('start_date') or '未設定'
        status_text = todo.get('status', '未開始')
        priority_text = todo.get('priority', '中')
        category_text = todo.get('category', '其他')

        self.checkbox_text = '☑' if self.completed else '☐'
        self.checkbox_id = canvas.create_text(
            left_x,
            top_y - 1,
            text=self.checkbox_text,
            font=(FONT_FAMILY, 18),
            fill=UI_COLORS["success"] if self.completed else UI_COLORS["muted"],
            anchor='nw',
            tags=(self.card_tag,)
        )
        self.item_ids.append(self.checkbox_id)

        self.title_id = canvas.create_text(
            text_x,
            top_y,
            text=todo.get('title', '無標題'),
            font=FONT_BODY_BOLD,
            fill=UI_COLORS["muted"] if self.completed else UI_COLORS["text"],
            anchor='nw',
            width=card_width - 150,
            tags=(self.card_tag,)
        )
        self.item_ids.append(self.title_id)

        chip_y = top_y + 31
        chips = [
            (f"📁 {category_text}", UI_COLORS["background_soft"], UI_COLORS["primary"]),
            (f"● {status_text}", "#ECFDF5" if status_text == "已完成" else "#FFFBEB" if status_text == "進行中" else UI_COLORS["divider"], UI_COLORS["success"] if status_text == "已完成" else UI_COLORS["warning"] if status_text == "進行中" else UI_COLORS["muted"]),
            (f"● {priority_text}優先", "#FEF2F2" if priority_text == "高" else "#FFFBEB" if priority_text == "中" else UI_COLORS["divider"], UI_COLORS["danger"] if priority_text == "高" else UI_COLORS["warning"] if priority_text == "中" else UI_COLORS["muted"]),
            (f"開始 {start_text}", UI_COLORS["divider"], UI_COLORS["muted"]),
        ]
        chip_x = text_x
        for label, fill, color in chips:
            text_width = max(46, len(label) * 9 + 16)
            chip_id = self._create_round_rect(
                chip_x,
                chip_y,
                chip_x + text_width,
                chip_y + 24,
                8,
                fill=fill,
                outline=fill,
                width=1,
                tags=(self.card_tag,)
            )
            self.item_ids.append(chip_id)
            label_id = canvas.create_text(
                chip_x + 8,
                chip_y + 4,
                text=label,
                font=FONT_SMALL,
                fill=color,
                anchor='nw',
                tags=(self.card_tag,)
            )
            self.item_ids.append(label_id)
            chip_x += text_width + 8

        self.text_id = canvas.create_text(
            text_x,
            top_y + 66,
            text=detail_text,
            font=FONT_SMALL,
            fill=UI_COLORS["muted"],
            anchor='nw',
            width=card_width - 150,
            tags=(self.card_tag,)
        )
        self.item_ids.append(self.text_id)

        notification_icon = '🔔' if todo.get('notification') else '🔕'
        self.notification_id = canvas.create_text(
            card_x + card_width - 82,
            top_y + 1,
            text=notification_icon,
            font=(FONT_FAMILY, 13),
            fill=UI_COLORS["primary"] if todo.get('notification') else UI_COLORS["muted"],
            anchor='nw',
            tags=(self.card_tag,)
        )
        self.item_ids.append(self.notification_id)

        self.delete_btn_id = canvas.create_text(
            card_x + card_width - 42,
            top_y,
            text='×',
            font=(FONT_FAMILY, 16, "bold"),
            fill=UI_COLORS["danger"],
            anchor='nw',
            tags=(self.card_tag,)
        )
        self.item_ids.append(self.delete_btn_id)

        canvas.tag_bind(self.checkbox_id, '<Button-1>', self.on_toggle)
        canvas.tag_bind(self.notification_id, '<Button-1>', self.on_notification)
        canvas.tag_bind(self.delete_btn_id, '<Button-1>', self.on_delete)
        canvas.tag_bind(self.text_id, '<Double-Button-1>', self.on_edit)
        canvas.tag_bind(self.title_id, '<Double-Button-1>', self.on_edit)
        canvas.tag_bind(self.card_tag, '<Enter>', self.on_hover)
        canvas.tag_bind(self.card_tag, '<Leave>', self.on_leave)

    def _create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=12, **kwargs)

    def on_hover(self, event):
        self.canvas.itemconfigure(self.card_id, fill="#FDFEFF", outline=UI_COLORS["primary_hover"])

    def on_leave(self, event):
        self.canvas.itemconfigure(self.card_id, fill=UI_COLORS["card"], outline=UI_COLORS["border"])
    
    def on_edit(self, event):
        self.edit_callback(self.todo['id'])
    
    def on_delete(self, event):
        self.delete_callback(self.todo['id'])
    
    def on_toggle(self, event):
        self.toggle_callback(self.todo['id'])
    
    def on_notification(self, event):
        self.notification_callback(self.todo['id'])
    
    def destroy(self):
        for item_id in self.item_ids:
            self.canvas.delete(item_id)

class TaskEditorWindow(tk.Toplevel):
    def __init__(self, parent, app, todo=None, callback=None):
        super().__init__(parent)
        self.title("編輯任務" if todo else "新增任務")
        self.geometry("560x720")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=UI_COLORS["background"])
        self.app = app
        self.todo = todo
        self.callback = callback

        main_frame = ttk.Frame(self, padding=PAD_WINDOW)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="任務詳細資訊", style="Title.TLabel").grid(row=0, column=0, sticky='w', pady=(0, 4))
        ttk.Label(main_frame, text="整理任務內容、分類、優先級與完成紀錄。", style="Subtitle.TLabel").grid(row=1, column=0, sticky='w', pady=(0, PAD_SECTION))

        form_frame = tk.Frame(main_frame, bg=UI_COLORS["card"], highlightbackground=UI_COLORS["border"], highlightthickness=1, bd=0)
        form_frame.grid(row=2, column=0, sticky='nsew')
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="標題", style="CardMuted.TLabel").grid(row=0, column=0, columnspan=2, sticky='w', padx=18, pady=(18, 6))
        self.title_entry = ttk.Entry(form_frame, font=FONT_BODY)
        self.title_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=18, pady=(0, 14))

        ttk.Label(form_frame, text="內容", style="CardMuted.TLabel").grid(row=2, column=0, columnspan=2, sticky='w', padx=18, pady=(0, 6))
        self.content_text = tk.Text(form_frame, height=7, wrap='word', font=FONT_BODY, bg=UI_COLORS["card"], fg=UI_COLORS["text"], insertbackground=UI_COLORS["text"], relief='solid', bd=1, highlightthickness=1, highlightbackground=UI_COLORS["border"], highlightcolor=UI_COLORS["primary"])
        self.content_text.grid(row=3, column=0, columnspan=2, sticky='ew', padx=18, pady=(0, 14))

        ttk.Label(form_frame, text="分類", style="CardMuted.TLabel").grid(row=4, column=0, sticky='w', padx=18, pady=(0, 6))
        ttk.Label(form_frame, text="進度", style="CardMuted.TLabel").grid(row=4, column=1, sticky='w', padx=18, pady=(0, 6))

        self.category_box = ttk.Combobox(form_frame, values=CATEGORIES, state='readonly')
        self.category_box.grid(row=5, column=0, sticky='ew', padx=18, pady=(0, 14))

        self.status_box = ttk.Combobox(form_frame, values=STATUS_OPTIONS, state='readonly')
        self.status_box.grid(row=5, column=1, sticky='ew', padx=18, pady=(0, 14))

        ttk.Label(form_frame, text="優先級", style="CardMuted.TLabel").grid(row=6, column=0, sticky='w', padx=18, pady=(0, 6))
        ttk.Label(form_frame, text="開始日期", style="CardMuted.TLabel").grid(row=6, column=1, sticky='w', padx=18, pady=(0, 6))

        self.priority_box = ttk.Combobox(form_frame, values=PRIORITY_LEVELS, state='readonly')
        self.priority_box.grid(row=7, column=0, sticky='ew', padx=18, pady=(0, 14))

        self.start_date_label = ttk.Label(form_frame, text="", style="Card.TLabel")
        self.start_date_label.grid(row=7, column=1, sticky='ew', padx=18, pady=(0, 14))

        ttk.Label(form_frame, text="完成紀錄／心得（選填）", style="CardMuted.TLabel").grid(row=8, column=0, columnspan=2, sticky='w', padx=18, pady=(0, 6))
        self.history_text = tk.Text(form_frame, height=5, wrap='word', font=FONT_BODY, bg=UI_COLORS["card"], fg=UI_COLORS["text"], insertbackground=UI_COLORS["text"], relief='solid', bd=1, highlightthickness=1, highlightbackground=UI_COLORS["border"], highlightcolor=UI_COLORS["primary"])
        self.history_text.grid(row=9, column=0, columnspan=2, sticky='ew', padx=18, pady=(0, 18))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, sticky='ew', pady=(PAD_SECTION, 0))

        ttk.Button(btn_frame, text="取消", command=self.destroy, style="Secondary.TButton").pack(side='right', padx=(8, 0))
        ttk.Button(btn_frame, text="保存", command=self.save, style="Primary.TButton").pack(side='right')

        if todo:
            self.title_entry.insert(0, todo.get('title', ''))
            self.content_text.insert('1.0', todo.get('content', ''))
            self.category_box.set(todo.get('category', '其他'))
            self.priority_box.set(todo.get('priority', '中'))
            self.status_box.set(todo.get('status', '未開始'))
            self.start_date_label.config(text=todo.get('start_date', datetime.now().date().isoformat()))
            # 只在新增完成紀錄時使用文字框，避免編輯任務時把現有歷史再次追加為新紀錄
            history_records = todo.get('completion_history', [])
            if history_records:
                self.history_text.insert('1.0', '已存在完成紀錄，若要新增請在上方輸入新的心得。')
        else:
            self.category_box.set(CATEGORIES[0])
            self.priority_box.set(PRIORITY_LEVELS[1])
            self.status_box.set(STATUS_OPTIONS[0])
            self.start_date_label.config(text=datetime.now().date().isoformat())

        self.center_window()

    def save(self):
        title = self.title_entry.get().strip() or '無標題'
        content = self.content_text.get('1.0', 'end-1c').strip()
        start_date = self.start_date_label.cget('text') or datetime.now().date().isoformat()
        category = self.category_box.get() or '其他'
        priority = self.priority_box.get() or '中'
        status = self.status_box.get() or '未開始'
        history_notes = self.history_text.get('1.0', 'end-1c').strip()

        todo_data = {
            'title': title,
            'content': content,
            'start_date': start_date,
            'category': category,
            'priority': priority,
            'status': status,
            'notification': self.todo.get('notification') if self.todo else None,
            'completion_history': list(self.todo.get('completion_history', [])) if self.todo else []
        }

        if history_notes:
            note_text = history_notes.strip()
            if self.todo and note_text:
                existing_notes = [record.get('notes', '') for record in todo_data['completion_history']]
                if note_text not in existing_notes:
                    todo_data['completion_history'].append({
                        'time': datetime.now().isoformat(),
                        'notes': note_text
                    })
            elif note_text:
                todo_data['completion_history'].append({
                    'time': datetime.now().isoformat(),
                    'notes': note_text
                })

        if self.todo:
            self.callback(self.todo['id'], todo_data)
        else:
            self.callback(todo_data)
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class ExportWindow(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.title('匯出設定')
        self.geometry('760x760')
        self.minsize(760, 700)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=UI_COLORS["background"])

        self.app = app
        self.task_vars = []
        self.field_vars = {}
        self.selected_format = tk.StringVar(value='markdown')
        self.category_filter = tk.StringVar(value='所有')
        self.status_filter = tk.StringVar(value='所有')
        self.priority_filter = tk.StringVar(value='所有')
        self.scope_filter = tk.StringVar(value='all')
        self.date_filter = tk.StringVar(value='')

        self.selected_format.trace_add('write', lambda *args: self.update_export_path_extension())
        self.category_filter.trace_add('write', lambda *args: self.update_preview())
        self.status_filter.trace_add('write', lambda *args: self.update_preview())
        self.priority_filter.trace_add('write', lambda *args: self.update_preview())
        self.scope_filter.trace_add('write', lambda *args: self.update_preview())
        self.date_filter.trace_add('write', lambda *args: self.update_preview())

        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0, bg=UI_COLORS["background"])
        self.canvas.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        main_frame = ttk.Frame(self.canvas, padding=PAD_WINDOW)
        self.canvas_frame = self.canvas.create_window((0, 0), window=main_frame, anchor='nw')

        main_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.canvas_frame, width=e.width))

        ttk.Label(main_frame, text='匯出設定', style="Title.TLabel").pack(anchor='w', pady=(0, 4))
        ttk.Label(main_frame, text='預設勾選所有任務與欄位，您可從下方手動調整篩選條件、選擇要匯出的任務與內容欄位。', wraplength=680, justify='left', style="Subtitle.TLabel").pack(anchor='w', pady=(0, PAD_SECTION))

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))

        task_frame = ttk.Labelframe(top_frame, text='選擇任務', padding='10')
        task_frame.pack(side='left', fill='both', expand=True, padx=(0, 6))

        self.select_all_var = tk.IntVar(value=1)
        ttk.Button(task_frame, text='全選/取消全選', command=self.toggle_select_all, style="Secondary.TButton").pack(anchor='w')

        canvas = tk.Canvas(task_frame, borderwidth=0, height=260, bg=UI_COLORS["card"], highlightthickness=0)
        self.task_scroll = ttk.Scrollbar(task_frame, orient='vertical', command=canvas.yview)
        self.task_panel = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=self.task_scroll.set)
        self.task_scroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=self.task_panel, anchor='nw')
        self.task_panel.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        self.build_task_list()

        filter_frame = ttk.Labelframe(top_frame, text='篩選範圍', padding='10')
        filter_frame.pack(side='left', fill='both', expand=True, padx=(6, 0))

        ttk.Label(filter_frame, text='匯出範圍').pack(anchor='w', pady=(0, 4))
        for value, label in [('all','全部'), ('category','分類'), ('date','日期'), ('manual','手動勾選')]:
            ttk.Radiobutton(filter_frame, text=label, variable=self.scope_filter, value=value, command=self.update_preview).pack(anchor='w', pady=1)

        ttk.Label(filter_frame, text='分類').pack(anchor='w', pady=(8, 4))
        ttk.Combobox(filter_frame, values=['所有'] + CATEGORIES, state='readonly', textvariable=self.category_filter).pack(fill='x')

        ttk.Label(filter_frame, text='狀態').pack(anchor='w', pady=(8, 4))
        ttk.Combobox(filter_frame, values=['所有'] + STATUS_OPTIONS, state='readonly', textvariable=self.status_filter).pack(fill='x')

        ttk.Label(filter_frame, text='優先級').pack(anchor='w', pady=(8, 4))
        ttk.Combobox(filter_frame, values=['所有'] + PRIORITY_LEVELS, state='readonly', textvariable=self.priority_filter).pack(fill='x')

        ttk.Label(filter_frame, text='日期').pack(anchor='w', pady=(8, 4))
        ttk.Entry(filter_frame, textvariable=self.date_filter).pack(fill='x')

        field_frame = ttk.Labelframe(main_frame, text='選擇內容', padding='10')
        field_frame.pack(fill='x', pady=(0, 10))
        for key, label in [
            ('title', '標題'),
            ('content', '內容'),
            ('category', '分類'),
            ('priority', '優先級'),
            ('status', '進度'),
            ('start_date', '開始日期'),
            ('completion_history', '完成紀錄')
        ]:
            var = tk.IntVar(value=1)
            self.field_vars[key] = var
            ttk.Checkbutton(field_frame, text=label, variable=var, command=self.update_preview).pack(side='left', padx=6, pady=4)

        format_frame = ttk.Labelframe(main_frame, text='匯出格式', padding='10')
        format_frame.pack(fill='x', pady=(0, 10))
        ttk.Radiobutton(format_frame, text='Markdown', variable=self.selected_format, value='markdown', command=self.update_preview).pack(side='left', padx=12)
        ttk.Radiobutton(format_frame, text='JSON', variable=self.selected_format, value='json', command=self.update_preview).pack(side='left', padx=12)

        path_frame = ttk.Labelframe(main_frame, text='匯出路徑', padding='10')
        path_frame.pack(fill='x', pady=(0, 10))
        self.export_path_var = tk.StringVar(value='')
        ttk.Entry(path_frame, textvariable=self.export_path_var, state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 6))
        ttk.Button(path_frame, text='選擇路徑', command=self.choose_export_path, style="Secondary.TButton").pack(side='right')

        preview_frame = ttk.Labelframe(main_frame, text='匯出預覽', padding='10')
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        self.preview_text = tk.Text(preview_frame, wrap='word', state='disabled', font=FONT_SMALL, bg=UI_COLORS["card"], fg=UI_COLORS["text"], relief='solid', bd=1, highlightthickness=1, highlightbackground=UI_COLORS["border"])
        self.preview_text.pack(fill='both', expand=True)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x')
        ttk.Button(action_frame, text='更新預覽', command=self.update_preview, style="Secondary.TButton").pack(side='left')
        ttk.Button(action_frame, text='執行匯出', command=self.on_export, style="Primary.TButton").pack(side='right')
        ttk.Button(action_frame, text='取消', command=self.destroy, style="Secondary.TButton").pack(side='right', padx=(0, 5))

        self.update_preview()

    def choose_export_path(self):
        default_ext = '.md' if self.selected_format.get() == 'markdown' else '.json'
        filetypes = [('Markdown 檔案', '*.md')] if self.selected_format.get() == 'markdown' else [('JSON 檔案', '*.json')]
        path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            title='選擇匯出檔案'
        )
        if path:
            self.export_path_var.set(self.adjust_path_extension(path))

    def adjust_path_extension(self, path):
        if not path:
            return ''
        ext = '.md' if self.selected_format.get() == 'markdown' else '.json'
        base, current_ext = os.path.splitext(path)
        if current_ext.lower() != ext:
            return base + ext
        return path

    def update_export_path_extension(self):
        current_path = self.export_path_var.get().strip()
        if current_path:
            self.export_path_var.set(self.adjust_path_extension(current_path))

    def build_task_list(self):
        for widget in self.task_panel.winfo_children():
            widget.destroy()
        self.task_vars.clear()
        for todo in self.app.todos:
            var = tk.IntVar(value=1)
            self.task_vars.append((todo, var))
            cb = ttk.Checkbutton(self.task_panel, text=f"{todo.get('title', '無標題')} ({todo.get('category','其他')}/{todo.get('status','未開始')})", variable=var, command=self.update_preview)
            cb.pack(anchor='w', pady=2, fill='x')

    def toggle_select_all(self):
        should_select = not all(var.get() for _, var in self.task_vars)
        for _, var in self.task_vars:
            var.set(1 if should_select else 0)
        self.select_all_var.set(1 if should_select else 0)
        self.update_preview()

    def filtered_tasks(self):
        selected = []
        for todo, var in self.task_vars:
            if self.scope_filter.get() == 'manual' and not var.get():
                continue
            if self.scope_filter.get() == 'manual' and var.get():
                pass
            if self.scope_filter.get() != 'manual' and not var.get():
                continue
            if self.category_filter.get() != '所有' and todo.get('category') != self.category_filter.get():
                continue
            if self.status_filter.get() != '所有' and todo.get('status') != self.status_filter.get():
                continue
            if self.priority_filter.get() != '所有' and todo.get('priority') != self.priority_filter.get():
                continue
            if self.scope_filter.get() == 'date' and self.date_filter.get():
                if str(todo.get('start_date', '')) != str(self.date_filter.get()):
                    continue
            selected.append(todo)
        return selected

    def selected_fields(self):
        return [k for k, v in self.field_vars.items() if v.get()]

    def generate_preview_text(self):
        todos = self.filtered_tasks()
        fields = self.selected_fields()
        if self.selected_format.get() == 'json':
            filtered = [{k: todo.get(k) for k in fields} for todo in todos]
            return json.dumps(filtered, ensure_ascii=False, indent=2)
        lines = ['# 預覽 - 匯出內容', '']
        for todo in todos:
            if 'title' in fields:
                lines.append(f"## {todo.get('title', '無標題')}")
            if 'category' in fields:
                lines.append(f"- 類別：{todo.get('category', '其他')}")
            if 'priority' in fields:
                lines.append(f"- 優先級：{todo.get('priority', '中')}")
            if 'status' in fields:
                lines.append(f"- 進度：{todo.get('status', '未開始')}")
            if 'start_date' in fields:
                lines.append(f"- 開始日期：{todo.get('start_date') or '未設定'}")
            if 'content' in fields:
                lines.append(f"- 內容：{todo.get('content', '')}")
            if 'completion_history' in fields and todo.get('completion_history'):
                lines.append('- 完成紀錄：')
                for record in todo['completion_history']:
                    lines.append(f"  - {record.get('time')}：{record.get('notes')}")
            lines.append('')
        return '\n'.join(lines)

    def update_preview(self):
        text = self.generate_preview_text()
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0', 'end')
        self.preview_text.insert('1.0', text)
        self.preview_text.config(state='disabled')

    def on_export(self):
        todos = self.filtered_tasks()
        fields = self.selected_fields()
        if not todos:
            messagebox.showwarning('警告', '請先選擇要匯出的任務。')
            return
        if not fields:
            messagebox.showwarning('警告', '請至少選擇一個欄位。')
            return
        path = self.export_path_var.get().strip()
        if not path:
            self.choose_export_path()
            path = self.export_path_var.get().strip()
        if not path:
            return
        if self.selected_format.get() == 'json':
            self.app.export_to_json(todos, fields, path=path)
        else:
            self.app.export_to_markdown(todos, fields, path=path)
        self.destroy()

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.title("Discord 設定")
        self.callback = callback

        # 設定視窗大小和位置
        self.geometry("480x320")  # 增加高度以容納說明文字
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=UI_COLORS["background"])

        # 創建主框架
        main_frame = ttk.Frame(self, padding=PAD_WINDOW)
        main_frame.pack(fill='both', expand=True)

        # 添加說明文字
        ttk.Label(main_frame, text="Discord 設定", style="Title.TLabel").pack(anchor='w', pady=(0, 4))
        ttk.Label(
            main_frame,
            text="請設定 Discord Webhook URL\n"
            "1. 在 Discord 中右鍵點擊頻道\n"
            "2. 選擇「編輯頻道」→「整合」→「建立 Webhook」\n"
            "3. 複製 Webhook URL 並貼到下方\n",
            justify='left',
            wraplength=420,
            style="Subtitle.TLabel"
        ).pack(anchor='w', pady=(0, PAD_SECTION))

        # Discord Webhook URL 輸入
        ttk.Label(main_frame, text="Discord Webhook URL：").pack(anchor='w', pady=(0, 5))
        self.webhook_entry = ttk.Entry(main_frame, width=50)
        self.webhook_entry.pack(fill='x', pady=(0, 15))
        self.webhook_entry.insert(0, DISCORD_WEBHOOK_URL)
        self.webhook_entry.configure(show='*')

        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(15, 0))

        ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy,
            style="Secondary.TButton"
        ).pack(side='right', padx=(5, 0))

        ttk.Button(
            button_frame,
            text="保存",
            command=self.save_settings,
            style="Primary.TButton"
        ).pack(side='right')

        self.center_window()

    def save_settings(self):
        global DISCORD_WEBHOOK_URL
        webhook_url = self.webhook_entry.get().strip()
        
        if not webhook_url:
            messagebox.showerror("錯誤", "請輸入 Discord Webhook URL")
            return
        
        # 更新配置
        config = {"discord_webhook_url": webhook_url}
        DISCORD_WEBHOOK_URL = webhook_url
        save_config(config)
        self.webhook_entry.delete(0, 'end')
        self.webhook_entry.insert(0, webhook_url)
        
        if self.callback:
            self.callback()
        
        messagebox.showinfo("成功", "設定已保存")
        self.destroy()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Schedule")
        self.root.geometry("760x820")
        self.root.minsize(560, 620)
        self.root.resizable(True, True)
        self.style = setup_style(self.root)
        self.root.configure(bg=UI_COLORS["background"])
        
        # 設定應用程式圖示
        try:
            self.root.iconbitmap('icon.ico')
        except:
            print("無法載入圖示檔案，使用預設圖示")
        
        # 設定顏色主題
        self.colors = UI_COLORS

        self.background = GradientFrame(
            self.root,
            theme="theme1",
            highlightthickness=0
        )
        self.background.place(x=0, y=0, relwidth=1, relheight=1)

        self.main_container = ttk.Frame(self.root, style="TFrame", padding=PAD_WINDOW)
        self.main_container.place(relx=0.5, rely=0, anchor='n', relwidth=1, relheight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(2, weight=1)

        self.header_frame = tk.Frame(
            self.main_container,
            bg=UI_COLORS["card"],
            highlightbackground=UI_COLORS["border"],
            highlightthickness=1,
            bd=0
        )
        self.header_frame.grid(row=0, column=0, sticky='ew', pady=(0, PAD_SECTION))
        self.header_frame.columnconfigure(0, weight=1)

        ttk.Label(self.header_frame, text="📋 Schedule", style="HeaderTitle.TLabel").grid(row=0, column=0, sticky='w', padx=18, pady=(16, 4))
        ttk.Label(self.header_frame, text="任務進度&提醒集中管理", style="HeaderSubtitle.TLabel").grid(row=1, column=0, sticky='w', padx=18, pady=(0, 12))

        self.metric_frame = tk.Frame(self.header_frame, bg=UI_COLORS["card"])
        self.metric_frame.grid(row=2, column=0, sticky='ew', padx=18, pady=(0, 16))
        for i in range(3):
            self.metric_frame.columnconfigure(i, weight=1)

        self.today_value = self._create_metric(0, "今天")
        self.rate_value = self._create_metric(1, "完成率")
        self.today_task_value = self._create_metric(2, "今日任務")

        self.input_frame = tk.Frame(
            self.main_container,
            bg=UI_COLORS["card"],
            highlightbackground=UI_COLORS["border"],
            highlightthickness=1,
            bd=0
        )
        self.input_frame.grid(row=1, column=0, sticky='ew', pady=(0, PAD_SECTION))
        self.input_frame.columnconfigure(1, weight=1)

        self.search_icon = tk.Label(self.input_frame, text="🔍", bg=UI_COLORS["card"], fg=UI_COLORS["muted"], font=FONT_BODY)
        self.search_icon.grid(row=0, column=0, padx=(16, 8), pady=14)

        self.placeholder_text = "搜尋或輸入新任務..."
        self.input_entry = ttk.Entry(self.input_frame, font=FONT_BODY)
        self.input_entry.grid(row=0, column=1, sticky='ew', pady=14)
        self.input_entry.insert(0, self.placeholder_text)
        self.input_entry.configure(foreground=UI_COLORS["muted"])

        self.add_btn = ttk.Button(
            self.input_frame,
            text='＋新增',
            command=self.open_task_editor,
            style="Primary.TButton"
        )
        self.add_btn.grid(row=0, column=2, padx=(12, 8), pady=14)

        self.export_btn = ttk.Button(
            self.input_frame,
            text='匯出',
            command=self.open_export_window,
            style="Secondary.TButton"
        )
        self.export_btn.grid(row=0, column=3, padx=(0, 16), pady=14)

        self.list_frame = tk.Frame(
            self.main_container,
            bg=UI_COLORS["background_soft"],
            highlightbackground=UI_COLORS["border"],
            highlightthickness=1,
            bd=0
        )
        self.list_frame.grid(row=2, column=0, sticky='nsew')
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(1, weight=1)

        self.list_header = tk.Frame(self.list_frame, bg=UI_COLORS["background_soft"])
        self.list_header.grid(row=0, column=0, sticky='ew', padx=18, pady=(16, 8))
        self.list_header.columnconfigure(0, weight=1)
        ttk.Label(self.list_header, text="任務列表", style="SurfaceSubtitle.TLabel").grid(row=0, column=0, sticky='w')
        self.task_count_label = ttk.Label(self.list_header, text="", style="SurfaceMuted.TLabel")
        self.task_count_label.grid(row=0, column=1, sticky='e')

        self.task_canvas = tk.Canvas(self.list_frame, bg=UI_COLORS["background_soft"], highlightthickness=0, bd=0)
        self.task_canvas.grid(row=1, column=0, sticky='nsew', padx=(18, 8), pady=(0, 18))
        self.task_scrollbar = ttk.Scrollbar(self.list_frame, orient='vertical', command=self.task_canvas.yview)
        self.task_scrollbar.grid(row=1, column=1, sticky='ns', pady=(0, 18), padx=(0, 10))
        self.task_canvas.configure(yscrollcommand=self.task_scrollbar.set)
        
        # 載入待辦事項
        self.load_todos()
        self.todo_items = []
        
        # 綁定回車鍵
        self.input_entry.bind('<FocusIn>', self._clear_placeholder)
        self.input_entry.bind('<FocusOut>', self._restore_placeholder)
        self.input_entry.bind('<Return>', lambda e: self.add_todo())
        
        # 渲染待辦事項
        self.render_todos()
        
        # 啟動通知服務
        self.notification_service = NotificationService(self, DISCORD_WEBHOOK_URL)
        self.notification_service.start()
        
        # 創建菜單欄
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 添加設定菜單
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="Discord 設定", command=self.show_config)
        
        # 綁定視窗大小改變事件
        self.root.bind('<Configure>', self.on_resize)
        
        # 初始化響應式佈局
        self.root.after(100, self.on_resize)
    
    def on_resize(self, event=None):
        """響應式佈局更新"""
        if event and event.widget != self.root:
            return
        self.main_container.configure(padding=PAD_WINDOW)
        self.update_header_stats()
        self.render_todos()

    def _create_metric(self, column, label):
        metric = tk.Frame(self.metric_frame, bg=UI_COLORS["card"])
        metric.grid(row=0, column=column, sticky='ew', padx=(0, 12 if column < 2 else 0))
        ttk.Label(metric, text=label, style="HeaderMetric.TLabel").pack(anchor='w')
        value_widget = ttk.Label(metric, text="", style="HeaderValue.TLabel")
        value_widget.pack(anchor='w', pady=(2, 0))
        return value_widget

    def _clear_placeholder(self, event=None):
        if self.input_entry.get() == self.placeholder_text:
            self.input_entry.delete(0, 'end')
            self.input_entry.configure(foreground=UI_COLORS["text"])

    def _restore_placeholder(self, event=None):
        if not self.input_entry.get().strip():
            self.input_entry.insert(0, self.placeholder_text)
            self.input_entry.configure(foreground=UI_COLORS["muted"])

    def update_header_stats(self):
        total = len(getattr(self, 'todos', []))
        completed = len([todo for todo in getattr(self, 'todos', []) if todo.get('completed')])
        today = datetime.now().date().isoformat()
        today_count = len([todo for todo in getattr(self, 'todos', []) if todo.get('start_date') == today])
        rate = int((completed / total) * 100) if total else 0
        self.today_value.configure(text=datetime.now().strftime("%Y/%m/%d"))
        self.rate_value.configure(text=f"{rate}%")
        self.today_task_value.configure(text=f"{today_count} / {total}")
        self.task_count_label.configure(text=f"{total} 項任務")
    
    def load_todos(self):
        """載入待辦事項"""
        self.todos = load_storage_todos()
        print("成功載入待辦事項：", self.todos)
    
    def save_todos(self):
        """保存待辦事項"""
        try:
            save_storage_todos(self.todos)
            print("成功保存待辦事項：", self.todos)
        except Exception as e:
            print(f"保存待辦事項時發生錯誤：{e}")
    
    def check_notifications(self):
        """檢查並發送通知"""
        return None
    
    def update_notification(self, todo_id, notification_time):
        """更新待辦事項的通知時間"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['notification'] = notification_time
                break
        self.save_todos()
        self.render_todos()
    
    def show_notification_settings(self, todo_id):
        # 找到對應的待辦事項
        todo = next((t for t in self.todos if t['id'] == todo_id), None)
        if todo:
            current_notification = todo.get('notification')
            if current_notification:
                try:
                    # 嘗試解析新格式
                    notification_data = json.loads(current_notification)
                except json.JSONDecodeError:
                    # 如果是舊格式，轉換為新格式
                    try:
                        notification_time = datetime.fromisoformat(current_notification)
                        current_notification = json.dumps({
                            'time': notification_time.isoformat(),
                            'type': 'system'
                        })
                    except:
                        current_notification = None
            
            NotificationWindow(self.root, todo_id, current_notification, self)
    
    def open_task_editor(self):
        TaskEditorWindow(self.root, self, callback=self.create_todo)

    def create_todo(self, todo_data):
        todo_data['id'] = str(uuid.uuid4())
        todo_data['text'] = todo_data.get('title', '無標題')
        todo_data['completed'] = todo_data.get('status') == '已完成'
        if todo_data['completed'] and not todo_data.get('completion_time'):
            todo_data['completion_time'] = datetime.now().isoformat()
        if 'completion_history' not in todo_data:
            todo_data['completion_history'] = []
        self.todos.append(todo_data)
        self.save_todos()
        self.render_todos()

    def open_edit_task(self, todo_id):
        todo = next((t for t in self.todos if t['id'] == todo_id), None)
        if todo:
            TaskEditorWindow(self.root, self, todo=todo, callback=self.update_todo)

    def update_todo(self, todo_id, todo_data):
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo.update(todo_data)
                todo['text'] = todo_data.get('title', todo.get('text', '無標題'))
                todo['completed'] = todo_data.get('status') == '已完成'
                if todo['completed'] and not todo.get('completion_time'):
                    todo['completion_time'] = datetime.now().isoformat()
                if not todo['completed']:
                    todo.pop('completion_time', None)
                break
        self.save_todos()
        self.render_todos()

    def open_export_window(self):
        ExportWindow(self.root, self)

    def export_to_json(self, todos, fields, path=None):
        ExportService.export_to_json(todos, fields, path=path)

    def export_to_markdown(self, todos, fields, path=None):
        ExportService.export_to_markdown(todos, fields, path=path)
    
    def render_todos(self):
        # 清除現有的待辦事項
        for item in self.todo_items:
            item.destroy()
        self.todo_items.clear()

        self.update_header_stats()
        canvas = getattr(self, 'task_canvas', None)
        if canvas is None:
            return
        canvas.delete('empty-state')
        canvas.update_idletasks()
        canvas_width = max(canvas.winfo_width(), 360)
        start_y = 8
        item_height = 134

        if not self.todos:
            canvas.create_text(
                canvas_width // 2,
                96,
                text="目前沒有任務",
                font=FONT_SUBTITLE,
                fill=UI_COLORS["muted"],
                anchor='center',
                tags=('empty-state',)
            )
            canvas.configure(scrollregion=(0, 0, canvas_width, 200))
            return

        # 重新渲染所有待辦事項
        for i, todo in enumerate(self.todos):
            y = start_y + i * item_height
            todo_item = TodoItem(
                canvas,
                y,
                todo,
                self.delete_todo,
                self.toggle_todo,
                self.show_notification_settings,
                self.open_edit_task
            )
            self.todo_items.append(todo_item)
        canvas.configure(scrollregion=(0, 0, canvas_width, start_y + len(self.todos) * item_height + 8))
    
    def add_todo(self):
        """添加新的待辦事項"""
        text = self.input_entry.get().strip()
        if text and text != getattr(self, 'placeholder_text', ''):
            new_todo = {
                'id': str(uuid.uuid4()),
                'title': text,
                'content': '',
                'start_date': datetime.now().date().isoformat(),
                'category': CATEGORIES[0],
                'priority': PRIORITY_LEVELS[1],
                'status': '未開始',
                'completed': False,
                'notification': None,
                'completion_history': []
            }
            self.todos.append(new_todo)
            self.save_todos()
            self.render_todos()
            self.input_entry.delete(0, 'end')
            self._restore_placeholder()
    
    def delete_todo(self, todo_id):
        """刪除待辦事項"""
        self.todos = [todo for todo in self.todos if todo['id'] != todo_id]
        self.save_todos()
        self.render_todos()
    
    def toggle_todo(self, todo_id):
        """切換待辦事項的完成狀態"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = not todo['completed']
                break
        self.save_todos()
        self.render_todos()
    
    def show_config(self):
        ConfigWindow(self.root)

def main():
    # 先載入配置
    load_config()

    # 創建主窗口
    root = tk.Tk()
    app = SearchApp(root)

    # 如果沒有配置文件或 webhook url 是預設值，自動打開設定視窗
    if not os.path.exists(CONFIG_FILE) or DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        root.after(100, app.show_config)

    root.mainloop()


def run_app():
    main()


if __name__ == '__main__':
    run_app() 
