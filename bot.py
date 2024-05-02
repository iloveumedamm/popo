from pyrogram import Client
from config import *
from flask import Flask, jsonify
from threading import Thread
   
app = Flask('')

@app.route('/')
def main():
    
    res = {
        "status":"running",
    }
    
    return jsonify(res)

def run():
  app.run(host="0.0.0.0", port=8000)

async def keep_alive():
  server = Thread(target=run)
  server.start()


class Bot(Client):

    def __init__(self):
        super().__init__(
        "movie_finder",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
        )

    async def start(self):  
        # await keep_alive()
        await super().start()
        me = await self.get_me()
        self.username = f'@{me.username}'
        self.raw_username = me.username
        self.owner = await self.get_users(OWNER_ID)
        print('Bot started')


    async def stop(self, *args):

        await super().stop()
        print('Bot Stopped Bye')

Bot().run()
