FROM python:3.6-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /fejudge/invoker
WORKDIR /fejudge/invoker

ENTRYPOINT [ "python3", "invoker.py" ]
