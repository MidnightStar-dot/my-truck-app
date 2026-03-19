from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from datetime import datetime
import openpyxl
import os

# Проверка платформы для специфических функций Android
if platform == 'android':
    from android.permissions import request_permissions, Permission

KV = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)

        MDLabel:
            text: "TRUCK LOGBOOK"
            halign: "center"
            font_style: "H5"
            bold: True
            size_hint_y: None
            height: dp(50)

        # Поля ввода с иконками микрофона (заглушки для дизайна)
        MDRelativeLayout:
            size_hint_y: None
            height: dp(60)
            MDTextField:
                id: preplan
                hint_text: "Pre Plan #"
                mode: "fill"
            MDIconButton:
                icon: "microphone"
                pos_hint: {"center_y": .5, "right": 1}

        MDRelativeLayout:
            size_hint_y: None
            height: dp(60)
            MDTextField:
                id: trailer
                hint_text: "Trailer #"
                mode: "fill"
            MDIconButton:
                icon: "microphone"
                pos_hint: {"center_y": .5, "right": 1}

        MDTextField:
            id: loaded_miles
            hint_text: "Loaded Miles"
            input_filter: "int"
            mode: "fill"

        MDLabel:
            id: status_label
            text: "Status: Ready"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 0.7, 0, 1

        MDRaisedButton:
            text: "SAVE TO LOG"
            size_hint_x: 1
            height: dp(50)
            md_bg_color: 1, 0.7, 0, 1
            on_release: app.save_to_excel()

        Widget: # Распорка, чтобы поджать всё вверх
'''

class TruckLogApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        
        # Запрос прав при запуске основного приложения
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.RECORD_AUDIO
            ])
            
        return Builder.load_string(KV)

    def save_to_excel(self):
        file_name = 'mileage.xlsx'
        
        # Путь к папке Documents на Android или текущая папка на ПК
        if platform == 'android':
            from android.storage import primary_external_storage_path
            path = os.path.join(primary_external_storage_path(), 'Documents')
        else:
            path = os.getcwd()

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
        target_path = os.path.join(path, file_name)

        try:
            # Создаем файл, если его нет
            if not os.path.exists(target_path):
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["Date", "PrePlan", "Trailer", "Miles"])
                wb.save(target_path)

            # Добавляем данные
            wb = openpyxl.load_workbook(target_path)
            ws = wb.active
            ws.append([
                datetime.now().strftime("%m-%d-%y"),
                self.root.ids.preplan.text,
                self.root.ids.trailer.text,
                self.root.ids.loaded_miles.text
            ])
            wb.save(target_path)
            self.root.ids.status_label.text = f"✅ Saved to Documents"
        except Exception as e:
            self.root.ids.status_label.text = f"❌ Error: {str(e)[:30]}"

if __name__ == '__main__':
    TruckLogApp().run()
