from kivy.app import App
from kivy.uix.button import Button
from kivy.utils import platform
import os

class TruckLogApp(App):
    def build(self):
        # Самая простая кнопка, чтобы проверить запуск
        return Button(
            text="APP IS WORKING!\nCLICK TO TEST PERMISSIONS",
            on_release=self.ask_perm
        )

    def ask_perm(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            instance.text = "Permissions requested!"

if __name__ == '__main__':
    TruckLogApp().run()
