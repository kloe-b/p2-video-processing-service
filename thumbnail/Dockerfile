FROM python:3.9

WORKDIR /app

COPY ./requirements.txt .

COPY ./thumbnail_worker.py .

RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip install -r requirements.txt


CMD ["python", "thumbnail_worker.py"]