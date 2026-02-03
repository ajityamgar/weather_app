import customtkinter as ctk
import requests
import threading
import datetime
import random

API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.unit = "metric"
        self.history = []

        self.configure(fg_color="#0f172a")

        self.create_gradient_background()
        self.create_layout()

    # ================= Animated Gradient =================

    def create_gradient_background(self):
        self.gradient = ctk.CTkFrame(self, fg_color="#1e293b")
        self.gradient.place(relwidth=1, relheight=1)

    def change_theme_color(self, color):
        self.gradient.configure(fg_color=color)

    # ================= Layout =================

    def create_layout(self):

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0,
                                    fg_color="#111827")
        self.sidebar.pack(side="left", fill="y")

        title = ctk.CTkLabel(self.sidebar, text="Weather",
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=(40, 20))

        self.history_frame = ctk.CTkScrollableFrame(
            self.sidebar, width=200, fg_color="#0f172a")
        self.history_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Main Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=40)

        # Search Bar
        top_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        top_frame.pack(pady=10)

        self.city_entry = ctk.CTkEntry(
            top_frame,
            width=350,
            height=45,
            corner_radius=20,
            placeholder_text="Search city..."
        )
        self.city_entry.pack(side="left", padx=10)

        self.search_btn = ctk.CTkButton(
            top_frame,
            text="Search",
            height=45,
            corner_radius=20,
            command=self.get_weather
        )
        self.search_btn.pack(side="left", padx=10)

        self.unit_toggle = ctk.CTkSwitch(
            top_frame,
            text="°C / °F",
            command=self.toggle_unit
        )
        self.unit_toggle.pack(side="left", padx=15)

        # Glass Card
        self.card = ctk.CTkFrame(
            self.container,
            corner_radius=30,
            fg_color="#1e293b"
        )
        self.card.pack(pady=40, ipadx=40, ipady=40)

        # Weather Info
        self.emoji_label = ctk.CTkLabel(
            self.card,
            text="🌤️",
            font=ctk.CTkFont(size=100)
        )
        self.emoji_label.pack(pady=(10, 0))

        self.temp_label = ctk.CTkLabel(
            self.card,
            text="--°",
            font=ctk.CTkFont(size=72, weight="bold")
        )
        self.temp_label.pack()

        self.desc_label = ctk.CTkLabel(
            self.card,
            text="Weather info",
            font=ctk.CTkFont(size=22)
        )
        self.desc_label.pack(pady=5)

        self.location_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(size=16)
        )
        self.location_label.pack()

        self.time_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.time_label.pack(pady=(5, 25))

        # Stats Section
        self.stats_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.stats_frame.pack()

        self.humidity_label = self.create_stat("Humidity")
        self.wind_label = self.create_stat("Wind")
        self.pressure_label = self.create_stat("Pressure")
        self.cloud_label = self.create_stat("Clouds")

    def create_stat(self, title):
        frame = ctk.CTkFrame(
            self.stats_frame,
            width=120,
            height=90,
            corner_radius=20,
            fg_color="#0f172a"
        )
        frame.pack(side="left", padx=15)

        ctk.CTkLabel(frame, text=title).pack(pady=(15, 5))
        value = ctk.CTkLabel(frame, text="--",
                             font=ctk.CTkFont(weight="bold"))
        value.pack()

        return value

    # ================= API =================

    def toggle_unit(self):
        self.unit = "imperial" if self.unit == "metric" else "metric"
        if self.city_entry.get():
            self.get_weather()

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            return

        threading.Thread(
            target=self.fetch_weather,
            args=(city,),
            daemon=True
        ).start()

    def fetch_weather(self, city):
        params = {
            "q": city,
            "appid": API_KEY,
            "units": self.unit
        }

        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if response.status_code != 200:
                raise Exception(data.get("message"))

            self.after(0, lambda: self.update_ui(data))

        except Exception as e:
            print("Error:", e)

    # ================= Update UI =================

    def update_ui(self, data):

        condition = data["weather"][0]["main"]
        desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        pressure = data["main"]["pressure"]
        clouds = data["clouds"]["all"]

        city = data["name"]
        country = data["sys"]["country"]

        timezone_offset = data.get("timezone", 0)
        utc_now = datetime.datetime.utcnow()
        local_time = utc_now + datetime.timedelta(seconds=timezone_offset)
        time_str = local_time.strftime("%A | %d %b | %H:%M")

        emoji_map = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Drizzle": "🌦️",
            "Mist": "🌫️"
        }

        color_map = {
            "Clear": "#f59e0b",
            "Clouds": "#64748b",
            "Rain": "#2563eb",
            "Snow": "#94a3b8",
            "Thunderstorm": "#4c1d95"
        }

        emoji = emoji_map.get(condition, "🌤️")
        accent = color_map.get(condition, "#1e293b")

        unit_symbol = "°C" if self.unit == "metric" else "°F"

        self.change_theme_color(accent)

        self.emoji_label.configure(text=emoji)
        self.temp_label.configure(text=f"{temp:.1f}{unit_symbol}")
        self.desc_label.configure(text=desc)
        self.location_label.configure(text=f"{city}, {country}")
        self.time_label.configure(text=time_str)

        self.humidity_label.configure(text=f"{humidity}%")
        self.wind_label.configure(text=f"{wind}")
        self.pressure_label.configure(text=f"{pressure}")
        self.cloud_label.configure(text=f"{clouds}%")


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
