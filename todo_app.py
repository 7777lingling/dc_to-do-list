import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import json
from datetime import datetime, time as dt_time
import uuid
from plyer import notification
from tkcalendar import DateEntry
import threading
import time
import requests
import os

# 配置文件路徑
CONFIG_FILE = "config.json"
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"  # 預設值
CATEGORIES = ["學習", "工作", "生活", "其他"]
PRIORITY_LEVELS = ["低", "中", "高"]
STATUS_OPTIONS = ["未開始", "進行中", "已完成"]

# 加載配置
def load_config():
    global DISCORD_WEBHOOK_URL
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                DISCORD_WEBHOOK_URL = config.get('discord_webhook_url', DISCORD_WEBHOOK_URL)
        except Exception as e:
            print(f"加載配置文件時發生錯誤: {e}")

# 保存配置
def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存配置文件時發生錯誤: {e}")

class GradientFrame(tk.Canvas):
    # 預設顏色組
    COLOR_SCHEMES = {
        "theme1": {
            "start": "#ff8177",  # 粉紅色
            "end": "#b12a5b"     # 深紅色
        },
        "theme2": {
            "start": "#00c6fb",  # 淺藍色
            "end": "#005bea"     # 深藍色
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
        
        # 創建漸層效果
        limit = width
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
        self.geometry("400x580")  # 增加一點高度來容納新的輸入欄位
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # 創建主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 創建日期選擇器
        ttk.Label(main_frame, text="選擇日期：").pack(anchor='w', pady=(0, 5))
        self.date_picker = DateEntry(
            main_frame,
            width=20,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd'
        )
        self.date_picker.pack(fill='x', pady=(0, 15))
        
        # 創建時間選擇器
        ttk.Label(main_frame, text="選擇時間：").pack(anchor='w', pady=(0, 5))
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
        ttk.Label(main_frame, text="設定人：").pack(anchor='w', pady=(0, 5))
        self.creator_entry = ttk.Entry(main_frame)
        self.creator_entry.pack(fill='x', pady=(0, 15))
        self.creator_entry.insert(0, "用戶")  # 預設值
        
        # 創建通知內容編輯區
        ttk.Label(main_frame, text="通知內容：").pack(anchor='w', pady=(0, 5))
        self.content_text = tk.Text(
            main_frame,
            height=5,
            wrap='word',
            font=('Microsoft YaHei UI', 10)
        )
        self.content_text.pack(fill='x', pady=(0, 15))
        
        # 添加圖片 URL 輸入
        ttk.Label(main_frame, text="圖片 URL（可選）：").pack(anchor='w', pady=(0, 5))
        self.image_url_entry = ttk.Entry(main_frame)
        self.image_url_entry.pack(fill='x', pady=(0, 15))

        # 通知類型選擇
        ttk.Label(main_frame, text="通知方式：").pack(anchor='w', pady=(0, 5))
        self.notify_type = tk.StringVar(value='discord')
        notify_frame = ttk.Frame(main_frame)
        notify_frame.pack(fill='x', pady=(0, 15))
        ttk.Radiobutton(notify_frame, text='Discord', variable=self.notify_type, value='discord').pack(side='left', padx=(0, 10))
        ttk.Radiobutton(notify_frame, text='系統通知', variable=self.notify_type, value='system').pack(side='left')
        
        # 創建變數選擇區
        ttk.Label(main_frame, text="可用變數：").pack(anchor='w', pady=(0, 5))
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
                command=lambda v=var: self.insert_variable(v)
            )
            btn.pack(side='left', padx=5)
        
        # 創建按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy
        ).pack(side='right', padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="確定",
            command=self.save_notification
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
        
        canvas_width = canvas.winfo_reqwidth()
        if canvas_width <= 1:
            canvas_width = 500
        
        item_width = int(canvas_width * 0.74)
        detail_text = todo.get('content', '') or '未填寫說明'
        start_text = todo.get('start_date') or '未設定'
        status_text = todo.get('status', '未開始')
        meta = f"{todo.get('category', '其他')} | {todo.get('priority', '中')} | {status_text} | 開始 {start_text}"
        display_text = f"{todo.get('title', '無標題')}\n{meta}\n{detail_text}"
        
        self.checkbox_text = '☑' if self.completed else '☐'
        self.checkbox_id = canvas.create_text(
            int(canvas_width * 0.05),
            y,
            text=self.checkbox_text,
            font=('Microsoft YaHei UI', 16),
            fill='#00c6fb',
            anchor='nw'
        )
        
        self.text_id = canvas.create_text(
            int(canvas_width * 0.12),
            y,
            text=display_text,
            font=('Microsoft YaHei UI', 11),
            fill='#ffffff',
            anchor='nw',
            width=item_width
        )
        
        notification_icon = '🔔' if todo.get('notification') else '🔕'
        self.notification_id = canvas.create_text(
            int(canvas_width * 0.78),
            y + 10,
            text=notification_icon,
            font=('Microsoft YaHei UI', 14),
            fill='#7289DA',
            anchor='w'
        )
        
        self.delete_btn_id = canvas.create_text(
            int(canvas_width * 0.92),
            y + 10,
            text='❌',
            font=('Microsoft YaHei UI', 12),
            fill='#ff8177',
            anchor='w'
        )
        
        canvas.tag_bind(self.checkbox_id, '<Button-1>', self.on_toggle)
        canvas.tag_bind(self.notification_id, '<Button-1>', self.on_notification)
        canvas.tag_bind(self.delete_btn_id, '<Button-1>', self.on_delete)
        canvas.tag_bind(self.text_id, '<Double-Button-1>', self.on_edit)
    
    def on_edit(self, event):
        self.edit_callback(self.todo['id'])
    
    def on_delete(self, event):
        self.delete_callback(self.todo['id'])
    
    def on_toggle(self, event):
        self.toggle_callback(self.todo['id'])
    
    def on_notification(self, event):
        self.notification_callback(self.todo['id'])
    
    def destroy(self):
        self.canvas.delete(self.text_id)
        self.canvas.delete(self.delete_btn_id)
        self.canvas.delete(self.checkbox_id)
        self.canvas.delete(self.notification_id)

class TaskEditorWindow(tk.Toplevel):
    def __init__(self, parent, app, todo=None, callback=None):
        super().__init__(parent)
        self.title("編輯任務" if todo else "新增任務")
        self.geometry("450x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.app = app
        self.todo = todo
        self.callback = callback

        main_frame = ttk.Frame(self, padding="16")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="標題：").pack(anchor='w', pady=(0, 5))
        self.title_entry = ttk.Entry(main_frame, font=('Microsoft YaHei UI', 13))
        self.title_entry.pack(fill='x', pady=(0, 12))

        ttk.Label(main_frame, text="內容：").pack(anchor='w', pady=(0, 5))
        self.content_text = tk.Text(main_frame, height=6, wrap='word', font=('Microsoft YaHei UI', 11))
        self.content_text.pack(fill='both', pady=(0, 12))

        meta_frame = ttk.Frame(main_frame)
        meta_frame.pack(fill='x', pady=(0, 12))

        left_meta = ttk.Frame(meta_frame)
        left_meta.pack(side='left', fill='x', expand=True)
        right_meta = ttk.Frame(meta_frame)
        right_meta.pack(side='left', fill='x', expand=True, padx=(10, 0))

        ttk.Label(left_meta, text="分類：").pack(anchor='w', pady=(0, 5))
        self.category_box = ttk.Combobox(left_meta, values=CATEGORIES, state='readonly')
        self.category_box.pack(fill='x')

        ttk.Label(left_meta, text="優先級：").pack(anchor='w', pady=(10, 5))
        self.priority_box = ttk.Combobox(left_meta, values=PRIORITY_LEVELS, state='readonly')
        self.priority_box.pack(fill='x')

        ttk.Label(right_meta, text="進度：").pack(anchor='w', pady=(0, 5))
        self.status_box = ttk.Combobox(right_meta, values=STATUS_OPTIONS, state='readonly')
        self.status_box.pack(fill='x')

        ttk.Label(right_meta, text="開始日期：").pack(anchor='w', pady=(10, 5))
        self.start_date_label = ttk.Label(right_meta, text="")
        self.start_date_label.pack(fill='x')

        ttk.Label(main_frame, text="完成紀錄／心得（選填）：").pack(anchor='w', pady=(0, 5))
        self.history_text = tk.Text(main_frame, height=4, wrap='word', font=('Microsoft YaHei UI', 11))
        self.history_text.pack(fill='both', pady=(0, 12))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side='right', padx=(5, 0))
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side='right')

        if todo:
            self.title_entry.insert(0, todo.get('title', ''))
            self.content_text.insert('1.0', todo.get('content', ''))
            self.category_box.set(todo.get('category', '其他'))
            self.priority_box.set(todo.get('priority', '中'))
            self.status_box.set(todo.get('status', '未開始'))
            self.start_date_label.config(text=todo.get('start_date', datetime.now().date().isoformat()))
            history_records = todo.get('completion_history', [])
            if history_records:
                history_lines = [f"[{r.get('time')}] {r.get('notes')}" for r in history_records]
                self.history_text.insert('1.0', '\n'.join(history_lines))
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
            todo_data['completion_history'].append({
                'time': datetime.now().isoformat(),
                'notes': history_notes
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

        self.app = app
        self.task_vars = []
        self.field_vars = {}
        self.selected_format = tk.StringVar(value='markdown')
        self.category_filter = tk.StringVar(value='所有')
        self.status_filter = tk.StringVar(value='所有')
        self.priority_filter = tk.StringVar(value='所有')

        self.selected_format.trace_add('write', lambda *args: self.update_export_path_extension())

        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        main_frame = ttk.Frame(self.canvas, padding='12')
        self.canvas_frame = self.canvas.create_window((0, 0), window=main_frame, anchor='nw')

        main_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.canvas_frame, width=e.width))

        ttk.Label(main_frame, text='匯出說明', font=('Microsoft YaHei UI', 12, 'bold')).pack(anchor='w', pady=(0, 6))
        ttk.Label(main_frame, text='預設勾選所有任務與欄位，您可從下方手動調整篩選條件、選擇要匯出的任務與內容欄位。', wraplength=680, justify='left').pack(anchor='w', pady=(0, 14))

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))

        task_frame = ttk.Labelframe(top_frame, text='選擇任務', padding='10')
        task_frame.pack(side='left', fill='both', expand=True, padx=(0, 6))

        self.select_all_var = tk.IntVar(value=1)
        ttk.Checkbutton(task_frame, text='全部選取', variable=self.select_all_var, command=self.toggle_select_all).pack(anchor='w')

        canvas = tk.Canvas(task_frame, borderwidth=0, height=260)
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

        ttk.Label(filter_frame, text='分類').pack(anchor='w', pady=(0, 4))
        ttk.Combobox(filter_frame, values=['所有'] + CATEGORIES, state='readonly', textvariable=self.category_filter).pack(fill='x')

        ttk.Label(filter_frame, text='狀態').pack(anchor='w', pady=(8, 4))
        ttk.Combobox(filter_frame, values=['所有'] + STATUS_OPTIONS, state='readonly', textvariable=self.status_filter).pack(fill='x')

        ttk.Label(filter_frame, text='優先級').pack(anchor='w', pady=(8, 4))
        ttk.Combobox(filter_frame, values=['所有'] + PRIORITY_LEVELS, state='readonly', textvariable=self.priority_filter).pack(fill='x')

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
        ttk.Button(path_frame, text='選擇路徑', command=self.choose_export_path).pack(side='right')

        preview_frame = ttk.Labelframe(main_frame, text='匯出預覽', padding='10')
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        self.preview_text = tk.Text(preview_frame, wrap='word', state='disabled', font=('Microsoft YaHei UI', 10))
        self.preview_text.pack(fill='both', expand=True)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x')
        ttk.Button(action_frame, text='更新預覽', command=self.update_preview).pack(side='left')
        ttk.Button(action_frame, text='執行匯出', command=self.on_export).pack(side='right')
        ttk.Button(action_frame, text='取消', command=self.destroy).pack(side='right', padx=(0, 5))

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
        value = self.select_all_var.get()
        for _, var in self.task_vars:
            var.set(value)
        self.update_preview()

    def filtered_tasks(self):
        selected = []
        for todo, var in self.task_vars:
            if not var.get():
                continue
            if self.category_filter.get() != '所有' and todo.get('category') != self.category_filter.get():
                continue
            if self.status_filter.get() != '所有' and todo.get('status') != self.status_filter.get():
                continue
            if self.priority_filter.get() != '所有' and todo.get('priority') != self.priority_filter.get():
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
        self.geometry("400x250")  # 增加高度以容納說明文字
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # 創建主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill='both', expand=True)

        # 添加說明文字
        ttk.Label(
            main_frame,
            text="請設定 Discord Webhook URL\n\n"
            "1. 在 Discord 中右鍵點擊頻道\n"
            "2. 選擇「編輯頻道」→「整合」→「建立 Webhook」\n"
            "3. 複製 Webhook URL 並貼到下方\n",
            justify='left',
            wraplength=350
        ).pack(anchor='w', pady=(0, 10))

        # Discord Webhook URL 輸入
        ttk.Label(main_frame, text="Discord Webhook URL：").pack(anchor='w', pady=(0, 5))
        self.webhook_entry = ttk.Entry(main_frame, width=50)
        self.webhook_entry.pack(fill='x', pady=(0, 15))
        self.webhook_entry.insert(0, DISCORD_WEBHOOK_URL)

        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(15, 0))

        ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy
        ).pack(side='right', padx=(5, 0))

        ttk.Button(
            button_frame,
            text="保存",
            command=self.save_settings
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
        self.root.title("待辦事項")
        self.root.geometry("500x700")
        self.root.resizable(True, True)
        
        # 設定應用程式圖示
        try:
            self.root.iconbitmap('icon.ico')
        except:
            print("無法載入圖示檔案，使用預設圖示")
        
        # 設定顏色主題
        self.colors = {
            'background_start': GradientFrame.COLOR_SCHEMES["theme1"]["start"],
            'background_end': GradientFrame.COLOR_SCHEMES["theme1"]["end"],
            'text': GradientFrame.COLOR_SCHEMES["theme2"]["start"],
            'white': '#ffffff'
        }
        
        # 創建主背景（漸層）
        self.background = GradientFrame(
            self.root,
            theme="theme1",
            highlightthickness=0
        )
        self.background.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 創建標題
        self.title_text = self.background.create_text(
            0,  # 將在 on_resize 中更新
            0,  # 將在 on_resize 中更新
            text="✨ 待辦事項",
            font=('Microsoft YaHei UI', 24, 'bold'),
            fill=self.colors['text'],
            anchor='center'
        )
        
        # 創建輸入框容器
        self.input_frame = ttk.Frame(self.background)
        self.input_frame.place(relx=0.1, rely=0.2, relwidth=0.8)
        
        # 創建輸入框
        self.input_entry = ttk.Entry(
            self.input_frame,
            font=('Microsoft YaHei UI', 14)
        )
        self.input_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        # 創建添加按鈕
        self.add_btn = ttk.Button(
            self.input_frame,
            text='➕',
            command=self.open_task_editor
        )
        self.add_btn.pack(side='right', padx=5)

        # 創建匯出按鈕
        self.export_btn = ttk.Button(
            self.input_frame,
            text='匯出',
            command=self.open_export_window
        )
        self.export_btn.pack(side='right', padx=5)
        
        # 載入待辦事項
        self.load_todos()
        self.todo_items = []
        
        # 綁定回車鍵
        self.input_entry.bind('<Return>', lambda e: self.add_todo())
        
        # 渲染待辦事項
        self.render_todos()
        
        # 啟動通知檢查線程
        self.notification_thread = threading.Thread(target=self.check_notifications, daemon=True)
        self.notification_thread.start()
        
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
            
        # 獲取視窗大小
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 更新標題位置（水平居中，距離頂部 15%）
        title_x = width // 2
        title_y = int(height * 0.15)
        self.background.coords(self.title_text, title_x, title_y)
        
        # 更新輸入框位置（距離頂部 25%）
        input_y = int(height * 0.25)
        self.input_frame.place(relx=0.1, rely=input_y/height, relwidth=0.8)
        
        # 重新渲染待辦事項以適應新的大小
        self.render_todos()
    
    def load_todos(self):
        """載入待辦事項"""
        try:
            with open('todos.json', 'r', encoding='utf-8') as f:
                self.todos = json.load(f)
                print("成功載入待辦事項：", self.todos)  # 添加調試信息
        except (FileNotFoundError, json.JSONDecodeError):
            self.todos = []
            print("創建新的待辦事項列表")  # 添加調試信息
    
    def save_todos(self):
        """保存待辦事項"""
        try:
            with open('todos.json', 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
            print("成功保存待辦事項：", self.todos)  # 添加調試信息
        except Exception as e:
            print(f"保存待辦事項時發生錯誤：{e}")  # 添加調試信息
    
    def check_notifications(self):
        """檢查並發送通知"""
        print("開始檢查通知...")
        while True:
            current_time = datetime.now()
            print(f"\n當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            for todo in self.todos:
                if not todo['completed'] and todo.get('notification'):
                    try:
                        # 解析通知數據
                        notification_data = json.loads(todo['notification'])
                        notification_time = datetime.fromisoformat(notification_data['time'])
                        template = notification_data.get('template', "🔔 待辦事項提醒\n📝 {content}")
                        notification_type = notification_data.get('type', 'discord')  # 預設為 discord
                        creator = notification_data.get('creator', '用戶')  # 獲取設定人
                        
                        # 添加日誌
                        time_diff = (notification_time - current_time).total_seconds()
                        print(f"\n待辦事項: {todo['text']}")
                        print(f"預定通知時間: {notification_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"距離通知還有: {int(time_diff)} 秒")
                        print(f"通知類型: {notification_type}")
                        print(f"設定人: {creator}")
                        
                        if time_diff <= 0:
                            print(f"\n正在發送通知...")
                            
                            # 準備變數數據
                            current_time_str = current_time.strftime("%Y/%m/%d %H:%M")
                            variables = {
                                'content': todo['text'],
                                'time': current_time_str,
                                'creator': creator
                            }
                            
                            # 格式化通知內容
                            message = template.format(**variables)
                            
                            # 根據通知類型發送通知
                            if notification_type == 'discord':
                                # 發送 Discord 通知
                                print("發送 Discord 通知...")
                                try:
                                    # 準備 Discord 消息數據
                                    webhook_data = {"content": message}
                                    
                                    # 如果有圖片 URL，添加到 embeds 中
                                    if 'image_url' in notification_data:
                                        print(f"添加圖片: {notification_data['image_url']}")
                                        webhook_data["embeds"] = [{
                                            "image": {
                                                "url": notification_data['image_url']
                                            }
                                        }]
                                    
                                    # 發送請求
                                    response = requests.post(DISCORD_WEBHOOK_URL, json=webhook_data)
                                    print(f"Discord 響應狀態碼: {response.status_code}")
                                    
                                    if response.status_code == 204:
                                        print("Discord 通知發送成功！")
                                    else:
                                        print(f"Discord 通知發送失敗: {response.status_code}")
                                        print(f"錯誤信息: {response.text}")
                                except Exception as e:
                                    print(f"Discord 通知錯誤: {e}")
                            else:
                                # 發送系統通知
                                print("發送系統通知...")
                                notification.notify(
                                    title='待辦事項提醒',
                                    message=message,
                                    app_icon=None,
                                    timeout=10,
                                )
                            
                            # 移除通知時間
                            todo['notification'] = None
                            self.save_todos()
                            self.render_todos()
                            print("通知發送完成！")
                    except Exception as e:
                        print(f"處理通知時發生錯誤: {e}")
                        continue
            
            time.sleep(10)  # 每10秒檢查一次
    
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
        if not path:
            path = filedialog.asksaveasfilename(
                defaultextension='.json',
                filetypes=[('JSON 檔案', '*.json')],
                title='匯出為 JSON'
            )
        if path:
            try:
                filtered = [ {k: todo.get(k) for k in fields} for todo in todos ]
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(filtered, f, ensure_ascii=False, indent=2)
                messagebox.showinfo('完成', f'已匯出 JSON 到：{path}')
            except Exception as e:
                messagebox.showerror('錯誤', f'匯出 JSON 失敗：{e}')

    def export_to_markdown(self, todos, fields, path=None):
        if not path:
            path = filedialog.asksaveasfilename(
                defaultextension='.md',
                filetypes=[('Markdown 檔案', '*.md')],
                title='匯出為 Markdown'
            )
        if path:
            try:
                lines = ['# 待辦事項清單', '']
                for todo in todos:
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
                        lines.append(f"- 說明：{todo.get('content', '')}")
                    if 'completion_history' in fields and todo.get('completion_history'):
                        lines.append('- 完成紀錄：')
                        for record in todo['completion_history']:
                            lines.append(f"  - {record.get('time')}：{record.get('notes')}")
                    lines.append('')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                messagebox.showinfo('完成', f'已匯出 Markdown 到：{path}')
            except Exception as e:
                messagebox.showerror('錯誤', f'匯出 Markdown 失敗：{e}')
    
    def render_todos(self):
        # 清除現有的待辦事項
        for item in self.todo_items:
            item.destroy()
        self.todo_items.clear()
        
        # 獲取視窗大小
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 計算待辦事項的起始位置（距離頂部 35%）
        start_y = int(height * 0.35)
        item_height = max(40, int(height * 0.06))  # 動態調整項目高度
        
        # 重新渲染所有待辦事項
        for i, todo in enumerate(self.todos):
            y = start_y + i * item_height
            todo_item = TodoItem(
                self.background,  # 直接在背景上繪製
                y,
                todo,
                self.delete_todo,
                self.toggle_todo,
                self.show_notification_settings,
                self.open_edit_task
            )
            self.todo_items.append(todo_item)
    
    def add_todo(self):
        """添加新的待辦事項"""
        text = self.input_entry.get().strip()
        if text:
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
        root.after(100, app.show_config)  # 使用 after 延遲調用，確保主窗口已完全初始化
    
    root.mainloop()

if __name__ == '__main__':
    main() 