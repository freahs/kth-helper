FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y \
    curl unzip gnupg xvfb

RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list \
 && curl -O https://dl.google.com/linux/linux_signing_key.pub \
 && apt-key add linux_signing_key.pub \
 && apt-get update && apt-get install -y google-chrome-stable

RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
 && curl -O https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
 && unzip chromedriver_linux64.zip -d /usr/bin \
 && chmod +x /usr/bin/chromedriver

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME
COPY ./app .
RUN pip install -r requirements.txt

CMD ["python", "kth_helper.py"]
