FROM python:3.9

WORKDIR /app

COPY ./../../video-processing-service/requirements.txt .

COPY ./../../video-processing-service/src ./src

COPY ./../../video-processing-service/src/processing ./src/processing

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "./src/processing/converter_worker.py"]