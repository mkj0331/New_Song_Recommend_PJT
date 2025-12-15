FROM python:3.10-slim

WORKDIR /django-backend

# Python 의존성 복사 및 설치
COPY requirements.txt /django-backend/

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 복사
COPY . /django-backend/

# 환경변수 셋팅은 compose에서 할 수 있음

# 서버 시작 커맨드 (마이그레이트 후 서버 실행, 필요시 수정)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]