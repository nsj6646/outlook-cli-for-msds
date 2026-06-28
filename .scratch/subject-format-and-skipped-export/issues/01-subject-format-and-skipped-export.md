# 이슈 01: 제목 포맷 다변화 및 실패(스킵) 건 재송용 엑셀 자동 추출 통합 구현

Status: resolved

## What to build

엑셀 `Recipients` 시트에서 신설할 `Company` 및 `Contact` 컬럼 데이터를 로딩하여 메일 제목("Subject - Company")과 본문 최상단("수신: Company Contact님")을 동적 조립하고, 정보 누락 시 해당 수신인은 스킵합니다.
동시에 대량 메일 발송 사이클 중 단 1건이라도 스킵이 발생하면 완료 시점에 현재 디렉토리에 스킵된 수신 정보와 매핑 제품 데이터만 발라낸 `[원본파일명]_skipped_[YYYYMMDD_HHMMSS].xlsx` 파일을 자동 생성해 주는 기능까지 종단(End-to-End)으로 통합 구현합니다.

## Acceptance criteria

- [ ] `ExcelParser`가 `Recipients` 시트에서 `Company` 및 `Contact` 컬럼을 수집하여 메타데이터에 적재한다.
- [ ] `Company` 또는 `Contact` 컬럼이 비어있거나 누락된 수신처 행은 `MailJob` 변환 대기열에서 스킵(제외)하며 경고 이력을 감사 로그에 남긴다.
- [ ] 변환 성공한 메일은 제목이 `Subject` + `" - "` + `Company` 로 조립되고, 본문 최상단에 `"수신: Company Contact님<br><br>"` 문구가 자동 삽입된다.
- [ ] 일괄 배포 구동 중 스킵된 건이 존재할 경우, 프로그램 마감 시점에 `[원본파일명]_skipped_[YYYYMMDD_HHMMSS].xlsx` 파일을 엑셀 포맷으로 자동 생성한다. 이 파일은 `Recipients` 및 `TableData` 시트 레이아웃을 그대로 유지하며, 스킵된 해당 수신인의 데이터 행과 그가 취급하는 제품 데이터 행만 걸러내어 저장한다.
- [ ] 단위 테스트를 통해 스킵 재송용 엑셀 추출이 원본과 동일한 두 시트 구조로 필터링되어 원만하게 생성되는지 보증한다.

## Blocked by

None - can start immediately
