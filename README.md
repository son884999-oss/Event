# 오르페우스호의 마지막 기록

**주최: 대전 코디세이** · 3일 온라인 미스터리 추리 이벤트

이 저장소에는 참가자용 이미지 22장(오프닝 1, 문제 10, 후일담 10, 엔딩 1), 행사 종료 후 공개할 해설 이미지 10장, 그리고 **32장 전부를 담은 스포일러 포함 마스터 PDF**가 있다. 별도의 승인용 개요 이미지도 제공한다.

> **공개 범위:** 이 저장소는 공개 상태이며 `answer_release/`와 마스터 PDF에 모든 정답·결말이 포함된다. 참가자에게 저장소 전체 링크를 배포하면 스포일러가 공개된다.

## 시작

1. [최종 마스터 PDF](pdf/오르페우스호_마스터_운영기획서_2차.pdf)를 읽는다. 앞부분에 기획·운영 구조, 각 LOG에 정확한 Form 문항·해설·후일담, 뒷부분에 실행용 인계 프롬프트가 있다.
2. Google Drive·Forms·Sheets·Apps Script에 접근 가능한 Codex 작업 환경에 이 저장소를 연결한다.
3. [인계 프롬프트](automation/form_sheet_lottery_prompt.txt)를 그대로 전달한다. 이 프롬프트는 10개 문항의 정확한 원문·선택지·정답·후일담까지 포함하므로 PDF에서 복사해서 전달해도 된다.
4. 행사 일정, 참가 대상, 경품·수량, 예산, 개인정보 고지·보관·파기일을 운영자가 입력한다.
5. 테스트 Form/Sheet에서 문제 진행, 마지막 제출, DAY별 중복 처리, 점수 경계값, 추첨 중복 방지를 검증한 후 실제 Form을 공개한다.

## 파일

| 경로 | 내용 |
|---|---|
| `image_assets/participant/00_opening.png` | DAY 1 오프닝 |
| `image_assets/participant/01_LOG01_problem.png` ~ `10_LOG10_problem.png` | Google Form에 한 문제당 한 장씩 삽입 |
| `image_assets/participant/01_LOG01_story.png` ~ `10_LOG10_story.png` | 답변 후 다음 섹션에서 정답·오답 모두에게 공개 |
| `image_assets/participant/31_ending.png` | LOG 10 후일담 뒤 공개 |
| `image_assets/answer_release/` | 행사 종료 후 공개할 해설 이미지 10장 |
| `image_assets/proposal/overview.png` | 예산 승인용 전체 구조 이미지 |
| `pdf/오르페우스호_마스터_운영기획서_2차.pdf` | 핵심 32장 전부와 승인용 개요 이미지, 실행 프롬프트가 포함된 49쪽 마스터 PDF |
| `automation/form_sheet_lottery_prompt.txt` | 3개 Form, 중앙 Sheet, 채점·추첨 생성 지시 |
| `storyboard/production_blueprint.md` | 원문과 공개 구조 기준표 |
| `storyboard/validate_logic.py` | 10개 문제의 논리·선택지 검산 |
| `pdf/build_master.py` | PDF 수정·재생성용 원본 |

## 운영 핵심

- DAY 1: LOG 01~03 · 이상 징후
- DAY 2: LOG 04~06 · 마지막 회의
- DAY 3: LOG 07~10 · 퇴선 기록
- 공개된 DAY Form은 행사 종료까지 계속 열어 둔다.
- 각 문제에서 답을 고르면 다음 섹션의 후일담을 볼 수 있다. 정답과 오답 모두 같은 흐름이다. DAY Form의 최종 제출 버튼을 눌러야 응답이 저장된다.
- 동일 참가자의 같은 DAY 중복 제출은 가장 늦은 제출을 채점한다. 유효 제출이 하나라도 있으면 참가상 대상이다.
- 정답 0~4개는 추첨권 1장, 5~9개는 2장, 10개는 3장. 1인 1회 당첨.
- **이미지 속 AI 생성 글자는 참고용이다.** Form의 질문·선택지와 채점 기준은 인계 프롬프트의 정확한 운영 데이터를 사용한다.

라이브 Google Form/Sheet와 추첨 시스템은 이 저장소에 포함된 프롬프트를 운영 계정에서 실행해 생성한다. 계정 접근 권한과 미정 운영값이 필요하다.
