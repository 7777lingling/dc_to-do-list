import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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

# 加載配置
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加載配置文件時發生錯誤: {e}")
    return {"discord_webhook_url": "YOUR_WEBHOOK_URL_HERE"}

# 保存配置
def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存配置文件時發生錯誤: {e}")

# 獲取配置
config = load_config()
DISCORD_WEBHOOK_URL = config.get('discord_webhook_url', "YOUR_WEBHOOK_URL_HERE")

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
    def __init__(self, parent, todo_id, current_notification=None, app=None):
        super().__init__(parent)
        self.title("設定通知")
        self.todo_id = todo_id
        self.app = app
        
        # 設定視窗大小和位置
        self.geometry("400x550")  # 增加一點高度來容納新的輸入欄位
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
                'type': 'discord',  # 添加通知類型
                'creator': creator  # 添加設定人
            }
            
            # 如果有設定圖片 URL，則添加到通知數據中
            if image_url:
                notification_data['image_url'] = image_url
            
            # 更新待辦事項的通知設定
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
        self.edit_callback = edit_callback  # 添加編輯回調
        
        # 創建複選框狀態
        self.completed = todo['completed']
        
        # 在Canvas上創建複選框
        self.checkbox_text = '☑' if self.completed else '☐'
        self.checkbox_id = canvas.create_text(
            50,  # x座標
            y,   # y座標
            text=self.checkbox_text,
            font=('Microsoft YaHei UI', 16),
            fill='#00c6fb',  # 使用主題2的顏色
            anchor='w'
        )
        
        # 在Canvas上創建文字
        self.text_id = canvas.create_text(
            90,  # x座標
            y,   # y座標
            text=todo['text'],
            font=('Microsoft YaHei UI', 12),
            fill='#00c6fb',  # 使用主題2的顏色
            anchor='w'
        )
        
        # 在Canvas上創建通知圖標
        notification_icon = '🔔' if todo.get('notification') else '🔕'
        self.notification_id = canvas.create_text(
            canvas.winfo_reqwidth() - 60,  # x座標
            y,   # y座標
            text=notification_icon,
            font=('Microsoft YaHei UI', 12),
            fill='#7289DA',  # Discord 品牌色
            anchor='e'
        )
        
        # 在Canvas上創建刪除按鈕文字
        self.delete_btn_id = canvas.create_text(
            canvas.winfo_reqwidth() - 30,  # x座標
            y,   # y座標
            text='❌',
            font=('Microsoft YaHei UI', 10),
            fill='#ff8177',  # 使用主題1的顏色
            anchor='e'
        )
        
        # 綁定點擊事件
        canvas.tag_bind(self.checkbox_id, '<Button-1>', self.on_toggle)
        canvas.tag_bind(self.notification_id, '<Button-1>', self.on_notification)
        canvas.tag_bind(self.delete_btn_id, '<Button-1>', self.on_delete)
        canvas.tag_bind(self.text_id, '<Double-Button-1>', self.on_edit)
        
        # 編輯模式變數
        self.edit_window = None
    
    def on_edit(self, event):
        # 如果已經在編輯中，不要重複開啟編輯窗口
        if self.edit_window is not None:
            return
            
        # 創建編輯窗口
        self.edit_window = tk.Toplevel(self.canvas)
        self.edit_window.title("編輯待辦事項")
        self.edit_window.geometry("300x150")
        self.edit_window.resizable(False, False)
        
        # 設置窗口樣式
        self.edit_window.configure(bg='#2C2F33')  # Discord 深色主題
        
        # 創建框架
        frame = ttk.Frame(self.edit_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        # 創建輸入框
        ttk.Label(frame, text="待辦事項內容：").pack(anchor='w', pady=(0, 5))
        entry = ttk.Entry(frame, font=('Microsoft YaHei UI', 12))
        entry.pack(fill='x', pady=(0, 20))
        entry.insert(0, self.todo['text'])
        entry.select_range(0, 'end')
        entry.focus()
        
        # 創建按鈕
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(
            btn_frame,
            text="取消",
            command=self.edit_window.destroy
        ).pack(side='right', padx=(5, 0))
        
        ttk.Button(
            btn_frame,
            text="確定",
            command=lambda: self.save_edit(entry.get())
        ).pack(side='right')
        
        # 綁定回車鍵
        entry.bind('<Return>', lambda e: self.save_edit(entry.get()))
        
        # 綁定窗口關閉事件
        self.edit_window.protocol("WM_DELETE_WINDOW", self.edit_window.destroy)
        
        # 使窗口居中
        self.center_edit_window()
    
    def save_edit(self, new_text):
        if new_text.strip():  # 確保不是空白文字
            old_text = self.todo['text']
            new_text = new_text.strip()
            print(f"正在保存更改：'{old_text}' -> '{new_text}'")  # 添加調試信息
            
            # 使用編輯回調保存更改
            self.edit_callback(self.todo['id'], new_text)
            print("保存完成")  # 添加調試信息
        
        if self.edit_window:
            self.edit_window.destroy()
            self.edit_window = None
    
    def center_edit_window(self):
        self.edit_window.update_idletasks()
        width = self.edit_window.winfo_width()
        height = self.edit_window.winfo_height()
        x = (self.edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.edit_window.winfo_screenheight() // 2) - (height // 2)
        self.edit_window.geometry(f'{width}x{height}+{x}+{y}')
    
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

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.title("設定")
        self.callback = callback
        
        # 設定視窗大小和位置
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # 創建主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill='both', expand=True)
        
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
        config['discord_webhook_url'] = webhook_url
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
            250,
            70,
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
            command=self.add_todo
        )
        self.add_btn.pack(side='right', padx=5)
        
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
    
    def render_todos(self):
        # 清除現有的待辦事項
        for item in self.todo_items:
            item.destroy()
        self.todo_items.clear()
        
        # 重新渲染所有待辦事項
        for i, todo in enumerate(self.todos):
            y = 250 + i * 40  # 從y=250開始，每個項目間隔40像素
            todo_item = TodoItem(
                self.background,  # 直接在背景上繪製
                y,
                todo,
                self.delete_todo,
                self.toggle_todo,
                self.show_notification_settings,
                self.edit_todo  # 添加編輯回調
            )
            self.todo_items.append(todo_item)
    
    def add_todo(self):
        """添加新的待辦事項"""
        text = self.input_entry.get().strip()
        if text:
            new_todo = {
                'id': str(uuid.uuid4()),
                'text': text,
                'completed': False,
                'notification': None
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
    
    def edit_todo(self, todo_id, new_text):
        """編輯待辦事項"""
        print(f"正在編輯待辦事項 {todo_id}: {new_text}")  # 添加調試信息
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['text'] = new_text
                break
        self.save_todos()
        self.render_todos()
    
    def show_config(self):
        ConfigWindow(self.root)

def main():
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 