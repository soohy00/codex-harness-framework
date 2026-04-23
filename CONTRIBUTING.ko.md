# Contributing

[English](./CONTRIBUTING.md) | [한국어](./CONTRIBUTING.ko.md)

Codex Harness Framework에 기여해주셔서 감사합니다.

## 시작 전에

- 프로젝트 목표를 보려면 `README.md`를 읽어주세요.
- 워크플로 규칙을 보려면 `AGENTS.md`를 읽어주세요.
- 로그나 설정을 공유하기 전에는 `SECURITY.md`를 먼저 확인해주세요.

## 기여하기 좋은 영역

- `skills/` 안 skill 설명 개선
- `templates/phases-starter/` 예제 개선
- `docs/` 문서 보완
- `scripts/test_*.py` 테스트 보강
- GitHub 공개용 안내와 온보딩 개선

## 기여 규칙

- 이 프로젝트는 Codex 중심으로 유지해주세요.
- `.claude` 전용 실행 동작을 다시 넣지 말아주세요.
- 예제는 공개 재사용에 안전한 상태로 유지해주세요.
- secret, token, private key, 실제 `.env` 파일은 커밋하지 말아주세요.
- 문서에서 repo 파일을 가리킬 때는 상대 경로 링크를 써주세요.

## 기본 흐름

1. 변경이 크면 먼저 issue를 만들거나 기존 issue에서 시작해주세요.
2. 변경 범위는 작고 분명하게 유지해주세요.
3. 동작이 바뀌면 문서도 같이 수정해주세요.
4. 필요하면 테스트를 추가하거나 수정해주세요.
5. 변경 요약이 분명한 pull request를 열어주세요.

## 로컬 확인

pull request를 열기 전에 전체 테스트를 돌려주세요.

```bash
python3 -m unittest scripts.test_execute scripts.test_install_codex_skills scripts.test_skill_metadata scripts.test_phase_template scripts.test_repo_hygiene -v
```

문법 검사도 함께 돌려주세요.

```bash
PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile scripts/execute.py scripts/test_execute.py scripts/install_codex_skills.py scripts/test_install_codex_skills.py scripts/test_skill_metadata.py scripts/test_phase_template.py scripts/test_repo_hygiene.py
```

## Pull Request 체크리스트

- 변경 범위가 작고 이해하기 쉬운가
- 필요할 때 문서를 같이 고쳤는가
- 테스트가 로컬에서 통과하는가
- secret이나 로컬 산출물이 포함되지 않았는가
- `.gitignore`가 로컬 전용 파일을 계속 막고 있는가

## 라이선스

이 저장소에 기여하면 기여 내용은 `LICENSE`의 MIT License로 배포되는 것에 동의하는 것으로 봅니다.
