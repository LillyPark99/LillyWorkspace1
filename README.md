# 업무허브

흩어진 업무 정보(메모, 카톡, 메일)를 폴더 하나에 모으고, Claude가 위키와 할 일로 정리해 매일 아침 카톡 나챗방으로 브리핑을 보내는 개인 업무 시스템입니다. 만드는 방법 전체는 [업무허브_가이드.md](업무허브_가이드.md)에 있습니다.

> 지금 들어 있는 위키·할 일·판매 데이터는 실습용 **가상 데이터**입니다. 이 저장소는 공개 저장소라 누구나 볼 수 있습니다.

## 바로 보기

| 무엇 | 링크 (GitHub Pages를 켜면 열림) |
|---|---|
| 첫 화면 (위키·대시보드 메뉴) | https://lillypark99.github.io/LillyWorkspace1/ |
| 업무 위키 | https://lillypark99.github.io/LillyWorkspace1/output/wiki.html |
| 대시보드 목록 | https://lillypark99.github.io/LillyWorkspace1/output/dashboards/index.html |

## 무엇이 있나

| 기능 | 하는 일 | 결과물 |
|---|---|---|
| 업무 위키 | 메모·카톡·메일에서 업무 정보를 뽑아 주제별 페이지에 쌓음 | `wiki/*.md` → `output/wiki.html` |
| AI 비서 | 할 일·마감을 뽑아 평일 09:00에 카톡 나챗방으로 2통 발송 | `tasks/todo.md`, `logs/briefing/` |
| 대시보드 | `data/raw/`의 엑셀·CSV를 차트와 표로 | `output/dashboards/*.html` |

모든 HTML은 외부 자원 없이 파일 하나로 열립니다(인터넷 없이 동작).

## 폴더

```
CLAUDE.md          Claude 운영 규칙
inbox/             정리할 자료를 넣는 곳 (memo/, kakao/) → 처리 후 processed/날짜/
wiki/              업무 지식 원본 (accounts, work, people, terms, projects, journal)
tasks/todo.md      할 일 목록
data/raw/          엑셀·CSV 원본 (data/README.md에 목록)
scripts/           build_wiki.py, build_dashboards.py, build_home.py, auto_sync.sh
output/            만들어진 HTML (언제든 다시 생성 가능)
logs/briefing/     보낸 브리핑 기록
index.html         첫 화면 (build_home.py가 생성)
```

## Claude에게 이렇게 말하기

| 상황 | 말 |
|---|---|
| inbox에 메모·카톡 파일을 넣었을 때 | 정리해줘 |
| 바로 브리핑 받고 싶을 때 | 브리핑 보내줘 |
| 할 일을 끝냈을 때 | 할 일 완료: 주간보고 작성 |
| 할 일을 추가할 때 | 할 일 추가: 금요일까지 견적서 회신 |
| 데이터를 넣거나 바꿨을 때 | data/raw에 파일 넣었어, 대시보드 만들어줘 / 대시보드 갱신 |
| 정보를 찾을 때 | ○○ 관련해서 위키에 뭐 있어? |

## 자동으로 돌아가는 것

- **아침 브리핑**: Claude 데스크탑 앱 예약 작업 `morning-briefing`, 평일 09:00. 정리 → 나챗방 2통 → 로그 저장. Mac과 Claude 앱이 켜져 있어야 돕니다.
- **자동 동기화**: Claude 응답이 끝날 때마다 `scripts/auto_sync.sh`가 바뀐 자료를 다시 빌드하고 커밋·push합니다. `inbox/`는 올리지 않고, 비밀번호·주민번호 같은 내용이 보이면 멈춥니다.

## 연결된 도구

| 도구 | 용도 | 상태 |
|---|---|---|
| Gmail 커넥터 | 메일 읽기 (정리 단계) | 연결됨 |
| PlayMCP 카카오톡 나챗방 | 브리핑 발송 (한 통 200자 이내) | 연결됨 |
| GitHub (`gh` CLI) | 커밋·push, Pages 배포 | 로그인됨 |
| Google Calendar 커넥터 | 브리핑에 실제 일정 넣기 | 추천 (연결하면 자동 사용) |
| Google Drive 커넥터 | 공유드라이브 양식·매출 파일 가져오기 | 선택 |
| Slack 커넥터 | 메신저 내용 정리 | 선택 (워크스페이스가 있을 때) |

## 실행 환경

- Mac, Python 3.9.6 (`python3`), 패키지: markdown, pandas, openpyxl, plotly
- 수동 빌드: `python3 scripts/build_wiki.py`, `python3 scripts/build_dashboards.py`

## 지금까지 한 일 (2026-11-24)

1. Step 0~1: 환경 점검, 폴더 뼈대와 CLAUDE.md
2. Step 2: 예시 메모 5개·카톡 대화·Gmail로 정리 기능 시연 → 위키 13페이지, 할 일 10건
3. Step 3: 오프라인 위키 HTML (검색, `[[링크]]`, 분류별 목록)
4. Step 4~5: 나챗방 브리핑 발송 테스트, 평일 09:00 예약 작업 등록
5. Step 6: 가상 판매 데이터(444행)와 plotly 대시보드
6. GitHub 저장소 연결, Pages 배포, 첫 화면 메뉴, 중국어 공부 노트 추가, 자동 동기화
7. Step 7(컴퓨터 유즈로 카톡 내보내기)은 컴퓨터 유즈가 꺼져 있어 보류
