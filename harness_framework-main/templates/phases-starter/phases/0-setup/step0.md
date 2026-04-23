---
complexity: medium
review: spec-only
principle: [ADR.md#철학]
context: [PRD.md#핵심 기능, ARCHITECTURE.md#디렉토리 구조]
---

# Step 0: contracts

## 읽어야 할 파일

먼저 아래 파일들을 읽고 설계 의도를 파악하라:

- `/AGENTS.md`
- `/docs/PRD.md`
- `/docs/ADR.md`
- `/docs/ARCHITECTURE.md`

## 작업

- [ ] 실패하는 테스트를 먼저 작성한다 (`src/types/index.test.ts`)
- [ ] 테스트 실패를 확인한다: `npm test -- src/types/index.test.ts`
- [ ] 구현한다 (`src/types/index.ts`)
- [ ] 아래 인터페이스를 정의한다.
  - `NeighborhoodNote`
  - `CreateNeighborhoodNoteInput`
  - `NeighborhoodFeedItem`
- [ ] 테스트 통과를 확인한다: `npm test -- src/types/index.test.ts`
- [ ] git 저장소라면 커밋한다: `git add src/types/index.ts src/types/index.test.ts && git commit -m "feat(setup): define note contracts"`

## Acceptance Criteria

```bash
npm run build
npm test -- src/types/index.test.ts
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아래를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 선택을 벗어나지 않았는가?
   - AGENTS.md ABSOLUTE 가드레일을 위반하지 않았는가?
3. `phases/0-setup/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "노트 도메인 타입 계약을 정의했다."`
   - 이 실행에서 더 이상 진행 불가 → `"status": "error"`, `"error_message": "구체적 에러와 시도한 접근법"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 중단

## 금지사항

- 타입 이름을 모호하게 짓지 마라. 이유: 다음 step에서 계약을 다시 해석해야 한다.
- 기존 테스트를 삭제하거나 skip 처리하지 마라. 이유: 회귀 방지가 속도보다 중요하다.
