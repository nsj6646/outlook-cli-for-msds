# Original User Request

## 2026-06-17T15:22:13Z

# SW 아키텍처 기반 리팩토링 지침(REFACTORING.md) 작성 및 코드 품질 감사 서브에이전트 가동 프로젝트

본 프로젝트는 현재 구현된 소프트웨어 아키텍처의 품질을 유지하고 미래의 리팩토링 과정에서 오버엔지니어링을 철저히 차단할 수 있도록 극도로 간결한 지침서를 작성하고, 이를 바탕으로 코드 품질을 상시 검사해 주는 감사 전용 서브에이전트를 구축 및 검증하는 것을 목표로 합니다.

Working directory: C:\Users\seungjoo.na\Documents\antigravity\clever-darwin
Integrity mode: demo

---

## Requirements

### R1. 리팩토링 지침서 (REFACTORING.md) 작성
- 현재 SW 아키텍처 기반 하에 SOLD 원칙을 준수하는 리팩토링 지침을 작성합니다.
- **텍스트 크기 제약**: 전체 라인 수가 **50줄 이내(<= 50 lines)**여야 합니다.
- **필수 포함 항목**:
  1. 리팩토링 전/후 프로그램 기능 동작 유지 (기능 차이 방지)
  2. 오버엔지니어링 금지 (최소 구현 원칙)
  3. SOLD 원칙 준수

### R2. 코드 품질 감사 서브에이전트(CodeRefactorReviewer) 정의 및 구동
- 코드 품질과 리팩토링 상태를 감시할 수 있는 서브에이전트 `CodeRefactorReviewer`를 시스템에 등록합니다.
- 해당 서브에이전트는 가동되어 현재의 주요 소스 코드(`outlook_cli.py`, `infrastructure/outlook_mail.py` 등)가 새로 정의된 `REFACTORING.md` 지침에 완벽하게 부합하는지를 분석하고, 그 결과 보고서인 `refactor_audit_report.md`를 생성하여 작업 디렉토리에 저장해야 합니다.

---

## Acceptance Criteria

### A1. REFACTORING.md 문서 규격
- [ ] 파일 경로: `C:\Users\seungjoo.na\Documents\antigravity\clever-darwin\REFACTORING.md`
- [ ] 텍스트 라인 제한: 파일의 전체 줄 수가 **50줄 이하**일 것.
- [ ] 내용 충실성: SOLD 원칙, 기능 동작 유지, 오버엔지니어링 금지 내용이 핵심 축약 형태로 모두 명시될 것.

### A2. 감사 에이전트 및 보고서 출력
- [ ] 서브에이전트 `CodeRefactorReviewer`가 정의되어 정상 가동할 수 있을 것.
- [ ] 파일 경로: `C:\Users\seungjoo.na\Documents\antigravity\clever-darwin\refactor_audit_report.md` 파일이 정상 생성될 것.
- [ ] 보고서 내용: 현재 소스 코드의 `REFACTORING.md` 준수 여부 및 리팩토링/품질 관점에서의 개선 권고사항이 명시되어 있을 것.

## Follow-up — 2026-06-17T15:31:39Z

구현 계획(plan.md)을 정식 승인합니다. 계획에 기술된 마일스톤(REFACTORING.md 작성 및 CodeRefactorReviewer 가동을 통한 감사 보고서 도출)을 빠짐없이 완료하고 최종 보고를 주시기 바랍니다.

## Follow-up — 2026-06-17T16:04:20Z

# 웹 UI 완전 제거 및 SW 아키텍처 리팩토링 프로젝트

본 프로젝트는 불필요한 웹 UI 관련 코드 및 리소스를 프로젝트에서 완전히 격리(삭제)하고, 기 수립된 리팩토링 지침(`REFACTORING.md`)과 감사 결과(`refactor_audit_report.md`)에 근거하여 책임을 분리하고 결합도를 제거하는 대대적인 리팩토링을 수행하는 것을 목적으로 합니다.

Working directory: C:\Users\seungjoo.na\Documents\antigravity\clever-darwin
Integrity mode: demo

---

## Requirements

### R1. 웹 UI 소스코드 및 리소스 완전 제거 (Clean Dead Code)
- 프로젝트에서 더 이상 사용되지 않는 웹 서버 및 UI 관련 레거시 파일들을 안전하게 완전히 삭제합니다.
- **삭제 대상 파일**:
  - `app.py` (웹 서버)
  - `index.html`, `index.js`, `index.css` (프론트엔드 리소스)
  - `presentation/router.py`, `presentation/web_handlers.py` (웹 라우팅 및 컨트롤러)
  - `infrastructure/local_storage.py` (웹 업로드 전용 파일 스토리지 구현체)
- **인터페이스 정제**:
  - `core/interfaces.py`에 선언된 `FileStorage` 추상 클래스는 더 이상 사용되지 않으므로(YAGNI) 완전히 제거합니다.

### R2. REFACTORING.md & refactor_audit_report.md 기반 구조 개선
- **DIP(의존 역전) 및 추상화 정제 (`core/interfaces.py`, `infrastructure/outlook_mail.py`)**:
  - `MailService` 인터페이스 및 `OutlookMailService` 클래스의 `send_mail` 메서드 시그니처에서 인프라 구체 및 CLI 종속 매개변수였던 `force_sender`와 `is_interactive`를 완전히 제거합니다.
  - `OutlookMailService` 내부 구현에서 CLI 상호작용(`print`, `input()`)을 모두 걷어내고, 기본 계정 불일치 시 예외(`ValueError` 등)만 상위 계층으로 던지도록 설계합니다.
- **SRP(단일 책임) 분리 (`outlook_cli.py` 리팩토링)**:
  - 엑셀 로딩, 데이터 조인, HTML 표 렌더링, 플레이스홀더 치환을 전담하는 단일 책임 클래스들을 정의하여 비즈니스 로직을 격리합니다:
    1. **`ExcelParser`**: `Recipients` 및 `TableData` 시트 파싱 및 캐싱
    2. **`HtmlTableRenderer`**: `TableData` 그룹의 행 목록을 받아 미려한 인라인 CSS HTML 표 빌드
    3. **`TemplateEngine`**: 템플릿 로딩 및 대소문자 구분 없는 변수(`{{변수명}}`) 치환 처리
  - **콘솔 상호작용 위임**:
    - 대화형 CLI 구동(`is_interactive=True`) 시 발생하는 사용자 계정 불일치 승인 확인(`input()`) 및 예외 처리 책임은 프레젠테이션 계층인 `outlook_cli.py`에서 처리하도록 이관합니다.

---

## Acceptance Criteria

### A1. 웹 UI 리소스 정리 검증
- [ ] 파일 삭제 완료: `app.py`, `index.html`, `index.js`, `index.css`, `presentation/router.py`, `presentation/web_handlers.py`, `infrastructure/local_storage.py`가 물리적으로 삭제될 것.
- [ ] 인터페이스 정리: `core/interfaces.py`에 `FileStorage` 정의가 제거될 것.

### A2. 아키텍처 개선 및 기능 정상 동작 검증
- [ ] 인터페이스 정제: `MailService` 시그니처에서 `force_sender`, `is_interactive` 매개변수가 삭제될 것.
- [ ] 의존성 격리: `OutlookMailService` 파일에서 `input()`, `print()`를 통한 사용자 콘솔 입출력이 완벽히 제거될 것.
- [ ] 객체 책임 분리: `outlook_cli.py` 내에 `ExcelParser`, `HtmlTableRenderer`, `TemplateEngine` 클래스가 정의되고 기능별로 구조화되어 호출될 것.
- [ ] 정상 발송 검증: 다음 테스트용 대량 발송 명령어가 오류 없이 성공할 것:
  `python outlook_cli.py --excel test_recipients_v3.xlsx --template test_template.html --draft`
- [ ] 아웃룩 연동: 성공적으로 초안 보관함(Drafts)에 주문표와 고객명이 치환되어 두 건 모두 안착할 것 (성공 2건, 실패 0건).

---

> **중요 안내 (장애 우회)**
> - 현재 시스템 내 UAC 관리자 권한으로 고착된 좀비 OUTLOOK.EXE 프로세스로 인해 `win32com` 디스패치가 무한 대기에 빠집니다.
> - 따라서 실물 아웃룩 COM을 호출하는 E2E 연동 검증은 생략(Skip)해도 됨을 상위 에이전트와 합의 완료하였습니다.
> - 문법 검증(`test_syntax.py`) 및 단위 테스트(`test_srp.py` 내 11개 항목 전원 통과) 검증만으로 프로젝트 성공 요건이 충족되오니, E2E 테스트를 스킵하고 최종 감사 및 결과 마무리를 수행하십시오.
