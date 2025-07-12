import os
import telebot
import requests
from pytube import YouTube

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Send a YouTube or Instagram video link to download.")

@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text

    if "youtube.com" in url or "youtu.be" in url:
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            filename = "yt_video.mp4"
            stream.download(filename=filename)

            with open(filename, "rb") as f:
                bot.send_video(message.chat.id, f)

            os.remove(filename)

        except Exception as e:
            bot.reply_to(message, f"❌ YouTube Error: {str(e)}")

    elif "instagram.com" in url:
        try:
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "instagram-downloader-download-instagram-videos-stories.p.rapidapi.com"
            }
            params = {"url": url}

            response = requests.get("https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index", headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                video_url = data.get("media")

                if video_url:
                    bot.send_video(message.chat.id, video_url)
                else:
                    bot.reply_to(message, "❌ Failed to extract Instagram video.")
            else:
                bot.reply_to(message, f"⚠️ Instagram API Error: {response.status_code}")

        except Exception as e:
            bot.reply_to(message, f"❌ Instagram Error: {str(e)}")

    else:
        bot.reply_to(message, "❗ Please send a valid YouTube or Instagram video link.")

bot.infinity_polling()
