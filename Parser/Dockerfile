FROM ubuntu:22.04
RUN apt-get update
RUN apt-get -y install python3.11
RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip
RUN apt-get -y install fontconfig 

RUN apt-get -y install wget
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar xjf phantomjs-2.1.1-linux-x86_64.tar.bz2

RUN ln -s /phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/share/phantomjs
RUN ln -s /phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs
RUN ln -s /phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin/phantomjs
ENV OPENSSL_CONF /dev/null

RUN pip3 install --upgrade pip
RUN pip3 install pika==1.3.2
RUN pip3 install beautifulsoup4==4.12.3
RUN pip3 install lxml==5.2.1
RUN pip3 install requests==2.31.0
RUN pip3 install -U selenium==3.3.0

COPY ./app /app
WORKDIR /app

EXPOSE 5680
ENTRYPOINT ["python3", "app.py"]