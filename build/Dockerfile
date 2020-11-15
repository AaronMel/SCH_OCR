FROM ubuntu:18.04


RUN apt-get update 
RUN apt-get install  python3 -y python3-pip -y


ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# tesseract-ocr
RUN apt-get install tesseract-ocr -y
RUN apt-get install tesseract-ocr-ces -y
RUN apt-get install tesseract-ocr-deu -y

# enchant
RUN apt-get install enchant -y
RUN apt-get install -y myspell-cs-cz
RUN apt-get install -y myspell-de-de

RUN apt-get clean 
RUN apt-get autoremove


ADD . /home/App
WORKDIR /home/App


COPY pip3install.conf .
RUN pip3 install -r pip3install.conf

COPY src/ .
VOLUME ["/data"]


CMD ["python3","app.py"]
