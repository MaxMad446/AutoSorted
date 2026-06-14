import os
import threading
import time
import subprocess
from tkinter import Tk, filedialog, messagebox
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from sorter_engine import FileSorter # Импортируем наш созданный класс
from settings_gui import SettingsWindow

# Расширенный список расширений
EXTENSIONS = {
    'Images': [
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico', '.tiff', '.tif', 
        '.raw', '.heic', '.eps', '.ai', '.psd', '.psb', '.indd'
    ],
    'Documents': [
        '.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.csv', '.pptx', '.ppt', '.rtf', 
        '.odt', '.ods', '.odp', '.pages', '.numbers', '.key', '.epub', '.fb2', '.djvu'
    ],
    'Archives': [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg', '.pkg', '.deb', '.rpm'
    ],
    'Video': [
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.3gp', '.flv', '.webm', '.vob', '.m4v', '.mts'
    ],
    'Audio': [
        '.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma', '.mid', '.midi', '.aiff'
    ],
    'Code_and_Data': [
        '.py', '.js', '.html', '.css', '.json', '.xml', '.cpp', '.c', '.cs', '.java', 
        '.php', '.sh', '.sql', '.yaml', '.yml', '.md', '.ipynb'
    ],
    'Executables': [
        '.exe', '.msi', '.apk', '.bat', '.cmd', '.com', '.jar', '.vbs', '.ps1'
    ],
    'Fonts': [
        '.ttf', '.otf', '.woff', '.woff2', '.fnt'
    ],
    '3D_and_Design': [
        '.obj', '.stl', '.fbx', '.3ds', '.max', '.blend', '.c4d', '.sketch', '.fig'
    ],
    'System_and_Logs': [
        '.log', '.ini', '.cfg', '.tmp', '.bak', '.dmp', '.sys', '.dll'
    ]
}


# --- ГЛОБАЛЬНОЕ УПРАВЛЕНИЕ ---
state = {
    'running': True,
    'watch_paths': [],
    'use_dates': False,
    'reopen_settings': False,
    'icon': None
}

state = {
    'running': True,        # Флаг жизни всей программы
    'folder_data': [],     # Список словарей: [{'path': '...', 'use_dates': True}, ...]
    'active_session': True  # Управляет паузой мониторинга при открытии настроек
}

def open_folder(path):
    """Открыть папку в проводнике Windows"""
    try:
        os.startfile(os.path.normpath(path))
    except Exception:
        pass

def create_icon_image():
    """Создать иконку для трея"""
    image = Image.new('RGB', (64, 64), (30, 144, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill="white")
    return image

def monitor_thread_func(sorter):
    """Фоновый поток: обрабатывает папки согласно их индивидуальным настройкам"""
    while state['running']:
        if state['folder_data'] and state['active_session']:
            # Движок обрабатывает каждую папку с её флагом use_dates
            sorter.process_folders(state['folder_data'])
        time.sleep(10)

def setup_tray(icon_obj):
    """Динамическое формирование меню трея"""
    
    def on_open_folder(icon, item):
        label = str(item)
        for folder in state['folder_data']:
            path = folder['path']
            if os.path.basename(path) in label or path == label:
                open_folder(path)
                break

    def on_settings(icon, item):
        state['active_session'] = False
        icon.stop() # Выход из icon.run() для возврата в цикл main

    def on_exit(icon, item):
        state['running'] = False
        icon.stop()

    def no_op(icon, item):
        pass

    # Сборка пунктов меню
    menu_items = [MenuItem("Папки в мониторинге:", no_op, enabled=False)]
    
    for folder in state['folder_data']:
        path = folder['path']
        mode_text = " (даты: ВКЛ)" if folder['use_dates'] else " (даты: ВЫКЛ)"
        label = f"Открыть: {os.path.basename(path) or path}{mode_text}"
        menu_items.append(MenuItem(label, on_open_folder))
    
    menu_items.append(Menu.SEPARATOR)
    menu_items.append(MenuItem("Настройки", on_settings))
    menu_items.append(MenuItem("Выход", on_exit))
    
    return Menu(*menu_items)

def main():
    sorter = FileSorter(EXTENSIONS)
    
    # Запуск единого фонового потока мониторинга
    threading.Thread(target=monitor_thread_func, args=(sorter,), daemon=True).start()

    while state['running']:
        # 1. Вызов графического окна настроек
        settings_ui = SettingsWindow()
        # Получаем обновленные данные (индивидуальные настройки для каждой папки)
        new_data, mode = settings_ui.get_settings(current_data=state['folder_data'])

        if mode == 'sort':
            state['folder_data'] = new_data
            state['active_session'] = True
            
            # 2. Создание и запуск иконки в трее
            icon = Icon("AutoSorter", create_icon_image(), "AutoSorter", menu=None)
            icon.menu = setup_tray(icon)
            icon.run()
            
        elif mode == 'undo':
            # Выполняем откат для текущего набора папок
            sorter.undo_sorting(new_data)
            state['active_session'] = False # Возврат в меню после завершения
            
        else:
            # Если окно закрыто на крестик без выбора действия
            if not state['folder_data']:
                state['running'] = False
            else:
                state['active_session'] = True
                icon = Icon("AutoSorter", create_icon_image(), "AutoSorter", menu=None)
                icon.menu = setup_tray(icon)
                icon.run()

if __name__ == "__main__":
    main()