FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  && apt-get install -y build-essential \
  && apt-get install -y libpq-dev \
  && apt-get install -y gettext \
  && apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./compose/local/start /start
RUN chmod +x start

COPY . /app

WORKDIR /app