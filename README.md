
API KEY = f1ae5ffd216663cf47417adb358df1c7


🌦️ Weather Pro – Advanced Python GUI Weather Application

A modern and interactive Weather Application built using Python + CustomTkinter, providing real-time weather updates with dynamic UI, multilingual support, voice input, animated background, and 5-day forecast visualization.

🚀 Overview

Weather Pro is a feature-rich desktop application that fetches real-time weather data from the OpenWeatherMap API and presents it in a clean, modern GUI with smooth animations and chart-based forecast visualization.

This project demonstrates:

API Integration

Multithreading

GUI Design with CustomTkinter

Data Visualization using Matplotlib

Speech Recognition Integration

Language Translation Support

Local Data Persistence (History)

✨ Features

🔍 Real-time weather information using OpenWeatherMap API

🗣️ Voice input for city search (Speech Recognition)

🌐 Multilingual support (English, Hindi, Marathi)

🌈 Animated dynamic background

📊 5-day forecast with interactive temperature graph

🌡 Temperature display (°C)

💧 Humidity

💨 Wind speed

🧭 Pressure

☁ Cloud coverage

🌅 Sunrise & Sunset time

📝 Search history persistence (JSON-based storage)

🎨 Modern GUI using customtkinter

⚡ Threaded API calls (Non-blocking UI)

🛠 Tech Stack

Python 3.x

customtkinter – Modern GUI framework

requests – API calls

speech_recognition – Voice input

translate – Weather description translation

matplotlib – Forecast chart visualization

pytz – Timezone handling

threading – Background API calls

json – History storage

📦 Installation
1️⃣ Clone the Repository
git clone https://github.com/ajityamgar/weather_app.git
cd weather_app

2️⃣ Install Dependencies
pip install -r requirements.txt


Or manually install:

pip install customtkinter requests speechrecognition pyaudio matplotlib translate pytz

3️⃣ Add Your OpenWeatherMap API Key

Open main.py and replace:

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"


With your actual API key from:

👉 https://openweathermap.org/api

▶️ Run the Application
python main.py

📁 Project Structure
weather_app/
│
├── main.py
├── weather_history.json
├── requirements.txt
└── README.md

🧠 How It Works

User enters city (or uses voice input).

App fetches current weather + forecast via OpenWeatherMap API.

Background thread prevents UI freezing.

Weather data updates:

Temperature

Stats

Sunrise / Sunset

5-day forecast chart

Search history is stored locally in JSON.

🔐 Security Note

Do NOT publish your API key publicly.

Always keep this line in main.py:

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"


And add real key locally only.