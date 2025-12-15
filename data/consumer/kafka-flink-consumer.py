import json
import os

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import MapFunction
from pyflink.common import Configuration

import psycopg2
from pydantic import BaseModel, Field
from typing import Optional

from lyrics_to_mood import classify_song_mood


class Music(BaseModel):
    """입력받은 음악 데이터를 위한 Pydantic 모델"""
    title: str = Field(description="노래 제목")
    artist: str = Field(description="가수")
    album: str = Field(description="앨범 제목")
    lyrics: str = Field(description="가사")
    genre: str = Field(description="장르")
    emotion_keyword: Optional[int] = Field(default=None, description="감정 키워드")


def process_message(json_str: str) -> Music:
    try:
        data = json.loads(json_str)
        return Music(**data)
    except Exception as e:
        print(f"메시지 파싱 오류: {e}")
        # 오류 발생 시 기본값으로 빈 기사 반환
        return Music(
            title="오류 발생",
            artist="",
            album="",
            lyrics="",
            genre=""
        )
    

def add_mood(music_data: Music) -> Music:
    mood = classify_song_mood(music_data.lyrics)
    return music_data.model_copy(update={"emotion_keyword": mood})


class DBInsertionMapFunction(MapFunction):
    def __init__(self):
        # lazy initialization 플래그
        self._initialized = False

    def _initialize(self):
        """
        DB 연결을 초기화합니다.
        이 메서드는 워커에서 최초 호출 시 한 번 실행됩니다.
        """
        # PostgreSQL DB 연결
        self._db_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="music",              # 데이터베이스 이름
            user="ssafyuser",            # 사용자명
            password="ssafy"     # 비밀번호
        )
        self._db_conn.autocommit = True

        self.genre_pk = {
            "발라드": 1,
            "댄스/팝": 2,
            "포크/어쿠스틱": 3,
            "아이돌": 4,
            "랩/힙합": 5,
            "알앤비/소울": 6,
            "일렉트로닉": 7,
            "락/메탈": 8,
            "재즈": 9,
            "인디": 10,
            "성인가요": 11,
        }

        self._initialized = True

    def map(self, music_data: Music) -> Music:
        if not self._initialized:
            self._initialize()

        # DB 연결 생성
        cursor = self._db_conn.cursor()
        db_id = None
        
        # 장르
        if music_data.genre in self.genre_pk:
            genre_num = self.genre_pk[music_data.genre]
        else:
            genre_num = 0

        # artist 조회 및 없으면 새로 생성하는 구문
        try:
            cursor.execute("""SELECT id FROM artist WHERE artist_name = %s;""", (music_data.artist,))
            result = cursor.fetchone()
            if result:
                artist_id = result[0]
            else:
                cursor.execute("""
                    INSERT INTO artist (artist_name) VALUES (%s) RETURNING id;
                """, (music_data.artist,))
                artist_id = cursor.fetchone()[0]
            print(f"Successfully loaded artist pk from Postgresql, id: {artist_id}")
        except Exception as e:
            print("DB read error:", e)

        # 음악 데이터 저장 파트
        try:
            cursor.execute("""
                INSERT INTO music (title, artist, album, lyrics, genre)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                music_data.title,
                music_data.artist,
                music_data.album,
                music_data.lyrics,
                genre_num
            ))
            result = cursor.fetchone()
            db_id = result[0] if result else None
            print(f"Successfully saved article to Postgresql, id: {db_id}")
        except Exception as e:
            print("DB insertion error:", e)
        finally:
            cursor.close()

        return music_data


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
        properties={'bootstrap.servers': KAFKA_SERVER,
                        'group.id': 'flink-group'}
    )

    data_stream = env.add_source(kafka_consumer)

    processed_stream = data_stream.map(process_message)

    # processed_stream = processed_stream.map(add_mood)

    processed_stream = processed_stream.map(DBInsertionMapFunction())

    processed_stream.print()

    env.execute("Kafka Music Data Processing")


if __name__ == "__main__":
    main()