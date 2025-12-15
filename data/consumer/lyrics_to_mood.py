from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import os 

load_dotenv() # .env 파일에 api key 입력 필요


# (선택) 너무 긴 가사 토큰 제한 처리
def preprocess_lyrics(lyrics: str) -> str:
    """
    GPT 입력 토큰 제한용 전처리.
    """
    if not lyrics:
        return ""

    # 혹시 모를 타입 문제 방지
    lyrics = str(lyrics)

    # tiktoken으로 토큰 기준 자르기 (한글도 상관 없음)
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(lyrics)

    if len(tokens) > 5000:
        tokens = tokens[:5000]
        return encoding.decode(tokens)

    return lyrics


def classify_song_mood(lyrics: str) -> str:
    """
    🎵 GPT-4o-mini 기반  
    '가사 → 노래 분위기' 분류 함수
    """

    lyrics = preprocess_lyrics(lyrics)


    client = OpenAI(
        api_key=os.getenv("GMS_API_KEY"),
        base_url=os.getenv("GMS_BASE_URL"),
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                "당신은 음악 분위기 분석 전문가입니다.\n"
                "사용자가 입력한 노래 가사를 분석하여, 아래 mood 리스트 중 "
                "가장 알맞은 분위기 **단 1개만 선택하여 반환하세요**.\n\n"
                "반드시 아래 mood 리스트에서만 선택하세요.\n"
                "새로운 단어를 만들어내지 마세요.\n"
                "출력은 단 하나의 단어만 반환하세요. (예: '슬픔')\n"
                "절대 설명하지 마세요. 단어만 반환하세요.\n\n"
                "Mood 선택지:\n"
                "- 밝음\n- 희망찬\n- 행복한\n- 설레는\n- 따뜻한\n- 사랑스러운\n"
                "- 잔잔한\n- 차분한\n- 감성적인\n- 여유로운\n- 위로되는\n- 포근한\n"
                "- 슬픔\n- 우울한\n- 아련한\n- 쓸쓸한\n- 외로운\n"
                "- 신나는\n- 활기찬\n- 에너지 넘치는\n- 역동적인\n- 강렬한\n"
                "- 몽환적인\n- 꿈같은\n- 서정적인\n- 영화적인\n- 드라마틱한\n"
                "- 어두운\n- 무거운\n- 긴장감 있는\n- 절망적인\n"
            )
            },
            {
                "role": "user",
                "content": lyrics
            }
        ],
        max_tokens=20,
        temperature=0.4
    )

    mood = response.choices[0].message.content.strip()
    return mood


# 테스트 실행용
if __name__ == "__main__":
    sample_lyrics = """
    널 처음 만난 순간부터
    내 마음은 너로 가득 채워져
    밤하늘 별빛처럼 반짝이는 너의 눈
    나를 숨 쉬게 해
    """

    print("가사 분석 결과:")
    mood = classify_song_mood(sample_lyrics)
    print(mood)
