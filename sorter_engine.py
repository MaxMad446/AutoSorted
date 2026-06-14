import os
import shutil
import time
from datetime import datetime

class FileSorter:
    def __init__(self, extensions_map):
        """
        Инициализация движка.
        extensions_map: словарь категорий и расширений из основного файла.
        """
        self.extensions = extensions_map

    def process_folders(self, folder_data):
        """
        Обработка списка папок с индивидуальными настройками.
        folder_data: список вида [{'path': '...', 'use_dates': True}, ...]
        """
        for item in folder_data:
            path = item.get('path')
            use_dates = item.get('use_dates', False)
            
            if not path or not os.path.exists(path):
                continue

            try:
                # Получаем список всех объектов в папке
                items = os.listdir(path)
            except PermissionError:
                continue

            for file_name in items:
                full_item_path = os.path.join(path, file_name)
                
                # Сортируем ТОЛЬКО файлы (игнорируем уже созданные папки категорий)
                if os.path.isfile(full_item_path):
                    self._move_file(path, file_name, use_dates)

    def _get_project_category(self, filename, projects_config):
        """
        Проверяет, подходит ли файл под правила проектов.
        projects_config: словарь {'ProjectName': ['keyword1', 'keyword2']}
        """
        filename_lower = filename.lower()
        for project_name, keywords in projects_config.items():
            for kw in keywords:
                if kw.lower() in filename_lower:
                    return project_name
        return None                

    def _move_file(self, base_path, filename, use_dates):
        """Внутренняя логика перемещения одного файла"""
        filepath = os.path.join(base_path, filename)
        name_only, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # 1. Определяем категорию по расширению
        category = 'Other'
        for cat, exts in self.extensions.items():
            if ext in exts:
                category = cat
                break
        
        # 2. Формируем путь назначения в зависимости от настроек папки
        if use_dates:
            # Индивидуальная настройка: Категория / Дата / Файл
            mtime = os.path.getmtime(filepath)
            date_folder = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            target_dir = os.path.join(base_path, category, date_folder)
        else:
            # Индивидуальная настройка: Категория / Файл
            target_dir = os.path.join(base_path, category)
            
        # Создаем папки, если их нет
        try:
            os.makedirs(target_dir, exist_ok=True)
            
            # 3. Защита от перезаписи (если файл с таким именем уже существует)
            dest_path = os.path.join(target_dir, filename)
            if os.path.exists(dest_path):
                timestamp = int(time.time())
                dest_path = os.path.join(target_dir, f"{name_only}_{timestamp}{ext}")
                
            # 4. Перемещение
            shutil.move(filepath, dest_path)
        except Exception as e:
            print(f"Ошибка при обработке {filename} в {base_path}: {e}")

    def undo_sorting(self, folder_data):
        """
        Метод отката: возвращает файлы в корень каждой папки из списка.
        folder_data: список вида [{'path': '...', ...}, ...]
        """
        for item in folder_data:
            path = item.get('path')
            if not path or not os.path.exists(path):
                continue

            abs_path = os.path.abspath(path)
            
            # Обход дерева папок снизу вверх для корректного удаления пустых директорий
            for root, dirs, files in os.walk(abs_path, topdown=False):
                for filename in files:
                    source = os.path.join(root, filename)
                    target = os.path.join(abs_path, filename)
                    
                    # Если файл не в корне — возвращаем
                    if os.path.abspath(source) != os.path.abspath(target):
                        if os.path.exists(target):
                            n, e = os.path.splitext(filename)
                            target = os.path.join(abs_path, f"{n}_back_{int(time.time())}{e}")
                        
                        try:
                            shutil.move(source, target)
                        except:
                            pass

                # Удаляем папки, которые опустели
                for dirname in dirs:
                    dir_to_check = os.path.join(root, dirname)
                    try:
                        if not os.listdir(dir_to_check):
                            os.rmdir(dir_to_check)
                    except:
                        pass
