import os
import time
import requests
import discord
from discord.ext import tasks, commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

guild_intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=guild_intents)

TWITCH_TOKEN = None
TWITCH_USER_ID = None
STREAM_LIVE = False

def get_app_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    return response.json().get('access_token')

def get_user_id(token):
    url = f'https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers).json()
    return response['data'][0]['id'] if response['data'] else None

def check_stream_status(token, user_id):
    url = f'https://api.twitch.tv/helix/streams?user_id={user_id}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers).json()
    return bool(response['data'])

@bot.event
async def on_ready():
    global TWITCH_TOKEN, TWITCH_USER_ID
    print(f'Logged in as {bot.user}')
    TWITCH_TOKEN = get_app_access_token()
    TWITCH_USER_ID = get_user_id(TWITCH_TOKEN)
    check_stream.start()

@tasks.loop(minutes=1)
async def check_stream():
    global STREAM_LIVE
    is_live = check_stream_status(TWITCH_TOKEN, TWITCH_USER_ID)
    channel = bot.get_channel(CHANNEL_ID)

    if is_live and not STREAM_LIVE:
        STREAM_LIVE = True
        await channel.send(f'🚨 Стрим начался! Заходи смотреть: https://twitch.tv/{TWITCH_USERNAME}')
    elif not is_live and STREAM_LIVE:
        STREAM_LIVE = False

bot.run(TOKEN)