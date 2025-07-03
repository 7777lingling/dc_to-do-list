import PyInstaller.__main__
import os

def build_exe():
    PyInstaller.__main__.run([
        'todo_app.py',
        '--onefile',
        '--windowed',
        '--name=待辦事項清單',
        '--icon=icon.ico',
        '--add-data=todos.json;.',
        '--clean'
    ])

if __name__ == "__main__":
    build_exe() 