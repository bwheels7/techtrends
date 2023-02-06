FROM python:3.10
LABEL maintainer="Brian Wheeless"

COPY . /app
WORKDIR /app

ADD . .

RUN pip install -r requirements.txt

RUN python init_db.py

EXPOSE 3111
# command to run on container start
CMD [ "python", "app.py" ]
