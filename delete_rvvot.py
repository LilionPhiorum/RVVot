#common module
import discord
from discord.ext import commands#bot操作
from discord import app_commands#コマンド
from discord import FFmpegPCMAudio
import io
#original module
import rv_voicevox
from rv_remove import Empty as rv_empty
import test

intents = discord.Intents.default()
intents.message_content=True#メッセージ読み取りの許可
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

rmemp=rv_empty
vv=rv_voicevox

readChannel=[]

"""
なんかわけわからんことになってる
実行するとver34が起動したあとにCtrl+Cをするとver35が起動
ver34のprintなんてどこにもないのに表記される
再起動、ver34を動かしていた端末の停止と再起動までしても解決しなかった
"""


#これは独自フィールドを作って消す。独自フィールド内で完結させるので一時的に
#discord condition checking
#===============================================================
"""order isn't bot"""
def is_user(interaction):
    return not(interaction.user.bot)

"""order is joinning VC"""
def is_user_talking(interaction):
    #convert to bool by adding not
    return not not interaction.user.voice

"""bot is joinning VC"""
def is_bot_reading(interaction):
    return not not interaction.guild.voice_client
#===============================================================

# discord's function
#===============================================================
class Discord:
    """send hidden message"""
    async def hidden_response(interaction,cont:str=None):#引数はinteractionとメッセージ内容
        if cont != None:
            await interaction.response.send_message(cont,ephemeral=True)
        else:
            await interaction.response.send_message("none content",ephemeral=True)

    """connect VC"""
    async def connect_voice_channel(interaction,msg:str=None):#interaction,応答内容
        global readChannel
        readChannel.append(interaction.channel)
        await interaction.user.voice.channel.connect()
        await Discord.hidden_response(interaction,msg)

    """disconnect VC"""
    async def disconnect_voice_channel(interaction,msg:str=None):#interaction,応答内容
        global readChannel
        await interaction.guild.voice_client.disconnect()
        readChannel=[]
        await Discord.hidden_response(interaction,msg)

    """add read up channel"""
    async def add_read_channel(interaction,msg:str=None):
        global readChannel
        readChannel.append(interaction.channel)
        await Discord.hidden_response(interaction,msg)

    """remove read up channel"""
    async def remove_read_channel(interaction,msg:str=None):
        global readChannel
        readChannel.remove(interaction.channel)
        await Discord.hidden_response(interaction,msg)
#===============================================================

#error message
#===============================================================
async def common_error_message(interaction):
    if not(vv.isConnect(interaction)):#can't check connecting VOICEVOX
        await Discord.hidden_response(interaction,"VOICEVOXとの接続ができていません")
    elif not(is_user(interaction)):#error : the order by bot
        await Discord.hidden_response(interaction,"botによるコマンドは受け付けていません")
    else:#fatal error : Unknown
        await Discord.hidden_response(interaction,"未知のエラーです")
#===============================================================

#awake
#===============================================================
@client.event
async def on_ready():
    await tree.sync()#コマンド同期
    print("ver 3.5 awaked")
#===============================================================

"""command"""
#class Commands:
#===============================================================
"""join order's VC"""
@tree.command(name="on",description="VCへの参加し、コマンドを利用したテキストチャンネルの読み上げを開始")
async def on(interaction:discord.Interaction,force:bool=False) :
    global readChannel#変更を行うならglobal宣言が必要
    #指令がbotでなくて、ボイチャに接続していて、再宣言されたときに入る先が同じでない
    if is_user(interaction) and is_user_talking(interaction):
        #botがボイスチャットに接続していない場合にvoice_client.channelにアクセスするなどがないように
        if interaction.guild.voice_client != None:
            #同じチャンネルに接続するというコマンドの場合
            if interaction.guild.voice_client.channel == interaction.user.voice.channel:
                await Discord.hidden_response(interaction,"接続済みです")
            #ボイスチャンネルAにいる状態でボイスチャンネルBに呼び出され、forceがTrueの場合
            elif force and (interaction.guild.voice_client.channel != interaction.user.voice.channel):
                #一度切断して再接続
                await Discord.disconnect_voice_channel(interaction,"一時切断")
                await Discord.connect_voice_channel(interaction,"再接続")
            #事故防止のためにforceを有効にしない限り移動処理を行わないように
            if not(force):
                await Discord.hidden_response(interaction,"すでに接続済みです。移動を行う場合はforceをTrueにしてください")
        else:
            #一般的な接続・読み上げ開始処理
            await Discord.connect_voice_channel(interaction,"接続")#
    else:#error
        if not(is_user_talking(interaction)):
            await Discord.hidden_response(interaction,"コマンド実行者がVCに接続した後に使用してください")
        else:
            await common_error_message(interaction)

"""add read up channel"""
@tree.command(name="add",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def add(interaction:discord.Interaction):
    global readChannel#変更を行うならglobal宣言が必要
    #指令がbotでなくて、読み上げ対象チャンネルとされていない
    if is_user(interaction) and (not interaction.channel in readChannel) and (is_bot_reading(interaction)):
        await Discord.add_read_channel(interaction,"追加")#
    else:
        #追加するチャンネルがすでに追加されている場合
        if (interaction.channel in readChannel):
            await Discord.hidden_response(interaction,"すでに追加されています")
        #読み上げがまだ始まっていない場合に、StartReadingとは違い、接続チャンネル変更なしで接続
        elif not(is_bot_reading(interaction)):
            if is_user_talking(interaction):
                await Discord.connect_voice_channel(interaction,"未接続のため接続")
            else:#is_userには入れていて、is_user_talkingがfalse出ないとここに入らない
                await Discord.hidden_response(interaction,"コマンド実行者がVCに接続した後に使用してください")
        else:#error
            await common_error_message(interaction)

"""remove from read up channel"""
@tree.command(name="remove",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def remove(interaction:discord.Interaction):
    global readChannel
    if is_user(interaction) and (interaction.channel in readChannel):
        await Discord.remove_read_channel(interaction,"除外")#
        #読み上げチャンネルがない状態で使用されると通話から抜ける
    elif is_user(interaction) and (readChannel == []):
        await Discord.disconnect_voice_channel(interaction,"読み上げ対象がないため切断")
    else:
        if not(interaction.channel in readChannel):
            await Discord.hidden_response(interaction,"読み上げるチャンネルではありません")
        else:
            await common_error_message(interaction)

"""disconnect VC(any channel)"""
@tree.command(name="off",description="VCからの離脱")
async def off(interaction:discord.Interaction):
    global readChannel
    if is_user(interaction) and is_bot_reading(interaction):
        await Discord.disconnect_voice_channel(interaction,"切断")#
    else:
        if not is_bot_reading(interaction):
            await Discord.hidden_response(interaction,"botはVCに参加していません")
        else:
            await common_error_message(interaction)
#===============================================================

# これは実際にはrv_voicevox.pyに任せる
#音声合成
#===============================================================
async def synthesize_voice(msg):
    #voiceコマンド(chgVoiceメソッド)完成までの一時設定
    talking_setting = (
        ('text', msg.content),
        ('speaker', 10),
    )
    #===========================================
    return vv.gene_voice(msg,talking_setting)
#===============================================================

#基本状況
#===============================================================
@client.event
async def on_message(msg):
    print(msg.content)
    global readChannel#変更を行うならglobal宣言が必要->いらない？これの整理をする
    #botでなく、読み上げ対象のチャンネルである場合
    if (not msg.author.bot) and (msg.channel in readChannel):
        msg=rmemp.remove(msg) #文字列にURL,emojiが含まれる場合はそれを取り除き、その上で記号のみなら空文字を返す
        if not(msg.content.strip()):
            print("Ignored because it was predicted as an non-message")
        else:
            #print(msg.content)
            voice = await synthesize_voice(msg)
            audio_stream=io.BytesIO(voice)#音声変換1
            audio_source=FFmpegPCMAudio(audio_stream,pipe=True)#音声変換2
            voice_client = discord.utils.get(client.voice_clients, guild=msg.guild)
            if not voice_client.is_playing():
                voice_client.play(audio_source)
#===============================================================

# 
client.run("")