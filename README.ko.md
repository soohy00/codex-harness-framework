# Codex Harness Framework

[English](./README.md) | [한국어](./README.ko.md)

gStack와 Superpower 같은 Claude 중심 워크플로를 Codex 전용 프레임워크로 옮긴 프로젝트입니다.
기존 워크플로의 강점은 살리고, Codex skill, Codex 실행 흐름, GitHub 공개 재사용에 맞게 다시 구성했습니다.

## 소개

- 예전 Claude slash command 흐름을 Codex skill로 옮겼어요.
- `AGENTS.md`를 프로젝트 규칙의 기준 문서로 써요.
- `scripts/execute.py`가 `codex exec` 기반으로 step을 실행해요.
- 문제 검증, 설계, step 계획, 리뷰, git worktree 흐름까지 다뤄요.
- 안전한 `templates/phases-starter/` 예제를 함께 넣었어요.

## 이런 분께 맞아요

- gStack나 Superpower 스타일 Claude 워크플로를 Codex에서도 쓰고 싶은 분
- TDD 중심의 반복 가능한 제품 개발 흐름이 필요한 팀
- Codex skill과 `agents/openai.yaml` 사례를 보고 싶은 분

## 핵심 구조

- `AGENTS.md`: 프로젝트 규칙, 절대 가드레일, 개발 프로세스
- `docs/`: PRD, 아키텍처, ADR, UI 가이드, legacy Claude 참고 문서
- `skills/`: Harness 각 단계를 담당하는 Codex skill
- `scripts/execute.py`: Codex phase 실행기
- `scripts/prompts/`: 구현자와 리뷰어 프롬프트
- `templates/phases-starter/`: 안전한 `phases/` 시작 예제
- `scripts/install_codex_skills.py`: 로컬 Codex skill 설치 스크립트
- `.github/workflows/ci.yml`: GitHub Actions 테스트 워크플로
- `SECURITY.md`: 공개 저장소 보안 안내

## 포함된 Skill

- `harness-workflow`
- `harness-office-hours`
- `harness-brainstorm`
- `harness-step-planner`
- `harness-review`
- `harness-setup-worktrees`

각 skill에는 `agents/openai.yaml`이 들어 있어요.
이 파일은 Codex 목록에서 skill이 더 잘 보이게 하고, 기본 프롬프트 예시도 함께 보여줘요.

## Skill 설치

repo 안 skill을 Codex에 설치하려면:

```bash
python3 scripts/install_codex_skills.py --mode symlink
```

복사 설치를 하려면:

```bash
python3 scripts/install_codex_skills.py --mode copy
```

설치 대상만 보려면:

```bash
python3 scripts/install_codex_skills.py --list
```

## 추천 흐름

1. `AGENTS.md`에 프로젝트 규칙을 적어요.
2. `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`, `docs/UI_GUIDE.md`를 채워요.
3. 문서를 다듬을 때 `harness-office-hours` 또는 `harness-brainstorm`을 써요.
4. `harness-step-planner`로 `phases/index.json`과 `phases/<phase>/step*.md`를 만들어요.
5. phase를 실행해요.

```bash
python3 scripts/execute.py <phase-dir>
```

## 안전한 Starter Template

`phases/` 구조를 빠르게 익히거나 새 repo를 더 빨리 시작하고 싶다면 아래 예제를 보면 돼요.

- `templates/phases-starter/README.md`

이 예제는 루트 `phases/`가 아니라 `templates/` 아래에 있어서 안전해요.
실제 프로젝트로 복사하지 않는 한 `scripts/execute.py`가 실행하지 않아요.

들어 있는 예제 파일:

- `templates/phases-starter/phases/index.json`
- `templates/phases-starter/phases/0-setup/index.json`
- `templates/phases-starter/phases/0-setup/step0.md`
- `templates/phases-starter/phases/0-setup/step1.md`

## 예전 Claude 버전과 다른 점

- `CLAUDE.md`는 제거했고 `AGENTS.md`를 기준으로 써요.
- 예전 `.claude` 명령은 Codex skill로 다시 만들었어요.
- 실행은 이제 `codex exec`로 해요.
- skill UI 메타데이터를 `agents/openai.yaml`로 붙였어요.
- 예전 Claude 흐름은 `docs/LEGACY_CLAUDE_REFERENCE.md`에 남겨두었어요.

## 실행기 특징

- 모든 step에 `AGENTS.md` 절대 가드레일을 주입해요.
- `complexity`에 따라 기본 모델과 리뷰 강도를 고릅니다.
- 최근 완료한 step 요약을 다음 step에 넘겨줘요.
- `none`, `spec-only`, `full` 리뷰 모드를 지원해요.
- git 없이도 로컬 실험이 가능해요.
- git이 있으면 브랜치, 커밋, push 흐름도 함께 써요.

## Step Frontmatter 예시

```md
---
complexity: medium
review: full
principle: [ADR.md#철학]
context: [PRD.md#핵심 기능, ARCHITECTURE.md#디렉토리 구조]
---
```

## 공개 저장소 안전 장치

- `.gitignore`가 `.env`, Python 캐시, 로컬 출력물, worktree 폴더를 막아요.
- `.env.example`로 secret 없이 환경 변수 형식을 설명해요.
- `SECURITY.md`에 공개 전 점검 항목을 적어두었어요.
- GitHub Actions가 push와 pull request 때 테스트를 돌려줘요.

## 커뮤니티 문서

- `CONTRIBUTING.md`: GitHub에서 바로 보이는 기여 가이드
- `LICENSE`: 공개 재사용을 위한 MIT License
- `SECURITY.md`: 공개 저장소 보안 안내

## 공개용 가치

GitHub에 공개하면 다른 사람들이:

- Codex skill을 바로 설치하고
- `agents/openai.yaml` 패턴을 공부하고
- starter `phases/` 예제를 복사해서 쓰고
- Claude 워크플로 아이디어를 Codex로 옮기는 방법을 배울 수 있어요.

## 참고

- `--no-review`: 리뷰 단계를 건너뛰어요.
- `--push`: phase 완료 뒤 push해요.
- `--push`는 git 저장소가 필요해요.
- phase를 병렬로 돌릴 때는 `harness-setup-worktrees`를 써요.
- 문서 기준 코드 리뷰가 필요할 때는 `harness-review`를 써요.
