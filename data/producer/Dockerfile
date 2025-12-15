FROM python:3.11-slim

WORKDIR /data_producer

COPY requirements.txt /data_producer/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /data_producer/

# 수집용 파이썬 실행 파일
CMD ["python", "kafka_producer.py"]