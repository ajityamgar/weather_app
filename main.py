import customtkinter as ctk
import requests
import threading
import datetime
import pytz
import json
import os
import speech_recognition as sr
from translate import Translator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ================= CONFIG =================

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
HISTORY_FILE = "weather_history.json"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr"
}

UI_TEXT = {
    "English": {"search": "Search city...", "forecast": "5-Day Forecast"},
    "Hindi": {"search": "शहर खोजें...", "forecast": "5 दिन का पूर्वानुमान"},
    "Marathi": {"search": "शहर शोधा...", "forecast": "5 दिवसांचा अंदाज"}
}

# ================= Utility =================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(city):
    data = load_history()
    if city in data:
        data.remove(city)
    data.insert(0, city)
    data = data[:8]
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)

# ================= App =================

class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Weather Pro")
        self.geometry("1200x760")
        self.minsize(1000, 650)

        self.unit = "metric"
        self.language = "English"

        self.bg_frame = ctk.CTkFrame(self, fg_color="#0f172a")
        self.bg_frame.place(relwidth=1, relheight=1)

        self.container = ctk.CTkFrame(self, corner_radius=25, fg_color="#111827")
        self.container.pack(padx=50, pady=50, fill="both", expand=True)

        self.create_top_bar()
        self.create_main_card()
        self.create_forecast_section()
        self.update_history_ui()

        self.animate_background()

    # ================= Background Animation =================

    def animate_background(self):
        current = self.bg_frame.cget("fg_color")
        if isinstance(current, tuple):
            current = current[0]
        r = int(current[1:3], 16)
        g = int(current[3:5], 16)
        b = int(current[5:7], 16)
        r = (r + 1) % 255
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.bg_frame.configure(fg_color=color)
        self.after(100, self.animate_background)

    # ================= UI =================

    def create_top_bar(self):
        top = ctk.CTkFrame(self.container, fg_color="transparent")
        top.pack(pady=15)

        self.city_entry = ctk.CTkEntry(
            top, width=300, height=40,
            placeholder_text=UI_TEXT[self.language]["search"]
        )
        self.city_entry.pack(side="left", padx=10)

        ctk.CTkButton(top, text="Search", command=self.get_weather).pack(side="left", padx=5)
        ctk.CTkButton(top, text="🎤", width=40, command=self.voice_input).pack(side="left", padx=5)

        self.lang_menu = ctk.CTkOptionMenu(
            top, values=list(LANGUAGES.keys()),
            command=self.change_language
        )
        self.lang_menu.pack(side="left", padx=10)

    def create_main_card(self):
        self.card = ctk.CTkFrame(self.container, corner_radius=30, fg_color="#1e293b")
        self.card.pack(pady=30, ipadx=40, ipady=40)

        self.city_label = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.city_label.pack()

        self.temp_label = ctk.CTkLabel(self.card, text="--°", font=ctk.CTkFont(size=60, weight="bold"))
        self.temp_label.pack()

        self.desc_label = ctk.CTkLabel(self.card, text="")
        self.desc_label.pack(pady=5)

        self.time_label = ctk.CTkLabel(self.card, text="")
        self.time_label.pack(pady=5)

        self.details_label = ctk.CTkLabel(self.card, text="")
        self.details_label.pack(pady=10)

    def create_forecast_section(self):
        self.forecast_title = ctk.CTkLabel(
            self.container,
            text=UI_TEXT[self.language]["forecast"],
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.forecast_title.pack()

        self.chart_frame = ctk.CTkFrame(self.container)
        self.chart_frame.pack(pady=20, fill="both", expand=True)

    # ================= Language =================

    def change_language(self, choice):
        self.language = choice
        self.city_entry.configure(placeholder_text=UI_TEXT[self.language]["search"])
        self.forecast_title.configure(text=UI_TEXT[self.language]["forecast"])

    # ================= Voice =================

    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5)
                city = recognizer.recognize_google(audio)
                self.city_entry.delete(0, "end")
                self.city_entry.insert(0, city)
                self.get_weather()
            except:
                pass

    # ================= Weather =================

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            return
        threading.Thread(target=self.fetch_weather, args=(city,), daemon=True).start()

    def fetch_weather(self, city):
        params = {"q": city, "appid": API_KEY, "units": self.unit}
        try:
            current = requests.get(CURRENT_URL, params=params).json()
            forecast = requests.get(FORECAST_URL, params=params).json()
            if current.get("cod") != 200:
                return
            self.after(0, lambda: self.update_ui(current, forecast))
            save_history(city)
        except:
            pass

    def update_ui(self, data, forecast):

        city = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        pressure = data["main"]["pressure"]
        clouds = data["clouds"]["all"]

        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"])

        timezone_offset = data.get("timezone", 0)
        utc_now = datetime.datetime.utcnow()
        local_time = utc_now + datetime.timedelta(seconds=timezone_offset)
        time_str = local_time.strftime("%A | %d %b | %H:%M")

        if self.language != "English":
            try:
                translator = Translator(to_lang=LANGUAGES[self.language])
                desc = translator.translate(desc)
            except:
                pass

        self.city_label.configure(text=f"{city}, {country}")
        self.temp_label.configure(text=f"{temp:.1f}°C")
        self.desc_label.configure(text=desc)
        self.time_label.configure(text=time_str)

        self.details_label.configure(
            text=f"Humidity: {humidity}% | Wind: {wind} m/s | "
                 f"Pressure: {pressure} hPa | Clouds: {clouds}%\n"
                 f"Sunrise: {sunrise.strftime('%H:%M')} | Sunset: {sunset.strftime('%H:%M')}"
        )

        self.draw_forecast_chart(forecast)

    # ================= Forecast Chart =================

    def draw_forecast_chart(self, forecast):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        temps = []
        dates = []

        for item in forecast["list"][::8][:5]:
            temps.append(item["main"]["temp"])
            dt = datetime.datetime.fromtimestamp(item["dt"])
            dates.append(dt.strftime("%a"))

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, temps)
        ax.set_title("Temperature Trend")
        ax.set_ylabel("°C")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= History UI =================

    def update_history_ui(self):
        history = load_history()
        for city in history:
            pass  # Simplified (history saved & reusable)

# ================= Run =================

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
