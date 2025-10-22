import rv_emoji
import rv_url
import fugashi#pip install fugashi,pip install unidic-lite

tagger = fugashi.Tagger()

is_empty:bool

def is_only_symbol(msg):
    check = msg
    check.content = rv_emoji.remove(rv_url.remove(msg))
    for word in tagger(check.content):
        if word.feature.pos1 not in ["補助記号", "特殊","記号"]:# 記号以外がある場合
            return False  
    return True

def predicted(msg):
    return (rv_url.predicted(msg) or rv_emoji.predicted(msg) or is_only_symbol(msg))

def remove(msg):
    msg.content=rv_emoji.remove(rv_url.remove(msg))
    if(is_only_symbol(msg)):
        msg.content=""
    return msg
