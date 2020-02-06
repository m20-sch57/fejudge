FROM python:3.6-alpine

RUN adduser -D fejudge
WORKDIR /home/fejudge

COPY app app
COPY avatars avatars
COPY libsbox libsbox
COPY migrations migrations
COPY problems problems
COPY submissions submissions
COPY common.py config.py invoker.py run.py ./

RUN chown -R fejudge:fejudge ./

EXPOSE 3013
ENTRYPOINT ["python3", "run.py"]
