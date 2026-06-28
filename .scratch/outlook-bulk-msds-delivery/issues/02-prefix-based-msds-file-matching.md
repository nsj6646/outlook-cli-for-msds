# 이슈 02: 취급 제품코드 접두사(Prefix) 매칭 MSDS 파일 자동 다중 첨부

Status: ready-for-agent

## Parent

- [PRD.md](../PRD.md)

## What to build

각 수신인이 취급하는 제품의 `제품코드` 목록을 확인하여, 지정한 로컬 디렉토리 내에 존재하는 파일들 중 파일명 시작 부분이 해당 제품코드와 완벽히 일치하는(대소문자 무관 접두사 비교) MSDS 파일들을 탐색하여 메일 작성 시 다중 첨부하는 파일 시스템 스캐너 및 자동 매핑 알고리즘을 개발합니다.
실무자가 파일 경로를 직접 입력하지 않고 디렉토리에 파일만 추가하면 메일에 연계 첨부되도록 처리하며, 폴더를 읽지 못하거나 비어 있을 때 경고 로그를 출력하되 전체 메일 발송 프로세스는 중단되지 않도록 탄력적으로 구성합니다.

## Acceptance criteria

- [ ] 수신인별 취급 제품코드(`TableData` 시트에서 이메일 매핑 데이터 활용)를 정상 스캔함.
- [ ] 파일 검색 디렉토리(예: `attachments/` 또는 `MSDS/`) 내에서 제품코드 문자열로 시작하는 파일(예: `제품코드_MSDS.pdf`, `제품코드-v2.pdf` 등)들을 누락 없이 수집함.
- [ ] 수집된 로컬 절대 경로 파일 리스트를 아웃룩 MailItem의 `Attachments.Add` 컬럼에 안전하게 다중 추가함.
- [ ] 지정된 디렉토리가 없거나 조회가 실패했을 때 적절한 예외 메시지를 로그로 남김.

## Blocked by

- [01-from-and-deferred-delivery-outlook-binding.md](./01-from-and-deferred-delivery-outlook-binding.md)
