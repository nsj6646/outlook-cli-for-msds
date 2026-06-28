# Project: Web UI Removal and Architecture Refactoring

## Architecture
본 프로젝트는 불필요한 웹 UI 관련 코드 및 리소스를 프로젝트에서 완전히 격리(삭제)하고, 수립된 리팩토링 지침(`REFACTORING.md`)과 감사 결과(`refactor_audit_report.md`)에 근거하여 책임을 분리하고 결합도를 제거하는 리팩토링을 수행합니다.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | 구현 계획 승인 | 상세 구현 계획을 수립하여 사용자에게 승인 요청 및 대기 | None | DONE |
| M2 | R1 웹 UI 리소스 완전 제거 | app.py, 프론트엔드 리소스, 웹 핸들러, local_storage.py 및 test_web.py 물리적 삭제 및 FileStorage 인터페이스 제거 | M1 | DONE |
| M3 | R2.1 DIP 및 추상화 정제 | MailService 시그니처에서 CLI/인프라 매개변수(force_sender, is_interactive) 제거 및 OutlookMailService 내부 CLI 상호작용 제거 | M1 | DONE |
| M4 | R2.2 SRP 단일 책임 분리 | outlook_cli.py 내 ExcelParser, HtmlTableRenderer, TemplateEngine 클래스 정의 및 로직 격리 | M3 | DONE |
| M5 | 통합 E2E 및 테스트 검증 | test_syntax.py, test_cli.py 실행 및 실제 대량 발송 명령 검증을 통한 A1, A2 인수 조건 충족 확인 | M2, M4 | DONE (Outlook COM E2E 생략) |
| M6 | 최종 완료 보고 | 모든 검증 완료 후 Sentinel에게 작업 완료(Milestones complete) 보고 | M5 | DONE |

## Interface Contracts
- **MailService ↔ OutlookMailService**: `send_mail` 메서드는 인프라 및 CLI 종속 매개변수(`force_sender`, `is_interactive`) 없이 순수 메일 발송 파라미터만 가집니다.
- **Presentation ↔ Infrastructure**: `force_sender` 바인딩은 `OutlookMailService` 생성 시점에 주입받으며, 계정 불일치 시 예외를 발생시키고 이를 상위 프레젠테이션 계층(`outlook_cli.py`)에서 잡아서 처리합니다.
- **outlook_cli.py 내 구조 분리**: `ExcelParser`, `HtmlTableRenderer`, `TemplateEngine` 간의 입력 및 출력 데이터는 원시 타입 또는 표준 Python 컬렉션(dict, list)으로만 연동하여 모듈 간 결합도를 낮춥니다.
