# ADR 0004: 아웃룩 네이티브 표 그리드 스타일 및 참조(Cc) 연동 세부 사양 결정

## 상태 (Status)
승인됨 (Accepted)

## 컨텍스트 (Context)
이메일 본문에 삽입되는 취급 제품 목록 표의 기본 비주얼 스타일이 인위적인 인라인 CSS(회색 연한 테두리 및 회색 배경)를 사용하고 있어 아웃룩의 본래 내장 서식과 결합 시 시각적 이질감을 유발했습니다.
또한 발송 명단 엑셀 양식에서 수신인뿐만 아니라 참조처(Cc)에 대한 추가가 요구되었으며, 메일 전체의 기본 폰트와 본문 크기를 맑은 고딕 규격으로 정렬해야 하는 문제가 있었습니다.

## 결정 (Decision)
1. **맑은 고딕 본문 랩핑**:
   - 메일 본문을 렌더링할 때 전체 문자열을 `<div style="font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 11.0pt; color: #000000; line-height: 1.6;">` 블록으로 랩핑하여 아웃룩 기본 폰트(맑은 고딕, 11pt)를 강제 지향합니다.
2. **아웃룩 순정 표 스타일 모방**:
   - `HtmlTableRenderer` 클래스의 CSS 스타일을 `표희망사항.html` 분석 결과에 맞추어 `MsoTableGrid` 규격으로 변경합니다.
   - 테이블: `border-collapse: collapse; border: none; font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 11.0pt;`
   - 셀(th, td): `border: solid windowtext 1.0pt; padding: 0cm 5.4pt 0cm 5.4pt;`
   - 헤더(th)의 경우 별도의 연한 배경색 없이 얇은 실선 테두리와 볼드 서식만 적용합니다.
3. **엑셀 참조(Cc) 컬럼 추가 및 다중 참조**:
   - 가이드용 [test_recipients_v4.xlsx](file:///C:/Users/seungjoo.na/Documents/antigravity/clever-darwin/test_recipients_v4.xlsx)에 `Cc` 컬럼을 명시적으로 반영합니다.
   - 엑셀 상의 `Cc` 컬럼에 세미콜론 `;`으로 구분된 다중 이메일이 있을 시, 아웃룩의 참조(CC)에 다중 바인딩하여 초안을 생성하도록 설정합니다. (본문 내 플레이스홀더 치환 매핑은 하지 않습니다.)

## 결과 (Consequences)
- **장점**: 생성된 메일 초안을 아웃룩에서 열었을 때, 사용자가 직접 메일 내에 작성한 것과 똑같은 맑은 고딕 11pt 폰트와 기본 격자 실선 표 서식이 적용되어 시각적 이질감이 완벽히 사라집니다. 참조 대상 수신처가 엑셀 데이터 파일 변경만으로 온전히 바인딩되어 편리합니다.
- **단점**: 없음.
