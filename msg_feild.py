#メッセージ作成用のフィールドを作成する予定
class materials:
  id=None         # ユーザーid、声の振り分けに利用
  message=None    # メッセージ内容、読み上げ内容
  is_user=None    # 送信者がユーザーであるかどうか
  guild=None      # 送信されたテキストチャンネル

  def __init__(self,msg):
    self.id = msg.author.id
    self.message=msg.content
    self.is_user=not(msg.author.bot)
    self.guild=msg.guild

  def test(self):
    # return self.id
    # return self.message
    # return self.is_user
    return self.guild