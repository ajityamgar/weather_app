import tkinter as tk
from tkinter import ttk, messagebox
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

import requests
import threading
import io
import time
import math
import speech_recognition as sr
from translate import Translator
import datetime
import pytz

API_KEY = "f1ae5ffd216663cf47417adb358df1c7"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"

LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Marathi': 'mr',
}

# Weather condition to (color, emoji) mapping
WEATHER_STYLES = {
    'Clear':    ("#ffe066", "☀️"),
    'Clouds':   ("#d0d3d4", "☁️"),
    'Rain':     ("#5dade2", "🌧️"),
    'Drizzle':  ("#aed6f1", "🌦️"),
    'Thunderstorm': ("#85929e", "⛈️"),
    'Snow':     ("#f4f6f7", "❄️"),
    'Mist':     ("#d5dbdb", "🌫️"),
    'Fog':      ("#d5dbdb", "🌫️"),
    'Haze':     ("#f9e79f", "🌫️"),
    'Smoke':    ("#cacfd2", "🌫️"),
    'Dust':     ("#f5cba7", "🌫️"),
    'Sand':     ("#f5cba7", "🌫️"),
    'Ash':      ("#aeb6bf", "🌋"),
    'Squall':   ("#85929e", "💨"),
    'Tornado':  ("#85929e", "🌪️"),
}

UI_TEXTS = {
    'English': {
        'app_title': 'Weather App',
        'search': 'Search',
        'mic': '🎤',
        'unit': '°C',
        'history': 'History',
        'weather_info': 'Weather info will appear here.',
        'humidity': 'Humidity',
        'wind': 'Wind',
    },
    'Hindi': {
        'app_title': 'मौसम ऐप',
        'search': 'खोजें',
        'mic': '🎤',
        'unit': '°से',
        'history': 'इतिहास',
        'weather_info': 'यहाँ मौसम जानकारी दिखेगी।',
        'humidity': 'नमी',
        'wind': 'हवा',
    },
    'Marathi': {
        'app_title': 'हवामान ॲप',
        'search': 'शोधा',
        'mic': '🎤',
        'unit': '°से',
        'history': 'इतिहास',
        'weather_info': 'येथे हवामान माहिती दिसेल.',
        'humidity': 'आर्द्रता',
        'wind': 'वारा',
    }
}

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Animated Weather App")
        self.root.attributes('-fullscreen', True)
        self.root.update_idletasks()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.resizable(True, True)
        self.unit = 'metric'  # 'metric' for Celsius, 'imperial' for Fahrenheit
        self.current_bg = "#ffe066"
        self.target_bg = "#ffe066"
        self.emoji = "☀️"
        self.emoji_y = 0
        self.emoji_anim_phase = 0
        self.animating = True
        self.history = []
        self.weather_icons = {}
        self.bg_colors = {
            'Clear': '#f7dc6f',
            'Clouds': '#d6dbdf',
            'Rain': '#85c1e9',
            'Drizzle': '#aed6f1',
            'Thunderstorm': '#85929e',
            'Snow': '#f4f6f7',
            'Mist': '#d5dbdb',
            'Fog': '#d5dbdb',
            'Haze': '#f9e79f',
            'Smoke': '#cacfd2',
            'Dust': '#f5cba7',
            'Sand': '#f5cba7',
            'Ash': '#aeb6bf',
            'Squall': '#85929e',
            'Tornado': '#85929e',
        }
        self.weather_labels = []
        self.selected_language = tk.StringVar(value='English')
        self.setup_styles()
        self.create_widgets()
        self.animate_bg()
        self.animate_emoji()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f8f9f9')
        style.configure('TLabel', background='#f8f9f9', font=('Segoe UI', 12))
        style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'))
        style.configure('TButton', font=('Segoe UI', 11), padding=8, relief='flat', borderwidth=0)
        style.configure('TEntry', font=('Segoe UI', 13), relief='flat', borderwidth=0)
        style.configure('History.TButton', font=('Segoe UI', 10, 'bold'), padding=6, relief='flat', borderwidth=0, foreground='#4f4f4f', background='#e3e6f3')
        style.map('TButton', background=[('active', '#a3bffa')])
        style.map('History.TButton', background=[('active', '#b2a4ff')])

    def create_widgets(self):
        # Gradient background using a canvas (full screen)
        self.bg_canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, highlightthickness=0, bd=0)
        self.bg_canvas.pack(fill='both', expand=True)
        self.draw_gradient()
        # Main card centered, responsive
        card_width = min(400, int(self.screen_width * 0.32))
        card_height = min(520, int(self.screen_height * 0.7))
        self.weather_card = tk.Frame(self.bg_canvas, bg='#ffffff', bd=0)
        self.weather_card.place(relx=0.5, rely=0.5, anchor='center', width=card_width, height=card_height)
        self.weather_card.config(highlightbackground='#e0e0e0', highlightthickness=0)
        self.weather_card.pack_propagate(False)
        # Add shadow effect (simulate with extra frame behind)
        self.shadow = tk.Frame(self.bg_canvas, bg='#d1d9e6', bd=0)
        self.shadow.place(relx=0.5, rely=0.5+0.01, anchor='center', width=card_width+12, height=card_height+12)
        self.bg_canvas.tag_lower(self.shadow)
        self.bg_canvas.tag_lower(self.weather_card)
        # Card content
        # Date (top)
        self.date_label = tk.Label(self.weather_card, text="", font=("Segoe UI", 13, "bold"), bg='#ffffff', fg='#888')
        self.date_label.pack(pady=(22, 0))
        # Time (large)
        self.time_label = tk.Label(self.weather_card, text="", font=("Segoe UI", 32, "bold"), bg='#ffffff', fg='#6c63ff')
        self.time_label.pack(pady=(8, 0))
        # City
        self.city_label = tk.Label(self.weather_card, text="", font=("Segoe UI", 15, "bold"), bg='#ffffff', fg='#444')
        self.city_label.pack(pady=(0, 8))
        # Weather icon
        self.emoji_label = tk.Label(self.weather_card, text=self.emoji, font=("Segoe UI", 64), bg='#ffffff')
        self.emoji_label.pack(pady=(0, 0))
        # Temperature (large)
        self.temp_label = tk.Label(self.weather_card, text="--°C", font=("Segoe UI", 38, "bold"), bg='#ffffff', fg='#222')
        self.temp_label.pack(pady=(0, 0))
        # Weather description
        self.cond_label = tk.Label(self.weather_card, text=UI_TEXTS[self.selected_language.get()]['weather_info'], font=("Segoe UI", 15), bg='#ffffff', fg='#666')
        self.cond_label.pack(pady=(0, 0))
        # Day (bottom)
        self.day_label = tk.Label(self.weather_card, text="", font=("Segoe UI", 13), bg='#ffffff', fg='#888')
        self.day_label.pack(pady=(0, 10))
        # Placeholder for forecast (bottom)
        self.forecast_placeholder = tk.Label(self.weather_card, text="(Forecast coming soon)", font=("Segoe UI", 11, "italic"), bg='#ffffff', fg='#cccccc')
        self.forecast_placeholder.pack(side='bottom', pady=(0, 18))
        # IST toggle button (if needed)
        self.ist_btn = None
        self.showing_ist = False
        self.time_info = None
        self.timezone_offset = None
        self.city_country = None
        # Remove main_frame and other widgets, only use weather_card
        self.weather_labels = [self.emoji_label, self.temp_label, self.cond_label, self.time_label, self.date_label, self.day_label]

    def draw_gradient(self):
        # Blue-purple vertical gradient
        self.bg_canvas.delete('gradient')
        for i in range(self.screen_height):
            r = int(108 + (108-108)*i/self.screen_height)
            g = int(99 + (195-99)*i/self.screen_height)
            b = int(255 + (255-255)*i/self.screen_height)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.bg_canvas.create_line(0, i, self.screen_width, i, fill=color, tags='gradient')
        for i in range(self.screen_height):
            r = int(108 + (255-108)*i/self.screen_height)
            g = int(99 + (99-99)*i/self.screen_height)
            b = int(255 + (195-255)*i/self.screen_height)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.bg_canvas.create_line(0, i, self.screen_width, i, fill=color, tags='gradient', stipple='gray50')

    def toggle_unit(self):
        self.unit = 'imperial' if self.unit == 'metric' else 'metric'
        self.unit_btn.config(text=UI_TEXTS[self.selected_language.get()]['unit'])
        if self.city_var.get():
            self.get_weather()

    def get_weather(self, city=None):
        city = city or self.city_var.get().strip()
        if not city:
            messagebox.showinfo("Input Required", "Please enter a city name.")
            return
        self.show_spinner()
        threading.Thread(target=self.fetch_weather, args=(city,), daemon=True).start()

    def fetch_weather(self, city):
        params = {
            'q': city,
            'appid': API_KEY,
            'units': self.unit
        }
        try:
            response = requests.get(BASE_URL, params=params, timeout=8)
            data = response.json()
            if response.status_code != 200:
                raise Exception(data.get('message', 'Error fetching weather.'))
            icon_code = data['weather'][0]['icon']
            icon_img = self.get_icon(icon_code)
            condition = data['weather'][0]['main']
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].capitalize()
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            style = WEATHER_STYLES.get(condition, ("#ffe066", "❓"))
            timezone_offset = data.get('timezone', 0)
            country = data['sys'].get('country', '')
            self.city_country = country
            # Calculate local time
            utc_now = datetime.datetime.utcnow()
            local_time = utc_now + datetime.timedelta(seconds=timezone_offset)
            day = local_time.strftime('%A')
            date = local_time.strftime('%Y-%m-%d')
            time_str = local_time.strftime('%H:%M')
            time_info = {'local': (time_str, date, day), 'offset': timezone_offset}
            self.time_info = time_info
            self.timezone_offset = timezone_offset
            self.root.after(0, lambda: self.update_weather_display(temp, desc, humidity, wind, style, condition, time_info, country))
            self.add_to_history(city)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
        finally:
            self.root.after(0, self.hide_spinner)

    def get_icon(self, icon_code):
        if icon_code in self.weather_icons:
            return self.weather_icons[icon_code]
        if Image is None or ImageTk is None:
            return None
        try:
            url = ICON_URL.format(icon_code)
            resp = requests.get(url, timeout=5)
            img_data = resp.content
            img = Image.open(io.BytesIO(img_data)).resize((70, 70))
            tk_img = ImageTk.PhotoImage(img)
            self.weather_icons[icon_code] = tk_img
            return tk_img
        except Exception:
            return None

    def update_weather_display(self, temp, desc, humidity, wind, style, condition, time_info=None, country=None):
        color, emoji = style
        self.emoji = emoji
        temp_unit = '°C' if self.unit == 'metric' else '°F'
        lang = LANGUAGES.get(self.selected_language.get(), 'en')
        self.last_weather_args = (temp, desc, humidity, wind, style, condition, time_info, country)
        translated_desc = desc
        if lang != 'en':
            try:
                translator = Translator(to_lang=lang)
                translated_desc = translator.translate(desc)
            except Exception as e:
                messagebox.showerror("Translation Error", f"Could not translate: {e}")
        self.temp_label.config(text=f"{temp:.1f}{temp_unit}")
        self.cond_label.config(text=translated_desc)
        self.emoji_label.config(text=self.emoji)
        # Show time info
        if time_info:
            time_str, date, day = time_info['local'] if not self.showing_ist else self.get_ist_time(time_info['offset'])
            self.time_label.config(text=time_str)
            self.date_label.config(text=date)
            self.day_label.config(text=day)
            # City label
            if hasattr(self, 'city_var') and self.city_var.get():
                self.city_label.config(text=self.city_var.get().title())
            # Show/hide IST button
            if country and country != 'IN':
                if not self.ist_btn:
                    self.ist_btn = ttk.Button(self.weather_card, text="Show in IST", command=self.toggle_ist)
                    self.ist_btn.place(relx=0.5, rely=0.97, anchor='s')
                self.ist_btn.config(text="Show in IST" if not self.showing_ist else "Show Local Time")
            else:
                if self.ist_btn:
                    self.ist_btn.destroy()
                    self.ist_btn = None
        else:
            self.time_label.config(text="")
            self.date_label.config(text="")
            self.day_label.config(text="")
            self.city_label.config(text="")
            if self.ist_btn:
                self.ist_btn.destroy()
                self.ist_btn = None

    def show_spinner(self):
        self.spinner.config(text="Loading ⏳")
        self.search_btn.config(state='disabled')
        self.unit_btn.config(state='disabled')

    def hide_spinner(self):
        self.spinner.config(text="")
        self.search_btn.config(state='normal')
        self.unit_btn.config(state='normal')

    def show_error(self, msg):
        messagebox.showerror("Error", msg.capitalize())

    def add_to_history(self, city):
        city = city.title()
        if city in self.history:
            self.history.remove(city)
        self.history.insert(0, city)
        if len(self.history) > 8:
            self.history = self.history[:8]
        self.update_history()

    def update_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        for city in self.history:
            btn = ttk.Button(self.history_frame, text=city, style='History.TButton', command=lambda c=city: self.city_from_history(c))
            btn.pack(side='left', padx=4, pady=4)

    def city_from_history(self, city):
        self.city_var.set(city)
        self.get_weather(city)

    def animate_bg(self):
        # Smoothly transition background color
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb
        cur = hex_to_rgb(self.current_bg)
        tgt = hex_to_rgb(self.target_bg)
        step = tuple(
            c + (t - c) // 10 if abs(t - c) > 2 else t
            for c, t in zip(cur, tgt)
        )
        self.current_bg = rgb_to_hex(step)
        self.update_bg_all()
        self.root.after(40, self.animate_bg)

    def update_bg_all(self):
        # Update backgrounds for all widgets
        self.main_frame.config(bg='#ffffff')
        widgets = [
            self.main_frame, self.header, self.input_frame, self.spinner,
            self.weather_card, self.weather_frame, self.history_label, self.history_frame
        ]
        for w in widgets:
            w.config(bg='#ffffff')
        for lbl in self.weather_labels:
            lbl.config(bg='#f7f8fa' if lbl in [self.emoji_label, self.temp_label, self.cond_label, self.details_label, self.time_label] else '#ffffff')
        self.icon_label.config(bg='#ffffff')
        self.weather_frame.config(bg='#ffffff')
        self.history_frame.config(bg='#ffffff')

    def animate_emoji(self):
        # Only move emoji label up/down, don't change font size
        y_offset = int(10 * math.sin(self.emoji_anim_phase))
        self.emoji_anim_phase += 0.15
        self.emoji_label.place_configure(relx=0.6, y= -20 + y_offset, anchor='n')
        self.root.after(30, self.animate_emoji)

    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.spinner.config(text="Listening... 🎤")
            self.root.update()
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                self.spinner.config(text="Recognizing...")
                self.root.update()
                city = recognizer.recognize_google(audio)
                self.city_var.set(city)
                self.spinner.config(text="")
                self.get_weather()
            except sr.WaitTimeoutError:
                self.spinner.config(text="")
                messagebox.showerror("Error", "Listening timed out. Please try again.")
            except sr.UnknownValueError:
                self.spinner.config(text="")
                messagebox.showerror("Error", "Could not understand audio. Please try again.")
            except sr.RequestError:
                self.spinner.config(text="")
                messagebox.showerror("Error", "Could not request results from Google Speech Recognition service.")
            except Exception as e:
                self.spinner.config(text="")
                messagebox.showerror("Error", f"Voice input failed: {e}")

    def language_changed(self, *args):
        lang = self.selected_language.get()
        self.header.config(text=UI_TEXTS[lang]['app_title'])
        self.search_btn.config(text=UI_TEXTS[lang]['search'])
        self.mic_btn.config(text=UI_TEXTS[lang]['mic'])
        self.unit_btn.config(text=UI_TEXTS[lang]['unit'])
        self.history_label.config(text=UI_TEXTS[lang]['history'])
        # Weather info label update
        if not hasattr(self, 'last_weather_args'):
            self.cond_label.config(text=UI_TEXTS[lang]['weather_info'])
        # Weather info translation already handled
        # ...baaki code...

    def get_ist_time(self, city_offset):
        # city_offset: seconds offset from UTC
        utc_now = datetime.datetime.utcnow()
        ist = pytz.timezone('Asia/Kolkata')
        ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)
        time_str = ist_now.strftime('%H:%M')
        date = ist_now.strftime('%Y-%m-%d')
        day = ist_now.strftime('%A')
        return (time_str, date, day)

    def toggle_ist(self):
        self.showing_ist = not self.showing_ist
        # Redraw time label
        if self.last_weather_args:
            self.update_weather_display(*self.last_weather_args)

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 