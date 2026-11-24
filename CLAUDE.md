# 업무허브 운영 규칙

이 폴더는 사용자의 개인 업무허브다. 업무 정보를 모아 wiki/에 쌓고,
할 일을 tasks/todo.md에 관리하고, data/의 데이터를 대시보드로 만든다.
폴더 구조와 상세 흐름은 업무허브_가이드.md를 따른다.

## 절대 규칙
- 비밀번호, 인증번호, 주민번호, 계좌번호는 어디에도 저장하지 않는다. 발견하면 저장하지 않고 사용자에게 알린다.
- 위키의 기존 기록 줄은 삭제하지 않는다. 새 정보는 날짜와 출처를 붙여 추가한다.
- 출력 HTML에는 외부 자원(CDN, 웹폰트, 외부 스크립트)을 쓰지 않는다.
- inbox 파일은 처리 후 inbox/processed/YYYY-MM-DD/로 옮긴다. 삭제하지 않는다.
- 나챗방 메시지는 한 통에 200자 이내로 쓴다.

## 분류 기준
- accounts: 시스템, 사이트, 계정, 접속 방법
- work: 업무 절차, 처리 방법, 규정
- people: 사람, 부서, 담당 업무
- terms: 용어, 약어
- projects: 진행 중인 일 단위
- journal: 날짜별 일지 (그날 처리한 내용 요약)
- 애매하면 가장 가까운 분류에 넣고, 관련 페이지에 [[링크]]를 건다.

## 명령어
- "정리해줘": 흐름 A 실행
- "브리핑 보내줘": 흐름 A 실행 후 흐름 B 실행
- "위키 빌드": python3 scripts/build_wiki.py 실행
- "대시보드 갱신": python3 scripts/build_dashboards.py 실행 (scripts/dashboards/*.py 전부 실행 후 index.html 갱신)
- "할 일 완료: <내용>": tasks/todo.md에서 해당 항목을 완료로 옮김
- "할 일 추가: <내용>": tasks/todo.md 진행 중에 마감·출처(직접 입력)·우선순위를 붙여 추가

## 연결된 도구
- Gmail 커넥터: 흐름 A에서 메일 읽기. 메일을 보내거나 답장하지 않는다.
- PlayMCP 카카오톡 나챗방(KakaotalkChat-MemoChat): 흐름 B 브리핑 발송 전용.
- gh CLI(~/.local/bin/gh, LillyPark99 로그인): 커밋·push (저장소 LillyPark99/LillyWorkspace1). GitHub Pages: https://lillypark99.github.io/LillyWorkspace1/
- Google Calendar 커넥터(연결되어 있을 때만): 흐름 B의 "다가오는 일정"에 오늘~7일 일정을 넣는다. 일정을 만들거나 바꾸지 않는다.
- Google Drive 커넥터(연결되어 있을 때만): 사용자가 요청하면 파일을 data/raw/로 가져와 대시보드에 쓴다.
- Slack 커넥터(연결되어 있을 때만): 흐름 A에서 마지막 처리 시점 이후 메시지를 읽는다.

## 실행 환경
- Mac, Python 3.9.6 (`python3`). 스크립트는 3.9에서 돌아가게 작성한다 (`match`문, `X | Y` 타입 힌트 금지).
- 이 폴더(클로드 프로젝트1)가 가이드의 `업무허브/` 폴더다.

## 자동 동기화
- 응답이 끝날 때마다 Stop 훅(.claude/settings.json)이 scripts/auto_sync.sh를 실행한다: 바뀐 자료가 있으면 위키·대시보드를 다시 빌드하고 커밋 후 GitHub(LillyWorkspace1, 공개 저장소)에 push한다.
- inbox/는 자동으로 올리지 않는다. 민감정보로 보이는 내용이 있으면 커밋하지 않고 멈춘다.

## 저장소
- 이 폴더는 GitHub LillyPark99/LillyWorkspace1 (공개 저장소)에 연결되어 있다. push한 내용은 누구나 볼 수 있다.
- 공부 노트(중국어·일본어·영어)는 여기 두지 않는다. 별도 폴더 ~/Desktop/공부위키 (저장소 Lilly1, 공개)에서 관리한다.
