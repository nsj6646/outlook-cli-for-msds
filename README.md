# Outlook Bulk MSDS Delivery CLI (outlook-cli)

아웃룩(Outlook)과 엑셀 데이터 소스를 연동하여, 다수의 수신처에 제품별 물질안전정보자료(MSDS) 파일을 안전하게 배포하는 CLI 기반 자동화 릴리즈 도구입니다.

---

## 1. 주요 기능
* **제품코드 엄격 접두사 매칭 (`제품코드_`)**: MSDS 폴더 내 파일명 첫부분이 `제품코드_` 형태로 시작하는 파일들을 식별하여 자동 수집 및 첨부합니다.
* **메일 서명 자동 삽입 및 예비 탐색**: 메일 하단에 HTML 형식의 서명을 자동 결합합니다. 경로 미지정 시 현재 작업 폴더의 `signature.html` 또는 `signature/signature.html`을 예비 자동 검색 적용합니다. (다양한 파일 인코딩 자동 복원 지원)
* **맑은 고딕(11pt) 본문 및 표 서식 지정**: 메일 전체 글꼴과 제품 명세 표의 스타일을 맑은 고딕 11pt 서식으로 강제 일원화합니다.
* **아웃룩 순정 격자 표 양식 재현**: 얇은 검정 실선 격자 테두리(`MsoTableGrid` 스타일) 디자인으로 표를 인라인 렌더링합니다.
* **표 번호 자동 매김 (Auto Numbering)**: 엑셀 `TableData` 시트에서 "번호" 컬럼을 수동 작성할 필요 없이, 메일 본문 표 생성 시 프로그램이 순차 순번(1, 2, 3...)을 자동 기입합니다.
* **다중 참조(Cc) 수신인 바인딩**: 엑셀 명단 내 세미콜론 `;` 구분자를 사용해 참조 수신인을 다중 지정할 수 있습니다.
* **예약 발송 및 발신계정 지정**: 엑셀 행별로 아웃룩 다중 계정(`From`) 및 예약 일시(`DeferredTime`)를 개별 주입합니다.
* **세션별 감사 로그 및 7일 자동 정리**: 실행 시마다 고유 로그 파일을 적재하며, 7일이 지난 레거시 로그 파일들을 구동 시점에 자동 탐색하여 청소합니다.

---

## 2. 엑셀 데이터 소스 레이아웃

동일한 엑셀 파일 내에 아래 두 개의 시트가 필수로 구성되어야 합니다.

### (1) `Recipients` 시트 (수신 명단)
| To | Cc | Bcc | Subject | Body | From | 예약시간 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 수신자 이메일 | 참조자 이메일 (여러 명일 경우 `;` 구분) | 비밀참조자 이메일 (여러 명일 경우 `;` 구분) | 메일 제목 | 메일 본문 내용 (`{{table}}` 플레이스홀더 포함 가능) | 아웃룩 등록 발신계정 주소 | 예약 발송 일시 (포맷: `YYYY-MM-DD HH:MM:SS`) |

### (2) `TableData` 시트 (제품 취급 정보)
| Email | 제품코드 | 제품명 |
| :--- | :--- | :--- |
| 수신인 이메일 (수신처와 매핑 키) | 제품 코드 (예: `P1003`) | 취급 제품 명칭 (예: `알파`) |
*(※ "번호" 컬럼은 기재하지 않으며, 만약 기존 엑셀 구조로 인해 존재하더라도 프로그램이 자동으로 파싱 과정에서 무시하고 스스로 번호를 매깁니다.)*

---

## 3. 실행 방법 (CLI CLI Usage)

바이너리 또는 파이썬 스크립트를 기동하여 사용합니다.

```powershell
# 임시 보관함(Drafts)에 안전하게 초안 일괄 생성 (권장)
./outlook-cli.exe --excel test_recipients_v4.xlsx --msds-dir ./test_msds --draft

# 화면 방해 없이 완전히 백그라운드 모드로 저장
./outlook-cli.exe --excel test_recipients_v4.xlsx --msds-dir ./test_msds --draft --non-interactive

# 즉시 발송 모드 (안전이 완전히 검증되었을 때만 사용)
./outlook-cli.exe --excel test_recipients_v4.xlsx --msds-dir ./test_msds
```

### CLI 옵션 상세
* `--excel`, `-e`: 필수. 엑셀 설정 파일의 로컬 경로를 지정합니다.
* `--msds-dir`, `-d`: 필수. 매칭할 MSDS 파일들이 적재된 폴더 경로를 지정합니다.
* `--draft`: 초안 모드를 활성화합니다. (메일을 즉시 발송하지 않고 임시 보관함에 작성)
* `--non-interactive`: 비대화형 백그라운드 저장을 강제합니다. (아웃룩 창이 화면에 뜨지 않고 일괄 저장)
* `--force-primary`: 기본 송신 계정이 아닌 보조 계정으로 발송 시도 시 차단하는 안전장치를 무시하고 발송을 허용합니다.
* `--signature`: 메일 하단에 자동 결합할 HTML 서명 파일 경로입니다. (미지정 시 현재 실행 경로의 `signature.html` 또는 `signature/signature.html`을 예비로 우선 자동 탐색합니다.)

---

## 4. 빌드 방법 (Build Guide)

가볍고 불필요한 모듈이 배제된 단일 바이너리(EXE)를 빌드하려면 다음 순서로 기동합니다.

```powershell
# 1. 빌드용 독립 가상환경 진입 (uv 권장)
uv venv
.venv\Scripts\activate

# 2. 필수 라이브러리 및 빌더 설치
pip install openpyxl pywin32 pyinstaller

# 3. YAGNI 기반 초경량 빌드 실행 (불필요 UI/테스트 모듈 배제)
pyinstaller --onefile --clean --name outlook-cli --exclude-module tkinter --exclude-module unittest --exclude-module pydoc outlook_cli.py
```
* **결과물**: `dist/outlook-cli.exe` 단일 바이너리가 초경량 크기로 출력됩니다.
