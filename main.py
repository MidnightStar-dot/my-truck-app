from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from datetime import datetime
import openpyxl
import os

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

            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(8)
                size_hint_y: None
                height: dp(56)
                MDTextField:
                    id: preplan
                    hint_text: "Pre Plan #"
                    mode: "fill"
                MDIconButton:
                    icon: "microphone"
                    theme_icon_color: "Custom"
                    icon_color: app.mic_color('preplan')
                    on_release: app.start_voice('preplan')

            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(8)
                size_hint_y: None
                height: dp(56)
                MDTextField:
                    id: trailer
                    hint_text: "Trailer #"
                    mode: "fill"
                MDIconButton:
                    icon: "microphone"
                    theme_icon_color: "Custom"
                    icon_color: app.mic_color('trailer')
                    on_release: app.start_voice('trailer')

            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(8)
                size_hint_y: None
                height: dp(56)
                MDTextField:
                    id: destination
                    hint_text: "Destination"
                    mode: "fill"
                MDIconButton:
                    icon: "microphone"
                    theme_icon_color: "Custom"
                    icon_color: app.mic_color('destination')
                    on_release: app.start_voice('destination')

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

            MDLabel:
                id: status_label
                text: ""
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 0.7, 0, 1

            MDRaisedButton:
                text: "SAVE TO LOG"
                md_bg_color: 1, 0.7, 0, 1
                text_color: 0, 0, 0, 1
                size_hint_x: 1
                on_release: app.confirm_save()
'''


class TruckLogApp(MDApp):
    active_field = None
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Builder.load_string(KV)

    # ── Вибрация ─────────────────────────────────────────────────────────
    def vibrate(self, duration=0.05):
        if platform == 'android':
            try:
                from android.runnable import run_on_ui_thread
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')

                @run_on_ui_thread
                def _vibrate():
                    vibrator = PythonActivity.mActivity.getSystemService(
                        Context.VIBRATOR_SERVICE
                    )
                    if vibrator and vibrator.hasVibrator():
                        vibrator.vibrate(int(duration * 1000))
                _vibrate()
            except Exception:
                pass

    # ── Диалог подтверждения ─────────────────────────────────────────────
    def confirm_save(self):
        ids = self.root.ids

        if not ids.loaded_miles.text and not ids.empty_miles.text:
            self.set_status("⚠️ Enter at least Loaded or Empty miles")
            return

        l_miles = float(ids.loaded_miles.text or 0)
        e_miles = float(ids.empty_miles.text or 0)
        adp_val = ids.adp.text or "0"
        total = l_miles + e_miles

        summary = (
            f"Pre Plan: {ids.preplan.text or '—'}\n"
            f"Trailer:  {ids.trailer.text or '—'}\n"
            f"Dest:     {ids.destination.text or '—'}\n"
            f"Loaded: {l_miles:.0f} mi   Empty: {e_miles:.0f} mi\n"
            f"Total:  {total:.0f} mi   ADP: ${adp_val}"
        )

        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        self.dialog = MDDialog(
            title="Save entry?",
            text=summary,
            auto_dismiss=False,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0.6, 0.6, 0.6, 1),
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    md_bg_color=(1, 0.7, 0, 1),
                    text_color=(0, 0, 0, 1),
                    on_release=lambda x: self.save_to_excel()
                ),
            ]
        )
        self.dialog.open()

    # ── Микрофон — цвет кнопки ───────────────────────────────────────────
    def mic_color(self, field_id):
        if self.active_field == field_id:
            return (1, 0.7, 0, 1)
        return (0.6, 0.6, 0.6, 1)

    def set_status(self, text):
        self.root.ids.status_label.text = text

    # ── Разрешение микрофона ─────────────────────────────────────────────
    def request_mic_permission(self, callback):
        if platform == 'android':
            from android.permissions import request_permissions, Permission, check_permission
            if check_permission(Permission.RECORD_AUDIO):
                callback()
            else:
                def on_result(permissions, grants):
                    if all(grants):
                        callback()
                    else:
                        self.set_status("❌ Microphone permission denied")
                request_permissions([Permission.RECORD_AUDIO], on_result)
        else:
            callback()

    # ── Голосовой ввод ───────────────────────────────────────────────────
    def start_voice(self, field_id):
        self.request_mic_permission(lambda: self._do_voice(field_id))

    def _do_voice(self, field_id):
        if platform == 'android':
            self.active_field = field_id
            self.set_status("🎤 Listening...")
            self._android_speech(field_id)
        else:
            self.set_status("⚠️ Voice input is Android only")

    def _android_speech(self, field_id):
        try:
            from jnius import autoclass, PythonJavaClass, java_method
            from android.runnable import run_on_ui_thread

            Intent = autoclass('android.content.Intent')
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            app_ref = self

            class RecognitionListener(PythonJavaClass):
                __javainterfaces__ = ['android/speech/RecognitionListener']
                __javacontext__ = 'app'

                @java_method('([B)V')
                def onBufferReceived(self, buffer): pass

                @java_method('(I)V')
                def onError(self, error):
                    app_ref.active_field = None
                    errors = {
                        1: "Network error", 2: "Network error",
                        3: "Audio error",   4: "Server error",
                        5: "Client error",  6: "No speech detected",
                        7: "No match found",8: "Service busy",
                        9: "No permission"
                    }
                    app_ref.set_status(f"❌ {errors.get(error, f'Error {error}')}")

                @java_method('(Landroid/os/Bundle;)V')
                def onReadyForSpeech(self, params):
                    app_ref.set_status("🎤 Speak now...")

                @java_method('(Landroid/os/Bundle;)V')
                def onResults(self, results):
                    app_ref.active_field = None
                    matches = results.getStringArrayList(
                        RecognizerIntent.EXTRA_RESULTS
                    )
                    if matches and matches.size() > 0:
                        text = matches.get(0)
                        app_ref.root.ids[field_id].text = text
                        app_ref.set_status(f"✅ Got: {text}")
                        app_ref.vibrate(0.05)
                    else:
                        app_ref.set_status("❌ Nothing recognized")

                @java_method('(Landroid/os/Bundle;)V')
                def onPartialResults(self, results): pass

                @java_method('(ILandroid/os/Bundle;)V')
                def onEvent(self, eventType, params): pass

                @java_method('()V')
                def onBeginningOfSpeech(self): pass

                @java_method('()V')
                def onEndOfSpeech(self):
                    app_ref.set_status("⏳ Processing...")

                @java_method('(FF)V')
                def onRmsChanged(self, rmsdB, unused): pass

            @run_on_ui_thread
            def _start():
                recognizer = SpeechRecognizer.createSpeechRecognizer(
                    PythonActivity.mActivity
                )
                recognizer.setRecognitionListener(RecognitionListener())
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(
                    RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
                )
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
                intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
                recognizer.startListening(intent)

            _start()

        except Exception as e:
            self.active_field = None
            self.set_status(f"❌ Error: {e}")

    # ── Сохранение в Excel ───────────────────────────────────────────────
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
        if self.dialog:
            self.dialog.dismiss()

        target_path = self.get_excel_path()

        try:
            if not os.path.exists(target_path):
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Sheet1"
                ws.append(["Date", "Pre Plan #", "Trailer #", "Destination",
                           "Loaded", "Empty", "ADP", "BW M", "BW $"])
                wb.save(target_path)

            wb = openpyxl.load_workbook(target_path)
            ws = wb["Sheet1"] if "Sheet1" in wb.sheetnames else wb.active

            l_miles = float(self.root.ids.loaded_miles.text or 0)
            e_miles = float(self.root.ids.empty_miles.text or 0)
            adp_val = float(self.root.ids.adp.text or 0)

            now = datetime.now()
            date_str = f"{now.month}-{now.day}-{str(now.year)[2:]}"

            ws.append([
                date_str,
                self.root.ids.preplan.text,
                self.root.ids.trailer.text,
                self.root.ids.destination.text,
                l_miles,
                e_miles,
                adp_val,
                l_miles + e_miles,
                adp_val
            ])

            wb.save(target_path)

            for field in ['preplan', 'trailer', 'destination',
                          'loaded_miles', 'empty_miles', 'adp']:
                self.root.ids[field].text = ""

            self.set_status("✅ Saved!")
            self.vibrate(0.1)

        except Exception as e:
            self.set_status(f"❌ Save error: {e}")


if __name__ == '__main__':
    TruckLogApp().run()
