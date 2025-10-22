import discord
from discord.ext import commands#bot操作
from discord import app_commands#コマンド
from discord import FFmpegPCMAudio#
import requests
import json
import io
import socket
import re
import emoji

intents = discord.Intents.default()
intents.message_content=True#メッセージ読み取りの許可
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

host="127.0.0.1"#localhost
port=50021

readChannel=[]#read channel 

#awake
#===============================================================
@client.event
async def on_ready():
    await tree.sync()#コマンド同期
    print("awaked")
#===============================================================

#discord condition checking
#===============================================================
"""connecting VOICEVOX"""
def VOICEVOX_Connection(interaction:discord.Interaction):
    try:
        test=socket.create_connection((host, port), timeout=1)#接続
        test.close()
        return True
    except socket.error:#接続不可
        return False

"""order isn't bot"""
def isUser(interaction):
    return not(interaction.user.bot)

"""order is joinning VC"""
def isUserTalking(interaction):
    #convert to bool by adding not
    return not not interaction.user.voice

"""bot is joinning VC"""
def is_bot_reading(interaction):
    return not not interaction.guild.voice_client
#===============================================================

#discord's function
#===============================================================
"""send hidden message"""
async def HiddenResponse(interaction,cont:str=None):#引数はinteractionとメッセージ内容
    if cont != None:
        await interaction.response.send_message(cont,ephemeral=True)
    else:
        await interaction.response.send_message("none content",ephemeral=True)

"""connect VC"""
async def ConnectVoiceChannel(interaction,msg:str=None):#interaction,応答内容
    global readChannel
    readChannel.append(interaction.channel)
    await interaction.user.voice.channel.connect()
    await HiddenResponse(interaction,msg)

"""disconnect VC"""
async def DisconnectVoiceChannel(interaction,msg:str=None):#interaction,応答内容
    global readChannel
    await interaction.guild.voice_client.disconnect()
    readChannel=[]
    await HiddenResponse(interaction,msg)

"""add read up channel"""
async def AddReadChannel(interaction,msg:str=None):
    global readChannel
    readChannel.append(interaction.channel)
    await HiddenResponse(interaction,msg)

"""remove read up channel"""
async def RemoveReadChannel(interaction,msg:str=None):
    global readChannel
    readChannel.remove(interaction.channel)
    await HiddenResponse(interaction,msg)
#===============================================================

#URL
#===============================================================
"""predict URL"""
patternURL = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[-\w./?%&=]*)')

"""check including URL"""
def PredictedURL(msg):
    return patternURL.search(msg.content)

"""remove URL from message"""
def RemoveURL(msg):
    return patternURL.sub("",msg.content)
#===============================================================

#Emoji(yet)
#===============================================================
# """predict Emoji"""
# patternEmoji = re.compile(r':[a-zA-Z0-9_]+:')#ディスコードの絵文字形式

"""predict discord's customized emoji"""
patternCustomizedEmoji = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

"""predict including Emoji"""
def PredictedEmoji(msg):
    return emoji.emoji_count(msg.content)!=0 or patternCustomizedEmoji.search(msg.content)

def RemoveEmoji(msg):
    
    return emoji.replace_emoji(patternCustomizedEmoji.sub("",msg.content),"")
#===============================================================

#error message
#===============================================================
async def CommonErrorMessage(interaction):
    if not(VOICEVOX_Connection(interaction)):#can't check connecting VOICEVOX
        await HiddenResponse(interaction,"VOICEVOXとの接続ができていません")
    elif not(isUser(interaction)):#error : the order by bot
        await HiddenResponse(interaction,"botによるコマンドは受け付けていません")
    else:#fatal error : Unknown
        await HiddenResponse(interaction,"未知のエラーです")
#===============================================================

#command
#===============================================================
"""join order's VC"""
@tree.command(name="on",description="VCへの参加し、コマンドを利用したテキストチャンネルの読み上げを開始")
async def On(interaction:discord.Interaction,force:bool=False) :
    global readChannel#変更を行うならglobal宣言が必要
    #指令がbotでなくて、ボイチャに接続していて、再宣言されたときに入る先が同じでない
    if isUser(interaction) and isUserTalking(interaction):
        #botがボイスチャットに接続していない場合にvoice_client.channelにアクセスするなどがないように
        if interaction.guild.voice_client != None:
            #同じチャンネルに接続するというコマンドの場合
            if interaction.guild.voice_client.channel == interaction.user.voice.channel:
                await HiddenResponse(interaction,"接続済みです")
            #ボイスチャンネルAにいる状態でボイスチャンネルBに呼び出され、forceがTrueの場合
            elif force and (interaction.guild.voice_client.channel != interaction.user.voice.channel):
                #一度切断して再接続
                await DisconnectVoiceChannel(interaction,"一時切断")
                await ConnectVoiceChannel(interaction,"再接続")
            #事故防止のためにforceを有効にしない限り移動処理を行わないように
            if not(force):
                await HiddenResponse(interaction,"すでに接続済みです。移動を行う場合はforceをTrueにしてください")
        else:
            #一般的な接続・読み上げ開始処理
            await ConnectVoiceChannel(interaction,"接続")#
    else:#error
        if not(isUserTalking(interaction)):
            await HiddenResponse(interaction,"コマンド実行者がVCに接続した後に使用してください")
        else:
            await CommonErrorMessage(interaction)

"""add read up channel"""
@tree.command(name="add",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def Add(interaction:discord.Interaction):
    global readChannel#変更を行うならglobal宣言が必要
    #指令がbotでなくて、読み上げ対象チャンネルとされていない
    if isUser(interaction) and (not interaction.channel in readChannel) and (is_bot_reading(interaction)):
        await AddReadChannel(interaction,"追加")#
    else:
        #追加するチャンネルがすでに追加されている場合
        if (interaction.channel in readChannel):
            await HiddenResponse(interaction,"すでに追加されています")
        #読み上げがまだ始まっていない場合に、StartReadingとは違い、接続チャンネル変更なしで接続
        elif not(is_bot_reading(interaction)):
            if isUserTalking(interaction):
                await ConnectVoiceChannel(interaction,"未接続のため接続")
            else:#isUserには入れていて、isUserTalkingがfalse出ないとここに入らない
                await HiddenResponse(interaction,"コマンド実行者がVCに接続した後に使用してください")
        else:#error
            await CommonErrorMessage(interaction)

"""remove from read up channel"""
@tree.command(name="remove",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def Remove(interaction:discord.Interaction):
    global readChannel
    if isUser(interaction) and (interaction.channel in readChannel):
        await RemoveReadChannel(interaction,"除外")#
        #読み上げチャンネルがない状態で使用されると通話から抜ける
    elif isUser(interaction) and (readChannel == []):
        await DisconnectVoiceChannel(interaction,"読み上げ対象がないため切断")
    else:
        if not(interaction.channel in readChannel):
            await HiddenResponse(interaction,"読み上げるチャンネルではありません")
        else:
            await CommonErrorMessage(interaction)

"""disconnect VC(any channel)"""
@tree.command(name="off",description="VCからの離脱")
async def Remove(interaction:discord.Interaction):
    global readChannel
    if isUser(interaction) and is_bot_reading(interaction):
        await DisconnectVoiceChannel(interaction,"切断")#
    else:
        if not is_bot_reading(interaction):
            await HiddenResponse(interaction,"botはVCに参加していません")
        else:
            await CommonErrorMessage(interaction)
#===============================================================

#音声合成
#===============================================================
async def SynthesizeVoice(msg):
    #botでなく、読み上げ対象のチャンネルである場合
    if (not msg.author.bot) and (msg.channel in readChannel):
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

#基本状況
#===============================================================
@client.event
async def on_message(msg):
    print(msg.content)
    global readChannel#変更を行うならglobal宣言が必要->いらない？これの整理をする
    #リンクがある場合、それを除外
    if PredictedURL(msg):
        msg.content = RemoveURL(msg)
    #絵文字の処理
    #未完成
    if PredictedEmoji(msg):
        msg.content = RemoveEmoji(msg)
    #メッセージなしの場合(スタンプ、メッセージなしのファイル送信)
    if not(msg.content.strip()):
        print("Ignored because it was predicted as an non-message")
    else:
        #print(msg.content)
        await SynthesizeVoice(msg)
#===============================================================

#試験用コマンド
#===============================================================
@tree.command(name="test",description="応答ありの関数のテスト")
async def Tester(interaction:discord.Interaction):
    # await HiddenResponse(interaction,"-..-")
    await interaction.response.send_message(not isUserTalking(interaction))
#===============================================================

client.run("")