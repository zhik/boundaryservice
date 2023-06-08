FROM python:3.8.17-slim

WORKDIR /app

RUN apt update
RUN apt-get install -y libgdal-dev gcc postgresql-client python3-dev --no-install-recommends && \
    apt-get clean -y

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

COPY . /app

CMD /wait & python app.py