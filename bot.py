import os
import logging
from aiogram import Bot, Dispatcher, executor, types
import requests
import time

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

REPLICATE_MODEL = "aitechtree/nsfw-novel-generation"

headers = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json",
}

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь любое описание, и я сгенерирую изображение.")

@dp.message_handler()
async def generate_image(message: types.Message):
    prompt = message.text
    await message.reply("Генерирую изображение, подожди немного...")

    data = {
        "version": "a1df7b2b0f5c7d434206abfc67440a9d29f8a3cc690325f2c143d5c89b3488e94",
        "input": {
            "prompt": prompt,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }

    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=headers,
        json=data
    )
    if response.status_code != 201:
        await message.reply("Ошибка генерации изображения, попробуй позже.")
        return

    prediction = response.json()
    prediction_id = prediction["id"]

    while True:
        check = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers=headers,
        )
        status = check.json()["status"]
        if status == "succeeded":
            image_url = check.json()["output"][0]
            await message.answer_photo(photo=image_url)
            break
        elif status == "failed":
            await message.reply("Генерация не удалась.")
            break
        time.sleep(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)