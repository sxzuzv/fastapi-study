# insta-api

지난주에 만든 insta를 화면 없이 JSON만 주고받는 API로 다시 만듭니다. 화면은 JavaScript와 React로 따로 만들고, 이 API를 불러서 씁니다.

테이블(`users`, `posts`, `comments`, `likes`)과 더미 데이터는 이미 들어 있습니다.

## 시작하기

### 1. 내 저장소 만들기

1. 이 저장소 오른쪽 위의 **Use this template** → **Create a new repository**를 누릅니다.
2. 저장소 이름은 `insta-api`, 공개 범위는 **Private**으로 만듭니다.

### 2. 내려받기

```bash
git clone https://github.com/내아이디/insta-api.git
cd insta-api
code .
```

VS Code 터미널에서 패키지를 설치합니다.

```bash
uv sync
```

### 3. DB 만들기

```bash
psql -d postgres     # macOS
psql -U postgres     # Windows
```

```sql
CREATE DATABASE insta_api OWNER sd4;
\q
```

### 4. 테이블과 더미 데이터

```bash
uv run alembic upgrade head
uv run python seed.py
```

`시드 완료: 사용자 3 · 글 4 · 댓글 3 · 좋아요 3`이 나오면 됩니다. 사용자는 `alice`, `bob`, `carol`이고 비밀번호는 모두 `pw1234`입니다. `seed.py`는 다시 돌리면 처음 상태로 돌아갑니다.

### 5. 실행하기

```bash
uv run fastapi dev
```

## 폴더 구조

```
insta-api/
├── main.py          # 앱 · 라우터 붙이는 곳
├── database.py      # DB 주소 · engine · Base
├── models.py        # 테이블 넷
├── deps.py          # SessionDep · 비밀번호 해시
├── seed.py          # 더미 데이터
├── routers/         # 주소 파일을 여기에
└── alembic/         # 테이블 리비전
```
