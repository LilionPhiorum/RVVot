
import requests
import json
import io
import discord
from discord import FFmpegPCMAudio
from bidict import bidict#双方向辞書

class VOICEVOX:
  host="127.0.0.1"#localhost
  port=50021

  """connecting VOICEVOX"""
  def is_connect(interaction: discord.Interaction):
    try:
      response = requests.get(f"http://{VOICEVOX.host}:{VOICEVOX.port}", timeout=1)  # 接続
      return response.status_code == 200
    except requests.RequestException:  # 接続不可
      return False

  def all_voice():
    response = requests.get(f"http://{VOICEVOX.host}:{VOICEVOX.port}/speakers")
    speakers = response.json()
    speaker_data = []
    for speaker in speakers:
      name = speaker['name']
      styles = speaker['styles']
      for style in styles:
        speaker_data.append((name, style['name'], style['id']))
    return speaker_data

  #音声合成用クエリ作成
  def _gene_voice(talking_setting):
    query=requests.post(
    f'http://{VOICEVOX.host}:{VOICEVOX.port}/audio_query',
            params=talking_setting
                        )
    #音声合成を実施
    synthesis = requests.post(
      f'http://{VOICEVOX.host}:{VOICEVOX.port}/synthesis',
      headers = {"Content-Type": "application/json"},
      params = talking_setting,
      data = json.dumps(query.json())
      )
    return synthesis.content

  async def synthesize_voice(msg_content,usr_id):
    #voiceコマンド(chgVoiceメソッド)完成までの一時設定
    talking_setting = (
      ('text', msg_content),
      ('speaker', VoiceSet.get_private_speaker_id(usr_id)),
    )
    #===========================================
    return VOICEVOX._gene_voice(talking_setting)

class VoiceSet:
  file_name="rv_voice_dic.txt"
  voice_settings={}#ユーザーIDをキーに声を呼び出すdict

  voice_dic=bidict()#話者一覧({名前,id}で構成される)

  def get_private_speaker_id(usr_id):
    return VoiceSet.voice_settings.get(str(usr_id), 3)#3はずんだもん
      

  """テキストファイルとして保存しておいたボイス設定を読み込む"""
  #ここをenvに保存出来たらいいかも
  def load_voice():
    with open(VoiceSet.file_name,"r")as file:
      for line in file:
        words = line.strip().split()
        VoiceSet.voice_settings[str(words[0])]=words[1]

  """指定したユーザーidのデータがディクショナリ内にあるか探索"""
  def seach_id(usr_id):
    return str(usr_id) in VoiceSet.voice_settings


  """声設定をディクショナリに保存し、テキストファイルに書き込む"""
  def set_voice(usr_id,voice):
    usr_id = str(usr_id)
    voice = str(voice)
    VoiceSet.voice_settings[usr_id]=voice
    if VoiceSet.seach_id(usr_id):
      with open(VoiceSet.file_name,"w",encoding="utf-8") as file:
        for key,value in VoiceSet.voice_settings.items():
          file.write(f"{key} {value}\n")
    else:
      with open(VoiceSet.file_name,"a",encoding="utf-8") as file:
        file.write(f"{usr_id} {voice}\n")

  """声を変更するコマンドの選択肢を与えるための関数"""
  def mk_dic():
    data=VOICEVOX.all_voice()
    for name, feature, id in data:
      if len(VoiceSet.voice_dic) >= 25:
        break
      if not(name in VoiceSet.voice_dic) and (feature=="ノーマル"):
        if name not in {"剣崎雌雄", "玄野武宏", "麒ヶ島宗麟"}:
          VoiceSet.voice_dic[name]=id
    return VoiceSet.voice_dic
  
  """userIDからその人の読み上げボイスが誰か表示したい..."""
  def get_speaker_name(usr_id):
    usr_id = str(usr_id)
    return VoiceSet.voice_dic.inv.get(int(VoiceSet.get_private_speaker_id(usr_id)))