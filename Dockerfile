FROM --platform=linux/amd64 python:3.11

# Avoid pyc files that we do not need as program is built and run repeatadly from the same image
ENV PYTHONDONTWRITEBYTECODE=1
# Unbuffer the output so we always get logging
ENV PYTHONUNBUFFERED=1

ARG CHROME_VER='110.0.5481.30'

# Print the OS version for debug in two different ways
RUN cat /etc/os-release
RUN uname -m

# Install latest verision of pip
RUN pip install --no-cache-dir --upgrade pip

# install google chrome
RUN apt update
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get -y install ./google-chrome-stable_current_amd64.deb
RUN apt-get -f install
  
# install chromedriver
RUN wget https://chromedriver.storage.googleapis.com/${CHROME_VER}/chromedriver_linux64.zip
RUN apt-get install -yqq unzip
RUN unzip chromedriver_linux64.zip chromedriver -d /app/
RUN pip install webdriver-manager

# libnss3 required for chromedriver
RUN apt-get install -y libnss3

# Check our version are correct
RUN python3 --version
RUN pip3 --version

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

# For debugging the container
EXPOSE 8080

ENTRYPOINT [ "python" ]

CMD ["simple_web_scraper.py"]