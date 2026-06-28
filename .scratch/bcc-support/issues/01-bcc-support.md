# 이슈 01: 비밀참조(Bcc) 일괄 발송 기능 통합 구현

Status: resolved

## What to build

엑셀 명단의 `Recipients` 시트에서 `Bcc` 컬럼 데이터를 로딩하여 개별 메일의 비밀참조 대상으로 매핑하고, 아웃룩으로 메일을 일괄 조립하여 임시 보관함(또는 발송) 저장 시 `mail.BCC` 프로퍼티에 안전하게 대입하는 기능을 종단(End-to-End)으로 통합 구현합니다.
엑셀 파싱 단계에서 `Bcc` 컬럼이 누락되어 있더라도 에러를 발생시키지 않도록 하위 호환성을 제공해야 하며, 세미콜론 `;` 으로 구분된 다중 수신자를 올바르게 아웃룩에 결합해 줍니다.

## Acceptance criteria

- [ ] `ExcelParser`가 `Recipients` 시트에서 `Bcc` 컬럼이 존재할 경우 값을 성공적으로 추출하여 반환한다. (컬럼 누락 시 빈 문자열 처리 및 정상 구동 유지)
- [ ] `MailDistributionContext.load_jobs()` 수행 결과인 `MailJob` 개체에 `bcc` 속성이 추가되고, 파싱된 이메일 값이 온전히 정제된 문자열로 이식된다.
- [ ] `OutlookMailService`의 메일 작성 로직에서 주입받은 `MailJob.bcc` 값이 있는 경우 `mail.BCC = job.bcc` 구문을 통해 아웃룩 본체로 비밀참조를 전달한다.
- [ ] `tests/test_distribution.py`에 Bcc 로딩 및 매핑 결과를 단언 검증하는 통합 단위 테스트를 구현해 100% 그린 패스를 달성한다.

## Blocked by

None - can start immediately
