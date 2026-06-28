## 2026-06-17T15:46:08Z

당신은 'SRP Refactorer' 역할을 맡은 worker 서브에이전트입니다.
당신의 작업 디렉토리는 C:\Users\seungjoo.na\Documents\antigravity\clever-darwin\.agents\worker_m4 입니다.
모든 문서와 보고서는 한국어로 작성해 주십시오.

### 임무
사용자가 승인한 구현 계획에 따라 'R2.2: SRP(단일 책임) 분리 및 CLI 이관'을 수행해 주십시오.

1. **`outlook_cli.py` 내 단일 책임 클래스 구현**:
   - `outlook_cli.py` 내부의 엑셀 데이터 처리, HTML 렌더링, 템플릿 치환 로직을 격리하여 독립적인 클래스들로 재구축하십시오:
     1. **`ExcelParser`**: 엑셀 파일을 읽고, `Recipients` 시트와 `TableData` 시트를 로딩하여 수신자 메타데이터와 표 데이터를 파싱 및 캐싱하는 책임.
     2. **`HtmlTableRenderer`**: 특정 이메일에 귀속된 표 데이터를 바탕으로 인라인 CSS가 가미된 미려한 HTML 표 문자열을 빌드하는 책임.
     3. **`TemplateEngine`**: 이메일 템플릿 텍스트에 대해 대소문자 구분 없이 `{{변수명}}` 플레이스홀더를 치환하는 책임.
   - 단, 기존의 파싱 규칙과 인라인 CSS 속성, 템플릿 정규식 동작은 기존 기능과 완전히 동일하게(또는 더 안전하게) 구현되어야 합니다.

2. **콘솔 상호작용 및 예외 처리 책임 이관**:
   - `OutlookMailService`의 변경된 시그니처 및 생성자 주입 형태를 반영하십시오.
   - 대화형 CLI 모드(`is_interactive=True` 모드)에서 메일을 보낼 때, 기본 계정 불일치로 인한 `ValueError` 예외가 발생하면 프레젠테이션 계층인 `outlook_cli.py`가 이를 catch하십시오:
     - 사용자에게 `input()`으로 "기본 계정이 아닌 [sender] 계정으로 메일을 전송합니다. 계속 진행하시겠습니까? (y/N): " 라고 확인을 요청하십시오.
     - 사용자가 동의(y/yes)할 경우, `OutlookMailService(force_sender=True, is_interactive=True)`를 인스턴스화하여 메일을 재발송하거나, 해당 계정으로 보낼 수 있도록 우회 처리하십시오.
     - 동의하지 않을 경우 "사용자 요청으로 메일 발송이 취소되었습니다." 메시지를 출력하고 중단(False 반환 등)하십시오.
   - 비대화형 대량 엑셀 발송 모드(`send_bulk_mails_from_excel`) 등에서도 `--force-sender` 플래그 및 예외 처리가 기존 논리와 모순 없이 정상 작동하도록 구현하십시오.

3. **검증**:
   - 수정을 완료한 후 `python -X utf8 tests/test_syntax.py`를 실행하여 모든 파이썬 파일의 문법 상태를 확인하십시오.
   - `python -X utf8 tests/test_cli.py`를 실행하여 기능 단위 동작을 검증하십시오.

4. **산출물**:
   - 작업 결과를 요약한 `handoff.md`를 본인의 작업 디렉토리에 작성하십시오.
   - 작성 완료 후 `send_message`를 통해 부모 에이전트(Conversation ID: 9dc1fcff-9406-43ae-8039-37dfc335f88b)에게 완료 보고를 해주십시오. 보고서에는 리팩토링된 클래스 명세와 검증 통과 여부가 포함되어야 합니다.
