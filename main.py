import json
import asyncio

import discord
from fastapi import FastAPI
import uvicorn
from bot_client import MyClient, JoinModal, get_user_key
from model import AlarmData
from config import get_config




client = MyClient()


async def run_bot():
    config = get_config()
    await client.start(config['bot_token'])


@client.tree.command(guild=None, description="유저 등록 커맨드")
async def join(interaction):
    await interaction.response.send_modal(JoinModal())

@client.tree.command(guild=None, description="key 확인 커맨드")
async def key(interaction: discord.Interaction):
    user_key = get_user_key(interaction.user.id)


app = FastAPI()


@app.get("/", status_code=200)
def root():
    return "hi"


# post로 받은 값 json임. (디스코드 유저 id, 아이템 정보)
@app.post("/alarm", status_code=200)
async def alarm(alarm_data: AlarmData):
    result = await client.alarm(alarm_data.user_id, alarm_data.items)

    return {"message": "알람 등록"}


async def run_server():
    config = get_config()
    uvicorn_config = uvicorn.Config(app=app, host=config['server_host'], port=config['server_port'])
    server = uvicorn.Server(config=uvicorn_config)
    await server.serve()


async def main():
    await asyncio.gather(run_bot(), run_server())


if __name__ == '__main__':
    asyncio.run(main())
