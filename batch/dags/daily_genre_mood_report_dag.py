# docker-compose.yaml 키고 localhost:8080에서 connection 만들어서 실행하기

import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_genre_mood_report_dag',
    default_args=default_args,
    description='장르별 감정 Top5 리포트를 매일 생성',
    schedule_interval='0 1 * * *',  # 매일 새벽 1시
    start_date=datetime(2025, 5, 1, tzinfo=local_tz),
    catchup=False,
    tags=['daily', 'report', 'spark', 'mood-trend']
) as dag:

    spark_daily_genre_mood = SparkSubmitOperator(
        task_id='spark_daily_genre_mood',
        application='/opt/airflow/dags/scripts/spark_daily_genre_mood.py',
        conn_id='spark_default',
        conf={
            "spark.master": "spark://spark-master:7077"
        },
        application_args=['--date', '{{ ds }}'],
    )


    notify = BashOperator(
        task_id='notify_report_generated',
        bash_command='echo "음악 감정 리포트 생성 완료"'
    )

    spark_daily_genre_mood >> notify
