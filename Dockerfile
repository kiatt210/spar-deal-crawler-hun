FROM python:slim-buster

WORKDIR /usr/src/app

RUN apt-get -y update
RUN apt-get -y upgrade
                       
RUN apt-get install -y gcc libffi-dev python3-dev musl-dev cargo
RUN apt-get install -y apt-utils libssl-dev

RUN python3 -m pip install --upgrade pip
ADD requirements.txt .
RUN apt-get install -y python3-lxml libxml2-dev libxslt-dev python-dev
RUN apt-get install -y libjpeg-dev zlib1g-dev g++ qpdf libqpdf-dev 

RUN apt-get -y install wget unzip cmake
RUN wget https://github.com/qpdf/qpdf/archive/refs/tags/release-qpdf-10.6.3.zip
RUN unzip release-qpdf-10.6.3.zip
WORKDIR /usr/src/app/qpdf-release-qpdf-10.6.3

RUN ./configure
RUN make
RUN make install

WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install webdriver_manager

RUN apt-get install -y chromium-driver


ADD main.py .

ENTRYPOINT  ["python3",  "main.py"]
