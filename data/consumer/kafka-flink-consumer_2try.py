# ERD : artist (1) ----- (N) music (N) ----- (1) genre
'''
producer.py, kafka-flink-consumer_2try.py 돌리기 전에 실행해야 할 사전 작업
순서    작업 
 1      PostgreSQL 실행 (https://lab.ssafy.com/s14/b04/de_project/-/tree/master/data-pjt?ref_type=heads)
 2      DB 생성 (music_db) 
 3      사용자 생성 (ssafyuser) 
 4      테이블 생성 (artist, genre, music, mood) 
 5      Kafka (zookeeper + broker) 실행 
 6      producer.py 실행 → Kafka에 메시지 쌓임 
 7      kafka-flink-consumer.py 실행 → DB 적재 시작 
'''

import json
import os
from typing import Optional, List

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import MapFunction
from pyflink.common import Configuration
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel, Field
from datetime import datetime
from threading import Lock
from pathlib import Path

from openai import OpenAI
from lyrics_to_mood import classify_song_mood

load_dotenv() 

# ============================================================
#  Pydantic Music 모델
# ============================================================
class Music(BaseModel):
    title: str
    artist: str
    album: str
    lyrics: str
    genre: str
    emotion_keyword: Optional[str] = None
    embedding: Optional[List[float]] = None   # 🔥 1536차원 벡터 저장용
    collected_at: datetime = Field(default_factory=datetime.now)


# ============================================================
#  Kafka → JSON → Music 객체
# ============================================================
def process_message(json_str: str) -> Music:
    try:
        data = json.loads(json_str)
        data["collected_at"] = datetime.now()
        return Music(**data)
    except Exception as e:
        print(f"[ERROR] 메시지 파싱 실패: {e}")
        return None


# ============================================================
#  중복 제거
# ============================================================
class DedupMapFunction(MapFunction):
    def __init__(self):
        self._initialized = False

    def open(self, runtime_context):
        self.seen_keys = set()
        self._initialized = True

    def map(self, m: Music) -> Optional[Music]:
        key = f"{m.title}_{m.artist}"

        if key in self.seen_keys:
            print(f"[DROP] 중복 감지 → {m.title} - {m.artist}")
            return None

        self.seen_keys.add(key)
        return m


# ============================================================
#  감정 분석 (GPT)
# ============================================================
def add_mood(m: Music) -> Music:
    mood = "UNKNOWN"
    if m.lyrics.strip():
        try:
            mood = classify_song_mood(m.lyrics).strip()
            if not mood:
                mood = "UNKNOWN"
        except Exception as e:
            print(f"[WARN] 감정 분석 실패: {m.title} | {e}")
            mood = "UNKNOWN"

    return m.model_copy(update={"emotion_keyword": mood})



# ============================================================
#  임베딩 생성 (text-embedding-3-small → 1536-dimensional)
# ============================================================

class EmbeddingMapFunction(MapFunction):
    def open(self, runtime_context):
        self.client = OpenAI(
            api_key=os.getenv("GMS_API_KEY"),
            base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1"
        )

    def map(self, m: Music) -> Music:

        text = (
            f"Title: {m.title}\n"
            f"Artist: {m.artist}\n"
            f"Album: {m.album}\n"
            f"Genre: {m.genre}\n"
            f"Mood: {m.emotion_keyword}\n"
            f"Lyrics: {m.lyrics}"
        )

        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
        except Exception as e:
            print(f"[ERROR] 임베딩 생성 실패: {m.title} | {e}")
            embedding = None

        return m.model_copy(update={"embedding": embedding})

# ============================================================
#  JSON Logging
# ============================================================


class JsonLineFileWriter(MapFunction):

    def __init__(self, log_dir: str="/home/ssafy/06-pjt/batch/data/realtime"):
        self.log_dir = log_dir
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)


    def map(self, value: Music):
        # 태스크별 고유 파일명
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.log_dir}/music_{date_str}.jsonl"
        
        json_data = value.model_dump_json(exclude={"embedding"}, ensure_ascii=False)

        # 파일 접근 동기화
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json_data + "\n")

        return value

# ============================================================
#  DB Insert
# ============================================================
class DBInsertionMapFunction(MapFunction):

    def __init__(self):
        self._initialized = False

    def _initialize(self):
        self._db_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="music_db",
            user="ssafyuser",
            password="ssafy"
        )
        self._db_conn.autocommit = True
        self._initialized = True

    def map(self, m: Music) -> Music:
        if not self._initialized:
            self._initialize()

        cursor = self._db_conn.cursor()

        # --------------------------
        # 1) ARTIST
        # --------------------------
        try:
            cursor.execute("SELECT id FROM artist WHERE artist_name = %s;", (m.artist,))
            row = cursor.fetchone()

            if row:
                artist_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO artist (artist_name) VALUES (%s) RETURNING id;",
                    (m.artist,)
                )
                artist_id = cursor.fetchone()[0]
        except Exception as e:
            print("[DB ERROR] Artist 처리 실패:", e)
            self._db_conn.rollback()
            cursor.close()
            return m

        # --------------------------
        # 2) GENRE
        # --------------------------
        try:
            cursor.execute("SELECT id FROM genre WHERE genre_name = %s;", (m.genre,))
            row = cursor.fetchone()

            if row:
                genre_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO genre (genre_name) VALUES (%s) RETURNING id;",
                    (m.genre,)
                )
                genre_id = cursor.fetchone()[0]
        except Exception as e:
            print("[DB ERROR] Genre 처리 실패:", e)
            self._db_conn.rollback()
            cursor.close()
            return m

        # --------------------------
        # 3) MOOD
        # --------------------------
        mood_id = None
        if m.emotion_keyword:
            try:
                cursor.execute(
                    """
                    INSERT INTO mood (name) 
                    VALUES (%s) 
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (m.emotion_keyword,)
                )
                cursor.execute(
                    "SELECT mood_id FROM mood WHERE name = %s;",
                    (m.emotion_keyword,)
                )
                row = cursor.fetchone()
                if row:
                    mood_id = row[0]
            except Exception as e:
                print("[DB ERROR] Mood 처리 실패:", e)
                self._db_conn.rollback()
                cursor.close()
                return m

        # --------------------------
        # 4) MUSIC + EMBEDDING
        # --------------------------
        try:
            cursor.execute(
                """
                INSERT INTO music 
                (title, album, lyrics, artist_id, genre_id, mood_id, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    m.title,
                    m.album,
                    m.lyrics,
                    artist_id,
                    genre_id,
                    mood_id,
                    m.embedding,   # 🔥 pgvector
                )
            )
            db_id = cursor.fetchone()[0]
            print(f"[OK] Saved music ID: {db_id}")

        except Exception as e:
            print("[DB ERROR] Music Insert 실패:", e)
            self._db_conn.rollback()

        cursor.close()
        return m


# ============================================================
#  MAIN — Kafka → Flink Pipeline
# ============================================================
KAFKA_TOPIC = "music_topic"
KAFKA_SERVER = "localhost:9092"


def main():
    kafka_jar_path = os.path.abspath("flink-sql-connector-kafka-3.3.0-1.19.jar")

    config = Configuration()
    config.set_string("pipeline.jars", f"file://{kafka_jar_path}")

    env = StreamExecutionEnvironment.get_execution_environment(configuration=config)
    env.set_parallelism(1)

    kafka_consumer = FlinkKafkaConsumer(
        topics=KAFKA_TOPIC,
        deserialization_schema=SimpleStringSchema(),
        properties={
            "bootstrap.servers": KAFKA_SERVER,
            "group.id": "flink-group"
        }
    )

    stream = env.add_source(kafka_consumer)

    stream = stream.map(process_message).filter(lambda x: x is not None)
    stream = stream.map(DedupMapFunction()).filter(lambda x: x is not None)
    stream = stream.map(add_mood)
    stream = stream.map(EmbeddingMapFunction())      # 🔥 임베딩 생성 단계
    stream = stream.map(JsonLineFileWriter())
    stream = stream.map(DBInsertionMapFunction())    # 🔥 DB 저장 단계

    stream.print()

    env.execute("Kafka → Flink → PostgreSQL (Music Pipeline)")


if __name__ == "__main__":
    main()
