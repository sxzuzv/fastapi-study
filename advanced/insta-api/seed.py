# 더미 데이터 — 다시 돌리면 처음 상태로 돌아간다
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import engine
from models import User, Post, Comment, Like
from deps import password_hash


with Session(engine) as db:
  # 테이블을 비우고 번호(id)도 1부터 다시
  db.execute(text('TRUNCATE likes, comments, posts, users RESTART IDENTITY'))

  alice = User(username='alice', password_hash=password_hash.hash('pw1234'))
  bob = User(username='bob', password_hash=password_hash.hash('pw1234'))
  carol = User(username='carol', password_hash=password_hash.hash('pw1234'))
  db.add_all([alice, bob, carol])
  db.flush()

  # 글마다 쓴 시각을 다르게 — 최신순이 보이도록
  now = datetime.now()
  p1 = Post(content='안녕하세요 저는 햄입니당', user_id=alice.id, created_at=now - timedelta(hours=3))
  p2 = Post(content='오늘 점심은 김치찌개', user_id=bob.id, created_at=now - timedelta(hours=2))
  p3 = Post(content='FastAPI 공부 중', user_id=alice.id, created_at=now - timedelta(hours=1))
  p4 = Post(content='주말에 한강 갈 사람?', user_id=carol.id, created_at=now)
  db.add_all([p1, p2, p3, p4])
  db.flush()

  db.add_all([
    Comment(content='여기 어디예요?', post_id=p1.id, user_id=bob.id),
    Comment(content='저도 가 보고 싶어요', post_id=p1.id, user_id=carol.id),
    Comment(content='맛있겠다', post_id=p2.id, user_id=alice.id),
    Like(user_id=bob.id, post_id=p1.id),
    Like(user_id=carol.id, post_id=p1.id),
    Like(user_id=alice.id, post_id=p2.id),
  ])
  db.commit()

print('시드 완료: 사용자 3 · 글 4 · 댓글 3 · 좋아요 3 (비밀번호 모두 pw1234)')