from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from datetime import datetime
import openpyxl
import os

# Оставляем только нужные импорты
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

KV = '''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            text: "TRUCK LOGBOOK"
            halign: "center"
            font_style: "H5"
            bold: True

        MDTextField:
            id: preplan
            hint_text: "Pre Plan #"
            mode: "fill"

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
            text: "SAVE TO EXCEL"
            size_hint_x: 1
            on_release: app.save_to_excel()
'''

class TruckLogApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        
        if platform == 'android':
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.MANAGE_EXTERNAL_STORAGE
            ])
        return Builder.load_string(KV)

    def save_to_excel(self):
        file_name = 'mileage.xlsx'
        
        # Определяем путь
        if platform == 'android':
            path = os.path.join(primary_external_storage_path(), 'Documents')
        else:
            path = os.getcwd()

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            
        target_path = os.path.join(path, file_name)

        try:
            if not os.path.exists(target_path):
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["Date", "PrePlan", "Miles"])
                wb.save(target_path)

            wb = openpyxl.load_workbook(target_path)
            ws = wb.active
            ws.append([
                datetime.now().strftime("%m-%d-%y"),
                self.root.ids.preplan.text,
                self.root.ids.loaded_miles.text
            ])
            wb.save(target_path)
            self.root.ids.status_label.text = f"✅ Saved to {path}"
        except Exception as e:
            self.root.ids.status_label.text = f"❌ Error: {str(e)[:30]}"

if __name__ == '__main__':
    TruckLogApp().run()
