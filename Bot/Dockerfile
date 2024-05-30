FROM python:3.11.2-alpine3.17
RUN pip3 install --upgrade pip
RUN pip3 install pika==1.3.2
RUN pip3 install pyTelegramBotAPI==4.17.0
RUN pip3 install aiohttp==3.9.5

COPY ./app /app
WORKDIR /app
EXPOSE 5680
ENTRYPOINT ["python3", "app.py"]