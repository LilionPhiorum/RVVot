import discord
from discord.ext import commands#botの制御に使用
from discord import app_commands#botコマンド動作に使用
from discord import FFmpegPCMAudio
import requests
import json
import io
import socket

intents = discord.Intents.default()
intents.message_content=True#メッセージ内容の読み取り許可
client = discord.Client(intents=intents)#botに置き換えても使える？
tree = app_commands.CommandTree(client)

host="127.0.0.1"#localhost
port=50021

ready=False#読み上げ許可
readChannel=[]#読み上げ対象となるチャンネル

@client.event
async def on_ready():
    await tree.sync()#スラッシュコマンドを同期
    print("awaked")


#点検用コマンド
#===============================================================
#VOICEVOXとの接続確認コマンド
@tree.command(name="connect",description="VOICEVOXへの接続確認")
async def VVConnection(interaction:discord.Interaction):
    try:
        test=socket.create_connection((host, port), timeout=1)#接続確立
        test.close()#testの終了
        await interaction.response.send_message("Connection Confirmation",ephemeral=True)
    except socket.error:#接続ができなかった場合
        await interaction.response.send_message("Connection Faild",ephemeral=True)
#===============================================================



#コマンドを起動したユーザーのいるボイスチャンネルに参加するコマンド
@tree.command(name="on",description="VCへの参加")
async def Connect_VoiceChannel(interaction:discord.Interaction):
    await interaction.user.voice.channel.connect()
    await interaction.response.send_message("connect",ephemeral=True)
    global ready
    ready=True
    
    

#現在いるボイスチャンネルから離脱するコマンド
@tree.command(name="off",description="vcからの離脱")
async def Disconnect_VoiceChannel(interaction:discord.Integration):
    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("disconnect",ephemeral=True)
    


@client.event
async def on_message(msg):
    talking_setting = (
        ('text', msg.content),
        ('speaker', 10),
    )
    #音声合成用クエリ作成
    query=requests.post(
    f'http://{host}:{port}/audio_query',
            params=talking_setting
                    )
    #音声合成を実施
    synthesis = requests.post(
            f'http://{host}:{port}/synthesis',
            headers = {"Content-Type": "application/json"},
            params = talking_setting,
            data = json.dumps(query.json())
        )
    #synthesis.contentに生成した音声がある
    audio_stream=io.BytesIO(synthesis.content)
    audio_source=FFmpegPCMAudio(audio_stream,pipe=True)
    voice_client = discord.utils.get(client.voice_clients, guild=msg.guild)
    if not voice_client.is_playing():
        voice_client.play(audio_source)

#=============================
client.run("")