from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dotenv import load_dotenv
import os

from google import genai
from google.genai.errors import ClientError
import time

# -----------------------------
# Настройка приложения
# -----------------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# -----------------------------
# Gemini API
# -----------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# -----------------------------
# Модель запроса
# -----------------------------

class AskRequest(BaseModel):
    passport_received: bool
    message: str

# -----------------------------
# Главная страница
# -----------------------------

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# -----------------------------
# Запрос к ИИ
# -----------------------------

@app.post("/ask")
def ask(data: AskRequest):
    response = None
    for _ in range(3):
        try:
            passport_status = (
                "Паспорт получен"
                if data.passport_received
                else "Паспорт НЕ получен"
            )

            prompt = f"""
Ты помощник сервиса бронирования.

Статус паспорта:
    {passport_status}

Сообщение гостя:
    {data.message}

Отвечай кратко и вежливо.

Если паспорт НЕ получен и пользователь спрашивает,
как заселиться, объясни, что сначала необходимо предоставить паспорт.

Обязательно добавь ссылку:

https://example.com/passport

Если паспорт получен и пользователь спрашивает,
что делать дальше,
скажи, что паспорт принят и следующим шагом необходимо оплатить депозит.
"""

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            return {
                "answer": response.text
            }

        except ClientError as e:
            return {
            "answer": f"Ошибка Gemini API: {e}"
        }

        except Exception as e:
            return {
                "answer": f"Неизвестная ошибка: {e}"
        }