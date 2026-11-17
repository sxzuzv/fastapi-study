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
- 이 카드 레이아웃은 바꾸지 않고 유지한다 (`list.html` 기준)
- 위에서 아래로: 글쓴이 — 40×40 동그란 프로필 사진(없으면 이름이 든 회색 동그라미)과 이름 링크(`card-header`) → 사진 → 좋아요 버튼·좋아요 수·댓글 수 → 본문 → 올린 시각(왼쪽)과 상세 링크 `...`(오른쪽, 같은 줄) (`card-body` 안)
- 카드·헤더 배경색은 없앰 (`bg-transparent`), 카드 사이 간격은 `mb-5`
- 좋아요 버튼: 테두리 없음(`btn btn-sm`), 누르면 ♥ · 안 눌렀으면 ♡
- 상세 링크는 "자세히" 대신 굵은 `...` (`fw-bold`). 하나의 영역으로 두고 가로·세로 가운데 정렬 (`d-flex justify-content-center align-items-center px-3`)
- 페이지 제목("전체 게시물")은 화면에 보이지 않게 뺀다 (`<title>`은 그대로)

## 게시글 상세

- 목록의 게시물 카드와 같은 모양의 카드를 쓴다 (`card mb-5 bg-transparent`, 헤더도 `bg-transparent`)
- 위에서 아래로: 글쓴이(40×40 동그란 프로필 사진 또는 이름 첫 글자가 든 회색 동그라미 + 이름 링크, `card-header`) → 사진(있을 때만) → 본문 → 올린 시각 (`card-body`, 시각은 `text-body-secondary`)
- 목록 카드의 상세 링크 `...`는 상세 화면에 없다. 대신 글쓴이 본인에게만 헤더 오른쪽 끝에 `...` 버튼을 보여 주고, 누르면 드롭다운 메뉴가 열린다 (`dropdown ms-auto`, 메뉴는 `dropdown-menu-end`)
- 드롭다운 메뉴: 아이콘 + 글자 — 수정하기(가위 아이콘) · 삭제하기(휴지통 아이콘, 글자 빨강 `text-danger`)
- 40×40 크기는 `static/style.css`의 `avatar-40` 클래스로 준다
- 댓글 영역은 아직 꾸미지 않았다 (아래 "댓글" 항목에서 이어서 정한다)

## 사진

- Bootstrap 반응형 이미지 `img-fluid`(+ `card-img-top`)로, 화면이 줄어도 카드 폭에 맞춰 사각형 그대로 크기가 변한다
- 상세 화면의 사진도 같은 방식

## 프로필

- 위쪽 메뉴의 프로필: 사진이 있으면 50×50 둥근 모서리 사진(`rounded-circle`), 없으면 이름 첫 글자가 든 회색 동그라미(`rounded-circle text-bg-secondary`)
- 상세 화면 글쓴이의 프로필도 같은 규칙 (사진 없으면 이름 첫 글자)

## 댓글
## 폼
## 배치

- 위쪽 메뉴: 흰색, 화면 위에 고정 (`navbar fixed-top bg-white border-bottom`)
- 본문: 가운데 좁은 폭, 최대 630px (`container page-narrow`)
- 위쪽 메뉴(로그인 후): 글 작성은 글자 대신 ⊕ 아이콘(`static/new-post.png`, `nav-icon`) → 내 프로필 → 로그아웃 버튼(`btn btn-sm btn-outline-secondary`). "님, 반갑습니다" 문구는 뺌
- 위쪽 메뉴(로그인 전): 회원가입 · 로그인 글자 링크

## 쓰지 않는 것
