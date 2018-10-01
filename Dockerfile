FROM python:3.6-alpine

RUN adduser -D dockerflaskblog

WORKDIR /home/dockerflaskblog

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY flaskblogengine flaskblogengine
COPY run_blog_engine.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run_blog_engine.py

RUN chown -R flaskblogengine:flaskblogengine ./
USER dockerflaskblog

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
