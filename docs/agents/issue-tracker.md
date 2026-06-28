# 이슈 트래커: 로컬 마크다운 (Local Markdown)

이 저장소의 이슈와 PRD는 `.scratch/` 폴더 밑에 마크다운 파일로 저장됩니다.

## 규칙 (Conventions)

- 피처(Feature)당 하나의 디렉토리: `.scratch/<feature-slug>/`
- PRD 파일 경로: `.scratch/<feature-slug>/PRD.md`
- 구현 이슈 파일 경로: `.scratch/<feature-slug>/issues/<NN>-<slug>.md` (번호는 `01`부터 시작)
- 트리아지 상태는 각 이슈 파일의 상단 근처에 `Status:` 라인으로 기록됩니다 (역할 문자열은 `triage-labels.md` 참고)
- 의견 및 대화 기록은 파일 하단의 `## Comments` 제목 아래에 추가됩니다.

## 스킬이 "이슈 트래커에 게시(publish to the issue tracker)"하라고 할 때

`.scratch/<feature-slug>/` 폴더 아래에 새 파일을 만듭니다 (필요한 경우 디렉토리 생성).

## 스킬이 "관련 티켓 가져오기(fetch the relevant ticket)"라고 할 때

참조된 경로의 파일을 읽습니다. 일반적으로 사용자가 경로 또는 이슈 번호를 직접 전달합니다.
