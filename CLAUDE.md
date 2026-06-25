# Georgian Vocab (단어장) — 조지아어 어휘 암기 앱

## 🔴 이 저장소는 레슨 사이트와 짝이다 — 챕터 작업은 둘 다
- **단어장(여기)**: `C:\조지아어\단어장`, repo `georgiavocab`, https://georgiavocab.onrender.com/
- **레슨 사이트**: `C:\georgian-biliki`, repo `georgian-biliki`, https://georgian-biliki.onrender.com/

새 챕터를 만들거나 수정할 때는 **두 저장소를 항상 함께** 업데이트한다. 하나만 하면 어긋난다.
챕터 제작 전체 지침(난이도 곡선·블록 스키마·체크리스트)은 레슨 저장소의
**`C:\georgian-biliki\docs\CHAPTER_AUTHORING.md`** 를 먼저 읽을 것.

## 단어 데이터 = 마크다운(.md), JSON 아님
- 위치: `chapters/chapterN.md`
- 형식: `# 챕터 제목`, `## 섹션`, 그리고 `조지아어 = 한국어 (english)` 한 줄당 한 단어.
- `=` 없는 줄은 무시됨.
- `server.py`가 `chapter*.md`를 glob으로 자동 탐색 → **파일만 추가하면 메뉴 자동 등록**(코드 수정 불필요).

예시:
```markdown
# 챕터 6 — 나의 사무실에서 (ჩემს ოფისში)

## 사무실·사물
ოფისი = 사무실 (office)
მაგიდა = 책상, 테이블 (desk/table)
```

## 구조
- `server.py` — http.server 기반. `/api/chapters`, `/api/chapter/<n>`(md 파싱 JSON), `/tts`(Edge TTS) 제공. 포트 7823.
- `index.html` — 단일 페이지 앱(라이트너 박스 SRS, TTS). 챕터는 `/api/chapters`로 동적 로드.
- `chapters/chapter1.md` ~ `chapterN.md` — 어휘 데이터.

## 장기 원칙
- **총 24과까지 확장.** 어휘 난도도 과가 오를수록 상승.
- **다국어 대비.** 지금 한국어, 추후 영어(`(english)` 부분 활용 가능). 한국어를 조지아어에 섞지 말 것.

## 규칙
- 레슨의 `vocab` 항목과 어휘를 일치시키되 더 폭넓게(과당 80~90단어 권장).
- 커밋 메시지 영어 + `Co-Authored-By: Claude <noreply@anthropic.com>`.
