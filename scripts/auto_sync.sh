#!/bin/bash
# 자료가 바뀌었으면 위키·대시보드를 다시 빌드하고 커밋 후 GitHub에 push한다.
# Claude Code Stop 훅(.claude/settings.json)에서 매 응답이 끝날 때 실행된다. 직접 실행해도 된다.
#
# - inbox/ 는 원본 메모·카톡 대화라 자동으로 올리지 않는다.
# - 비밀번호·인증번호·주민번호·계좌번호로 보이는 내용이 있으면 커밋하지 않고 멈춘다.
# - 출력은 Claude Code가 화면에 보여주는 JSON 한 줄({"systemMessage": ...})이다.

cd "$(dirname "$0")/.." || exit 0
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

say() { python3 -c 'import json,sys; print(json.dumps({"systemMessage": sys.argv[1]}, ensure_ascii=False))' "$1"; }

[ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "main" ] || exit 0
[ -e .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] && exit 0

EXCLUDE=(':!inbox' ':!.claude/settings.local.json')
changed=$(git status --porcelain -- . "${EXCLUDE[@]}" | sed -E 's/^...//; s/^"//; s/"$//')
[ -z "$changed" ] && exit 0

# 원본이 바뀐 쪽만 다시 빌드 (빌드 스크립트가 첫 화면 메뉴도 갱신)
log=$(mktemp)
if echo "$changed" | grep -qE '^(wiki/|scripts/build_wiki\.py|scripts/build_home\.py)'; then
  python3 scripts/build_wiki.py >>"$log" 2>&1 || { say "자동 동기화 중단: 위키 빌드 실패 ($(tail -1 "$log"))"; rm -f "$log"; exit 0; }
fi
if echo "$changed" | grep -qE '^(data/|scripts/dashboards/|scripts/build_dashboards\.py)'; then
  python3 scripts/build_dashboards.py >>"$log" 2>&1 || { say "자동 동기화 중단: 대시보드 빌드 실패 ($(tail -1 "$log"))"; rm -f "$log"; exit 0; }
fi
rm -f "$log"

git add -A -- . "${EXCLUDE[@]}"
git diff --cached --quiet && exit 0

# 민감정보 검사: 새로 추가되는 줄만 본다
hits=$(git diff --cached -U0 --no-color -- . ':!*.html' ':!*.xlsx' | grep -E '^\+[^+]' | grep -nE \
  '비밀번호[[:space:]]*[:=：][[:space:]]*[^[:space:]]|[Pp]assword[[:space:]]*[:=][[:space:]]*[^[:space:]]|인증번호[[:space:]]*[:=：]?[[:space:]]*[0-9]{4,8}|[0-9]{6}-[1-4][0-9]{6}|계좌(번호)?[[:space:]]*[:=：]?[[:space:]]*[0-9][0-9-]{7,}' | head -3)
if [ -n "$hits" ]; then
  git reset -q
  say "자동 동기화 중단: 비밀번호·인증번호·주민번호·계좌번호로 보이는 내용이 있어 커밋하지 않았습니다. 해당 내용을 지운 뒤 다시 시도하세요."
  exit 0
fi

areas=$(git diff --cached --name-only | awk -F/ '{print $1}' | sort -u | tr '\n' ' ' | sed 's/ $//')
count=$(git diff --cached --name-only | wc -l | tr -d ' ')
if [ -n "$AUTO_SYNC_DRY_RUN" ]; then  # 시험용: 커밋·push 없이 결과만 보여줌
  git reset -q; say "시험 실행: ${count}개 파일 커밋 예정 (${areas})"; exit 0
fi
git commit -q -m "자동 동기화: ${areas} (${count}개 파일, $(date '+%Y-%m-%d %H:%M'))" || { say "자동 동기화: 커밋 실패"; exit 0; }

if out=$(git push -q origin main 2>&1); then
  say "자동 동기화 완료: ${count}개 파일 커밋 후 GitHub에 push했습니다 (${areas})."
else
  say "자동 동기화: 커밋은 했지만 push 실패 — $(echo "$out" | tail -1)"
fi
exit 0
