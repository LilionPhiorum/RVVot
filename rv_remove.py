import re
import emoji
import fugashi

class _URL:
  _patternURL = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[-\w./?%&=]*)')

  """check including URL"""
  @staticmethod
  def is_include(msg):
    return bool(_URL._patternURL.search(msg.content))

  """remove URL from message"""
  def remove(msg):
    msg.content=_URL._patternURL.sub("",msg.content)
    return msg



class _Emoji:
  """predict discord's customized emoji"""
  _patternCustomizedEmoji = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

  """predict including Emoji"""
  def is_include(msg):
    return bool(emoji.emoji_count(msg.content)!=0 or _Emoji._patternCustomizedEmoji.search(msg.content))

  def remove(msg):
    return emoji.replace_emoji(_Emoji._patternCustomizedEmoji.sub("",msg.content),"")
  


class Empty:
  _tagger = fugashi.Tagger()
  _is_empty:bool

  def is_only_symbol(msg):
    check = msg
    check.content = _Emoji.remove(_URL.remove(msg))
    for word in Empty._tagger(check.content):
        if word.feature.pos1 not in ["補助記号", "特殊","記号"]:# 記号以外がある場合
            return False  
    return True

  def is_include(msg):
    return (_URL.is_include(msg) or _Emoji.is_include(msg) or Empty.is_only_symbol(msg))
  
  def remove(msg):
    msg.content=_Emoji.remove(_URL.remove(msg))
    if(Empty.is_only_symbol(msg)):
        msg.content=""
    return msg