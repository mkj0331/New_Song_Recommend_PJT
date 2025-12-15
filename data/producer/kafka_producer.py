# WSL 환경에서, zookeeper랑 kafka 켜놓고 돌려야함!
'''
✔ 5분마다 자동으로 새 데이터 크롤링
✔ BeautifulSoup로 최신 차트 파싱
✔ Kafka Producer JSON 직렬화 후 전송
✔ Flink에서 중복 제거할 수 있도록 원본 그대로 보내기
'''
from kafka import KafkaProducer
import json
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule


GENRE_MAP = {
    "nb": "발라드",
    "ndp": "댄스/팝",
    "nfa": "포크/어쿠스틱",
    "nid": "아이돌",
    "nrh": "랩/힙합",
    "nrs": "알앤비/소울",
    "nkelec": "일렉트로닉",
    "nkrock": "락/메탈",
    "nkjazz": "재즈",
    "nindie": "인디",
    "ntrot": "성인가요",
}

BASE_URL = "https://music.bugs.co.kr/newest/track/{genre_code}?page={page}"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_lyrics(track_url):
    try:
        res = requests.get(track_url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        xmp = soup.select_one("xmp")
        return xmp.text.strip() if xmp else ""
    except:
        return ""


def crawl_genre(genre_code, genre_name, max_page=2):

    titles = []
    artists = []
    albums = []
    lyrics_list = []

    for page in range(1, max_page + 1):
        url = BASE_URL.format(genre_code=genre_code, page=page)
        print(f"[{genre_name}] page={page} 수집 중 → {url}")

        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            print(f"❌ 페이지 접근 실패: {url}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        for p in soup.select("p.title"):
            a = p.select_one("a[title]")
            if a:
                titles.append(a.get("title").strip())

        for p in soup.select("p.artist"):
            a = p.select_one("a[title]")
            if a:
                artists.append(a.get("title").strip())

        for a in soup.select("a.album[title]"):
            albums.append(a.get("title").strip())

        track_urls = [a.get("href") for a in soup.select("a.trackInfo[href]")]

        for t_url in track_urls:
            lyrics_list.append(get_lyrics(t_url))
            time.sleep(0.2)

        time.sleep(0.3)


    min_len = min(len(titles), len(artists), len(albums), len(lyrics_list))

    df = pd.DataFrame({
        "title": titles[:min_len],
        "artist": artists[:min_len],
        "album": albums[:min_len],
        "lyrics": lyrics_list[:min_len],
        "genre": [genre_name] * min_len
    })
    return df


# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    acks="all"
)

TOPIC_NAME = 'music_topic'


def send_to_kafka(df):
    for idx, row in df.iterrows():
        
        if not row["lyrics"].strip():
            continue
        
        msg = {
            "title": row["title"],
            "artist": row["artist"],
            "album": row["album"],
            "lyrics": row["lyrics"],
            "genre": row["genre"],
        }

        producer.send(
            TOPIC_NAME,
            key=f"{row['title']}_{row['artist']}".encode('utf-8'),
            value=msg
        )

        print(f"[Kafka 전송 완료] {row['title']} - {row['artist']}")
        time.sleep(0.1)

    producer.flush()
    print("\n=== 모든 메시지 Kafka 전송 완료 ===")


def job():
    print("\n===============================")
    print("🔥 새로운 데이터 수집 & Kafka 전송 시작")
    print("===============================\n")

    all_dfs = []
    for genre_code, genre_name in GENRE_MAP.items():
        df_genre = crawl_genre(genre_code, genre_name, max_page=2)
        all_dfs.append(df_genre)

    final_df = pd.concat(all_dfs, ignore_index=True)
    send_to_kafka(final_df)

    print("\n===== 1회 작업 완료, 다음 실행까지 대기 =====\n")


schedule.every(5).minutes.do(job)

print("=== Kafka Producer 실행 시작 (5분마다 자동 실행) ===")

job()

while True:
    schedule.run_pending()
    time.sleep(1)
