FROM python:3.6-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /fejudge
WORKDIR /fejudge

EXPOSE 3013
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0", "--port=3013" ]
