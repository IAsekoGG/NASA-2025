#!/usr/bin/env python3
"""Рисунки для v5 (NE555 injection-locked): «екран монітора» з IL_*.npz та форма сигналу одного рядка."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from make_figures import screen, note
import sim_v4 as S

def load(n): return dict(np.load(f"results/{n}.npz"))

# ---------- Рис. 4: екран v5 на гарному сигналі та в складних випадках ----------
cases=[("IL_A_clean","чистий сигнал, камера 64.0 мкс","#2F7A4D"),
       ("IL_D_cam_65p0","чистий сигнал, камера 65.0 мкс (+1.6 %)","#2F7A4D"),
       ("IL_H_heavy_noise","постійний шум SNR 8 дБ, сигнал є","#8A6D1F"),
       ("IL_B_dropout","сніг 100–200 мс, далі сигнал","#8A6D1F")]
fig,ax=plt.subplots(2,4,figsize=(17,8.6),gridspec_kw=dict(height_ratios=[1,1.8]))
for j,(nm,ttl,c) in enumerate(cases):
    d=load(nm); tm=d["vco_edges"][:len(d["ph"])]*1e3
    ax[0,j].plot(tm,d["ph"],lw=.6,color=c); ax[0,j].set_ylim(-33,33); ax[0,j].axhspan(-1,2.3,color="g",alpha=.1); ax[0,j].axhline(0,color="k",lw=.5)
    ax[0,j].set_title(ttl,fontsize=10.5,fontweight="bold",loc="left"); ax[0,j].set_ylabel("зсув вставленого sync, мкс"); ax[0,j].set_xlabel("час, мс")
    screen_img,blue,tt=screen(d)
    ax[1,j].imshow(screen_img,aspect="auto",extent=[0,52,tt[-1],tt[0]],interpolation="nearest"); ax[1,j].set_xlabel("ширина кадру, мкс"); ax[1,j].set_ylabel("час, мс ↓")
    ax[1,j].set_title("що бачить монітор",fontsize=10,loc="left")
note(ax[0,0],"кожен рядок запущено справжнім sync:\nзсув = 0.65 мкс затримки LM1881,\nоднаковий для всіх рядків",(0.5,0.52),(0.05,0.8),"#2F7A4D")
note(ax[0,1],"T0 = 65.5 > 65.0 — sync камери\nвсе ще потрапляє у вікно,\nзахоплення тримається",(0.5,0.52),(0.05,0.8),"#2F7A4D")
note(ax[0,2],"LM1881 губить ~15 % sync у шумі →\nці рядки йдуть з вільного ходу (+1.5 мкс),\nа шумові фронти у вікні дають ±3 мкс",(0.5,0.62),(0.03,0.85),"#8A6D1F")
note(ax[0,3],"без сигналу фаза «їде» на 1.5 мкс/рядок\n(вільний хід); з поверненням — перший\nsync у вікні ставить рядок на місце",(0.5,0.3),(0.03,0.85),"#8A6D1F")
fig.suptitle("Рис. 4. v5 (NE555 injection-locked): «екран» на гарному сигналі, на камері з довгим періодом, у шумі та після пропадання",fontsize=12.5,x=0.02,ha="left")
fig.tight_layout(); fig.savefig("results/FIG4_v5_screens.png",dpi=120); plt.close(fig)

# ---------- Рис. 5: форма сигналу одного рядка на виході (розрахована з таймінгів моделі) ----------
t=np.arange(0,14,0.01)  # мкс
def cvbs_line(t):
    v=np.zeros_like(t); v[t<4.7]=-0.3
    b=(t>=5.6)&(t<7.85); v[b]=0.15*np.sin(2*np.pi*4.43361875*t[b])
    a=t>=10.4; v[a]=0.05+0.4*(0.5+0.5*np.sin(2*np.pi*(t[a]-10.4)/8))
    return v
rng=np.random.default_rng(5)
vin=cvbs_line(t)+rng.normal(0,0.018,len(t))            # SNR ≈ 35 дБ
V_CL=1.7; vin_clamped=vin+ (V_CL-(-0.3))              # clamp: sync tip → 1.7 В
t_lm=0.65; t_555_hi=4.3; V_E=1.6; Vce=0.06
vout=vin_clamped.copy(); ins=(t>=t_lm)&(t<t_lm+t_555_hi); vout[ins]=V_E+Vce
fig,ax=plt.subplots(2,1,figsize=(12,7.5))
ax[0].plot(t,vin_clamped,color="#2A6BB0",lw=1.2,label="вхід після clamp (вузол P0)")
ax[0].plot(t,vout,color="#C0392B",lw=1.2,label="вихід (вузол P) — те, що піде на скалер")
ax[0].axvspan(t_lm,t_lm+t_555_hi,color="#8A6D1F",alpha=.12); ax[0].axvspan(5.6,7.85,color="g",alpha=.08)
ax[0].axhline(V_CL,color="k",ls=":",lw=.7); ax[0].axhline(V_CL+0.3,color="k",ls=":",lw=.7)
ax[0].text(t_lm+0.1,2.62,"OUT 555 високий 4.3 мкс → Q2 замикає P на V_E",fontsize=9,color="#8A6D1F"); ax[0].text(5.7,2.5,"burst\nне чіпаємо",fontsize=9,color="g")
ax[0].text(13.9,V_CL+0.02,"sync tip 1.7 В",fontsize=8,ha="right"); ax[0].text(13.9,V_CL+0.32,"гасіння 2.0 В",fontsize=8,ha="right")
ax[0].annotate("0–0.65 мкс: проходить справжній sync\n(той самий рівень завдяки clamp)",xy=(0.3,1.7),xytext=(1.2,1.2),fontsize=8.5,arrowprops=dict(arrowstyle="->",lw=.8))
ax[0].annotate("4.7–4.95 мкс: ще тримаємо V_E,\nпоки справжній back porch вже почався",xy=(4.85,1.66),xytext=(8.0,1.3),fontsize=8.5,arrowprops=dict(arrowstyle="->",lw=.8))
ax[0].set_xlim(-0.5,14); ax[0].set_ylim(1.0,2.8); ax[0].set_ylabel("В"); ax[0].set_xlabel("мкс від початку справжнього sync"); ax[0].legend(loc="upper right",fontsize=9); ax[0].set_title("Рис. 5. Один рядок на гарному сигналі (SNR 35 дБ): вхід і вихід, розраховано з таймінгів моделі",loc="left",fontsize=11)
# пилка 555
tt=np.arange(-64,14,0.02); vc=np.zeros_like(tt)
T0=65.5; tl=61.2
for i,x in enumerate(tt):
    if x<0.65-64+T0 and x<0.65: # попередній розряд: від 3.33 експоненційно
        vc[i]=3.33*np.exp(-(x+64-0.65)/88.0) if x+64-0.65>=0 else 3.33
    elif x<0.65+t_555_hi: vc[i]=1.66+(3.33-1.66)*(1-np.exp(-(x-0.65)/4.6))*1.0
    else: vc[i]=3.33*np.exp(-(x-0.65-t_555_hi)/88.0)
ax[1].plot(tt,vc,color="k",lw=1.1,label="напруга на C_t (pins 2/6)")
ax[1].axhline(1.667,color="#C0392B",ls="--",lw=.8); ax[1].axhline(3.333,color="#C0392B",ls="--",lw=.8)
ax[1].text(-63,1.72,"1/3 Vcc — поріг запуску",fontsize=8,color="#C0392B"); ax[1].text(-63,3.38,"2/3 Vcc — кінець імпульсу",fontsize=8,color="#C0392B")
ax[1].axvspan(0.65-3,0.65,color="#8A6D1F",alpha=.18); ax[1].text(-2.4,2.6,"вікно ≈3 мкс:\nтут поштовх −60 мВ\nперетинає поріг",fontsize=8.5,color="#8A6D1F",ha="right")
ax[1].annotate("спад CSOUT → −60 мВ → запуск",xy=(0.65,1.68),xytext=(3,2.3),fontsize=8.5,arrowprops=dict(arrowstyle="->",lw=.8))
ax[1].axvspan(-64+32,-64+32+2.35,color="#2A6BB0",alpha=.15); ax[1].text(-31,2.9,"equalizing-імпульс на 32 мкс:\nпоштовх далеко від порогу — ігнорується",fontsize=8.5,color="#2A6BB0")
ax[1].set_xlim(-64,14); ax[1].set_ylim(1.2,3.6); ax[1].set_xlabel("мкс (0 = початок sync поточного рядка; −64 = попередній)"); ax[1].set_ylabel("В"); ax[1].legend(loc="upper right",fontsize=9)
fig.tight_layout(); fig.savefig("results/FIG5_v5_one_line.png",dpi=120); plt.close(fig)
print("ok")
