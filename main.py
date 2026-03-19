from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from datetime import datetime
import os


class TruckLogApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"  # Оранжевый лучше видно на солнце

        screen = MDScreen()
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)

        # Заголовок
        layout.add_widget(MDLabel(
            text="DRIVER LOGBOOK",
            halign="center",
            font_style="H5",
            size_hint_y=None, height=80
        ))

        # Поля ввода
        self.manifest = MDTextField(hint_text="Manifest #", mode="fill")
        self.trailer = MDTextField(hint_text="Trailer #", mode="fill")
        self.destination = MDTextField(hint_text="Destination", mode="fill")
        self.miles = MDTextField(hint_text="Miles Driven", mode="fill", input_filter="int")

        for field in [self.manifest, self.trailer, self.destination, self.miles]:
            layout.add_widget(field)

        # Кнопка сохранения
        save_btn = MDRaisedButton(
            text="SAVE TO LOG",
            pos_hint={"center_x": 0.5},
            size_hint=(0.9, None),
            height=100,
            on_release=self.save_data
        )

        layout.add_widget(save_btn)
        layout.add_widget(MDLabel())  # Отступ

        screen.add_widget(layout)
        return screen

    def save_data(self, *args):
        # Путь к файлу на Android (внутренняя память приложения)
        file_path = "truck_shif_logs.csv"

        log_entry = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')},"
            f"{self.manifest.text},{self.trailer.text},"
            f"{self.destination.text},{self.miles.text}\n"
        )

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

        # Очистка
        for field in [self.manifest, self.trailer, self.destination, self.miles]:
            field.text = ""


if __name__ == "__main__":
    TruckLogApp().run()