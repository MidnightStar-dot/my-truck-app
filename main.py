from kivymd.app import MDApp
from kivy.lang import Builder
from datetime import datetime
import openpyxl
import os
from kivy.utils import platform

KV = '''
MDScreen:
    MDScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(10)
            size_hint_y: None
            height: self.minimum_height

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
                id: trailer
                hint_text: "Trailer #"
                mode: "fill"

            MDTextField:
                id: destination
                hint_text: "Destination"
                mode: "fill"

            MDTextField:
                id: loaded_miles
                hint_text: "Loaded Miles"
                mode: "fill"
                input_filter: "int"

            MDTextField:
                id: empty_miles
                hint_text: "Empty Miles"
                mode: "fill"
                input_filter: "int"

            MDTextField:
                id: adp
                hint_text: "Additional Pay (ADP) $"
                mode: "fill"
                input_filter: "float"

            MDRaisedButton:
                text: "SAVE TO LOG"
                md_bg_color: 1, 0.7, 0, 1
                text_color: 0, 0, 0, 1
                size_hint_x: 1
                on_release: app.save_to_excel()
'''

class TruckLogApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Builder.load_string(KV)

    def get_excel_path(self):
        file_name = 'mileage.xlsx'
        if platform == 'android':
            from android.storage import primary_external_storage_path
            path = os.path.join(primary_external_storage_path(), 'Documents')
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path, file_name)
        return file_name

    def save_to_excel(self):
        target_path = self.get_excel_path()
        
        try:
            if not os.path.exists(target_path):
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Sheet1"
                ws.append(["Data", "Pre plan #", "Trailer #", "Destination", "Loaded", "Empty", "ADP", "BW M", "BW $"])
                wb.save(target_path)

            wb = openpyxl.load_workbook(target_path)
            ws = wb["Sheet1"] if "Sheet1" in wb.sheetnames else wb.active
            next_row = ws.max_row + 1

            l_miles = float(self.root.ids.loaded_miles.text or 0)
            e_miles = float(self.root.ids.empty_miles.text or 0)
            adp_val = float(self.root.ids.adp.text or 0)
            
            now = datetime.now()
            # Формат 3-19-26
            date_str = f"{now.month}-{now.day}-{str(now.year)[2:]}"

            ws.cell(row=next_row, column=1).value = date_str
            ws.cell(row=next_row, column=2).value = self.root.ids.preplan.text
            ws.cell(row=next_row, column=3).value = self.root.ids.trailer.text
            ws.cell(row=next_row, column=4).value = self.root.ids.destination.text
            ws.cell(row=next_row, column=5).value = l_miles
            ws.cell(row=next_row, column=6).value = e_miles
            ws.cell(row=next_row, column=7).value = adp_val
            ws.cell(row=next_row, column=8).value = l_miles + e_miles
            ws.cell(row=next_row, column=9).value = adp_val

            wb.active = wb.sheetnames.index(ws.title)
            wb.save(target_path)
            
            for field in ['preplan', 'trailer', 'destination', 'loaded_miles', 'empty_miles', 'adp']:
                self.root.ids[field].text = ""
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    TruckLogApp().run()
