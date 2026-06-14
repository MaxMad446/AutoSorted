import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SettingsWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AutoSorter — Индивидуальные настройки")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # Данные: [{'path': 'C:\\...', 'use_dates': True}, ...]
        self.folder_data = []
        self.mode = None

        self.root.grid_columnconfigure(0, weight=1)

        # 1. Заголовок
        self.title_label = ctk.CTkLabel(self.root, text="НАСТРОЙКА ПАПОК", font=("Roboto", 22, "bold"))
        self.title_label.grid(row=0, column=0, pady=(25, 10))

        # 2. Подзаголовок (шапка списка)
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.grid(row=1, column=0, padx=25, sticky="ew")
        ctk.CTkLabel(self.header_frame, text="Путь к папке", font=("Roboto", 12, "italic")).pack(side="left", padx=5)
        ctk.CTkLabel(self.header_frame, text="Сортировать по датам", font=("Roboto", 12, "italic")).pack(side="left", padx=200)

        # 3. Область со списком
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, width=580, height=250)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        
        # 4. Кнопки управления
        self.btn_path_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.btn_path_frame.grid(row=3, column=0, pady=15)
        
        self.add_btn = ctk.CTkButton(self.btn_path_frame, text="Добавить папку", width=180, command=self.add_path)
        self.add_btn.pack(side="left", padx=10)

        self.clear_btn = ctk.CTkButton(self.btn_path_frame, text="Очистить всё", width=180, 
                                       fg_color="#444444", hover_color="#333333", command=self.clear_paths)
        self.clear_btn.pack(side="left", padx=10)

        # 5. Кнопки запуска
        self.action_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.action_frame.grid(row=4, column=0, pady=(10, 20))

        self.start_btn = ctk.CTkButton(self.action_frame, text="ЗАПУСТИТЬ МОНИТОРИНГ", 
                                       width=400, height=35, font=("Roboto", 13), 
                                       fg_color="#48BE79", hover_color="#269253", command=self.start_sort)
        self.start_btn.pack(pady=10)

        self.undo_btn = ctk.CTkButton(self.action_frame, text="ВЕРНУТЬ ВСЁ (ОТКАТ)", 
                                      width=400, height=35, font=("Roboto", 13), 
                                      fg_color="#E74C3C", hover_color="#C0392B", command=self.start_undo)
        self.undo_btn.pack(pady=5)

    def refresh_list(self):
        """Отрисовывает строки с индивидуальными переключателями"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        for item in self.folder_data:
            row = ctk.CTkFrame(self.scroll_frame, fg_color="#2B2B2B")
            row.pack(fill="x", pady=3, padx=5)
            
            # Текст пути
            path = item['path']
            display_name = (path[:35] + '...') if len(path) > 38 else path
            lbl = ctk.CTkLabel(row, text=display_name, font=("Consolas", 12), width=280, anchor="w")
            lbl.pack(side="left", padx=10, pady=5)
            
            # Переключатель даты для конкретной папки
            # Используем i=item для фиксации текущего объекта в лямбде
            switch = ctk.CTkSwitch(row, text="", width=45)
            if item['use_dates']: 
                switch.select()
            switch.configure(command=lambda i=item, s=switch: i.update({'use_dates': s.get()}))
            switch.pack(side="left", padx=20)
            
            # Кнопка удаления папки
            del_btn = ctk.CTkButton(row, text="Удалить", width=70, height=24, 
                                    fg_color="#3D3D3D", hover_color="#E74C3C",
                                    command=lambda i=item: self.remove_single_path(i))
            del_btn.pack(side="right", padx=10)

    def add_path(self):
        p = filedialog.askdirectory()
        if p:
            p = os.path.normpath(p)
            # Проверка, чтобы не дублировать папки
            if not any(d['path'] == p for d in self.folder_data):
                self.folder_data.append({'path': p, 'use_dates': True})
                self.refresh_list()

    def remove_single_path(self, item_to_remove):
        self.folder_data.remove(item_to_remove)
        self.refresh_list()

    def clear_paths(self):
        if self.folder_data and messagebox.askyesno("Очистка", "Удалить все папки из списка?"):
            self.folder_data = []
            self.refresh_list()

    def start_sort(self):
        if not self.folder_data:
            messagebox.showwarning("Внимание", "Список папок пуст!")
            return
        self.mode = 'sort'
        self.root.quit()

    def start_undo(self):
        if not self.folder_data:
            messagebox.showwarning("Внимание", "Список папок пуст!")
            return
        if messagebox.askyesno("Откат", "Вернуть файлы в корень во всех указанных папках?"):
            self.mode = 'undo'
            self.root.quit()

    def get_settings(self, current_data=None):
        """Запуск окна с текущими данными"""
        if current_data:
            # Создаем копии словарей, чтобы не менять оригинал до нажатия кнопки
            self.folder_data = [d.copy() for d in current_data]
        
        self.refresh_list()
        self.root.mainloop()
        
        res_data, res_mode = self.folder_data.copy(), self.mode
        try:
            self.root.destroy()
        except:
            pass
        return res_data, res_mode
