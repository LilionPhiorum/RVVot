#作成するdockerイメージの指定
FROM ubuntu:24.04

#環境変数の指定
#最新のubuntuにおいては，pip install の際に --break-system-packages オプションをつけないといけない
#それを解消する環境変数の指定
ENV PIP_BREAK_SYSTEM_PACKAGES=1

#作業スペースの指定
WORKDIR /root

#必要なファイルをコピー
#pythonで用いるライブラリを描いたテキストファイル
COPY pyLibrary.txt .

RUN apt-get update -y

RUN apt-get install -y\
    python3.12\
    python3-pip

RUN pip install --break-system-packages -r pyLibrary.txt

RUN apt-get install -y ffmpeg

RUN apt-get install -y libopus-dev

# fugashiの辞書ファイルを置くための空のファイルを作成。多分どっちかでいいが、どちらになってるか特定するのもめんどい
RUN mkdir -p /usr/local/etc && touch /usr/local/etc/mecabrc
RUN mkdir -p /etc && touch /etc/mecabrc

RUN apt-get clean

WORKDIR /root/src
CMD ["python3","rvvot.py"]

#pythonコマンドでpython3.12を呼び出せるようにする
# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1