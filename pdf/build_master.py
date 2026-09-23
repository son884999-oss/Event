from __future__ import annotations

import argparse
import html
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
PARTICIPANT = ROOT / "image_assets" / "participant"
ANSWER = ROOT / "image_assets" / "answer_release"
PROPOSAL = ROOT / "image_assets" / "proposal"
PROMPT = ROOT / "automation" / "form_sheet_lottery_prompt.txt"
W, H = 841.89, 595.28  # A4 landscape
NAVY = colors.HexColor("#071B23")
NAVY2 = colors.HexColor("#102A32")
BRASS = colors.HexColor("#C7A66B")
PARCH = colors.HexColor("#E9DAB8")
PALE = colors.HexColor("#F2E8D3")
MUTED = colors.HexColor("#B4B7AE")
RED = colors.HexColor("#AC6F60")

pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBold", r"C:\Windows\Fonts\malgunbd.ttf"))


LOGS = [
    dict(n=1, day=1, old="Q4", scene="선장실의 잠긴 금고", q="2→6, 3→12, 4→20. 같은 규칙일 때 5→?", opts="25 / 30 / 35 / 40", answer="30", why="입력 n에 n+1을 곱한다. 5×6=30.", story="금고 속 항해 일지에서 비상절차 개시 흔적이 발견된다. 선박은 멈췄지만 기록은 의도적으로 남겨졌다.", role="비상 절차가 이미 시작됐다는 첫 증거"),
    dict(n=2, day=1, old="Q3", scene="의무실 약품 상자", q="10일치 약이 하루치씩 서로 다른 상자 10개에 담겨 있다. 첫날 약은 지금 바로 먹는다. 남은 상자들은 뒤섞일 수 있지만 이후에도 정해진 순서대로 하루에 하나씩 먹어야 한다. 마지막 날에는 상자 하나만 남는다. 순서를 헷갈리지 않으려면 처음에 최소 몇 개의 상자에 번호를 적어야 할까?", opts="7 / 8 / 9 / 10", answer="8", why="첫날 즉시 사용할 1개는 표시할 필요가 없다. 남은 9개 중 마지막 1개도 하나만 남으므로 표시할 필요가 없다. 따라서 8개.", story="의무실 기록에는 집단 부상이나 발병 흔적이 없다. 누군가 약품을 퇴선 준비물로 정리했다.", role="우발적 실종보다 준비된 퇴선을 시사"),
    dict(n=3, day=1, old="Q7", scene="무전실 연락망", q="A→B는 A가 B의 연락처를 가진다는 뜻이다. 연락망은 A→C, B→A, C→B, C→D, D→F, E→D, F→A다. 정확히 두 명의 연락처를 가진 사람은?", opts="A / B / C / D", answer="C", why="나가는 화살표를 세면 C→B와 C→D, 두 개다.", story="02:31, 끊어진 줄 알았던 무전이 여러 승무원을 거쳐 전해졌다. 실종 직전에도 연락망은 작동했다.", role="승무원 간 연락이 유지됐음을 확인"),
    dict(n=4, day=2, old="Q6", scene="회의실의 빈 좌석", q="여섯 사람이 원탁에 앉았다. 시계방향을 오른쪽으로 정의한다. E는 A의 오른쪽, D는 A의 왼쪽, C는 D의 맞은편, B는 A와 D에 인접하지 않는다. E의 맞은편에 앉은 사람은?", opts="A / B / C / F", answer="F", why="A를 고정하고 좌우의 E·D, D 맞은편의 C, B의 비인접 조건을 적용하면 E 맞은편에는 F가 남는다.", story="여섯 자리의 위치가 복원된다. 승무원들은 흔적 없이 사라진 것이 아니라 마지막 회의에 모여 있었다.", role="DAY 2의 ‘마지막 회의’ 장면을 물증화"),
    dict(n=5, day=2, old="Q8", scene="구명정 탑승 명단", q="A~F 중 정확히 네 명만 구명정에 탈 수 있다. A가 타면 B도 탄다. C와 D는 함께 탈 수 없다. E가 타면 A는 탈 수 없다. 가능한 조합은?", opts="A,B,C,F / A,C,E,F / B,C,D,F / A,D,E,F", answer="A,B,C,F", why="A와 B가 함께 타고, C·D 및 E·A 동시 탑승 금지를 모두 만족한다.", story="구명정 명단은 비상상황에서 급히 작성된 것이 아니다. 탑승 가능 인원이 미리 검토되어 있었다.", role="계획적인 퇴선 준비를 드러냄"),
    dict(n=6, day=2, old="Q9", scene="마지막 교대 기록", q="C는 A보다 먼저, B는 D보다 먼저, E는 정확히 세 번째, D는 A보다 먼저 만난다. 다음 보기 중 가능한 순서는?", opts="C-B-E-A-D / B-C-E-D-A / C-D-E-B-A / B-A-E-C-D", answer="B-C-E-D-A", why="네 조건을 동시에 만족하는 보기는 B-C-E-D-A뿐이다.", story="교대 기록의 순서는 준비된 퇴선 계획과 맞물린다. 승무원은 한꺼번에 사라진 것이 아니었다.", role="퇴선이 단계적으로 이뤄졌음을 입증"),
    dict(n=7, day=3, old="Q1", scene="조타실의 고장 난 시계", q="첫 번째 종은 0초, 여섯 번째 종은 10초에 울린다. 같은 간격이면 열두 번째 종은 몇 초에 울릴까?", opts="20초 / 21초 / 22초 / 24초", answer="22초", why="첫째부터 여섯째까지는 5간격이므로 간격당 2초. 열두째는 첫째부터 11간격 뒤인 22초.", story="종의 간격으로 조타실 기록의 시간 오차를 바로잡는다. 마지막 퇴선 시각을 가리키는 단서가 나타난다.", role="마지막 시각을 복원하는 계산 단서"),
    dict(n=8, day=3, old="Q2", scene="식량창고의 마지막 배급", q="식량 17개가 있다. 번갈아 한 번에 1~3개를 가져간다. 마지막을 가져간 사람이 이기며 양쪽 모두 최선으로 선택한다. 선공이 처음 가져가야 할 개수는?", opts="1개 / 2개 / 3개 / 상관없음", answer="1개", why="먼저 1개를 가져가 16개를 남긴다. 이후 상대가 가져간 수와 내 수의 합을 매번 4로 만든다.", story="식량은 무작위로 버려진 것이 아니라 이동 인원과 거리에 맞춰 배분되었다. 목적지는 배 밖에 있었다.", role="배 밖으로 향한 이동의 흔적"),
    dict(n=9, day=3, old="Q5", scene="식당의 원탁", q="1~8번 접시가 시계방향으로 놓여 있다. 먼저 1번 접시를 제거한다. 그 자리에서 시계방향으로 가장 가까운 남은 접시를 첫 번째로 세고, 두 번째 남은 접시를 제거한다. 같은 방법을 반복한다. 마지막 번호는?", opts="5 / 6 / 7 / 8", answer="8", why="제거 순서는 1→3→5→7→2→6→4이고, 8번이 남는다.", story="마지막 접시 아래에서 K-17 무인 기상관측소 좌표가 발견된다. 승무원이 향한 곳이 드러난다.", role="퇴선 목적지 K-17을 공개"),
    dict(n=10, day=3, old="Q10", scene="세 개의 비상문", q="A는 ‘탈출문은 B’, B는 ‘탈출문은 C가 아니다’, C는 ‘탈출문은 B가 아니다’라고 주장한다. 세 주장 중 정확히 하나만 참일 때 탈출문은?", opts="A / B / C / 결정할 수 없음", answer="C", why="탈출문을 A·B·C로 가정해 참인 주장 수를 세면 C일 때만 정확히 하나가 참이다.", story="C 문 뒤의 기록이 복원된다. 02:43 전원 퇴선 완료. 통신장치 파손 뒤 승무원은 K-17로 이동했다.", role="최종 퇴선 경로와 02:43 기록 복원"),
]


def style(size=11, color=PALE, bold=False, leading=None, align=TA_LEFT):
    return ParagraphStyle(
        name=f"s{size}{bold}{align}", fontName="MalgunBold" if bold else "Malgun",
        fontSize=size, leading=leading or size * 1.55, textColor=color,
        alignment=align, wordWrap="CJK", splitLongWords=True, spaceAfter=0,
    )


def para(c, s, x, top, width, size=11, color=PALE, bold=False, leading=None, align=TA_LEFT):
    p = Paragraph(html.escape(s).replace("\n", "<br/>"), style(size, color, bold, leading, align))
    _, h = p.wrap(width, 1000)
    p.drawOn(c, x, top-h)
    return top-h


def image_contain(c, path, x, y, w, h):
    if not Path(path).exists():
        return False
    im = Image.open(path)
    iw, ih = im.size
    scale = min(w/iw, h/ih)
    dw, dh = iw*scale, ih*scale
    # Keep the original PNG asset intact; compress only its copy embedded in PDF.
    encoded = BytesIO()
    im.convert("RGB").save(encoded, format="JPEG", quality=80, subsampling=0, optimize=True)
    encoded.seek(0)
    c.drawImage(ImageReader(encoded), x+(w-dw)/2, y+(h-dh)/2, dw, dh, preserveAspectRatio=True)
    return True


def line(c, x1, y1, x2, y2, color=BRASS, width=0.7):
    c.setStrokeColor(color); c.setLineWidth(width); c.line(x1,y1,x2,y2)


class Book:
    def __init__(self, output, version):
        self.c = canvas.Canvas(str(output), pagesize=(W,H), pageCompression=1)
        self.page = 0
        self.version = version
        self.c.setTitle(f"오르페우스호의 마지막 기록 | 마스터 운영기획서 {version}")
        self.c.setAuthor("대전 코디세이")

    def shell(self, tag, title=None, subtitle=None):
        self.page += 1
        c=self.c
        c.setFillColor(NAVY); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(NAVY2); c.rect(0,H-8,W,8,fill=1,stroke=0)
        line(c,28,H-31,W-28,H-31)
        para(c,"ORPHEUS  /  대전 코디세이",32,H-15,300,8,BRASS,True)
        para(c,tag,W-280,H-15,245,8,BRASS,True,align=2)
        if title:
            para(c,title,32,H-45,W-64,25,PARCH,True,31)
        if subtitle:
            para(c,subtitle,34,H-86,W-68,10,MUTED)
        line(c,28,27,W-28,27)
        para(c,f"MASTER PLAN  ·  {self.version}  ·  SPOILER INCLUDED",32,22,420,7,MUTED)
        para(c,f"{self.page:02d}",W-65,22,30,8,BRASS,True,align=2)

    def next(self):
        self.c.showPage()

    def save(self):
        self.c.save()


def block(c, x, top, w, label, body, accent=BRASS, size=10):
    c.setFillColor(NAVY2); c.roundRect(x, top-118, w, 118, 7, fill=1, stroke=0)
    c.setStrokeColor(accent); c.setLineWidth(1); c.line(x+14,top-18,x+w-14,top-18)
    para(c,label,x+14,top-3,w-28,11,accent,True)
    para(c,body,x+14,top-29,w-28,size,PALE)


def cover(b):
    b.shell("PROJECT OVERVIEW")
    c=b.c
    image_contain(c,PARTICIPANT/"00_opening.png",28,47,355,510)
    line(c,402,58,402,535)
    para(c,"3일 온라인 미스터리 추리 이벤트",425,520,370,12,BRASS,True)
    para(c,"오르페우스호의\n마지막 기록",425,475,370,29,PARCH,True,39)
    para(c,"사라진 승무원, 남겨진 10개의 기록. 참가자는 3일 동안 조각난 증거를 풀어 마지막 퇴선 경로를 복원한다.",425,368,360,13,PALE,False,21)
    para(c,"예산 승인용 제안 + 실행 가능한 운영 마스터 플랜",425,254,360,12,BRASS,True)
    para(c,"주최  대전 코디세이\n공개  DAY 1 이상 징후 → DAY 2 마지막 회의 → DAY 3 퇴선 기록\n미정  일정·참가 대상·경품·예산 금액",425,213,360,11,PALE)
    para(c,"※ 운영자·승인자용 스포일러 포함 문서",425,94,360,9,RED,True)
    b.next()


def overview_page(b):
    path=PROPOSAL/"overview.png"
    if not path.exists():
        return
    b.shell("VISUAL OVERVIEW", "한눈에 보는 오르페우스호", "콘텐츠·참여·운영을 하나의 시각 구조로 묶은 승인용 개요")
    c=b.c
    image_contain(c,path,33,45,342,450)
    line(c,393,62,393,480)
    para(c,"10개의 기록, 3일의 재방문",415,468,370,15,PARCH,True)
    para(c,"이상 징후에서 시작해 마지막 회의와 퇴선 기록으로 이어지는 서사. 참가자는 문제를 풀 때마다 새로운 사실을 확인한다.",415,425,355,11,PALE)
    para(c,"하나의 운영 구조",415,324,355,14,BRASS,True)
    para(c,"DAY별 Form 3개, 문제 이미지 10장, 응답 직후 후일담 10장. 중앙 Sheet가 참가·점수·추첨권을 일관되게 집계한다.",415,288,355,11,PALE)
    para(c,"예산 승인 관점",415,187,355,14,BRASS,True)
    para(c,"콘텐츠 제작물과 운영 체계가 같은 기획 안에서 연결된다. 실제 일정·대상·경품·금액은 승인 시 입력한다.",415,151,355,11,PALE)
    b.next()


def brief(b):
    b.shell("DECISION BRIEF","3분 안에 보는 기획","결재자가 알아야 할 콘텐츠, 참여 방식, 운영 가능성을 한 장에 묶었다.")
    c=b.c
    block(c,33,455,244,"무엇을 하는가","무인 상태로 발견된 탐사선의 마지막 10개 기록을 3일에 걸쳐 푼다. 각 답변 뒤 후일담이 열리고, 마지막에 전원 구조의 진상이 확인된다.")
    block(c,299,455,244,"왜 필요한가","짧은 참여형 서사로 재방문을 만든다. 이미지·퍼즐·후일담이 하나의 세계관을 이루며, 제출 데이터로 참여와 성과를 확인할 수 있다.")
    block(c,565,455,244,"어떻게 운영하나","DAY별 Google Form 3개와 중앙 Sheet 1개. 응답은 종료 때까지 접수하고 자동으로 중복 제거, 채점, 참가상 및 추첨권을 집계한다.")
    line(c,40,306,802,306)
    para(c,"승인 요청 범위",40,290,190,16,PARCH,True)
    para(c,"콘텐츠 이미지 제작  ·  Form/Sheet 구축  ·  행사 운영 및 검수  ·  참가상/추첨 경품",40,255,755,13,PALE)
    para(c,"예산 금액  [추후 입력]        경품 종류·수량  [추후 입력]        일정·대상  [추후 입력]",40,208,755,11,BRASS,True)
    para(c,"승인 판단 기준",40,145,180,14,PARCH,True)
    para(c,"① 10개 문제와 스토리가 연결되는가   ② 3개 Form의 제출·집계가 실제로 작동하는가   ③ 당첨 기준과 개인정보 운영이 검증 가능한가",40,113,755,10,PALE)
    b.next()


def journey(b):
    b.shell("PARTICIPANT EXPERIENCE","참가자가 실제로 겪는 흐름","정답 여부에 따라 이야기가 끊기지 않는다.")
    c=b.c
    steps=[("01","접속","공개된 DAY Form에 접속해 이름·휴대전화번호와 동의 항목을 입력한다."),
           ("02","기록 탐색","문제 이미지 1장을 보고, 같은 섹션의 정확한 텍스트 문제를 읽어 답을 선택한다."),
           ("03","후일담 확인","응답 뒤 다음 섹션에서 후일담을 본다. 정답·오답 모두 같은 이야기로 이동한다."),
           ("04","DAY 제출","해당 DAY 마지막 제출 버튼을 눌러야 응답이 저장된다. 이전 DAY Form도 행사 종료까지 열린다."),
           ("05","엔딩·추첨","DAY 3에서 최종 진상을 확인하고, 종료 후 점수에 따라 추첨권 1~3장이 부여된다.")]
    y=465
    for num,title,body in steps:
        c.setFillColor(BRASS); c.circle(62,y-17,20,fill=1,stroke=0)
        para(c,num,48,y-5,30,10,NAVY,True,align=TA_CENTER)
        para(c,title,99,y,132,15,PARCH,True)
        para(c,body,245,y,540,11,PALE)
        if num!="05": line(c,62,y-37,62,y-76,MUTED)
        y-=88
    b.next()


def story_arc(b):
    b.shell("NARRATIVE ARC","3일 동안 바뀌는 사건의 해석","각 DAY는 새 정보로 앞선 단서를 다시 읽게 한다.")
    c=b.c
    days=[
      ("DAY 1","이상 징후","LOG 01–03","무인 상태로 발견된 오르페우스호. 금고·의무실·무전실 기록을 통해 비상절차가 시작되고 승무원 간 연락이 계속됐음을 알게 된다.","질문: 그들은 갑자기 사라졌는가?"),
      ("DAY 2","마지막 회의","LOG 04–06","회의실 자리, 구명정 명단, 교대 순서가 이어진다. 급박한 탈출이 아니라 누군가 인원과 순서를 준비한 퇴선이었다.","전환: 실종 → 계획된 퇴선"),
      ("DAY 3","퇴선 기록","LOG 07–10","시각·식량·좌표·비상문을 복원한다. 02:43 전원 퇴선 후 K-17로 이동했고, 다음 날 조사선에 전원 구조됐다.","결론: 마지막 기록은 생존의 증거"),
    ]
    x=33
    for day,title,logs,body,tag in days:
        c.setFillColor(NAVY2); c.roundRect(x,132,244,330,8,fill=1,stroke=0)
        c.setStrokeColor(BRASS); c.roundRect(x,132,244,330,8,fill=0,stroke=1)
        para(c,day,x+16,443,210,12,BRASS,True)
        para(c,title,x+16,409,210,22,PARCH,True)
        para(c,logs,x+16,367,210,10,MUTED)
        line(c,x+16,348,x+228,348)
        para(c,body,x+16,328,210,12,PALE)
        para(c,tag,x+16,180,210,10,BRASS,True)
        x+=266
    b.next()


def structure(b):
    b.shell("CONTENT MAP","공개 순서와 제작 자산","새 LOG 번호는 공개 순서다. 옛 Q 번호는 제작 참고용으로만 남긴다.")
    c=b.c
    xcols=[38,115,188,255,485]
    headers=["DAY","새 LOG","기존","장소 / 문제","서사 기능"]
    for x,h in zip(xcols,headers): para(c,h,x,464,210,10,BRASS,True)
    line(c,36,444,804,444)
    y=431
    for l in LOGS:
        vals=[str(l["day"]),f'{l["n"]:02d}',l["old"],l["scene"],l["role"]]
        for x,val in zip(xcols,vals): para(c,val,x,y,210 if x<485 else 310,9,PALE)
        line(c,36,y-23,804,y-23,MUTED,0.25)
        y-=34
    para(c,"공개 이미지  00 오프닝 + 10 문제 + 10 후일담 + 31 엔딩  /  해설 10장은 행사 종료 후 별도 공개",38,82,758,10,BRASS,True)
    b.next()


def log_page(b,l):
    n=l["n"]
    b.shell(f'DAY {l["day"]}  /  LOG {n:02d}',f'{n:02d}  {l["scene"]}',f'기존 {l["old"]}  ·  승인·운영자용 해답 포함')
    c=b.c
    path=PARTICIPANT/f'{n:02d}_LOG{n:02d}_problem.png'
    image_contain(c,path,33,45,335,452)
    line(c,384,60,384,490)
    x=407; w=395
    y=488
    y=para(c,"FORM에 넣을 정확한 문항",x,y,w,10,BRASS,True)-8
    y=para(c,l["q"],x,y,w,11,PALE,False,17)-12
    y=para(c,"선택지  "+l["opts"],x,y,w,10,PARCH,True)-23
    line(c,x,y,x+w,y); y-=15
    y=para(c,"정답  "+l["answer"],x,y,w,13,BRASS,True)-7
    y=para(c,"해설  "+l["why"],x,y,w,9.5,PALE)-17
    y=para(c,"응답 직후 공개되는 후일담",x,y,w,10,BRASS,True)-6
    y=para(c,l["story"],x,y,w,9.5,PALE)-15
    if y>78: para(c,"사건 연결  "+l["role"],x,y,w,9,MUTED)
    b.next()


def ending(b):
    b.shell("ENDING / SPOILER","02:43, 전원 퇴선 완료","열 번째 기록의 결론은 실종이 아니라 구조다.")
    c=b.c
    image_contain(c,PARTICIPANT/"31_ending.png",34,47,345,450)
    line(c,398,62,398,480)
    para(c,"최종 복원",420,470,360,12,BRASS,True)
    para(c,"통신장치가 파손된 뒤 승무원들은 K-17 무인 기상관측소로 이동했다. 다음 날 인근 조사선이 승무원 전원을 구조한 것으로 확인된다.",420,435,355,14,PALE,False,23)
    para(c,"참가자 공개 순서",420,296,355,11,BRASS,True)
    para(c,"LOG 10 응답 → 후일담에서 퇴선 기록 공개 → 엔딩 이미지 → DAY 3 Form 마지막 제출",420,265,355,11,PALE)
    para(c,"해설 이미지 10장은 행사 종료 후 별도 공개한다.",420,170,355,11,RED,True)
    b.next()


def forms(b):
    b.shell("GOOGLE FORMS","DAY별 Form 3개의 실제 구성","이미지는 문제당 정확히 한 장, 원문은 별도 질문 텍스트로 넣는다.")
    c=b.c
    blocks=[
      ("DAY 1 Form","본인 확인·동의 → 오프닝 → LOG 01 문제/응답 → 후일담 → LOG 02 → 후일담 → LOG 03 → 후일담 → 제출"),
      ("DAY 2 Form","본인 확인·동의 → 전일 요약 → LOG 04 문제/응답 → 후일담 → LOG 05 → 후일담 → LOG 06 → 후일담 → 제출"),
      ("DAY 3 Form","본인 확인·동의 → 전일 요약 → LOG 07~10 각각 문제/응답/후일담 → 엔딩 → 제출"),
    ]
    y=465
    for title,body in blocks:
        block(c,38,y,766,title,body,size=10)
        y-=134
    para(c,"섹션 이동은 응답 저장이 아니다. 각 DAY Form의 최종 제출까지 완료해야 해당 DAY 점수에 반영된다.",39,63,760,9,RED,True)
    b.next()


def data_page(b):
    b.shell("DATA MODEL","중앙 Sheet: 원본과 확정 집계를 분리","재집계가 가능하도록 원본응답은 보존한다.")
    c=b.c
    rows=[
      ("설정","행사 시각, 경품 수량, 운영자, 개인정보 문안과 보관일"),
      ("문항/정답","LOG 01~10의 정확한 텍스트·선택지·정답"),
      ("원본응답","Form ID, DAY, 제출시각, 응답 ID, 이름, 전화번호, 선택값"),
      ("유효 DAY 응답","같은 번호·같은 DAY의 가장 늦은 제출 1건"),
      ("참가자 집계","DAY별 유효 점수, 합계 0~10, 참가상 대상 여부"),
      ("추첨권/결과","1·2·3장 산정, 후보 풀, 당첨 순서, 중복 당첨 차단"),
      ("운영 로그/검토","트리거, 재집계, 추첨 설정, 이름·번호 충돌, 오류"),
    ]
    y=463
    for title,desc in rows:
        c.setFillColor(NAVY2);c.roundRect(37,y-43,766,48,4,fill=1,stroke=0)
        para(c,title,51,y,160,11,BRASS,True)
        para(c,desc,215,y,575,10,PALE)
        y-=59
    para(c,"식별자: 정규화한 휴대전화번호 + 이름 확인. 동일 번호의 상이한 이름은 자동 병합하지 않고 운영자 검토.",39,52,765,9,RED,True)
    b.next()


def raffle(b):
    b.shell("SCORING & DRAW","참가 인정·추첨권·전자 추첨","정답을 하나도 맞히지 못해도 유효 제출자는 참가상 대상이다.")
    c=b.c
    tiers=[("0–4개 정답","추첨권 1장"),("5–9개 정답","추첨권 2장"),("10개 정답","추첨권 3장")]
    x=39
    for title,value in tiers:
        c.setFillColor(NAVY2);c.roundRect(x,341,238,114,7,fill=1,stroke=0)
        para(c,title,x+18,434,204,12,PARCH,True)
        para(c,value,x+18,393,204,20,BRASS,True)
        x+=262
    para(c,"유효 제출",40,316,120,12,BRASS,True)
    para(c,"동의·이름·전화번호가 있는 DAY Form 하나 이상. 같은 사람이 같은 DAY에 재제출하면 마지막 제출만 채점한다.",167,316,630,10,PALE)
    line(c,40,260,802,260)
    para(c,"추첨 실행",40,241,120,12,BRASS,True)
    para(c,"사람별 추첨권 수로 가중 추첨 → 당첨 시 그 사람의 모든 표를 제거 → 다음 경품 추첨. 1인 1회 당첨. 후보·설정·순서·시각을 기록한다.",167,241,630,10,PALE)
    line(c,40,179,802,179)
    para(c,"실제 운영",40,159,120,12,BRASS,True)
    para(c,"경품 수량, 추첨 시각, 공개 범위는 추후 입력한다. 테스트 추첨과 실제 추첨을 분리하고 결과 공개 때 전화번호를 마스킹한다.",167,159,630,10,PALE)
    b.next()


def ops(b):
    b.shell("RUNBOOK","운영 체크리스트와 복구 경로","예정 시각과 담당자는 설정 시트에서 확정한다.")
    c=b.c
    phases=[
      ("준비","원문·이미지 검수 / 개인정보 문안 입력 / 경품·예산 확정 / Forms 3개·Sheet 생성 / 테스트 계정으로 전 구간 제출"),
      ("DAY 1","Form 1 공개 / 오프닝·LOG 01~03 섹션 확인 / 응답·시트·트리거 확인"),
      ("DAY 2","Form 2 공개 / Form 1 열린 상태 확인 / 마지막 제출 중복 처리와 점수 집계 확인"),
      ("DAY 3","Form 3 공개 / Forms 1·2 열린 상태 확인 / LOG 10 뒤 엔딩 확인 / 종료 때 세 Form 동시 마감"),
      ("종료 후","원본 재집계 / 참가상 목록 확정 / 추첨 설정 확인 / 실제 추첨·로그 보존 / 해설 이미지 10장 공개"),
    ]
    y=463
    for title,body in phases:
        para(c,title,42,y,100,11,BRASS,True)
        para(c,body,154,y,638,10,PALE)
        line(c,40,y-48,802,y-48,MUTED,0.3)
        y-=78
    para(c,"트리거 오류 시: 응답 원본을 지우지 말고 설치 상태 점검 → 트리거 재설치 → 전체 재집계 → 샘플 대조.",42,62,755,9,RED,True)
    b.next()


def tests(b):
    b.shell("QUALITY GATE","공개 전 검증해야 할 경계 사례","1차 PDF와 자동화 프롬프트를 함께 사용한다.")
    c=b.c
    tests=[
      "정답 0·4·5·9·10개에서 추첨권 1·1·2·2·3장",
      "오답이어도 다음 후일담으로 이동하고 정답은 보이지 않음",
      "DAY별 마지막 제출만 유효하며 다른 DAY 점수는 합산",
      "LOG 02 약품 8개, LOG 09 접시 제거 순서, LOG 10 참인 주장 수 검산",
      "DAY 3에도 DAY 1·2 Forms 접수 가능, 종료 시 세 Form 모두 닫힘",
      "동일 전화번호·다른 이름은 검토 목록; 참가상은 1인 1회",
      "추첨권 가중치 반영, 당첨자 재당첨 불가, 실제 추첨 재실행 차단",
      "이미지 누락·트리거 중복·재집계 후 점수 변화 여부 확인",
    ]
    y=465
    for i,t in enumerate(tests,1):
        c.setStrokeColor(BRASS);c.rect(41,y-14,13,13,stroke=1,fill=0)
        para(c,f"{i:02d}  {t}",67,y,725,10,PALE)
        y-=47
    b.next()


def budget(b):
    b.shell("BUDGET CASE","예산 투입 항목과 기대효과","금액·수량은 승인 과정에서 입력한다.")
    c=b.c
    items=[
      ("콘텐츠 제작","32장 이미지, 문제·후일담·해설 검수, 기획 PDF","[금액 입력]"),
      ("운영 자동화","Form/Sheet/Apps Script 구축 및 사전 테스트","[금액 입력]"),
      ("참가상","유효 제출자 지급용 품목·예상 수량","[품목·수량·금액 입력]"),
      ("추첨 경품","점수별 추첨 구조에 맞춘 경품","[품목·수량·금액 입력]"),
      ("운영·예비","3일 모니터링, 문의 대응, 오류·추가 수요","[금액 입력]"),
    ]
    y=455
    for name,desc,cost in items:
        para(c,name,43,y,160,11,BRASS,True)
        para(c,desc,190,y,420,10,PALE)
        para(c,cost,627,y,170,9,PARCH)
        line(c,41,y-43,802,y-43,MUTED,0.3)
        y-=66
    para(c,"기대효과",42,112,130,13,PARCH,True)
    para(c,"3일 재방문, 완주율, 문제별 응답, 참가자 수, 추첨 참여를 실제 제출 데이터로 측정한다. 콘텐츠 자산은 이후 전시·홍보용으로 재사용 가능하다.",174,112,620,10,PALE)
    b.next()


def assets(b):
    b.shell("HANDOFF","파일 구조와 실행 인계","신규 Codex는 아래 파일을 함께 받으면 된다.")
    c=b.c
    rows=[
      ("storyboard/production_blueprint.md","정확한 문제·선택지·정답·후일담과 공개 규칙의 단일 기준"),
      ("image_assets/participant/","오프닝, LOG 01~10 문제, 후일담, 엔딩 이미지"),
      ("image_assets/answer_release/","행사 종료 후 공개하는 LOG 01~10 해설 이미지"),
      ("automation/form_sheet_lottery_prompt.txt","Form 3개·Sheet·채점·추첨 자동화 생성 지시"),
      ("pdf/","스포일러 포함 승인·운영용 마스터 PDF"),
    ]
    y=453
    for path,desc in rows:
        para(c,path,42,y,360,10,BRASS,True)
        para(c,desc,415,y,385,9.5,PALE)
        line(c,40,y-46,802,y-46,MUTED,0.3)
        y-=76
    para(c,"실제 계정 연동·공개 전에는 일정, 대상, 경품, 예산, 개인정보 문안·파기일을 입력하고 Form 및 Sheet 화면을 점검한다.",42,60,755,9,RED,True)
    b.next()


def asset_page(b,l,kind):
    n=l["n"]
    label,folder=("응답 직후 공개 · 후일담",PARTICIPANT) if kind=="story" else ("행사 종료 후 공개 · 해설",ANSWER)
    path=folder/f"{n:02d}_LOG{n:02d}_{kind}.png"
    if not path.exists():
        return
    b.shell(f"VISUAL ASSET  /  LOG {n:02d}",f"{n:02d}  {label}",l["scene"])
    image_contain(b.c,path,35,45,360,450)
    line(b.c,410,62,410,485)
    x=433
    para(b.c,"정확한 운영 원문",x,473,350,12,BRASS,True)
    if kind=="story":
        para(b.c,l["story"],x,432,345,13,PALE)
        para(b.c,"이 이미지는 정답·오답 모두의 응답 다음 섹션에 삽입한다.",x,300,345,10,BRASS,True)
    else:
        para(b.c,"정답  "+l["answer"],x,432,345,17,PARCH,True)
        para(b.c,l["why"],x,386,345,12,PALE)
        para(b.c,"행사 종료 전에는 참가자 Form에 삽입하지 않는다.",x,250,345,10,RED,True)
    b.next()


def prompt_appendix(b):
    b.shell("AUTOMATION PROMPT","실행용 인계 프롬프트","같은 내용은 automation/form_sheet_lottery_prompt.txt에도 저장되어 있다.")
    c=b.c
    text=PROMPT.read_text(encoding="utf-8")
    blocks=[x.strip() for x in text.split("\n\n") if x.strip()]
    y=475
    for item in blocks:
        p=Paragraph(html.escape(item).replace("\n","<br/>"),style(9.2,PALE,False,14))
        _,h=p.wrap(760,2000)
        if y-h<55:
            b.next()
            b.shell("AUTOMATION PROMPT / CONTINUED","실행용 인계 프롬프트")
            c=b.c;y=484
        p.drawOn(c,40,y-h)
        y-=h+12
    b.next()


def references(b):
    b.shell("SOURCE NOTES","구현 API 참고","Google Forms·Apps Script 기능은 공식 문서를 확인해 설계했다.")
    c=b.c
    sources=[
      ("Forms Form API","https://developers.google.com/apps-script/reference/forms/form"),
      ("ImageItem","https://developers.google.com/apps-script/reference/forms/image-item"),
      ("Form 제출 이벤트","https://developers.google.com/apps-script/guides/triggers/events"),
      ("FormTriggerBuilder","https://developers.google.com/apps-script/reference/script/form-trigger-builder"),
    ]
    y=462
    for label,url in sources:
        para(c,label,42,y,190,12,BRASS,True)
        para(c,url,220,y,565,9,PALE)
        y-=66
    para(c,"시행 전 API·권한·계정 정책은 실제 운영 환경에서 다시 확인한다.",42,140,750,10,RED,True)
    b.next()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--version", choices=["v1","v2"], default="v1")
    args=ap.parse_args()
    out=ROOT/"pdf"/("오르페우스호_마스터_운영기획서_1차.pdf" if args.version=="v1" else "오르페우스호_마스터_운영기획서_2차.pdf")
    b=Book(out,args.version.upper())
    cover(b);overview_page(b);brief(b);journey(b);story_arc(b);structure(b)
    for l in LOGS:
        log_page(b,l)
        if args.version=="v2":
            asset_page(b,l,"story")
            asset_page(b,l,"answer")
    ending(b);forms(b);data_page(b);raffle(b);ops(b);tests(b);budget(b);assets(b)
    prompt_appendix(b);references(b)
    b.save()
    print(out)
    print(f"pages={b.page}")


if __name__=="__main__":
    main()

