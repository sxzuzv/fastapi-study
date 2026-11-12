## 버전
## 참고한 화면

- 인스타그램

## 색

- 배경: 흰색 (`bg-white`)

## 글자

- 시스템 기본 글꼴, Bootstrap 기본 크기 (바꾸지 않음)

## 간격

- 카드와 카드 사이: `mb-5`

## 게시물 카드

- Bootstrap의 `card` 디자인(가는 테두리)을 그대로 사용, 배경색만 없앰
- 위에서 아래로: 글쓴이(`card-header`) → 사진 → 좋아요 버튼·좋아요 수·댓글 수 → 본문 → 올린 시각(왼쪽)과 상세 링크 `...`(오른쪽, 같은 줄) (`card-body` 안)
- 카드·헤더 배경색은 없앰 (`bg-transparent`), 카드 사이 간격은 `mb-5`
- 좋아요 버튼: 테두리 없음(`btn btn-sm`), 누르면 ♥ · 안 눌렀으면 ♡
- 상세 링크는 "자세히" 대신 굵은 `...` (`fw-bold`). 하나의 영역으로 두고 가로·세로 가운데 정렬 (`d-flex justify-content-center align-items-center px-3`)
- 페이지 제목("전체 게시물")은 화면에 보이지 않게 뺀다 (`<title>`은 그대로)

## 사진

- Bootstrap 반응형 이미지 `img-fluid`(+ `card-img-top`)로, 화면이 줄어도 카드 폭에 맞춰 사각형 그대로 크기가 변한다

## 프로필

- 위쪽 메뉴의 프로필: 사진이 있으면 50×50 둥근 모서리 사진(`rounded-circle`), 없으면 이름이 든 회색 동그라미(`rounded-circle text-bg-secondary`)

## 댓글
## 폼
## 배치

- 위쪽 메뉴: 흰색, 화면 위에 고정 (`navbar fixed-top bg-white border-bottom`)
- 본문: 가운데 좁은 폭, 최대 630px (`container page-narrow`)
- 위쪽 메뉴(로그인 후): 글 작성은 글자 대신 ⊕ 아이콘(`static/new-post.png`, `nav-icon`) → 내 프로필 → 로그아웃 버튼(`btn btn-sm btn-outline-secondary`). "님, 반갑습니다" 문구는 뺌
- 위쪽 메뉴(로그인 전): 회원가입 · 로그인 글자 링크

## 쓰지 않는 것
