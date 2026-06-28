## 2026-06-17T15:44:43Z

당신은 'DIP Refactorer' 역할을 맡은 worker 서브에이전트입니다.
당신의 작업 디렉토리는 C:\Users\seungjoo.na\Documents\antigravity\clever-darwin\.agents\worker_m3` 입니다.
모든 문서와 보고서는 한국어로 작성해 주십시오.

### 임무
사용자가 승인한 구현 계획에 따라 'R2.1: DIP(의존 역전) 및 추상화 정제'를 수행해야 합니다.

1. **`core/interfaces.py` 수정**:
   - `MailService.send_mail` 메서드의 시그니처 및 docstring(Args 및 설명 포함)에서 `force_sender`와 `is_interactive` 매개변수를 완전히 제거하십시오.
   - 단, `MailService` 추상 클래스의 본질적인 시그니처 스타일은 유지해야 합니다.

2. **`infrastructure/outlook_mail.py` 수정**:
   - `OutlookMailService.send_mail` 메서드의 시그니처 및 설명 주석에서 `force_sender`와 `is_interactive` 매개변수를 완전히 제거하십시오.
   - `OutlookMailService` 클래스 생성자(`__init__`)를 추가하여 `force_sender: bool = False`, `is_interactive: bool = False`를 주입받아 인스턴스 멤버 변수로 설정하십시오:
     ```python
     def __init__(self, force_sender: bool = False, is_interactive: bool = False):
         self.force_sender = force_sender
         self.is_interactive = is_interactive
     ```
   - `send_mail` 내부 구현에서 사용자 콘솔 입출력(`print()`, `input()`)을 모두 걷어내십시오. (오프라인 경고 출력 및 계정 불일치 시 input 확인 부분)
   - 기본 송신 계정(Primary)과 입력받은 발신자 계정(`sender`)이 불일치할 때:
     - `self.force_sender`가 `True`이면 경고 없이 진행하고,
     - `self.force_sender`가 `False`이면 `ValueError` 예외를 발생시키고 상위 계층으로 던지도록 구현하십시오.
   - `if draft:` 분기에서 기존의 `is_interactive` 매개변수 대신 `self.is_interactive` 인스턴스 필드를 사용하도록 처리하십시오.

3. **`outlook_cli.py` 임시 수정 (문법 및 호출 정합성 확보)**:
   - `outlook_cli.py` 내부에서 `OutlookMailService`를 인스턴스화하고 `send_mail`을 호출하는 부분(라인 99 근처 및 라인 444 근처)을 변경된 시그니처에 맞게 수정하십시오.
   - 즉, `mail_service = OutlookMailService(force_sender=force_sender, is_interactive=...)` 형태로 인스턴스를 생성할 때 해당 파라미터를 넘기고, `send_mail`을 호출할 때는 `force_sender`와 `is_interactive` 매개변수를 완전히 제외하도록 수정하십시오.

4. **검증**:
   - 수정을 마친 후, 문법 정합성을 확인하기 위해 `python tests/test_syntax.py`를 실행하여 모든 파이썬 파일이 정상 통과하는지 검증하십시오.

5. **산출물**:
   - 작업 결과를 요약한 `handoff.md`를 본인의 작업 디렉토리에 작성하십시오.
   - 작성 완료 후 `send_message`를 통해 부모 에이전트(Conversation ID: 9dc1fcff-9406-43ae-8039-37dfc335f88b)에게 완료 보고를 해주십시오. 보고서에는 수정한 파일 목록 및 syntax 테스트 통과 결과가 포함되어야 합니다.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
