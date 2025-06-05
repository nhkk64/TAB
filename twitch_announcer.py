import os
import discord
import requests
import asyncio
from discord.ext import tasks
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

TWITCH_CLIENT_ID = "ecnzsk9jwmowhg514a3homjeaksj79"
TWITCH_CLIENT_SECRET = "kf8k6tzcqvl99e09gmol65g0u6p18y"
TWITCH_USERNAME = "year_96"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

TWITCH_TOKEN = None
TWITCH_USER_ID = None
stream_was_live = False


def get_app_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params).json()
    return response.get("access_token")


def get_user_id(token):
    url = f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers).json()
    return response['data'][0]['id'] if response.get('data') else None


def is_stream_live(token, user_id):
    url = f"https://api.twitch.tv/helix/streams?user_id={user_id}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers).json()
    return bool(response.get('data'))


@client.event
async def on_ready():
    global TWITCH_TOKEN, TWITCH_USER_ID
    print(f"✅ Logged in as {client.user}")
    TWITCH_TOKEN = get_app_access_token()
    TWITCH_USER_ID = get_user_id(TWITCH_TOKEN)
    if TWITCH_USER_ID is None:
        print("❌ Не удалось получить Twitch User ID")
        return
    check_stream.start()


@tasks.loop(seconds=60)
async def check_stream():
    global stream_was_live, TWITCH_TOKEN

    if TWITCH_TOKEN is None:
        TWITCH_TOKEN = get_app_access_token()

    live = is_stream_live(TWITCH_TOKEN, TWITCH_USER_ID)
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if channel is None:
        print("❌ Канал не найден или нет прав на отправку сообщений")
        return

    if live and not stream_was_live:
        await channel.send(f" **year96** is currently streaming! Check it out: https://twitch.tv/{TWITCH_USERNAME}")
        stream_was_live = True
    elif not live and stream_was_live:
        stream_was_live = False


#заглушка для Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"bot is running")

def run_fake_web():
    server = HTTPServer(("0.0.0.0", 10000), SimpleHandler)
    server.serve_forever()

Thread(target=run_fake_web).start()

client.run(DISCORD_TOKEN)
