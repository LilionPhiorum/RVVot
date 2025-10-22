import re

"""predict URL"""
patternURL = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[-\w./?%&=]*)')

"""check including URL"""
def predicted(msg):
    return patternURL.search(msg.content)

"""remove URL from message"""
def remove(msg):
    msg.content=patternURL.sub("",msg.content)
    return msg