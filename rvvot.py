#common module
import discord
from discord.ext import commands#bot操作
from discord import app_commands#コマンド
from discord.app_commands import Choice
from discord import FFmpegPCMAudio
import io
from dotenv import load_dotenv
import os
#original module
import rv_voicevox as RV_voicevox
import rv_modify as RV_modify

import random

intents = discord.Intents.default()
intents.message_content=True#メッセージ読み取りの許可
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

readChannel=[]
voice_dic = RV_voicevox.VoiceSet.mk_dic();#名前とidの対応表

#botのトークンの読み込み
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

#for other commands



#awake
#===============================================================
@client.event
async def on_ready():
  await tree.sync()#コマンド同期
  RV_voicevox.VoiceSet.load_voice()#音声設定同期
  print("ver 4.0 awaked")
#===============================================================

#discord condition checking
#===============================================================
"""コマンドがbotによるものでない場合true"""
def is_user(interaction):
  return not(interaction.user.bot)

"""コマンド使用者がボイスチャットに入っている場合true"""
def is_user_talking(interaction):
  return bool(interaction.user.voice)

"""botがボイスチャットに入っている場合はtrue"""
def is_bot_reading(interaction):
  return bool(interaction.guild.voice_client)

"""botのVCへの呼び出し条件が整っていればtrue"""
#ユーザーによるコマンド使用、コマンド使用者がVCに接続済み、voicevoxへの接続済み
def is_bot_can_call(interaction):
  return bool(is_user(interaction) and is_user_talking(interaction) and RV_voicevox.VOICEVOX.is_connect(interaction))
#===============================================================

#discord's function
#===============================================================
"""隠しメッセージの送信"""
async def hidden_response(interaction,cont:str="none content"):#引数はinteractionとメッセージ内容
  if not interaction.response.is_done():
    await interaction.response.send_message(cont, ephemeral=True)
  else:
    await interaction.followup.send(cont, ephemeral=True)

"""オープンメッセージの送信"""
async def open_response(interaction,cont:str="none content"):#引数はinteractionとメッセージ内容
  if not interaction.response.is_done():
    await interaction.response.send_message(cont, ephemeral=False)
  else:
    await interaction.followup.send(cont, ephemeral=False)

"""VCへの接続"""
async def connect_voice_channel(interaction,msg:str=None):#interaction,応答内容
  global readChannel
  readChannel.append(interaction.channel)
  await interaction.user.voice.channel.connect()
  await hidden_response(interaction,msg)

"""VCからの切断"""
async def disconnect_voice_channel(interaction,msg:str=None):#interaction,応答内容
  global readChannel
  await interaction.guild.voice_client.disconnect()
  readChannel=[]
  await hidden_response(interaction,msg)

"""読み上げるテキストチャンネルの追加"""
async def add_read_channel(interaction,msg:str=None):
  global readChannel
  readChannel.append(interaction.channel)
  await hidden_response(interaction,msg)

"""読み上げチャンネルからの排除"""
async def remove_read_channel(interaction,msg:str=None):
  global readChannel
  readChannel.remove(interaction.channel)
  await hidden_response(interaction,msg)

"""読み上げチャンネルへの存在を確認"""
def is_read_channel(channel):
  global readChannel
  return channel in readChannel

"""UserIDをもとに表示名を返す"""
async def get_display_name(msg,user_id):
  name = (await msg.guild.fetch_member(user_id)).display_name
  return name
#===============================================================

#error message
#===============================================================
async def common_error_message(interaction):
  if not(RV_voicevox.is_connect(interaction)):#VOICEVOXとの接続ができていないとき
      await hidden_response(interaction,"VOICEVOXとの接続ができていません")
  elif not(is_user(interaction)):#error : botによるコマンド指示
    await hidden_response(interaction,"botによるコマンドは受け付けていません")
  else:#fatal error : Unknown
    await hidden_response(interaction,"未知のエラーです")
#===============================================================

#command
#===============================================================
"""VCへの呼び出しコマンド"""
@tree.command(name="on",description="VCへの参加し、コマンドを利用したテキストチャンネルの読み上げを開始")
async def on(interaction:discord.Interaction,force:bool=False) :
  await interaction.response.defer(ephemeral=True)#処理中というのをdiscordに送信
  #指令がbotでなくて、ボイチャに接続していて、再宣言されたときに入る先が同じでない
  if is_bot_can_call(interaction):
    #botがボイスチャットに接続していない場合にvoice_client.channelにアクセスするなどがないように
    if interaction.guild.voice_client != None:
      #同じチャンネルに接続するというコマンドの場合
      if interaction.guild.voice_client.channel == interaction.user.voice.channel:
        await hidden_response(interaction,"接続済みです")
      #ボイスチャンネルAにいる状態でボイスチャンネルBに呼び出され、forceがTrueの場合
      elif force and (interaction.guild.voice_client.channel != interaction.user.voice.channel):
        #一度切断して再接続
        await disconnect_voice_channel(interaction,"一時切断")
        await connect_voice_channel(interaction,"再接続")
      #事故防止のためにforceを有効にしない限り移動処理を行わないように
      if not(force):
        await hidden_response(interaction,"すでに接続済みです。移動を行う場合はforceをTrueにしてください")
    else:
      #一般的な接続・読み上げ開始処理
      await connect_voice_channel(interaction,"接続")
  else:#error
    if not(is_user_talking(interaction)):
      await hidden_response(interaction,"コマンド実行者がVCに接続した後に使用してください")
    else:
      await common_error_message(interaction)

"""読み上げチャンネルの追加コマンド"""
@tree.command(name="add",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def add(interaction:discord.Interaction):
  await interaction.response.defer(ephemeral=True)#処理中というのをdiscordに送信
  if is_bot_can_call(interaction):
    if is_bot_reading(interaction):#botが読み上げ中
      if not(is_read_channel(interaction.channel)):#追加チャンネルが読み上げチャンネルに入っていない場合
        await add_read_channel(interaction,"追加")
      else:#追加チャンネルが読み上げチャンネルに入っている場合
        await hidden_response(interaction,"すでに追加されています")
    else:#botが読み上げしてない場合
      await connect_voice_channel(interaction,"未接続のため接続")
  else:#error
    await common_error_message(interaction)

"""読み上げチャンネルからの排除コマンド"""
@tree.command(name="remove",description="コマンドを利用したテキストチャンネルを読み上げ対象として追加")
async def remove(interaction:discord.Interaction):
  await interaction.response.defer(ephemeral=True)#処理中というのをdiscordに送信
  if is_user(interaction) and (interaction.channel in readChannel):
    await remove_read_channel(interaction,"除外")
    #読み上げチャンネルがない状態で使用されると通話から抜ける
  elif is_user(interaction) and (readChannel == []) and is_bot_reading(interaction):
    await disconnect_voice_channel(interaction,"読み上げ対象がないため切断")
  else:
    if not(interaction.channel in readChannel):
      await hidden_response(interaction,"読み上げるチャンネルではありません")
    else:
      await common_error_message(interaction)

"""ボイスチャットからの切断"""
@tree.command(name="off",description="VCからの離脱")
async def off(interaction:discord.Interaction):
  await interaction.response.defer(ephemeral=True)#処理中というのをdiscordに送信
  if is_user(interaction) and is_bot_reading(interaction):
    await disconnect_voice_channel(interaction,"切断")
  else:
    if not is_bot_reading(interaction):
      await hidden_response(interaction,"敗北者め！")#またここは変更
    else:
      await common_error_message(interaction)

"""読み上げボイスの変更"""
voice_options = [Choice(name=key, value=value) for key,value in RV_voicevox.VoiceSet.mk_dic().items()]
@tree.command(name="voice",description="読み上げ音声の変更")
@app_commands.choices(voice=voice_options)
async def voice(interaction: discord.Interaction,voice:Choice[int]):
  await interaction.response.defer(ephemeral=True)#処理中というのをdiscordに送信
  RV_voicevox.VoiceSet.set_voice(interaction.user.id,voice.value)
  await hidden_response(interaction,(RV_voicevox.VoiceSet.get_speaker_name(interaction.user.id)+" が読み上げます"))

"""現状読み上げてくれてるボイスの確認"""
@tree.command(name="speaker",description="読み上げ話者の名前の表示")
async def speaker(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  await hidden_response(interaction,(RV_voicevox.VoiceSet.get_speaker_name(interaction.user.id)+" が読み上げています"))
#===============================================================

#other commands
#===============================================================
"""乱数生成コマンド"""
@tree.command(name="randnum",description="乱数")
async def randnum(interaction: discord.Interaction, min:int=0, max:int=100):
  await interaction.response.defer(ephemeral=False)
  randnum = random.uniform(min, max)
  await open_response(interaction, randnum)

"""今日はお休みコマンド"""
noticeChannelID = None

def _load_notice_channel_id():
  """othercommands.txt の noticeChannel 直下の行からID(int)を取得"""
  file_path = os.path.join(os.path.dirname(__file__), "othercommands.txt")
  try:
    with open(file_path, "r", encoding="utf-8") as f:
      lines = f.readlines()
    idx = next((i for i, l in enumerate(lines) if l.strip() == "noticeChannel"), None)
    if idx is not None and idx + 1 < len(lines):
      return int(lines[idx + 1].strip())
  except Exception:
    pass
  return None

@tree.command(name="setz", description="今日はお休みのメッセージのチャンネル設定")
async def zset(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=False)
  global noticeChannelID
  noticeChannelID = interaction.channel.id  # 数値IDを保持

  file_path = os.path.join(os.path.dirname(__file__), "othercommands.txt")
  channel_id_str = str(noticeChannelID) + "\n"

  try:
    with open(file_path, "r", encoding="utf-8") as f:
      lines = f.readlines()
  except FileNotFoundError:
    lines = []

  idx = next((i for i, l in enumerate(lines) if l.strip() == "noticeChannel"), None)
  if idx is not None:
    if idx + 1 < len(lines):
      lines[idx + 1] = channel_id_str
    else:
      lines.append(channel_id_str)
  else:
    lines.extend(["noticeChannel\n", channel_id_str])

  with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

  await open_response(interaction, "お休み通知チャンネルを設定しました")

@tree.command(name="z", description="今日はお休み")
async def rest(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  global noticeChannelID

  channel_id = noticeChannelID or _load_notice_channel_id()

  channel = await client.fetch_channel(channel_id)
  name = getattr(interaction.user, "display_name", interaction.user.name)
  await channel.send(interaction.user.display_name +"「今日はお休み」")
  await hidden_response(interaction, "送信しました")
#===============================================================

#基本状況
#将来的にはプロセス管理により安定化させる
#===============================================================
@client.event
async def on_message(msg):
  # print("msg.content="+msg.content)
  #botでなく、読み上げ対象のチャンネルである場合
  if (not msg.author.bot) and (msg.channel in readChannel):
    #メンションのユーザーID部分をユーザー名に変更
    if RV_modify.UserID.predicted(msg.content):
      msg.content = RV_modify.UserID.replace(msg.content,(await get_display_name(msg,RV_modify.UserID.retrieve(msg.content)))) 
    msg.content = RV_modify.Empty.remove(msg.content) #文字列にURL,emojiが含まれる場合はそれを取り除き、その上で記号のみなら空文字を返す
    if not(msg.content.strip()):
      print("Ignored because it was predicted as an non-message")
    else:
      print(msg.content)
      voice = await RV_voicevox.VOICEVOX.synthesize_voice(msg.content,msg.author.id)
      audio_stream=io.BytesIO(voice)#音声変換1
      audio_source=FFmpegPCMAudio(audio_stream,pipe=True)#音声変換2
      voice_client = discord.utils.get(client.voice_clients, guild=msg.guild)
      if not voice_client.is_playing():
          voice_client.play(audio_source)
#===============================================================


client.run(TOKEN)