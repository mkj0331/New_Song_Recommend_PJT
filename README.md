# 🎵 신곡 취향저격 음악 추천 데이터 엔지니어링 프로젝트

> 본 프로젝트는 실시간으로 수집되는 음악 데이터를 바탕으로 사용자의 취향에 맞는 새로운 음악을 추천하기 위한 데이터 파이프라인을 구축하고, 그 결과를 서비스하는 것을 목표로 합니다.
>
> 데이터의 수집, 처리, 분석, 그리고 서비스까지 전 과정에 걸친 데이터 엔지니어링 기술 스택을 종합적으로 활용합니다. 웹(Backend, Frontend)은 구축된 데이터 파이프라인의 최종 결과를 시각화하고 사용자와 상호작용하는 창구 역할을 합니다.

<br>

## 🚀 QuickStart

> ⚠️ **Note:** 본 프로젝트는 다양한 서비스로 구성되어 있어 Docker Compose를 통한 전체 환경 실행을 권장합니다. 현재 `docker-compose.yaml` 설정은 계속해서 개선되고 있습니다.

### Start using Docker

*   [Docker](https://www.docker.com/get-started) 설치
*   [Docker Compose](https://docs.docker.com/compose/install/) 설치

#### 설치 및 실행

1.  **Repository를 복제합니다.**
    ```bash
    git clone [Repository URL]
    cd [프로젝트 폴더]
    ```

2.  **환경 변수 파일을 설정합니다.**
    프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, `docker-compose.yaml`에서 참조하는 환경 변수(`GMS_API_KEY` 등)를 추가합니다.
    ```env
    # .env
    GMS_API_KEY=your_api_key_here
    GMS_BASE_URL=your_base_url_here
    ```

3.  **Docker Compose를 사용하여 모든 서비스를 빌드하고 실행합니다.**
    ```bash
    docker-compose up --build -d
    ```

#### 서비스 접속

*   **Frontend**: `http://localhost:5173`
*   **Backend API**: `http://localhost:8000`
*   **Elasticsearch**: `http://localhost:9200`
*   **PostgreSQL DB**: `localhost:5432`

### Start Locally

> ⚠️ **Note:** 이 섹션은 Docker 없이 개별 서비스를 로컬 환경에서 구동하는 방법을 안내합니다. 데이터 파이프라인 컴포넌트의 유기적인 연동 테스트에는 Docker 사용을 강력히 권장합니다.

#### Prerequisites
*   Python 3.10+
*   Node.js 20+
*   Docker & Docker Compose
*   **실행 중인** 로컬 PostgreSQL, Kafka, Flink 클러스터

---

#### 1. Backend (Django)

Django API 서버를 실행합니다.

```bash
# backend 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate
# (Windows: .\\venv\\Scripts\\activate)

# 필요 패키지 설치
pip install -r requirements.txt

# (필요시) .env 파일에 데이터베이스 접속 정보 설정
# 예: POSTGRES_HOST=localhost

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```
> ✅ 실행 후, `http://127.0.0.1:8000/` 에서 API 서버가 실행됩니다.

<br>

#### 2. Frontend (Vue.js)

Vue.js 프론트엔드 개발 서버를 실행합니다.

```bash
# (새 터미널에서) frontend 디렉토리로 이동
cd frontend

# 의존성 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```
> ✅ 실행 후, 터미널에 나타나는 주소 (기본: `http://localhost:5173`) 에서 프론트엔드 화면을 확인할 수 있습니다.

<br>

#### 3. Data Producer (Kafka)

데이터를 수집하여 Kafka로 전송하는 Producer 스크립트를 실행합니다.

```bash
# (새 터미널에서) data/producer 디렉토리로 이동
cd data/producer

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate
# (Windows: .\\venv\\Scripts\\activate)

# 필요 패키지 설치
pip install -r requirements.txt

# (필요시) .env 파일 등에 카프카 접속 정보 설정
# 예: KAFKA_BOOTSTRAP_SERVERS='localhost:9092'

# 프로듀서 스크립트 실행
python kafka_producer.py
```

<br>

#### 4. Data Consumer (Flink)

Kafka로부터 데이터를 받아 처리하는 Flink Consumer 스크립트를 실행합니다.

```bash
# (새 터미널에서) data/consumer 디렉토리로 이동
cd data/consumer

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate
# (Windows: .\\venv\\Scripts\\activate)

# 필요 패키지 설치
pip install -r requirements.txt

# (필요시) .env 파일 등에 카프카, DB 접속 정보 설정

# 컨슈머 스크립트 실행
python kafka-flink-consumer.py
```

#### 5. Elasticsearch 동기화 (Logstash)
> Logstash 파이프라인을 테스트하기 위한 독립 환경을 실행합니다. 이 환경은 자체 PostgreSQL, Elasticsearch, Kibana를 포함합니다.

1.  **Logstash 관련 Docker Compose 실행**
    ```bash
    cd data/migration
    docker-compose -f docker-compose-logstash.yml up -d
    ```

2.  **Elasticsearch 인덱스 생성**
    `music_index.json` 파일에 정의된 매핑으로 인덱스를 생성합니다.
    ```bash
    curl -X PUT "http://localhost:9200/music_index" \
      -H "Content-Type: application/json" \
      -d @data/migration/music_index.json
    ```

3.  **동기화 확인 (선택 사항)**
    `search_test.py` 스크립트로 데이터 동기화 상태를 확인할 수 있습니다.

> ✅ 실행 후 Kibana UI는 `http://localhost:5601`에서 접속할 수 있습니다.

---

#### 6. 배치 처리 환경 구성 (Airflow & Spark)
> 일괄 데이터 처리를 위한 Airflow와 Spark 클러스터를 실행합니다.

1.  **Docker 네트워크 생성 (최초 1회)**
    ```bash
    docker network create airflow
    ```

2.  **.env 파일 생성**
    `data/batch` 디렉토리로 이동하여 Airflow의 파일 소유권 설정을 위한 `.env` 파일을 생성합니다.
    ```bash
    cd data/batch
    echo "AIRFLOW_UID=1000" > .env
    ```

3.  **Airflow & Spark 관련 Docker Compose 실행**
    ```bash
    # (data/batch 디렉토리에서 실행)
    docker-compose -f docker-compose_Airflow_Spark.yaml up -d
    ```

4.  **Airflow UI에서 Spark Connection 설정**
    *   `http://localhost:8080` 로 접속 (ID/PW: `airflow`/`airflow`).
    *   `Admin` > `Connections` 메뉴로 이동하여 우측 상단의 `+` 버튼을 클릭해 새 연결을 추가합니다.
    *   **Connection Id**: `spark_default`
    *   **Connection Type**: `Spark`
    *   **Host**: `spark://spark-master`
    *   **Port**: `7077`
    *   `Save` 버튼을 눌러 저장합니다.

> ✅ 실행 후 Airflow UI는 `http://localhost:8080`, Spark UI는 `http://localhost:8083`에서 접속할 수 있습니다.

---

#### 7. HDFS 구성 (Hadoop)
> Spark 배치 처리 결과 등을 저장하기 위한 Hadoop HDFS를 실행합니다.

1.  **Hadoop 관련 Docker Compose 실행**
    ```bash
    cd data/hadoop
    docker-compose -f docker-compose_hadoop.yml up -d
    ```

2.  **HDFS 디렉토리 생성 및 권한 설정**
    `namenode` 컨테이너에 접속하여 DAG에서 사용할 경로를 미리 생성합니다.
    ```bash
    docker exec -it namenode bash
    ```
    컨테이너 내부에서 아래 명령어를 실행합니다.
    ```bash
    hdfs dfs -mkdir -p /user/music_archive
    hdfs dfs -chmod -R 777 /user/music_archive
    exit
    ```

---

#### 8. 배치 DAG 실행 및 검증
> 모든 환경 구성 후, Airflow UI에서 실제 배치 작업을 실행하고 결과를 확인합니다.

1.  **Airflow UI에서 DAG 실행**
    `http://localhost:8080` 로 접속하여 `daily_genre_mood_report_dag`를 찾아 활성화하고, 수동으로 실행합니다.

2.  **결과 검증**
    DAG 실행이 성공적으로 완료되면, 아래 방법으로 결과를 확인할 수 있습니다.
    *   **HDFS 적재 확인**: `namenode` 컨테이너에 다시 접속하여 아래 명령어를 실행합니다.
        ```bash
        # docker exec -it namenode bash
        hdfs dfs -ls /user/music_archive/
        ```
    *   **리포트 파일 확인**: `data/batch/reports` 디렉토리에 PDF 리포트 파일이 생성되었는지 확인합니다.

## 🏛️ 아키텍처

> 데이터 파이프라인의 전체 흐름은 다음과 같습니다.

```
[Producer] --(Kafka)--> [Consumer (Flink)] --+--> [PostgreSQL] <--+-- [Backend (Django)] <-- [Frontend]
                                            |                     |                            ^
                                            |                     +----(Logstash)-----> [Elasticsearch] --+
                                            |
                                            +--> [JSONL Files] --> [Batch (Airflow/Spark)]
```

<br>

## ✨ 데이터 파이프라인 상세

1.  **데이터 수집 (Producer)**
    *   Python을 사용하여 외부 음원 사이트에서 신곡 정보, 차트, 가사 등의 데이터를 크롤링합니다.
    *   수집된 데이터는 정제 후 실시간 처리를 위해 Kafka 토픽으로 전송(Produce)됩니다.

2.  **실시간 처리 (Consumer)**
    *   Apache Flink를 사용하여 Kafka 토픽의 데이터를 실시간으로 소비(Consume)합니다.
    *   소비된 데이터는 가사 분석을 통한 감정 분류 등의 스트림 처리 과정을 거칩니다.
    *   처리된 데이터는 최종적으로 메인 데이터베이스인 **PostgreSQL**에 저장됩니다.
    *   동시에, 처리된 데이터는 후속 배치 처리를 위해 **JSONL 파일** 형태로도 저장됩니다.

3.  **데이터 검색/인덱싱 (Search & Indexing)**
    *   **Logstash** 파이프라인(`logstash.conf`)이 1분 간격으로 실행되며 RDB와 검색 엔진 간의 데이터를 동기화합니다.
    *   PostgreSQL의 `music_search_view`를 `updated_at` 타임스탬프 기준으로 조회하여 변경된 데이터만 선택적으로 읽어옵니다. (증분 업데이트)
    *   읽어온 데이터를 **Elasticsearch**의 `music_index`로 인덱싱하여, 제목, 아티스트, 가사 등에 대한 강력하고 빠른 전문(Full-text) 검색 기능을 구현합니다.

4.  **배치 처리 (Batch Processing)**
    *   **Apache Airflow**가 `daily_genre_mood_report_dag.py`에 정의된 스케줄에 따라 매일 새벽 1시에 배치 파이프라인을 실행합니다.
    *   이 파이프라인은 Hadoop 클러스터 위에서 동작하는 **Apache Spark** 작업을 트리거합니다. (`spark_daily_genre_mood_hdfs.py`)
    *   Spark는 Consumer가 생성한 **JSONL 파일**를 분산 처리하여 '장르별 감정 Top 5'와 같은 통계 리포트를 생성합니다. 이는 실시간으로 계산하기 어려운 복잡한 분석을 효율적으로 수행하기 위함입니다.
    *   생성된 리포트 및 분석이 완료된 데이터는 **HDFS**에 저장되어 추후 과거 리포트 및 데이터 필요시 HDFS에서 가져올 수 있도록 구성되어 있습니다.

5.  **서비스 및 시각화**
    *   **Django(Backend)**는 PostgreSQL과 Elasticsearch의 데이터를 사용하여 추천 로직을 수행하고 API를 제공합니다.
    *   **Vue.js(Frontend)**는 백엔드 API를 호출하여 사용자에게 추천 음악을 보여주고, 상호작용을 제공합니다.

<br>

## ⚙️ 기술 스택

| 구분             | 기술 스택                               | 역할                               |
| ---------------- | --------------------------------------- | ---------------------------------- |
| **Data Ingestion**   | Python, Kafka                           | 데이터 크롤링 및 메시지 큐 발행    |
| **Real-time Proc** | Flink, Kafka                            | 실시간 데이터 스트림 처리 및 저장  |
| **Batch Proc**     | Airflow, Spark                          | 주기적 대용량 데이터 배치 처리     |
| **Search**         | Elasticsearch, Logstash                 | 데이터 인덱싱 및 검색 엔진         |
| **Database**       | PostgreSQL (pgvector)                   | 메인 데이터 저장소                 |
| **Backend**        | Django, Django REST framework           | API 서버 및 추천 로직 수행         |
| **Frontend**       | Vue.js, Vite                            | 데이터 시각화 및 사용자 인터페이스 |
| **Infrastructure** | Docker, Docker Compose                  | 전체 서비스 컨테이너화 및 오케스트레이션 |

<br>
