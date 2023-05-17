FROM python:3.11-slim-bullseye 

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install opencv-contrib-python-headless

CMD ["python3", "src/main.py"]
