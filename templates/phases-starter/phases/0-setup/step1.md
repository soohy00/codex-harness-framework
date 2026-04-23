---
complexity: low
prescriptive: [UI_GUIDE.md#컴포넌트]
---

# Step 1: app-shell

## 읽어야 할 파일

먼저 아래 파일들을 읽고 설계 의도를 파악하라:

- `/AGENTS.md`
- `/docs/UI_GUIDE.md`
- `/docs/ARCHITECTURE.md`
- `/src/types/index.ts`

## 작업

- [ ] 실패하는 테스트를 먼저 작성한다 (`src/app/page.test.tsx`)
- [ ] 테스트 실패를 확인한다: `npm test -- src/app/page.test.tsx`
- [ ] 구현한다 (`src/app/page.tsx`)
- [ ] 아래 내용을 가진 기본 화면을 만든다.
  - 동네 메모 목록 제목
  - 빈 상태 안내 문구
  - 메모 쓰기 버튼
- [ ] 테스트 통과를 확인한다: `npm test -- src/app/page.test.tsx`
- [ ] git 저장소라면 커밋한다: `git add src/app/page.tsx src/app/page.test.tsx && git commit -m "feat(setup): add app shell"`

## Acceptance Criteria

```bash
npm run build
npm test -- src/app/page.test.tsx
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아래를 확인한다:
   - UI_GUIDE.md 컴포넌트 방향을 따르는가?
   - ARCHITECTURE.md 구조를 벗어나지 않았는가?
   - AGENTS.md ABSOLUTE 가드레일을 위반하지 않았는가?
3. `phases/0-setup/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "기본 앱 셸과 빈 상태 화면을 추가했다."`
   - 이 실행에서 더 이상 진행 불가 → `"status": "error"`, `"error_message": "구체적 에러와 시도한 접근법"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 중단

## 금지사항

- 실제 데이터 호출을 먼저 붙이지 마라. 이유: 이 step의 목적은 기본 화면 구조 확인이다.
- 기존 테스트를 삭제하거나 skip 처리하지 마라. 이유: 회귀 방지가 속도보다 중요하다.
