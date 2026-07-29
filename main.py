from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dotenv import load_dotenv
from openai import OpenAI
import os

# -----------------------------
# Настройка приложения
# -----------------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# -----------------------------
# OpenRouter API
# -----------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

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

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        return {
            "answer": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "answer": f"Ошибка OpenRouter: {str(e)}"
        }