FROM python:3.11.9-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY src/ /app/src/
COPY templates/ /app/templates/
COPY app.py /app/
COPY InspectionHandler.py /app/
COPY config/ /app/config/
COPY .env /app/

EXPOSE 3000

CMD [ "python", "app.py"]