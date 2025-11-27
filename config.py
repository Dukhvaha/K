import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

# Telegram токен и ID канала
API_TOKEN = os.getenv("API_TOKEN", "8452758380:AAG1vWJcE8-bKPUVAV9hcqKdOxIaCuyvdAM")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1002084549848")

# Kinopoisk токен (опционально)
KINOPOISK_TOKEN = os.getenv("KINOPOISK_TOKEN", "SGFTDVY-RFPM0J2-Q454BH7-EHDSWC0")

# Для обратной совместимости
kinopoisk_token = KINOPOISK_TOKEN
