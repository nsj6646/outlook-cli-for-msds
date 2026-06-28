# 이슈 02: 메일 서명 자동 삽입 (Mail Signature)

Status: resolved

## What to build

메일 본문 맨 하단(제품 표 아래)에 HTML 형식의 서명을 자동 병합하여 삽입합니다.
프로그램 실행 시 `--signature` 옵션으로 서명 파일 경로를 지정할 수 있게 하고, 명시하지 않은 경우에는 현재 작업 경로 내의 `signature.html` 파일을 자동으로 탐색합니다.
만약 서명 파일이 존재하면 UTF-8로 해당 파일 내용을 읽어와 맑은 고딕 폰트 랩핑 직전에 메일 본문 뒤에 덧붙이고, 파일이 존재하지 않는다면 에러를 내지 않고 서명 없이 메일을 조립합니다.

## Acceptance criteria

- [ ] CLI 옵션으로 `--signature` 또는 `-s` (기존의 subject가 s를 점유하고 있으므로 `--sig`나 다른 축약어 검토 또는 `--signature` 전용) 경로를 수용할 수 있게 확장한다.
- [ ] 서명 파일 경로가 지정되었거나 현재 경로에 `signature.html`이 존재하면, 파일 내 HTML 코드를 읽어 메일 본문 맨 하단(제품 표 아래)에 덧붙인다.
- [ ] 서명 파일이 아예 발견되지 않더라도 예외가 터지지 않고 경고 로그만 남기며 서명 없이 조립한다.
- [ ] 조립 완료된 최종 메일 본문(MailJob.body)에서 서명 HTML 문자열이 정상적으로 검출되는지 단위 테스트로 검증한다.

## Blocked by

None - can start immediately
