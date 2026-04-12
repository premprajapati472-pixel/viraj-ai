import requests
import base64
from io import BytesIO
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage

class VirajApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.history = Label(text="Viraj AI: Symbol likhein (e.g. SBIN.NS)", size_hint_y=None, halign='left', valign='top')
        self.history.bind(size=lambda s, w: s.setter('text_size')(s, (w[0], None)))
        self.scroll = ScrollView(size_hint=(1, 0.4))
        self.scroll.add_widget(self.history)
        self.layout.add_widget(self.scroll)
        self.chart_img = Image(size_hint=(1, 0.4))
        self.layout.add_widget(self.chart_img)
        self.input = TextInput(hint_text="Stock Symbol...", multiline=False, size_hint_y=None, height=50)
        self.layout.add_widget(self.input)
        self.btn = Button(text="Puchhein", size_hint_y=None, height=50)
        self.btn.bind(on_press=self.send_request)
        self.layout.add_widget(self.btn)
        return self.layout

    def send_request(self, instance):
        sym = self.input.text.strip().upper()
        if sym:
            self.history.text += f"\n\nAap: {sym}\nViraj: Thinking..."
            try:
                # Yahan URL bilkul sahi hai
                url = "https://viraj-ai.onrender.com/ask"
                r = requests.post(url, json={"message": sym}, timeout=60)
                data = r.json()
                self.history.text += f"\nViraj: {data['reply']}"
                if data.get('chart'):
                    img_data = base64.b64decode(data['chart'])
                    buf = BytesIO(img_data)
                    ci = CoreImage(buf, ext="png")
                    self.chart_img.texture = ci.texture
            except Exception as e:
                self.history.text += f"\nError: Server busy hai, 1 minute baad try karein."

if __name__ == "__main__":
    VirajApp().run()