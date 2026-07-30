import json
import os
from tkinter import filedialog, messagebox


class ExportService:
    @staticmethod
    def export_to_json(todos, fields, path=None):
        if not path:
            path = filedialog.asksaveasfilename(
                defaultextension='.json',
                filetypes=[('JSON 檔案', '*.json')],
                title='匯出為 JSON'
            )
        if path:
            try:
                filtered = [{k: todo.get(k) for k in fields} for todo in todos]
                with open(path, 'w', encoding='utf-8') as handle:
                    json.dump(filtered, handle, ensure_ascii=False, indent=2)
                messagebox.showinfo('完成', f'已匯出 JSON 到：{path}')
            except Exception as exc:
                messagebox.showerror('錯誤', f'匯出 JSON 失敗：{exc}')

    @staticmethod
    def export_to_markdown(todos, fields, path=None):
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
                        lines.append(f"- 說明：{todo.get('content', '')}")
                    if 'completion_history' in fields and todo.get('completion_history'):
                        lines.append('- 完成紀錄：')
                        for record in todo['completion_history']:
                            lines.append(f"  - {record.get('time')}：{record.get('notes')}")
                    lines.append('')
                with open(path, 'w', encoding='utf-8') as handle:
                    handle.write('\n'.join(lines))
                messagebox.showinfo('完成', f'已匯出 Markdown 到：{path}')
            except Exception as exc:
                messagebox.showerror('錯誤', f'匯出 Markdown 失敗：{exc}')
