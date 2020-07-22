FROM python:3.6-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /fejudge
WORKDIR /fejudge

EXPOSE 3113
ENTRYPOINT [ "python3", "run.py" ]
