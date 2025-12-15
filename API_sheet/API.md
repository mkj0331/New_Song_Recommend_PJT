# API SHEET
## 데이터베이스 구성도
음악(순위 포함)   
```
PK: int, Primary Key   
music_name: varchar(50), required   
genre: int, Foreign Key references Genre   
artist: int, Foreign key references Singer   
lyrics: text   
created_at: datetime   
updated_at: datetime   
(순위: int)   
```
   
가수   
```
PK: int, Primary Key   
singer_name: varchar(50), required   
debut_date: datetime   
```
   
장르   
```
PK: int, Primary Key   
name: varchar(30), required   
```
   
분위기 <- 이걸 이제 어떻게 하느냐인데 <- AI 모델에 맡긴다!   
```
PK: int, Primary_key   
name: varchar(50), required   
```

로그   
```
pk: int, primary key   
account_pk: int, foreign key references accounts   
music_pk: int, foreign key references music   
time: int   
created_at: datetime   
updated_at: datetime   
```
   
플레이리스트   
```
pk: int, primary key   
name: varchar(100), required   
account_pk: int, foreign key   
created_at: datetime   
updated_at: datetime
ended_time: int
```
   
음악 <-> 분위기   
```
pk: int, primary key   
music_pk: int, foreign key   
mood_pk: int, foreign key   
confidence_score: float   
```
   
플레이리스트 <-> 음악   
```
pk: int, primary key   
playlist_pk: int, foreign key   
music_pk: int, foreign key   
created_at: datetime
```
   
좋아요   
```
pk: int, primary key   
music_pk: int, foreign key   
account_pk: int, foreign key   
liked_at: datetime   
```
   
## API 접근   
1. 전체 곡 리스트 접근(시간 순) (GET)   
입력: 없음   
출력:   
```json
[{
  song_name: str,
  song_pk: int,
  artist_pk: int,
  artist: str
},]
```
   
2. 개별 곡에 대한 데이터 접근(상세 데이터 보기 위함) (GET)   
입력:   
`{music_pk: int}`   
출력:   
```json
{
  song_name: str,
  genre_pk: int,
  genre: str,
  artist_pk: int,
  artist: str,
  lyrics: str,
  mood_pk: int,
  mood: str,
  n_likes: int,
  liked: bool
}
```

3. 분류별 곡 리스트 접근(시간 순) (GET)   
입력:
```json   
{
  artist_pk(optional): int,
  genre_pk(optional): int,
  mood_pk(optional): int
}   
```
출력:   
```json
[{
  song_name: str,
  song_pk: int,
  artist_pk: int,
  artist: str
},]
```

4. 좋아요 기록 (PUT)   
입력:   
`{music_pk: int}`   
출력:   
```json
{result: str}
```

5. 플레이리스트 생성 및 삭제 (POST, DELETE)   
입력:   
`{playlist_name: str}`   
출력:   
`{result: str}`   

6. 플레이리스트 조회 (GET)   
입력:
```json
{
  playlist(optional): str,
  author(optional): str
}
```
출력:
```json
[{
  playlist_name: str,
  playlist_pk: int,
  author: str,
  author_pk: int,
  first_music: str,
  first_artist: str
},]
```

7. 플레이리스트에 음악 등록 및 삭제 (POST, DELETE)   
입력:   
`{playlist_pk: int, music_pk: int}`   
출력:   
`{result: str}`

8. 플레이리스트 내 음악 리스트(GET)
입력:   
`{playlist_pk: int}`
출력:
```json
[{
  song_name: str,
  song_pk: int,
  artist_pk: int,
  artist: str
},]
```

9. 자신이 좋아요를 기록한 곡 조회 (GET)
입력: 없음   
출력:
```json
[{
  song_name: str,
  song_pk: int,
  artist_pk: int,
  artist: str
},]
```

10. 자신이 최근에 들었던 곡 조회 (GET)
입력: 없음   
출력:
```json
[{
  music_name: str,
  music_pk: int,
  artist_pk: int,
  artist: str
},]
```

11. 음악 플레이 엔드포인트 (GET) <- 더미 엔드포인트. 음악을 받아서 보여줄 수 있으면 그 때 구현 예정

12. 음악 로그 생성 (POST, PATCH)
입력:   
`{current_time: int}`   
출력:   
`{result: str}`


## 미래 계획
1. 실시간 데이터: 음악 순위 및 신곡 추적
2. 검색: 각 키워드별로 음악을 검색할 수 있도록 제공
3. 챗봇: 챗봇을 이용한 음악 추천 시스템