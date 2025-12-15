FROM python:3.11-slim

WORKDIR /data_consumer

COPY requirements.txt /data_consumer/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /data_consumer/

# 수집용 파이썬 실행 파일
CMD ["python", "kafka_flink_consumer_2try.py"]