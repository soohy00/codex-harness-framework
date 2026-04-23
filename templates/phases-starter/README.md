# Phases Starter Template

이 폴더는 바로 실행하는 phase가 아닙니다.
복사해서 시작하는 예제입니다.

## 목적

- `phases/` 구조를 처음 만드는 사람도 빠르게 시작할 수 있어요.
- `index.json`과 `step*.md`가 어떤 모양인지 바로 볼 수 있어요.
- 실제 프로젝트에 맞게 바꿔 쓰면 돼요.

## 안전한 이유

- 루트 `phases/`가 아니라 `templates/` 아래에 있어요.
- `scripts/execute.py`가 이 폴더를 자동으로 실행하지 않아요.
- 예제 파일이라서 그대로 두어도 현재 프로젝트 실행에는 영향이 없어요.

## 시작 방법

1. `templates/phases-starter/phases/`를 프로젝트 루트의 `phases/`로 복사해요.
2. 예제 프로젝트명과 파일 경로를 내 프로젝트에 맞게 바꿔요.
3. step 이름과 AC 커맨드를 내 프로젝트 기준으로 바꿔요.
4. `python3 scripts/execute.py <phase-dir>`로 실행해요.

## 들어있는 예제

- `phases/index.json`
- `phases/0-setup/index.json`
- `phases/0-setup/step0.md`
- `phases/0-setup/step1.md`

## 예제 특징

- 아주 작은 1개 phase만 넣었어요.
- `contracts` step으로 타입 계약부터 잡아요.
- `app-shell` step으로 첫 화면과 기본 검증 흐름을 보여줘요.
