import fugashi
import re
import emoji

class _EMOJI:
  """predict discord's customized emoji"""
  patternCustomizedEmoji = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

  """predict including Emoji"""
  def predicted(msg_content):
      return emoji.emoji_count(msg_content)!=0 or _EMOJI.patternCustomizedEmoji.search(msg_content)

  def remove(msg_content):
      return emoji.replace_emoji(_EMOJI.patternCustomizedEmoji.sub("",msg_content),"")
  


class _URL:
  """predict URL"""
  patternURL = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[-\w./?%&=]*)')

  """check including URL"""
  def predicted(msg_content):
      return _URL.patternURL.search(msg_content)

  """remove URL from message"""
  def remove(msg_content):
      msg_content=_URL.patternURL.sub("",msg_content)
      return msg_content
  

class Empty:
  tagger = fugashi.Tagger()

  def is_only_symbol(msg_content):
      check = msg_content
      check = _EMOJI.remove(_URL.remove(msg_content))
      for word in Empty.tagger(check):
          if word.feature.pos1 not in ["補助記号", "特殊","記号"]:# 記号以外がある場合
              return False  
      return True

  def predicted(msg_content):
      return (_URL.predicted(msg_content) or _EMOJI.predicted(msg_content) or Empty.is_only_symbol(msg_content))

  def remove(msg_content):
      msg_content=_EMOJI.remove(_URL.remove(msg_content))
      if(Empty.is_only_symbol(msg_content)):
          msg_content=""
      return msg_content