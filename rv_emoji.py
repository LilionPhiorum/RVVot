import re
import emoji#pip install emoji

"""predict discord's customized emoji"""
patternCustomizedEmoji = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

"""predict including Emoji"""
def predicted(msg):
    return emoji.emoji_count(msg.content)!=0 or patternCustomizedEmoji.search(msg.content)

def remove(msg):
    return emoji.replace_emoji(patternCustomizedEmoji.sub("",msg.content),"")