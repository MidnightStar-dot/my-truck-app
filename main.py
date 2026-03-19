from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from kivy.metrics import dp
from datetime import datetime
import openpyxl
import os

# Проверка платформы для Android
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

        Widget:
            size_hint_y: 1
'''

class TruckLogApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        return Builder.load_string(KV)

    def save_to_excel(self):
        file_name = 'mileage.xlsx'

        # Надёжный путь (работает везде)
        from kivy.app import App
        path = App.get_running_app().user_data_dir

        target_path = os.path.join(path, file_name)

        try:
            # Проверка ввода
            miles = self.root.ids.loaded_miles.text
            if not miles:
                self.root.ids.status_label.text = "❗ Enter miles"
                return

            # Создаем файл если нет
            if not os.path.exists(target_path):
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["Date", "PrePlan", "Trailer", "Miles"])
                wb.save(target_path)

            # Записываем данные
            wb = openpyxl.load_workbook(target_path)
            ws = wb.active
            ws.append([
                datetime.now().strftime("%m-%d-%y"),
                self.root.ids.preplan.text,
                self.root.ids.trailer.text,
                miles
            ])
            wb.save(target_path)

            self.root.ids.status_label.text = "✅ Saved successfully"

        except Exception as e:
            self.root.ids.status_label.text = f"❌ Error: {str(e)[:40]}"


if __name__ == '__main__':
    TruckLogApp().run()