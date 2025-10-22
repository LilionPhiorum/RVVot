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
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

host="127.0.0.1"#localhost
port=50021

readChannel=[]#読み上げ対象となるチャンネル

@client.event
async def on_ready():
    await tree.sync()#コマンド同期
    print("awaked")



#簡略化用関数
#===============================================================
#VOICEVOXとの接続確認コマンド
def VOICEVOX_Connection(interaction:discord.Interaction):
    try:
        test=socket.create_connection((host, port), timeout=1)#接続確立
        test.close()#testの終了
        return True
    except socket.error:#接続ができなかった場合
        return False

#指令者がbotでないことの確認
def isUser(interaction):#引数はinteraction.user
    return not(interaction.user.bot)

#指令者がVCに入っていることを確認
def isUserTalking(interaction):#引数はinteraction.user
    #notをつけない場合、voiceの中身すべてが出されるが、notを入れることでboolになる
    return not not interaction.user.voice

def is_bot_reading(interaction):
    return not not interaction.guild.voice_client

#応答を返す
async def HiddenResponse(interaction,cont:str):#引数はinteractionとメッセージ内容
    await interaction.response.send_message(cont,ephemeral=True)
#===============================================================



#試験用コマンド
#===============================================================
@tree.command(name="test",description="応答ありの関数のテスト")
async def Tester(interaction:discord.Interaction):
    #await HiddenResponse(interaction,"-..-")
    await interaction.response.send_message(not isUserTalking(interaction))
#===============================================================



#エラーメッセージ
#===============================================================
async def CommonErrorMessage(interaction):
    if not(VOICEVOX_Connection(interaction)):#
        await HiddenResponse(interaction,"VOICEVOXとの接続ができていません")
    elif not(isUser(interaction)):#error : the order by bot
        await HiddenResponse(interaction,"botによるコマンドは受け付けていません")
    else:#fatal error : Unknown
        await HiddenResponse(interaction,"未知のエラーです")
#===============================================================


#bot
#===============================================================
#コマンドを起動したユーザーのいるボイスチャンネルに参加するコマンド
@tree.command(name="on",description="VCへの参加し、コマンドを利用したテキストチャンネルの読み上げを開始")
async def StartReading(interaction:discord.Interaction,force:bool=False) :
    global readChannel
    #指令がbotでなくて、ボイチャに接続していて、再宣言されたときに入る先が同じでない
    if isUser(interaction) and isUserTalking(interaction):
        #botがボイスチャットに接続していない場合にvoice_client.channelにアクセスするなどが内容に
        if interaction.guild.voice_client != None:
            #同じチャンネルに接続するというコマンドの場合
            if interaction.guild.voice_client.channel == interaction.user.voice.channel:
                await HiddenResponse(interaction,"接続済みです")
            #チャンネルの移動
            elif force and (interaction.guild.voice_client.channel != interaction.user.voice.channel):
                #一度切断して再接続
                readChannel=[]
                await interaction.guild.voice_client.disconnect()
                readChannel.append(interaction.channel)
                await interaction.user.voice.channel.connect()
                await HiddenResponse(interaction,"移動しました")
            #事故防止のためにforceを有効にしない限り移動処理を行わないように
            if not(force):
                await HiddenResponse(interaction,"すでに接続済みです。移動を行う場合はforceをTrueにしてください")
        else:
            #一般的な接続・読み上げ開始処理
            readChannel.append(interaction.channel)
            await interaction.user.voice.channel.connect()
            await HiddenResponse(interaction,"接続しました")
    else:#error
        if not(isUserTalking(interaction)):
            await HiddenResponse(interaction,"コマンド実行者がVCに接続した後に使用してください")
        else:
            await CommonErrorMessage(interaction)

#読み上げチャンネルへの追加
@tree.command(name="add",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def AddReadChannel(interaction:discord.Interaction):
    global readChannel
    #指令がbotでなくて、読み上げ対象チャンネルとされていない
    if isUser(interaction) and (not interaction.channel in readChannel) and (is_bot_reading(interaction)):
        readChannel.append(interaction.channel)
        await HiddenResponse(interaction,"追加しました")
    else:
        #追加するチャンネルがすでに追加されている場合
        if (interaction.channel in readChannel):
            await HiddenResponse(interaction,"すでに追加されています")
        #読み上げがまだ始まっていない場合に、StartReadingとは違い、接続チャンネル変更なしで接続
        elif not(is_bot_reading(interaction)):
            if isUserTalking(interaction):
                readChannel.append(interaction.channel)
                await interaction.user.voice.channel.connect()
                await HiddenResponse(interaction,"読み上げを開始していないため接続しました")
            else:#isUserには入れていて、isUserTalkingがfalse出ないとここに入らない
                await HiddenResponse(interaction,"コマンド実行者がVCに接続した後に使用してください")
        else:#error
            await CommonErrorMessage(interaction)

#読み上げチャンネルからの除外
@tree.command(name="remove",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def RemoveReadChannel(interaction:discord.Interaction):
    global readChannel
    if isUser(interaction) and (interaction.channel in readChannel):
        readChannel.remove(interaction.channel)
        await HiddenResponse(interaction,"除外しました")
        #読み上げチャンネルがない状態で使用されると通話から抜ける
    elif isUser(interaction) and (readChannel == []):
        await interaction.guild.voice_client.disconnect()
        readChannel=[]
        await HiddenResponse(interaction,"読み上げチャンネルが存在しないため切断しました")
    else:
        if not(interaction.channel in readChannel):
            await HiddenResponse(interaction,"読み上げるチャンネルではありません")
        else:
            CommonErrorMessage(interaction)

#現在いるボイスチャンネルから離脱するコマンド(どのテキストチャンネルでも実行する)
@tree.command(name="off",description="vcからの離脱")
async def ExitingReading(interaction:discord.Interaction):
    global readChannel
    if isUser(interaction) and is_bot_reading(interaction):
        await interaction.guild.voice_client.disconnect()
        readChannel=[]
        await HiddenResponse(interaction,"切断しました")
    else:
        if not is_bot_reading(interaction):
            await HiddenResponse(interaction,"botはVCに参加していません")
        else:
            await CommonErrorMessage(interaction)

@client.event
async def on_message(msg):
    global readChannel
    #botでなく、読み上げ対象のチャンネルである場合
    if (not msg.author.bot) and (msg.channel in readChannel) :
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

#===============================================================
client.run("")