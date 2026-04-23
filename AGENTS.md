# 프로젝트: {프로젝트명}

## 프로젝트 유형
<!-- 해당하는 것 하나만 남기고 나머지는 삭제하라 -->
- [ ] 신규 프로덕트 — 사업 검증 필요 → `docs/DISCOVERY.md` 작성 → `docs/PRD.md` 작성 → `phases/` 설계
- [ ] 사이드 프로젝트 — 빠른 실험 → `docs/PRD.md` 간단 작성 → `phases/` 설계
- [ ] 외주 작업 — 스코프 확정됨 → `AGENTS.md`·`docs/PRD.md` 직접 작성 → `phases/` 설계

## 기술 스택
- {프레임워크 (예: Next.js 15 App Router)}
- {언어 (예: TypeScript strict mode)}
- {스타일링 (예: Tailwind CSS)}
- {테스트 (예: Vitest + Testing Library)}

## 아키텍처 규칙
- CRITICAL: {절대 지켜야 할 규칙 1 (예: 모든 API 로직은 app/api/ 라우트 핸들러에서만 처리)}
- CRITICAL: {절대 지켜야 할 규칙 2 (예: 클라이언트 컴포넌트에서 직접 외부 API 호출 금지)}
- {일반 규칙 (예: 컴포넌트는 components/, 타입은 types/, 유틸은 lib/ 에 위치)}

## ABSOLUTE 가드레일
<!-- execute.py가 모든 step에 자동 주입한다. 항목은 최소한으로 유지하라. -->
<!-- 규칙이 많을수록 AI의 판단 공간이 줄어든다. 진짜 위반 불가한 것만 적어라. -->

- 기존 테스트를 깨뜨리지 마라. 이유: 회귀 방지가 개발 속도보다 중요하다.
- secrets를 코드에 직접 작성하지 마라. 이유: 보안 사고는 복구가 불가능하다.
- 이 step에 명시되지 않은 파일을 수정하지 마라. 이유: step 격리가 무너지면 디버깅이 불가능해진다.
- 타입 계약 파일(`src/types/index.ts` 또는 프로젝트 기준 동등 파일)에 정의된 인터페이스를 임의로 변경하지 마라. 이유: 타입 계약은 모든 step의 공통 기반이다.
<!-- 경로는 프로젝트에 맞게 수정하라. Python이면 domain/models.py, Go이면 internal/types/types.go 등 -->

## 개발 프로세스
- CRITICAL: 새 기능 구현 시 테스트를 먼저 작성하고, 테스트가 통과하는 구현을 작성할 것 (TDD)
- 커밋 메시지는 conventional commits 형식 (feat:, fix:, docs:, refactor:, test:, chore:)

## 명령어
```
{dev}     # 개발 서버 (예: npm run dev)
{build}   # 프로덕션 빌드 (예: npm run build)
{lint}    # 린트 (예: npm run lint)
{test}    # 테스트 (예: npm run test)
```
