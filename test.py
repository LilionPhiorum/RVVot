#common module
import discord
from discord.ext import commands#bot操作
from discord import app_commands#コマンド
from discord import FFmpegPCMAudio
import io

import msg_feild

intents = discord.Intents.default()
intents.message_content=True#メッセージ読み取りの許可
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

test:msg_feild.materials

@client.event
async def on_ready():
    await tree.sync()#コマンド同期
    print("ver 3.4 awaked")

@client.event
async def on_message(msg):
    test=msg_feild.materials(msg)
    print(test.test())
    # print(msg.author.id)

client.run("")