FROM --platform=linux/amd64 python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG CHROME_VER='110.0.5481.30'

RUN cat /etc/os-release
RUN uname -m
RUN pip install --no-cache-dir --upgrade pip
# install google chrome
RUN apt update
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get -y install ./google-chrome-stable_current_amd64.deb
RUN apt-get -f install
  
# install chromedriver
RUN wget https://chromedriver.storage.googleapis.com/110.0.5481.30/chromedriver_linux64.zip
RUN apt-get install -yqq unzip
RUN unzip chromedriver_linux64.zip chromedriver -d /app/
RUN pip install webdriver-manager

# this version is dependant on chrome driver
RUN apt-get install -y libnss3=2:3.61-1+deb11u2
RUN python3 --version
RUN pip3 --version

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

EXPOSE 8080

ENTRYPOINT [ "python" ]

CMD ["simple_web_scraper.py"]

