#作成するdockerイメージの指定
FROM python:3.12-slim

# 作業スペースの指定
WORKDIR /root

# 必要なファイルをコピー
# pythonで用いるライブラリを描いたテキストファイル
COPY pyLibrary.txt .

RUN apt-get update -y

RUN pip install --no-cache-dir --upgrade pip

RUN apt-get install -y ffmpeg

RUN apt-get install -y libopus-dev

RUN pip install --break-system-packages -r pyLibrary.txt

# fugashiの辞書ファイルを置くための空のファイルを作成。多分どっちかでいいが、どちらになってるか特定するのもめんどい
RUN mkdir -p /usr/local/etc && touch /usr/local/etc/mecabrc
RUN mkdir -p /etc && touch /etc/mecabrc

RUN apt-get clean

WORKDIR /root/src
# CMD ["python3","rvvot.py"]

# pythonコマンドでpython3.12を呼び出せるようにする
# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12