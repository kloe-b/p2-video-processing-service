FROM python:3.9

WORKDIR /app

COPY ./../../video-processing-service/requirements.txt .

COPY ./../../video-processing-service/src ./src

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "./src/app.py"]