import customtkinter as ctk
import requests
import threading
import datetime

# ================= CONFIG =================
API_KEY = "f1ae5ffd216663cf47417adb358df1c7"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.unit = "metric"
        self.history = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

    # ================= SIDEBAR =================

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        title = ctk.CTkLabel(
            self.sidebar,
            text="Weather App",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(30, 20))

        history_label = ctk.CTkLabel(
            self.sidebar,
            text="Search History",
            font=ctk.CTkFont(size=16)
        )
        history_label.pack(pady=10)

        self.history_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            width=180,
            height=400
        )
        self.history_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # ================= MAIN AREA =================

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.main_frame.grid_columnconfigure(0, weight=1)

        # Search Section
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, pady=20)

        self.city_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search city..."
        )
        self.city_entry.grid(row=0, column=0, padx=10)

        self.search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.get_weather
        )
        self.search_btn.grid(row=0, column=1, padx=10)

        self.unit_toggle = ctk.CTkSwitch(
            search_frame,
            text="°C / °F",
            command=self.toggle_unit
        )
        self.unit_toggle.grid(row=0, column=2, padx=10)

        # Weather Card
        self.weather_card = ctk.CTkFrame(
            self.main_frame,
            corner_radius=25
        )
        self.weather_card.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")

        self.weather_card.grid_columnconfigure(0, weight=1)

        self.emoji_label = ctk.CTkLabel(
            self.weather_card,
            text="🌤️",
            font=ctk.CTkFont(size=80)
        )
        self.emoji_label.pack(pady=(30, 10))

        self.temp_label = ctk.CTkLabel(
            self.weather_card,
            text="--°",
            font=ctk.CTkFont(size=60, weight="bold")
        )
        self.temp_label.pack()

        self.desc_label = ctk.CTkLabel(
            self.weather_card,
            text="Weather info will appear here",
            font=ctk.CTkFont(size=20)
        )
        self.desc_label.pack(pady=5)

        self.location_label = ctk.CTkLabel(
            self.weather_card,
            text="",
            font=ctk.CTkFont(size=16)
        )
        self.location_label.pack()

        self.time_label = ctk.CTkLabel(
            self.weather_card,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.time_label.pack(pady=(10, 30))

        self.stats_frame = ctk.CTkFrame(
            self.weather_card,
            fg_color="transparent"
        )
        self.stats_frame.pack(pady=20)

        self.humidity_label = self.create_stat("Humidity")
        self.wind_label = self.create_stat("Wind")
        self.pressure_label = self.create_stat("Pressure")
        self.cloud_label = self.create_stat("Clouds")

    def create_stat(self, title):
        frame = ctk.CTkFrame(self.stats_frame)
        frame.pack(side="left", padx=15)

        ctk.CTkLabel(frame, text=title).pack()
        value_label = ctk.CTkLabel(
            frame,
            text="--",
            font=ctk.CTkFont(weight="bold")
        )
        value_label.pack()

        return value_label

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
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200:
                raise Exception(data.get("message", "Error fetching data"))

            self.after(0, lambda: self.update_ui(data))
            self.after(0, lambda: self.add_to_history(city.title()))

        except Exception as e:
            print("Error:", e)

    # ================= UI UPDATE =================

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

        emoji = emoji_map.get(condition, "🌤️")

        unit_symbol = "°C" if self.unit == "metric" else "°F"
        wind_unit = "m/s" if self.unit == "metric" else "mph"

        self.emoji_label.configure(text=emoji)
        self.temp_label.configure(text=f"{temp:.1f}{unit_symbol}")
        self.desc_label.configure(text=desc)
        self.location_label.configure(text=f"{city}, {country}")
        self.time_label.configure(text=time_str)

        self.humidity_label.configure(text=f"{humidity}%")
        self.wind_label.configure(text=f"{wind} {wind_unit}")
        self.pressure_label.configure(text=f"{pressure} hPa")
        self.cloud_label.configure(text=f"{clouds}%")

    # ================= HISTORY =================

    def add_to_history(self, city):
        if city in self.history:
            self.history.remove(city)

        self.history.insert(0, city)

        for widget in self.history_frame.winfo_children():
            widget.destroy()

        for city in self.history[:8]:
            btn = ctk.CTkButton(
                self.history_frame,
                text=city,
                width=160,
                command=lambda c=city: self.search_from_history(c)
            )
            btn.pack(pady=4)

    def search_from_history(self, city):
        self.city_entry.delete(0, "end")
        self.city_entry.insert(0, city)
        self.get_weather()


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
