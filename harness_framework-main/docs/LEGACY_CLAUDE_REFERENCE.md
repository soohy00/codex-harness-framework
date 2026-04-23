# Legacy Claude Reference

이 문서는 제거한 `.claude/` 폴더의 핵심 흐름만 남긴 참고 문서입니다.
이제 실제 실행 기준은 Codex skill과 `scripts/execute.py`입니다.

## 명령 매핑

| 이전 Claude 명령 | 현재 Codex skill | 목적 |
|---|---|---|
| `/office-hours` | `harness-office-hours` | 아이디어 검증과 `docs/DISCOVERY.md` 작성 |
| `/brainstorm` | `harness-brainstorm` | 기술 설계와 `docs/ADR.md`, `docs/ARCHITECTURE.md`, `docs/UI_GUIDE.md` 작성 |
| `/harness` | `harness-step-planner` | `phases/` 설계와 step 파일 생성 |
| `/review` | `harness-review` | 문서 기준 코드 리뷰 |
| `/setup-worktrees` | `harness-setup-worktrees` | phase별 git worktree 생성 |

## 유지한 흐름

### 1. Office Hours

- 목적: 문제를 먼저 확인합니다.
- 방식: 한 번에 한 질문만 합니다.
- 원칙: 증거가 없는 수요는 확정하지 않습니다.
- 제한: 이 단계에서는 구현 이야기를 꺼내지 않습니다.

### 2. Brainstorm

- 목적: 요구사항을 기술 설계로 바꿉니다.
- 방식: 2개 또는 3개의 접근법을 비교합니다.
- 원칙: 가장 단순한 방법을 먼저 추천합니다.
- 제한: 설계 승인 전에는 코드 구현을 시작하지 않습니다.

### 3. Harness

- 목적: Codex가 바로 실행할 수 있는 phase와 step을 만듭니다.
- 방식: 작은 step으로 나눕니다.
- 원칙: TDD 순서를 step 파일에 직접 씁니다.
- 제한: 승인 전에는 `phases/` 파일을 만들지 않습니다.

### 4. Review

- 목적: 변경사항이 문서와 규칙을 지키는지 확인합니다.
- 방식: 아키텍처, 테스트, 보안, 품질을 봅니다.
- 원칙: 위반 사항을 먼저 적습니다.

### 5. Setup Worktrees

- 목적: phase를 병렬로 실행할 준비를 합니다.
- 방식: phase마다 git worktree를 만듭니다.
- 제한: git 저장소가 있어야 합니다.

## 예전 settings.json 핵심 내용

### Stop hook

예전 Claude 설정은 세션 종료 때 아래 검사를 시도했습니다.

```bash
git diff --quiet HEAD 2>/dev/null || (npm run lint 2>&1 && npm run build 2>&1 && npm run test 2>&1)
```

의미는 간단합니다.

- 변경사항이 있으면 lint를 돌립니다.
- 이어서 build를 돌립니다.
- 이어서 test를 돌립니다.

### Bash safety hook

예전 Claude 설정은 아래 위험 명령을 막았습니다.

- `rm -rf`
- `git push --force`
- `git reset --hard`
- `DROP TABLE`

## 현재 Codex 기준 정리

- 실행 흐름은 skill과 `scripts/execute.py`로 옮겼습니다.
- 프로젝트 규칙은 `AGENTS.md`를 기준으로 씁니다.
- `.claude/settings.json` hook은 Codex가 직접 읽지 않습니다.
- 같은 안전 규칙이 필요하면 CI나 별도 스크립트로 옮기는 편이 더 안정적입니다.

## 참고

- 새 진입점: `skills/`
- 설치 스크립트: `scripts/install_codex_skills.py`
- 전체 사용 흐름: `README.md`
