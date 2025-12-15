import sys
import argparse
import os
import shutil
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, to_timestamp
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def main(report_date_str):
    print(f"보고서 기준 날짜: {report_date_str}")

    # 디렉터리 설정
    INPUT_PATH   = "/opt/airflow/data/realtime/*.jsonl"
    REALTIME_DIR = "/opt/airflow/data/realtime"
    ARCHIVE_DIR  = "/opt/airflow/data/music_archive"
    REPORT_DIR   = "/opt/airflow/data/reports"


    # Spark Session
    spark = SparkSession.builder \
            .appName("DailyGenreMoodReport") \
            .getOrCreate()

    # 날짜 계산
    report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
    start_date = report_date - timedelta(days=1)
    end_date = report_date

    ## 테스트용 날짜 범위 
    # start_date = report_date
    # end_date = report_date + timedelta(days=1)

    # JSON 데이터 읽기
    df = spark.read.json(INPUT_PATH)

    # 날짜 필터링
    df = df.withColumn("collected_at_ts",to_timestamp(col("collected_at")))
    df = df.filter((col("collected_at_ts") >= start_date) & (col("collected_at_ts") < end_date))

    if df.rdd.isEmpty():
        print("지정된 날짜 범위에 해당하는 음악 데이터가 없습니다.")
        spark.stop()
        sys.exit(0)

    # genre, emotion_keyword 별 count 집계
    genre_mood_count = (
        df.groupBy("genre", "emotion_keyword")
          .agg(count("*").alias("count"))
          .orderBy(col("genre"), col("count").desc())
    )

    # Pandas로 변환할 top5 데이터 준비
    # 장르별로 Top5 감정 키워드를 pandas에서 구분하려면 window 없이도 해결 가능
    # NOTE: 일 단위 집계 데이터이므로 Pandas 변환 허용
    genre_mood_pd = genre_mood_count.toPandas()

    # 장르 목록
    genres = genre_mood_pd["genre"].unique()

    # PDF 그래프 생성
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_file = os.path.join(REPORT_DIR, f"genre_mood_report_{report_date.strftime('%Y%m%d')}.pdf")

    # 폰트 설정 (나눔고딕)
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    font_prop = fm.FontProperties(fname=font_path, size=12)

    # 장르별 그래프 생성
    from matplotlib.backends.backend_pdf import PdfPages
    pdf = PdfPages(report_file)

    for genre in genres:
        genre_df = (genre_mood_pd[genre_mood_pd["genre"] == genre].sort_values("count", ascending=False).head(5))

        plt.figure(figsize=(10, 6))
        plt.bar(genre_df["emotion_keyword"], genre_df["count"], color="skyblue")
        plt.xlabel("감정 (emotion_keyword)", fontproperties=font_prop)
        plt.ylabel("등장 횟수", fontproperties=font_prop)
        plt.title(f"{genre} 장르 - 감정 Top5", fontproperties=font_prop)
        plt.xticks(rotation=45, fontproperties=font_prop)
        plt.tight_layout()

        pdf.savefig()
        plt.close()

    pdf.close()

    print(f"리포트 생성 완료 → {report_file}")

    spark.stop()

    # 원본 JSON 파일 archive 이동 (보고서 기준 날짜 -1일 파일만 이동)
    try:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)

        files = os.listdir(REALTIME_DIR)
        if not files:
            print(f"{REALTIME_DIR} 디렉터리에 이동할 파일이 없습니다.")
        else:
            target_date_str = (report_date - timedelta(days=1)).strftime("%Y-%m-%d")
            
            ## 테스트용 아카이브 이동 날짜 
            # target_date_str = report_date.strftime("%Y-%m-%d")

            for file in files:
                # 예: music_2025-12-11.jsonl
                if target_date_str in file:
                    src = os.path.join(REALTIME_DIR, file)
                    dst = os.path.join(ARCHIVE_DIR, file)
                    shutil.move(src, dst)
                    print(f"{src} → {dst} 이동 완료")

    except Exception as e:
        print("파일 이동 중 오류 발생:", e)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="장르별 감정 Top5 리포트 생성 Spark Job")
    parser.add_argument("--date", required=True, help="보고서 기준 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()

    main(args.date)
