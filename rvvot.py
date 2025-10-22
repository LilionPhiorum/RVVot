import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import requests
import socket#接続確認用
import json
import io

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=intents)#「.○○」で命令管理(.onなど)

host="127.0.0.1"#localhost
port=50021

ready=False#音声生成許可
read_channel=[]#読み上げチャンネル設定

#discord
#=============================
@bot.event
async def on_ready():
    print("awaked")

@bot.command()
async def on(order):#VC接続コマンド
    global ready#グローバル変数のreadyを用いる(pythonだと関数内だけの変更になるからそうでないことを明記)
    global read_channel
    if order.author.voice:#送信者がボイスチャットに接続している       
        if order.guild.voice_client:#ボイスチャンネルに接続している場合
            await off(order)#一度切って接続をする
        voice_channel = order.author.voice.channel#接続チャンネルを送信者のチャンネルに設定
        ready=True#読み上げ開始
        read_channel.append(order.channel)#読み上げ対象チャンネルに追加
        await voice_channel.connect()



@bot.command()
async def add(order):#読み上げチャンネル追加コマンド
    global read_channel
    if not order.channel in read_channel:
        read_channel.append(order.channel)



@bot.command()
async def remove(order):#読み上げチャンネル削除コマンド
    global read_channel
    if order.channel in read_channel:
        read_channel.remove(order.channel)



@bot.command()
async def off(order):#VC離脱コマンド
    global ready
    global read_channel
    for vc in bot.voice_clients:#bot接続チャンネルを取得
        if vc.guild == order.guild:#接続サーバーと現サーバーの一致確認
            ready=False
            read_channel=[]#読み上げチャンネルの初期化
            await vc.disconnect()



#検査用コマンド
@bot.command()
async def read_place(order):
    global read_channel
    if order.channel in read_channel:
        await order.channel.send("focused")
    else:
        await order.channel.send("out of sight")
#=============================

#API[VOICEBOX]
#=============================
@bot.command()
async def connection_state(order):#接続状態確認コマンド
    try:
        test=socket.create_connection((host, port), timeout=1)#接続確立
        test.close()#testの終了
        await order.channel.send("Connection Confirmation")
    except socket.error:#接続ができなかった場合
        await order.channel.send("Connection Faild")



@bot.event
async def on_message(msg):
    if msg.content.startswith(bot.command_prefix):#コマンドであるプレフィックス(「.」)の場合
        await bot.process_commands(msg)#コマンドの場合コマンドを実行する
    else:
        if ready and not msg.author.bot and msg.channel in read_channel:
            #文言,話者設定
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
            voice_client = discord.utils.get(bot.voice_clients, guild=msg.guild)
            if not voice_client.is_playing():
                voice_client.play(audio_source)

#=============================
bot.run("")