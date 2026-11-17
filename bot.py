import os
import json
import requests

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
TG_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL = os.environ["CHANNEL_ID"]
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")


def ask_gemini(prompt, as_json=False):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    if as_json:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    r = requests.post(url, headers={"x-goog-api-key": GEMINI_KEY}, json=body, timeout=60)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def send_message(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": CHANNEL, "text": text},
        timeout=30,
    )
    r.raise_for_status()


def send_post():
    prompt = (
        "Sen arab tili o'qituvchisan. O'zbek tilida Telegram kanal uchun qisqa kunlik post yoz. "
        "Boshlovchilar uchun bitta foydali arabcha so'z tanla. Tarkibi: "
        "1) arabcha so'z (harakatlar bilan), 2) o'qilishi (o'zbek harflarida), "
        "3) ma'nosi, 4) ikkita oddiy arabcha gap va ularning tarjimasi. "
        "Post 100 so'zdan oshmasin. Markdown ishlatma."
    )
    send_message(ask_gemini(prompt))


def send_quiz():
    prompt = (
        "Arab tilini o'rganuvchi boshlovchilar uchun bitta test savoli tuz. "
        "Savol o'zbek tilida bo'lsin. 4 ta variant, bittasi to'g'ri. "
        "Faqat JSON qaytar: "
        '{"question": "...", "options": ["...", "...", "...", "..."], '
        '"correct_index": 0, "explanation": "..."}. '
        "Savol 250 belgidan, har bir variant 90 belgidan, izoh 180 belgidan oshmasin."
    )
    data = json.loads(ask_gemini(prompt, as_json=True))
    r = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendPoll",
        json={
            "chat_id": CHANNEL,
            "question": data["question"],
            "options": data["options"],
            "type": "quiz",
            "correct_option_id": data["correct_index"],
            "explanation": data.get("explanation", ""),
            "is_anonymous": True,
        },
        timeout=30,
    )
    r.raise_for_status()


if __name__ == "__main__":
    send_post()
    send_quiz()
