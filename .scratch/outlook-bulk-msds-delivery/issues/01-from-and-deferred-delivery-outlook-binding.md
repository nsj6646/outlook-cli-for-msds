# 이슈 01: Recipients 시트 From 계정 및 DeferredTime 파싱과 아웃룩 연동

Status: ready-for-agent

## Parent

- [PRD.md](../PRD.md)

## What to build

엑셀 데이터 소스로부터 각 수신인별 발신용 이메일 주소와 예약 발송 일시(배달 지연) 정보를 추출하여, 아웃룩의 동적 발신 계정(`SendUsingAccount`) 및 예약 발송 속성(`DeferredDeliveryTime`)에 안전하게 바인딩하는 엔드투엔드 파이프라인을 구축합니다.
예약 일시가 주어질 경우 적절한 날짜/시간 포맷으로 변환하거나 타입 보정을 수행하고, 아웃룩 기본 계정이 아닌 계정으로 메일 작성 시 발생할 수 있는 보안 검증 충돌(ValueError 등)을 회피할 수 있는 우회 예외 처리 로직을 구현합니다.

## Acceptance criteria

- [ ] `ExcelParser`가 `Recipients` 시트에서 `From` 및 `DeferredTime`(한글 컬럼명 '예약시간' 등 포함) 헤더를 정상 감지하고 데이터를 추출함.
- [ ] 수신인 정보 중 예약 발송 시간이 유효할 경우, Outlook MailItem 객체의 `DeferredDeliveryTime` 속성에 정상 기입되어 아웃룩 메일 예약 기능이 세팅됨.
- [ ] 수신인 정보 중 `From` 계정이 명시되었을 경우, 아웃룩 프로필 내 해당 주소의 발신 계정을 식별하여 `SendUsingAccount` 속성에 정상 매핑됨.
- [ ] 발신 계정이 아웃룩 기본 계정과 다른 경우에도 오류로 인해 강제 중단되지 않고 메일 작성이 끝날 수 있도록 처리 플래그 지원.

## Blocked by

None - can start immediately
