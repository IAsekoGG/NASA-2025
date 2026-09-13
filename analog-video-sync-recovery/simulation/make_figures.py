#!/usr/bin/env python3
"""Композитні рисунки «до / після» з результатів sim_v4.py (results/*.npz).
Панель «екран»: кожен рядок тестової картинки зсунуто на реальну фазову похибку вставленого sync
(5 px = 1 мкс); під час пропадання — шум; синій — коли ≥32 рядки підряд мають похибку періоду >5 %."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def load(n): return dict(np.load(f"results/{n}.npz"))

def screen(d, step=6, W=260):
    ph=d["ph"]; err=d["err"]; edges=d["vco_edges"]
    n=min(len(ph),len(err)); ph=ph[:n]; err=err[:n]; edges=edges[1:n+1]
    t=d["t"]; amp=d["amp"]; sigma=d["sigma"]
    rng=np.random.default_rng(3)
    # тестова картинка: 4 смуги + горизонт + «об'єкт»
    x=np.arange(W); base=np.zeros((W,3))
    cols=[(0.85,0.85,0.85),(0.9,0.75,0.2),(0.2,0.6,0.9),(0.3,0.7,0.35)]
    for i,c in enumerate(cols): base[(x*4//W)==i]=c
    rows=[]; bad_run=0; blue=[]
    for k in range(0,n,step):
        a=np.interp(edges[k],t,amp); s=np.interp(edges[k],t,sigma)
        bad_run = bad_run+step if abs(err[k])>5 else 0
        isblue = bad_run>=32
        if isblue: row=np.tile([[0.05,0.15,0.75]],(W,1))
        elif a<0.5: row=np.tile(rng.uniform(0.15,0.85,(W,1)),(1,3))
        else:
            dx=int(round(ph[k]*5)); row=np.roll(base,dx,axis=0).copy()
            if s>0.12: row=np.clip(row+rng.normal(0,min(s,0.5),(W,1)),0,1)
            if abs((k/n)-0.5)<0.02: row[:]=[0.1,0.1,0.1]   # горизонт
        rows.append(row); blue.append(isblue)
    return np.array(rows), np.array(blue), edges[::step]*1e3

def panel_screen(ax,d,title):
    img,blue,tm=screen(d)
    ax.imshow(img,aspect="auto",extent=[0,52,tm[-1],tm[0]],interpolation="nearest")
    ax.set_title(title,fontsize=10,loc="left"); ax.set_xlabel("ширина кадру, мкс (52 = весь рядок)"); ax.set_ylabel("час, мс ↓")
    return blue.sum()

def note(ax,txt,xy,xytext,color="#C0392B"):
    ax.annotate(txt,xy=xy,xycoords="axes fraction",xytext=xytext,textcoords="axes fraction",fontsize=9,color=color,
                arrowprops=dict(arrowstyle="->",color=color,lw=1),bbox=dict(boxstyle="round,pad=.3",fc="white",ec=color,alpha=.9))

# ---------- Рис. 1: чистий сигнал, до/після (мертвий час) ----------
A0=load("A0_clean_nogate"); A=load("A_clean")
fig,ax=plt.subplots(2,2,figsize=(13,9),gridspec_kw=dict(height_ratios=[1,1.6]))
for j,(d,ttl,c) in enumerate([(A0,"ДО: ваш v2 — PC2 без мертвого часу","#C0392B"),(A,"ПІСЛЯ: v4 — мертвий час 50 мкс (Q5)","#2F7A4D")]):
    tm=d["vco_edges"][1:len(d["ph"])+1]*1e3
    ax[0,j].plot(tm,d["ph"],lw=.7,color=c); ax[0,j].set_ylim(-34,34); ax[0,j].axhspan(-1,2.3,color="g",alpha=.1)
    ax[0,j].set_title(ttl,fontsize=11,fontweight="bold",loc="left",color=c); ax[0,j].set_ylabel("зсув вставленого sync\nвідносно справжнього, мкс"); ax[0,j].set_xlabel("час, мс")
    ax[0,j].axhline(0,color="k",lw=.5)
    panel_screen(ax[1,j],d,"що бачить монітор (сигнал чистий, SNR 35 дБ)")
note(ax[0,0],"кожні 20 мс (кадр) equalizing-імпульси\nперекидають PC2 → фаза тікає на ±32 мкс\nі «перестрибує» на сусідній рядок",(0.36,0.92),(0.05,0.62))
note(ax[0,1],"зсув 0.6 мкс = затримка LM1881+ФНЧ,\nстала для всіх рядків → невидима",(0.5,0.52),(0.25,0.8),"#2F7A4D")
note(ax[1,0],"картинка «пливе» вбік і рветься —\nхоча період рядка майже правильний",(0.45,0.55),(0.08,0.12))
note(ax[1,1],"рівні краї, колір і горизонт на місці",(0.5,0.62),(0.25,0.12),"#2F7A4D")
fig.suptitle("Рис. 1. Чистий сигнал: чому без мертвого часу CD4046 не працює навіть без шуму",fontsize=13,x=0.02,ha="left")
fig.tight_layout(); fig.savefig("results/FIG1_clean_before_after.png",dpi=120); plt.close(fig)

# ---------- Рис. 2: пропадання 100 мс, до/після (діапазон VCO) ----------
BW=load("B_dropout_wide"); BN=load("B_dropout_narrow")
fig,ax=plt.subplots(3,2,figsize=(13,11),gridspec_kw=dict(height_ratios=[1,1,1.7]))
for j,(d,ttl,c) in enumerate([(BW,"ДО: VCO 10–20 кГц (як у v2)","#C0392B"),(BN,"ПІСЛЯ: v4 — VCO обмежено 15.3–16.3 кГц","#2F7A4D")]):
    tl=np.arange(len(d["f_log"]))*float(d["dtl"])*1e3
    ax[0,j].plot(tl,d["f_log"]/1e3,lw=1,color=c); ax[0,j].axhspan(15.625*.95,15.625*1.05,color="g",alpha=.1); ax[0,j].axhline(15.625,color="k",ls="--",lw=.6)
    ax[0,j].set_ylim(10.5,17.2); ax[0,j].set_ylabel("частота рядків VCO, кГц"); ax[0,j].set_title(ttl,fontsize=11,fontweight="bold",loc="left",color=c)
    ax[0,j].axvspan(100,200,color="0.6",alpha=.25)
    tm=d["vco_edges"][1:len(d["err"])+1]*1e3
    ax[1,j].plot(tm,d["err"],lw=.7,color=c); ax[1,j].axhspan(-5,5,color="g",alpha=.1); ax[1,j].set_ylim(-20,48); ax[1,j].set_ylabel("похибка періоду рядка, %"); ax[1,j].axvspan(100,200,color="0.6",alpha=.25)
    nb=panel_screen(ax[2,j],d,"що бачить монітор (100–200 мс: сигналу немає, на вході сніг)")
    ax[1,j].set_xlabel("час, мс")
note(ax[0,0],"сірий = пропадання: шум накачує PC2,\nVCO падає до 10.9 кГц (−30 %)",(0.6,0.12),(0.05,0.72))
note(ax[0,1],"той самий шум, але діапазон VCO\nне пускає далі ніж −2 %",(0.6,0.7),(0.05,0.15),"#2F7A4D")
note(ax[1,0],"32 рядки підряд поза ±5 % →\nдекодер втрачає lock → синій екран",(0.45,0.55),(0.03,0.85))
note(ax[1,1],"макс. 2 % — картинка злегка скошена,\nале декодер тримає",(0.6,0.33),(0.3,0.85),"#2F7A4D")
note(ax[2,0],"синій екран і ще ~50 мс\nхаосу після повернення сигналу",(0.5,0.5),(0.08,0.12))
note(ax[2,1],"сніг замість синього;\n~50 мс «хитання» після повернення, далі картинка на місці",(0.5,0.5),(0.05,0.9),"#2F7A4D")
fig.suptitle("Рис. 2. Пропадання сигналу на 100 мс (5 кадрів): чому діапазон VCO треба обмежити",fontsize=13,x=0.02,ha="left")
fig.tight_layout(); fig.savefig("results/FIG2_dropout_before_after.png",dpi=120); plt.close(fig)

# ---------- Рис. 3: v4 у складних умовах ----------
C=load("C_snr_ramp"); E=load("E_silence"); F=load("F_bursts")
fig,ax=plt.subplots(2,3,figsize=(15,8.5),gridspec_kw=dict(height_ratios=[1,1.7]))
for j,(d,ttl,sub) in enumerate([(C,"SNR падає 35 → 3 дБ за 300 мс","шум росте, сигнал є"),(E,"приймач мутить у тишу на 100 мс","PC2 без фронтів → VCO до fmin"),(F,"три пропадання по 40 мс (2 кадри)","типовий сценарій дрона")]):
    tl=np.arange(len(d["f_log"]))*float(d["dtl"])*1e3
    ax[0,j].plot(tl,d["f_log"]/1e3,lw=1,color="#2F7A4D"); ax[0,j].axhspan(15.625*.95,15.625*1.05,color="g",alpha=.1); ax[0,j].axhline(15.625,color="k",ls="--",lw=.6)
    ax[0,j].set_ylim(14.6,16.6); ax[0,j].set_title(ttl,fontsize=11,fontweight="bold",loc="left"); ax[0,j].set_ylabel("частота VCO, кГц")
    a=d["amp"]; t=d["t"]*1e3
    for k in range(1,len(a)):
        if a[k]<0.5 and a[k-1]>=0.5: t0=t[k]
        if a[k]>=0.5 and a[k-1]<0.5: ax[0,j].axvspan(t0,t[k],color="0.6",alpha=.25)
    panel_screen(ax[1,j],d,"екран: "+sub)
    ax[0,j].set_xlabel("час, мс")
note(ax[0,0],"до ~SNR 10 дБ VCO не рухається;\nдалі шумові фронти у вікні 14 мкс\nтягнуть на −2 % за 100 мс",(0.85,0.3),(0.05,0.12),"#2F7A4D")
note(ax[0,1],"у тиші PC2 «тримає низ» →\nсповзає до fmin = 15.3 кГц (−2 %),\nце межа, далі не піде",(0.6,0.36),(0.05,0.8),"#2F7A4D")
note(ax[0,2],"кожне пропадання: ≤1.5 % дрейфу\nі 35 мс на повернення",(0.45,0.38),(0.05,0.12),"#2F7A4D")
fig.suptitle("Рис. 3. v4 у трьох складних сценаріях: жодного синього екрана, ціна — легкий скіс на час пропадання",fontsize=13,x=0.02,ha="left")
fig.tight_layout(); fig.savefig("results/FIG3_v4_hard_cases.png",dpi=120); plt.close(fig)
print("done")
