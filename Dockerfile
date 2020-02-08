FROM python:3.6-buster

COPY . /fejudge
WORKDIR /fejudge

RUN pip3 install -r requirements.txt

EXPOSE 3013
ENTRYPOINT ["python3", "run.py"]
