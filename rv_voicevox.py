
import requests
import json
import io
import discord
from discord import FFmpegPCMAudio

host="127.0.0.1"#localhost
port=50021

"""connecting VOICEVOX"""
def is_connect(interaction: discord.Interaction):
    try:
        response = requests.get(f"http://{host}:{port}", timeout=1)  # 接続
        return response.status_code == 200
    except requests.RequestException:  # 接続不可
        return False

#音声合成用クエリ作成
def _gene_voice(talking_setting):
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
    return synthesis.content

async def synthesize_voice(msg_content):
    #voiceコマンド(chgVoiceメソッド)完成までの一時設定
    talking_setting = (
        ('text', msg_content),
        ('speaker', 10),
    )
    #===========================================
    return _gene_voice(talking_setting)