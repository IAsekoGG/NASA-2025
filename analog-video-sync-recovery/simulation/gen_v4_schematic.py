# Генерує SVG схеми v4 з примітивів (щоб не малювати сотні ліній вручну)
out = []
def L(x1,y1,x2,y2,c="currentColor",w=1.4): out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>')
def T(x,y,s,size=10,anchor="start",c="currentColor",mono=True,op=None):
    f=' font-family="IBM Plex Mono,monospace"' if mono else ''
    o=f' opacity="{op}"' if op else ''
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}"{f}{o}>{s}</text>')
def DOT(x,y,c="currentColor",r=3): out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
def GND(x,y):
    L(x-8,y,x+8,y,w=1.6); L(x-5,y+4,x+5,y+4,w=1.6); L(x-2,y+8,x+2,y+8,w=1.6)
def RV(x,y1,y2,label,side="r"):  # вертикальний резистор між y1..y2 (тіло 40)
    ym=(y1+y2)/2; out.append(f'<rect x="{x-6}" y="{ym-20}" width="12" height="40" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>')
    L(x,y1,x,ym-20); L(x,ym+20,x,y2)
    if side=="r": T(x+12,ym+4,label)
    else: T(x-12,ym+4,label,anchor="end")
def RH(x1,x2,y,label,above=True):
    xm=(x1+x2)/2; out.append(f'<rect x="{xm-20}" y="{y-6}" width="40" height="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>')
    L(x1,y,xm-20,y); L(xm+20,y,x2,y); T(xm,y-10 if above else y+20,label,anchor="middle")
def CV(x,y1,y2,label,side="r"):  # вертикальний конденсатор (пластини горизонтальні)
    ym=(y1+y2)/2; L(x,y1,x,ym-4); L(x-10,ym-4,x+10,ym-4,w=2); L(x-10,ym+4,x+10,ym+4,w=2); L(x,ym+4,x,y2)
    if side=="r": T(x+14,ym+4,label)
    else: T(x-14,ym+4,label,anchor="end")
def CH(x1,x2,y,label,above=True):
    xm=(x1+x2)/2; L(x1,y,xm-4,y); L(xm-4,y-10,xm-4,y+10,w=2); L(xm+4,y-10,xm+4,y+10,w=2); L(xm+4,y,x2,y)
    T(xm,y-14 if above else y+22,label,anchor="middle")
def DV(x,y1,y2,label,cathode="top",side="l"):  # вертикальний діод
    ym=(y1+y2)/2
    if cathode=="top":
        L(x,y1,x,ym-10); L(x-9,ym-10,x+9,ym-10,w=2); out.append(f'<polygon points="{x-9},{ym+10} {x+9},{ym+10} {x},{ym-10}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(x,ym+10,x,y2)
    else:
        L(x,y1,x,ym-10); out.append(f'<polygon points="{x-9},{ym-10} {x+9},{ym-10} {x},{ym+10}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(x-9,ym+10,x+9,ym+10,w=2); L(x,ym+10,x,y2)
    if side=="l": T(x-13,ym+4,label,anchor="end")
    else: T(x+13,ym+4,label)
def DH(x1,x2,y,label,cathode="right",below=False):
    xm=(x1+x2)/2
    if cathode=="right":
        L(x1,y,xm-10,y); out.append(f'<polygon points="{xm-10},{y-9} {xm-10},{y+9} {xm+10},{y}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(xm+10,y-9,xm+10,y+9,w=2); L(xm+10,y,x2,y)
    else:
        L(x1,y,xm-10,y); L(xm-10,y-9,xm-10,y+9,w=2); out.append(f'<polygon points="{xm+10},{y-9} {xm+10},{y+9} {xm-10},{y}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(xm+10,y,x2,y)
    T(xm,y+22 if below else y-14,label,anchor="middle")
def NPN(x,y,label,mirror=False,lab_dx=26):  # смуга бази в x, центр y; колектор вгору-вправо, емітер вниз-вправо
    s=-1 if mirror else 1
    out.append(f'<circle cx="{x+s*8}" cy="{y}" r="15" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".55"/>')
    L(x,y-14,x,y+14,w=2.2); L(x,y-6,x+s*18,y-18); L(x,y+6,x+s*18,y+18)
    ex,ey=x+s*18,y+18
    out.append(f'<polygon points="{ex},{ey} {ex-s*8},{ey-2} {ex-s*4},{ey-7}" fill="currentColor"/>')
    T(x+s*lab_dx+(0 if not mirror else 0),y-18 if mirror else y+4, label) if not mirror else T(x-24,y+4,label,anchor="end")
def RAIL(x,y,txt,c="var(--rail)"): DOT(x,y,c); T(x,y-8,txt,11,"middle",c)
def FLAG(x,y,txt,c="var(--ok)"): out.append(f'<polygon points="{x-6},{y} {x},{y-6} {x+66},{y-6} {x+66},{y+6} {x},{y+6}" fill="none" stroke="{c}" stroke-width="1.2"/>'); T(x+3,y+4,txt,9.5,c=c)
V="var(--video)"; K="var(--ctrl)"

# ===== Ряд 1: аналоговий тракт =====
out.append('<circle cx="40" cy="80" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>'); T(40,64,"J1 IN",11,"middle")
L(46,80,150,80,V,2.2); DOT(80,80,V,3.5); RV(80,80,150,"R1 75Ω"); GND(80,150)
DOT(110,80,V,3.5); L(110,80,110,330,V,1.6)
CH(150,158,80,"C4 470 nF"); L(158,80,300,80,V,2.2)  # C4 плати 150/158: підправимо нижче
DOT(220,80,V,3.5); T(228,74,"P0",11,c=V)
RV(220,80,135,"R16 1k",side="l"); DV(220,135,175,"D1",cathode="top",side="r"); DOT(220,175); T(232,179,"X")
RH(160,220,175,"R14 10k"); RAIL(145,175,"+5 V"); L(145,175,160,175,"var(--rail)")
DV(220,175,215,"D2",cathode="bottom",side="l"); FLAG(214,228,"V_CL 1.7 V")
DOT(260,80,V,3.5); RV(260,80,150,"R15 220k"); GND(260,150)
RH(300,340,80,"R_s 1k"); L(340,80,940,80,V,2.2); DOT(360,80,V,3.5); T(360,70,"P",11,"middle",V)
# Q2 шунт
DOT(878,80,V,3.5); L(878,80,878,106); NPN(860,133,"Q2 BC547"); L(878,160,878,185); FLAG(872,200,"V_E 1.6 V")
DOT(790,133); T(782,127,"W",10,"end"); RH(790,860,133,"R11 1k")
L(790,133,650,133); DOT(720,133); RV(720,133,200,"R10 2.2k",side="l"); GND(720,200)
DV(650,133,180,"D6",cathode="top",side="l"); GND(650,180)
CV(790,133,320,"C9 3.9 nF")   # стояк від pin 4 до W; пластини всередині
# Дарлінгтон
NPN(940,80,"Q3+Q4 BC547"); T(954,96,"(Дарлінгтон)",10,op=".7")
L(958,62,958,36,"var(--rail)"); RAIL(958,36,"+5 V")
L(958,98,958,140); DOT(958,140); RV(958,140,204,"R12 100Ω"); GND(958,204)
L(958,140,980,140,V,2.2); RH(980,1020,140,"R13 10Ω"); L(1020,140,1054,140,V,2.2)
out.append('<circle cx="1060" cy="140" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>'); T(1060,162,"J2 OUT",11,"middle"); T(1060,176,"→ монітор",10,"middle",op=".7")

# ===== Ряд 2: LM1881 =====
L(110,330,120,330,V,1.6); RH(120,160,330,"R2 620Ω"); DOT(175,330); L(160,330,192,330)
CV(175,330,380,"C1 510p",side="l"); GND(175,380)
CH(192,200,330,"C2 0.1µ"); L(200,330,220,330)
out.append('<rect x="220" y="300" width="160" height="130" rx="2" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/>')
T(300,362,"U1 LM1881N",14,"middle",mono=False); T(300,378,"сепаратор синхро",10.5,"middle",mono=False,op=".7"); T(300,414,"3 VS · 5 BURST · 7 BP: NC",9,"middle",op=".6")
T(226,333,"2 IN"); T(374,353,"1 CSOUT",anchor="end"); T(286,313,"8 VCC"); T(260,425,"4 GND",9.5,"middle"); T(320,425,"6 RSET",9.5,"middle")
L(320,300,320,250,"var(--rail)"); RAIL(320,250,"+5 V"); L(320,262,355,262); L(355,254,355,270,w=2); L(363,254,363,270,w=2); L(363,262,380,262); L(380,262,380,272); GND(380,272); T(392,266,"C3 100 nF",9.5)
L(260,430,260,445); GND(260,445); RV(320,430,495,"R3 680k"); GND(320,495)
# Q1 інвертор
RH(380,420,350,"R4 4.7k"); L(420,350,460,350); DOT(437,350)
NPN(465,350,"Q1"); L(483,332,483,300); DOT(483,300); L(483,368,483,400); GND(483,400)
RV(483,300,232,"R5 1k"); RAIL(483,232,"+5 V")
L(483,300,575,300,K); L(575,300,575,320,K); L(575,320,600,320,K); T(540,294,"S",11,"middle",K)
# Затвор (мертвий час): помпа заряду + Q5
DOT(500,300,K); CV(500,300,345,"C6 22 nF"); DOT(500,345); T(512,338,"X'",10)
DH(500,555,345,"D5",cathode="left",below=True); L(555,345,555,358); GND(555,358)
DV(500,345,460,"D4",cathode="bottom",side="r"); DOT(500,460); T(512,456,"H")
CV(500,460,500,"C7 10 nF",side="l"); GND(500,500)
L(500,460,520,460); RV(520,460,525,"R6 4.7k"); GND(520,525)
NPN(455,460,"Q5",mirror=True); RH(460,500,460,"R7 22k")
L(437,442,437,350); L(437,478,437,505); GND(437,505)
T(430,540,"мертвий час ≈50 мкс",9.5,"middle",K); T(430,552,"Q5 тримає базу Q1 на землі",9.5,"middle",K)

# ===== CD4046 =====
out.append('<rect x="600" y="290" width="170" height="270" rx="2" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/>')
T(685,410,"U2 CD4046BE",14,"middle",mono=False); T(685,426,"PC2 + VCO",10.5,"middle",mono=False,op=".7"); T(685,470,"1 · 2 · 10 · 15: NC",9,"middle",op=".6")
T(606,323,"14 SIG_IN"); T(606,353,"3 COMP_IN"); T(606,523,"5 INH")
T(764,323,"4 VCO_OUT",anchor="end"); T(764,383,"16 VDD",anchor="end"); T(764,443,"13 PC2_OUT",anchor="end"); T(764,483,"9 VCO_IN",anchor="end")
T(620,554,"6",9,"middle"); T(650,554,"7",9,"middle"); T(690,554,"11 R1",9,"middle"); T(722,554,"8",9,"middle"); T(750,554,"12 R2",9,"middle")
# петля 1:1
L(770,320,790,320); DOT(790,320); L(790,320,790,270); DOT(790,270); L(790,270,585,270); L(585,270,585,350); L(585,350,600,350)
T(690,264,"петля 1:1 (VCO_OUT → COMP_IN)",9.5,"middle")
# INH
L(600,520,575,520); L(575,520,575,535); GND(575,535)
# VDD
L(770,380,815,380,"var(--rail)"); RAIL(830,380,"+5 V"); L(815,380,830,380,"var(--rail)"); CV(815,380,420,"100 nF"); GND(815,420)
# фільтр петлі
L(770,440,800,440); RV(800,440,480,"R8 22k"); DOT(800,480); L(770,480,800,480)
CH(800,838,480,"C8 1 µF",above=False); L(838,480,855,480); RV(855,480,545,"R9 10k"); GND(855,545)
T(855,562,"плівка/X7R, не електроліт",9,"middle",op=".7")
# низ: C1, R1 діапазон, VSS, R2 трімер
L(620,560,620,585); L(650,560,650,585); L(620,585,631,585); L(631,575,631,595,w=2); L(639,575,639,595,w=2); L(639,585,650,585); T(635,610,"C1 1 nF C0G",9,"middle")
RV(690,560,625,"R1 діап.",side="l"); GND(690,625); T(690,644,"≈1 MΩ*",9,"middle")
L(722,560,722,575); GND(722,575)
RV(750,560,625,"RV1 fmin"); GND(750,625); L(742,600,758,588,w=1.2); out.append('<polygon points="758,588 752,590 756,594" fill="currentColor"/>'); T(750,644,"22k+100k*",9,"middle")
T(690,662,"* підібрати за частотоміром: fmin = 15.3 кГц (pin 9 на GND), fmax ≈ 16.3 кГц (pin 9 на +5 V)",9,"middle",op=".8")

# ===== дільник опорних напруг =====
RAIL(980,430,"+5 V"); RV(980,430,490,"R17 3.3k"); DOT(980,490); FLAG(994,490,"V_CL 1.7 V")
RV(980,490,540,"R18 100Ω"); DOT(980,540); FLAG(994,540,"V_E 1.6 V")
RV(980,540,605,"R19 1.6k"); GND(980,605)
L(980,490,950,490); L(950,482,950,498,w=2); L(942,482,942,498,w=2); L(942,490,925,490); L(925,490,925,503); GND(925,503); T(946,476,"C10 10µ",9,"middle")
L(980,540,950,540); L(950,532,950,548,w=2); L(942,532,942,548,w=2); L(942,540,925,540); L(925,540,925,553); GND(925,553); T(946,526,"C11 10µ",9,"middle")
T(980,626,"1 mA через дільник",9,"middle",op=".7")

# ===== маркери ідей =====
def MK(x,y,n): out.append(f'<circle cx="{x}" cy="{y}" r="11" fill="var(--ok)"/><text x="{x}" y="{y+4}" font-size="12" font-weight="500" text-anchor="middle" fill="#fff" font-family="IBM Plex Mono,monospace">{n}</text>')
MK(352,112,1); MK(190,250,2); MK(350,505,3); MK(830,600,4); MK(898,112,5)
T(20,706,"S1 (DPDT, BYPASS, не показано): J1 → J2 напряму та від’єднати R1. Уся схема від +5 V. Q3+Q4: два BC547 як Дарлінгтон або один BC517.",10,op=".8")

svg='<svg class="wide" viewBox="0 0 1100 715" role="img" aria-label="Схема v4: LM1881 читає вхід, Q1 інвертує CSYNC, Q5 з помпою заряду створює мертвий час 50 мкс, CD4046 (PC2, повільний фільтр 22k/1µF/10k, вузький діапазон VCO) формує стабільні рядкові фронти, RC-формувач і Q2 замикають вузол P на V_E на 4.7 мкс, діодний clamp прив’язує sync tip входу до V_CL, Дарлінгтон Q3+Q4 буферизує вихід." xmlns="http://www.w3.org/2000/svg">\n'+"\n".join(out)+'\n</svg>'
open("/tmp/claude-0/-home-user/cc56ab18-2071-51c7-bfda-d8df6159ae2c/scratchpad/v4_schematic.svg","w").write(svg)
print(len(out),"elements")
