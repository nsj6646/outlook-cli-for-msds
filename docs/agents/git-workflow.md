# 권장 Git 형상 관리 워크플로우 (docs/agents/git-workflow.md)

AI 에이전트의 자동적이고 잦은 Git 커밋은 히스토리를 파편화시켜 형상 관리에 안 좋은 영향을 줄 수 있습니다. 따라서 본 가이드는 개발 담당자(또는 사용자)가 개발 사이클 종료 시 수동으로 안전하게 변경사항을 커밋하고 원격 저장소에 푸시할 수 있는 표준 워크플로우를 제안합니다.

---

## 1. Git 형상 관리 표준 절차 (5-Step Workflow)

### 1단계: 변경 파일 및 차이점 검토 (Review)
본격적으로 스테이징하기 전, 로컬 디렉토리에서 어떤 파일들이 추가, 수정, 삭제되었는지 상태와 코드 차이점을 직접 육안 검수합니다.
```powershell
# 변경 파일 목록 요약 검사
git status

# 실시간 소스 코드 차이점(diff) 상세 검사
git diff
```

### 2단계: 선별 스테이징 (Selective Add)
의미적으로 묶이는 파일들만 선별하여 스테이징합니다. 관련 없는 임시 테스트 파일이나 임시 메모가 함께 올라가지 않도록 제어합니다.
```powershell
# 특정 소스 코드 및 문서만 선택적으로 스테이징
git add core/distribution.py outlook_cli.py docs/

# 모든 삭제 및 변경 사항을 일괄 스테이징할 경우
git add -A
```

### 3단계:Conventional Commits 기반 의미 있는 커밋 메시지 작성 (Commit)
누구나 변경 이력을 직관적으로 파악할 수 있도록 접두사(Type)와 구체적인 사유를 명시하여 커밋합니다.
* **Feat**: 신규 기능 구현 (예: `feat: implement mail signature auto injection`)
* **Fix**: 버그 픽스 (예: `fix: resolve prefix match check edgecase`)
* **Docs**: 문서 변경 (예: `docs: update PRD for signature feature`)
* **Chore**: 빌드 설정, 의존성 정리 (예: `chore: shrink .gitignore`)

```powershell
git commit -m "feat: implement auto row numbering for tables and automatic signature html injection"
```

### 4단계: 원격 브랜치 변경분 병합 (Sync)
원격 저장소에 다른 사람이 수정한 커밋이 먼저 푸시되어 있을 수 있으므로, 푸시 전 반드시 원격 이력을 로컬과 통합합니다. rebase를 사용하면 커밋 선형성을 깨끗하게 유지할 수 있습니다.
```powershell
git pull --rebase origin main
```

### 5단계: 원격 저장소 푸시 및 백업 (Push)
병합이 성공적으로 완료되었으면, 안전한 원격 백업 및 팀 협업을 위해 즉시 원격 저장소로 푸시합니다.
```powershell
git push origin main
```

---

## 2. 릴리즈 배포용 특수 가이드
- 바이너리 컴파일 결과물(`build/`, `dist/`, `*.spec`)은 로컬에서 독립적으로 실행되기 위한 배포 자원이며 소스코드가 아닙니다.
- [.gitignore](file:///C:/Users/seungjoo.na/Documents/antigravity/clever-darwin/.gitignore) 파일에 의해 자동으로 깃 추적에서 제외되어 있으므로, 릴리즈 시에는 이 워크플로우에 따라 소스 코드를 먼저 `git push`한 후, 로컬 `dist/outlook-cli.exe` 파일과 `usage.txt`를 수동으로 패킹하여 배포판을 릴리즈(Release)하십시오.
