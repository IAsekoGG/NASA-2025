# Генерує SVG принципової схеми Системи 2.0 з примітивів (той самий стиль, що v4–v6)
out = []
def L(x1,y1,x2,y2,c="currentColor",w=1.4): out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>')
def T(x,y,s,size=10,anchor="start",c="currentColor",mono=True,op=None,bold=False):
    f=' font-family="IBM Plex Mono,monospace"' if mono else ''
    o=f' opacity="{op}"' if op else ''
    b=' font-weight="600"' if bold else ''
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{c}"{f}{o}{b}>{s}</text>')
def DOT(x,y,c="currentColor",r=3): out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
def GND(x,y):
    L(x-8,y,x+8,y,w=1.6); L(x-5,y+4,x+5,y+4,w=1.6); L(x-2,y+8,x+2,y+8,w=1.6)
def RV(x,y1,y2,label,side="r"):
    ym=(y1+y2)/2; out.append(f'<rect x="{x-6}" y="{ym-20}" width="12" height="40" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>')
    L(x,y1,x,ym-20); L(x,ym+20,x,y2)
    if side=="r": T(x+12,ym+4,label)
    else: T(x-12,ym+4,label,anchor="end")
def RH(x1,x2,y,label,above=True):
    xm=(x1+x2)/2; out.append(f'<rect x="{xm-20}" y="{y-6}" width="40" height="12" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>')
    L(x1,y,xm-20,y); L(xm+20,y,x2,y); T(xm,y-10 if above else y+20,label,anchor="middle")
def CV(x,y1,y2,label,side="r"):
    ym=(y1+y2)/2; L(x,y1,x,ym-4); L(x-10,ym-4,x+10,ym-4,w=2); L(x-10,ym+4,x+10,ym+4,w=2); L(x,ym+4,x,y2)
    if side=="r": T(x+14,ym+4,label)
    else: T(x-14,ym+4,label,anchor="end")
def CH(x1,x2,y,label,above=True):
    xm=(x1+x2)/2; L(x1,y,xm-4,y); L(xm-4,y-10,xm-4,y+10,w=2); L(xm+4,y-10,xm+4,y+10,w=2); L(xm+4,y,x2,y)
    T(xm,y-14 if above else y+22,label,anchor="middle")
def DH(x1,x2,y,label,cathode="right",below=False):
    xm=(x1+x2)/2
    if cathode=="right":
        L(x1,y,xm-10,y); out.append(f'<polygon points="{xm-10},{y-9} {xm-10},{y+9} {xm+10},{y}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(xm+10,y-9,xm+10,y+9,w=2); L(xm+10,y,x2,y)
    else:
        L(x1,y,xm-10,y); L(xm-10,y-9,xm-10,y+9,w=2); out.append(f'<polygon points="{xm+10},{y-9} {xm+10},{y+9} {xm-10},{y}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(xm+10,y,x2,y)
    T(xm,y+22 if below else y-14,label,anchor="middle")
def DV(x,y1,y2,label,cathode="top",side="l"):
    ym=(y1+y2)/2
    if cathode=="top":
        L(x,y1,x,ym-10); L(x-9,ym-10,x+9,ym-10,w=2); out.append(f'<polygon points="{x-9},{ym+10} {x+9},{ym+10} {x},{ym-10}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(x,ym+10,x,y2)
    else:
        L(x,y1,x,ym-10); out.append(f'<polygon points="{x-9},{ym-10} {x+9},{ym-10} {x},{ym+10}" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(x-9,ym+10,x+9,ym+10,w=2); L(x,ym+10,x,y2)
    if side=="l": T(x-13,ym+4,label,anchor="end")
    else: T(x+13,ym+4,label)
def NMOS(x,y,label):  # затвор зліва в (x,y); стік вгору (x+18,y-18), витік вниз (x+18,y+18)
    out.append(f'<circle cx="{x+10}" cy="{y}" r="16" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".55"/>')
    L(x-4,y-12,x-4,y+12,w=2); L(x+2,y-12,x+2,y+12,w=2.2)
    L(x+2,y-8,x+18,y-8); L(x+18,y-8,x+18,y-18); L(x+2,y+8,x+18,y+8); L(x+18,y+8,x+18,y+18)
    L(x+2,y,x+12,y); out.append(f'<polygon points="{x+3},{y} {x+11},{y-4} {x+11},{y+4}" fill="currentColor"/>')
    T(x+30,y+4,label)
def RAIL(x,y,txt,c="var(--rail)"): DOT(x,y,c); T(x,y-8,txt,11,"middle",c)
def FLAG(x,y,txt,c="var(--ok)",w=None,left=False):
    w=w or (7*len(txt)+10)
    if left: out.append(f'<polygon points="{x+6},{y} {x},{y-6} {x-w},{y-6} {x-w},{y+6} {x},{y+6}" fill="none" stroke="{c}" stroke-width="1.2"/>'); T(x-w+4,y+4,txt,9.5,c=c)
    else: out.append(f'<polygon points="{x-6},{y} {x},{y-6} {x+w},{y-6} {x+w},{y+6} {x},{y+6}" fill="none" stroke="{c}" stroke-width="1.2"/>'); T(x+3,y+4,txt,9.5,c=c)
def BOX(x,y,w,h,title,sub=None):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="var(--paper)" stroke="currentColor" stroke-width="1.6"/>')
    T(x+w/2,y+h/2+(0 if sub else 4),title,13,"middle",mono=False,bold=True)
    if sub: T(x+w/2,y+h/2+15,sub,9.5,"middle",mono=False,op=".7")
def PINL(x,y,txt): L(x-14,y,x,y); T(x+4,y+4,txt,9.5)              # вивід зліва від корпусу (корпус праворуч)
def PINR(x,y,txt): L(x,y,x+14,y); T(x-4,y+4,txt,9.5,anchor="end")   # вивід справа
def RCONT(x,y,label,energized=False):  # контакт реле: COM зліва (x,y), NO (x+60,y-12), NC (x+60,y+12)
    DOT(x,y); out.append(f'<circle cx="{x+60}" cy="{y-12}" r="3" fill="none" stroke="currentColor" stroke-width="1.4"/>'); out.append(f'<circle cx="{x+60}" cy="{y+12}" r="3" fill="none" stroke="currentColor" stroke-width="1.4"/>')
    if energized: L(x,y,x+57,y+11,w=1.8)
    else: L(x,y,x+57,y-11,w=1.8)
    T(x+66,y-16,"NC",8.5); T(x+66,y+22,"NO",8.5); T(x+28,y-16,label,9.5,"middle")
def MK(x,y,n): out.append(f'<circle cx="{x}" cy="{y}" r="11" fill="var(--ok)"/><text x="{x}" y="{y+4}" font-size="12" font-weight="500" text-anchor="middle" fill="#fff" font-family="IBM Plex Mono,monospace">{n}</text>')
V="var(--video)"; K="var(--ctrl)"; R_="var(--rail)"

# ===================== РЯД 1: аналоговий тракт =====================
T(20,40,"АНАЛОГОВИЙ ТРАКТ (усе на одній платі, шини: +5 V буфер/реле, +3.3 V решта)",10.5,mono=False,op=".7")
out.append('<circle cx="40" cy="120" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>'); T(40,104,"J1 IN",11,"middle"); T(40,140,"від VRX",9,"middle",op=".7")
L(46,120,110,120,V,2.2)
RCONT(110,120,"K1a")
# NO → тракт, NC → bypass
L(173,132,200,132,V,2.2); L(200,132,200,120,V,2.2); L(200,120,250,120,V,2.2)
L(173,108,180,108,V,1.4); L(180,108,180,12,V,1.4); L(180,12,1090,12,V,1.4); L(1090,12,1090,108,V,1.4); L(1090,108,1097,108,V,1.4)
T(200,24,"BYPASS: без живлення J1 → J2 напряму (K1 = NC)",9,c=V,op=".85")
DOT(230,120,V,3.5); RV(230,120,190,"R1 75Ω"); GND(230,190)
CH(250,310,120,"C1 100 nF"); L(310,120,560,120,V,2.2)
DOT(330,120,V,3.5); T(330,108,"N",12,"middle",V,bold=True)
L(330,120,330,265,V,1.6); DOT(330,225,V,3.5); L(330,265,560,265,V,1.6)
RH(330,560,225,"R2 100Ω",above=False)
# 74HC4053
BOX(560,60,160,300,"U1 74HC4053","3× SPDT, живлення 3.3 В")
PINL(560,120,"12 X0"); PINL(560,150,"13 X1"); PINL(560,195,"2 Y1"); PINL(560,225,"15 Y"); PINL(560,265,"5 Z0"); PINL(560,295,"3 Z1")
PINR(720,120,"X 14"); PINR(720,180,"A 11"); PINR(720,210,"B 10"); PINR(720,240,"C 9"); PINR(720,295,"Z 4")
T(640,80,"16 VCC",9,"middle"); T(600,352,"8 GND",9,"middle"); T(645,352,"7 VEE",9,"middle"); T(690,352,"6 E",9,"middle"); T(640,336,"1 Y0: NC",9,"middle",op=".6")
L(640,60,640,36,R_); RAIL(640,36,"+3V3"); L(640,44,670,44); L(670,36,670,52,w=2); L(678,36,678,52,w=2); L(678,44,692,44); L(692,44,692,52); GND(692,52); T(704,48,"100n",9)
L(600,360,600,372); GND(600,372); L(645,360,645,372); GND(645,372); L(690,360,690,372); GND(690,372)
FLAG(546,150,"V_SYNC",left=True); FLAG(546,195,"V_BLANK",left=True); FLAG(546,295,"M",left=True,w=22)
FLAG(734,180,"SYNC_INS ← PA6",K); FLAG(734,210,"CLAMP ← PA7",K); FLAG(734,240,"SELFTEST ← PB0",K)
T(20,386,"U1: A=1 → X=X1 (V_SYNC замість відео на 0–4.7 мкс) · B=1 → Y=Y1 (clamp N→V_BLANK на 8.2–9.4 мкс)",8.5,c=K,op=".9")
T(20,398,"C=0 → компаратор дивиться на вхід N; C=1 → на власний вихід M (самоперевірка). M = вихід/2: ті самі рівні, що на N.",8.5,c=K,op=".9")
# X → THS7314
L(734,120,850,120,V,2.2)
BOX(850,62,140,160,"U2 THS7314","SOIC-8, ×2, ФНЧ 9.5 МГц")
PINL(850,120,"1 IN1"); PINL(850,195,"2 IN2"); PINL(850,210,"3 IN3"); PINR(990,120,"OUT1 7")
T(920,80,"8 VS+",9,"middle"); T(912,214,"4 GND",9,"middle"); T(960,200,"5,6: NC",8.5,"middle",op=".6")
L(836,195,830,195); L(830,195,830,210); L(836,210,830,210); L(830,210,830,220); GND(830,220)
L(920,62,920,36,R_); RAIL(920,36,"+5V"); L(920,44,950,44); L(950,36,950,52,w=2); L(958,36,958,52,w=2); L(958,44,972,44); L(972,44,972,52); GND(972,52); T(984,48,"100n",9)
L(880,222,880,234); GND(880,234)
# вихід
L(1004,120,1020,120,V,2.2); DOT(1010,120,V,3.5)
RH(1020,1075,120,"R4 75Ω"); L(1075,120,1085,120,V,2.2); L(1085,120,1085,132,V,2.2); L(1085,132,1097,132,V,2.2)
# K1b: COM справа (J2), контакти зліва — дзеркально (NC зверху)
DOT(1160,120); out.append('<circle cx="1100" cy="108" r="3" fill="none" stroke="currentColor" stroke-width="1.4"/>'); out.append('<circle cx="1100" cy="132" r="3" fill="none" stroke="currentColor" stroke-width="1.4"/>')
L(1160,120,1103,109,w=1.8); T(1130,140,"K1b",9.5,"middle"); T(1082,104,"NC",8.5,"end"); T(1082,142,"NO",8.5,"end")
L(1160,120,1194,120,V,2.2); out.append('<circle cx="1200" cy="120" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>'); T(1200,104,"J2 OUT",11,"middle"); T(1200,140,"→ монітор",9,"middle",op=".7")
# монітор амплітуди M
RV(1010,120,175,"R5 10k"); DOT(1010,175,V,3.5); FLAG(1024,175,"M → PA4, Z1",w=86); RV(1010,175,230,"R6 10k"); GND(1010,230)
# гілка компаратора
L(734,295,745,295,V,1.6); RH(745,800,295,"R3 4.7k"); L(800,295,822,295,V,1.6); DOT(822,295,V,3.5); T(822,284,"F",11,"middle",V,bold=True)
CV(822,295,345,"C3 100p"); GND(822,345); T(705,372,"R3·C3: ФНЧ 340 кГц (не в тракті відео)",8.5,op=".7")
L(822,295,880,295,V,1.6); L(880,295,880,315,V,1.6); L(880,315,891,315,V,1.6)
BOX(905,290,100,80,"",None); T(955,364,"U3 TLV3201",11,"middle",mono=False,bold=True); T(1046,350,"компаратор 40 нс, SOT-23-5",8.5,op=".7")
PINL(905,315,"3 IN+"); PINL(905,350,"4 IN−"); PINR(1005,332,"OUT 1")
T(955,303,"5 V+ = +3V3",8.5,"middle"); T(955,382,"2 GND",8.5,"middle"); L(955,370,955,382); GND(955,386)
FLAG(891,350,"V_THR",left=True)
L(1019,332,1040,332,K); DOT(1040,332,K,3); FLAG(1046,332,"COMP → PA0 (TIM2_CH1)",K,w=150)
# гістерезис R7 470k: OUT → над U3 → F
L(1040,332,1040,252,K); RH(1040,822,252,"R7 470k"); L(822,252,822,295,K)
T(1050,248,"R7: гістерезис ≈33 мВ",8.5,c=K,op=".9")
FLAG(808,317,"ADC_LPF → PA1",K,left=True,w=100)
T(20,412,"Рівні на вузлі N (після clamp): вершина sync 0.30 · blanking 0.60 · білий 1.30 В. Поріг компаратора 0.45 В — посередині між вершиною і blanking.",9,op=".85")
T(20,426,"Замінюється лише вершина sync (0–4.7 мкс синтетичної шкали); порч, burst і відео проходять через X0→X без обробки. THS7314: ×2, 75 Ω → на моніторі 1.0 Vpp.",9,op=".85")

# ===================== РЯД 2: MCU =====================
T(20,450,"MCU (усі часи від кварцу; жодного підстроювання)",10.5,mono=False,op=".7")
BOX(430,470,300,330,"",None); T(545,662,"U4 STM32G031K8T6",13,mono=False,bold=True)
T(580,832,"LQFP32 — той самий чип, що на Nucleo-G031K8; прошивка переноситься без змін",9.5,"middle",mono=False,op=".7")
# ліві виводи
PINL(430,500,"PA0  TIM2_CH1 (capture ↑↓)"); FLAG(416,500,"COMP",K,left=True,w=44)
PINL(430,525,"PA1  ADC_IN1"); FLAG(416,525,"ADC_LPF (F)",K,left=True,w=82)
PINL(430,550,"PA4  ADC_IN4"); FLAG(416,550,"M",K,left=True,w=22)
PINL(430,600,"PF0  OSC_IN"); PINL(430,640,"PF1  OSC_OUT")
PINL(430,690,"NRST"); PINL(430,730,"BOOT0 (PA14)")
# кварц
L(416,600,300,600); L(300,600,300,620); L(416,640,380,640); L(380,640,380,620)
out.append('<rect x="326" y="608" width="28" height="24" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); L(320,608,320,632,w=2); L(360,608,360,632,w=2)
L(300,620,320,620); L(360,620,380,620); DOT(300,620); DOT(380,640)
T(340,655,"X1 8 MHz",9.5,"middle")
CV(300,620,670,"12p",side="l"); GND(300,670)
CV(380,640,690,"12p"); GND(380,690)
L(416,690,400,690); CV(400,690,740,"100n",side="l"); GND(400,740); T(395,715,"",9)
L(416,730,400,730); RV(400,730,780,"10k",side="l"); GND(400,780)
# праві виводи
PINR(730,500,"PA6  TIM3_CH1"); FLAG(744,500,"SYNC_INS → A",K)
PINR(730,525,"PA7  TIM3_CH2"); FLAG(744,525,"CLAMP → B",K)
PINR(730,550,"PB0  GPIO"); FLAG(744,550,"SELFTEST → C",K)
PINR(730,575,"PB1  GPIO"); FLAG(744,575,"RELAY → Q1",K)
PINR(730,615,"PA2  USART2_TX"); PINR(730,635,"PA3  USART2_RX"); FLAG(744,625,"UART-лог 115200",w=112)
PINR(730,675,"PA5  GPIO"); PINR(730,700,"PA8  GPIO")
PINR(730,745,"PA13 SWDIO"); PINR(730,770,"PA14 SWCLK"); FLAG(744,757,"SWD",w=34)
# LEDs
L(744,675,780,675); RH(780,830,675,"1k"); DH(830,880,675,"LED1 LOCK",cathode="right"); L(880,675,895,675); GND(895,681)
L(744,700,780,700); RH(780,830,700,"1k",above=False); DH(830,880,700,"LED2 COAST",cathode="right",below=True); L(880,700,895,700); GND(895,706)
# живлення MCU
T(580,486,"VDD, VDDA",9,"middle"); L(580,470,580,440,R_); RAIL(580,440,"+3V3")
L(580,448,610,448); L(610,440,610,456,w=2); L(618,440,618,456,w=2); L(618,448,632,448); L(632,448,632,456); GND(632,456); T(644,452,"100n ×2 + 4.7µ",9)
T(580,795,"VSS, VSSA",9,"middle"); L(580,800,580,812); GND(580,812)
# драйвер реле
T(930,450,"Реле обходу",10.5,mono=False,op=".7")
L(744,575,940,575,K); RH(940,1000,575,"R8 1k"); L(1000,575,1016,575,K)
NMOS(1020,575,"Q1 2N7002")
RV(1000,575,640,"R9 100k",side="l"); GND(1000,640)
L(1038,593,1038,620); GND(1038,620)
L(1038,557,1038,530)
out.append('<rect x="1024" y="470" width="28" height="60" rx="3" fill="var(--paper)" stroke="currentColor" stroke-width="1.4"/>'); T(1038,504,"K1",9.5,"middle"); T(1060,494,"G6K-2F-Y",9); T(1060,506,"5 В, DPDT",9); T(1060,518,"котушка",9)
L(1038,470,1038,440,R_); RAIL(1038,440,"+5V")
L(1038,455,1140,455); DV(1140,455,540,"D1 1N4148",cathode="top",side="r"); L(1140,540,1140,548); L(1038,548,1140,548); DOT(1038,548)
T(1000,662,"MCU тримає реле ввімкненим лише",8.5,op=".85"); T(1000,674,"коли самоперевірка пройдена → fail-safe",8.5,op=".85")

# ===================== РЯД 3: дільник і живлення =====================
T(20,860,"Опорні рівні: один дільник 1 %, ≈1 мА",10.5,mono=False,op=".7")
RAIL(60,910,"+3V3"); L(60,910,80,910,R_)
RH(80,180,910,"R10 2.7k",above=False); DOT(180,910); FLAG(170,886,"V_BLANK 0.60 В",w=100)
RH(180,290,910,"R11 150Ω",above=False); DOT(290,910); FLAG(280,886,"V_THR 0.45 В",w=90)
RH(290,400,910,"R12 150Ω",above=False); DOT(400,910); FLAG(390,886,"V_SYNC 0.30 В",w=94)
RH(400,500,910,"R13 300Ω",above=False); GND(500,916)
CV(180,910,960,"C4 1µ"); GND(180,960); CV(290,910,960,"C5 100n"); GND(290,960); CV(400,910,960,"C6 1µ"); GND(400,960)
T(20,995,"Різниці рівнів задані відношенням резисторів: 0.15 В між сусідніми — це половина вершини sync (0.30 В). Абсолютна точність 3.3 В не важлива, важливі відношення.",9,op=".85")

T(560,860,"Живлення",10.5,mono=False,op=".7")
out.append('<circle cx="580" cy="910" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>'); T(580,934,"J3 5–26 В",10,"middle")
L(586,910,600,910); RH(600,640,910,"F1 0.5A"); DH(640,690,910,"D2 SS14"); L(690,910,720,910)
BOX(720,885,150,50,"U5 buck 5 В","TPS562200 / модуль MP1584")
L(870,910,900,910,R_); DOT(900,910,R_); RAIL(900,898,"+5V"); CV(900,910,960,"10µ"); GND(900,960)
L(900,910,930,910,R_)
BOX(930,885,120,50,"U6 AP2112K-3.3","LDO 3.3 В")
L(1050,910,1080,910,R_); DOT(1080,910,R_); RAIL(1080,898,"+3V3"); CV(1080,910,960,"10µ"); GND(1080,960)
T(20,1009,"+5 В: THS7314 (≈30 мА) і котушка реле (≈20 мА). +3.3 В: MCU, 4053, TLV3201, дільник (≈15 мА).",9,op=".85")
L(795,935,795,948); GND(795,948); L(990,935,990,948); GND(990,948)

MK(330,96,1); MK(790,96,2); MK(700,330,3); MK(1040,290,4); MK(430,440,5); MK(1130,160,6)

svg='<svg class="wide" viewBox="0 0 1240 1024" role="img" aria-label="Принципова схема Системи 2.0: вхід через реле обходу і роздільний конденсатор на вузол N, 74HC4053 підставляє V_SYNC замість вершини sync і робить keyed clamp вузла N до V_BLANK, THS7314 буферизує вихід через 75 Ом на монітор, гілка компаратора з ФНЧ 340 кГц і TLV3201 дає фронти в STM32G031K8 з кварцом 8 МГц, який синтезує sync, керує ключами, реле і самоперевіркою; один дільник дає рівні 0.60 / 0.45 / 0.30 В; живлення 5–26 В через buck 5 В і LDO 3.3 В." xmlns="http://www.w3.org/2000/svg">\n'+"\n".join(out)+'\n</svg>'
import os
os.makedirs("/tmp/claude-0/-home-user/cc56ab18-2071-51c7-bfda-d8df6159ae2c/scratchpad",exist_ok=True)
open("/tmp/claude-0/-home-user/cc56ab18-2071-51c7-bfda-d8df6159ae2c/scratchpad/s2_schematic.svg","w").write(svg)
print(len(out),"elements")
