#!/usr/bin/env python3
"""Рис. 6–7: v5 (лише 555) проти v6 (555 + 4046 як пам'ять частоти) — «екран монітора»."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from make_figures import screen, note
def load(n): return dict(np.load(f"results/{n}.npz"))

pairs=[("IL_A_clean","V6_A_clean","чистий сигнал"),
       ("IL_H_heavy_noise","V6_M_medium_noise","середній/сильний шум (v5: 8 дБ · v6: 14 дБ)"),
       ("IL_B_dropout","V6_B_dropout","сніг 100–200 мс"),
       ("IL_D_cam_65p0","V6_D_cam_65p0","камера 65.0 мкс (+1.6 %)")]
fig,ax=plt.subplots(2,4,figsize=(17,8.6))
for j,(a,b,ttl) in enumerate(pairs):
    for i,(nm,lab,c) in enumerate([(a,"v5: 555","#8A6D1F"),(b,"v6: 555 + 4046","#2F7A4D")]):
        d=load(nm); img,blue,tt=screen(d)
        ax[i,j].imshow(img,aspect="auto",extent=[0,52,tt[-1],tt[0]],interpolation="nearest")
        ax[i,j].set_title(f"{lab} — {ttl}",fontsize=9.5,loc="left",color=c); ax[i,j].set_xlabel("ширина кадру, мкс"); 
        if j==0: ax[i,j].set_ylabel("час, мс ↓")
fig.suptitle("Рис. 6. Екран монітора: v5 (тільки NE555) зверху, v6 (NE555 + CD4046 як пам'ять частоти) знизу",fontsize=12.5,x=0.02,ha="left")
fig.tight_layout(); fig.savefig("results/FIG6_v5_vs_v6_screens.png",dpi=120); plt.close(fig)

# Рис. 7: як v6 тримає частоту і хто запускає рядок
cases=[("V6_B_long_dropout","сніг 100–600 мс (25 кадрів)"),("V6_P_trap","камера 64.2 мкс, пропадання 50–100 мс, повторне захоплення"),("V6_M_medium_noise","постійний шум 14 дБ")]
fig,ax=plt.subplots(3,3,figsize=(16,10),gridspec_kw=dict(height_ratios=[1,1,1.6]))
for j,(nm,ttl) in enumerate(cases):
    d=load(nm); tl=np.arange(len(d["f_log"]))*float(d["dtl"])*1e3; src=d["src"]; st=d["vco_edges"]
    ax[0,j].plot(tl,d["f_log"]/1e3,lw=1,color="#2F7A4D"); ax[0,j].axhline(15.625,color="k",ls="--",lw=.6); ax[0,j].axhspan(15.625*.98,15.625*1.02,color="g",alpha=.1)
    ax[0,j].set_ylim(15.2,16.1); ax[0,j].set_title(ttl,fontsize=10.5,fontweight="bold",loc="left"); ax[0,j].set_ylabel("VCO, кГц (смуга ±2 %)")
    # хто запустив рядок: ковзне середнє по 50 рядках
    k=50; s1=np.convolve(src==1,np.ones(k)/k,mode="same")*100; s2=np.convolve(src==2,np.ones(k)/k,mode="same")*100
    ax[1,j].plot(st*1e3,s1,lw=1,label="справжній sync",color="#2A6BB0"); ax[1,j].plot(st*1e3,s2,lw=1,label="поштовх VCO",color="#2F7A4D"); ax[1,j].set_ylim(-5,105); ax[1,j].set_ylabel("хто запустив рядок, %"); ax[1,j].legend(loc="center right",fontsize=8)
    img,blue,tt=screen(d); ax[2,j].imshow(img,aspect="auto",extent=[0,52,tt[-1],tt[0]],interpolation="nearest"); ax[2,j].set_xlabel("ширина кадру, мкс"); ax[2,j].set_ylabel("час, мс ↓"); ax[2,j].set_title("що бачить монітор",fontsize=10,loc="left")
note(ax[0,0],"без сигналу VCO тримає вивчену частоту,\nстік 1 МОм тягне вниз ≈0.25 %/100 мс —\nнавмисно, щоб sync завжди був першим",(0.6,0.35),(0.03,0.85),"#2F7A4D")
note(ax[1,1],"після пропадання VCO кілька\nдесятків мс маскує sync, потім\nстік робить його повільнішим → sync\nвиграє → петля захоплює знову",(0.35,0.6),(0.4,0.15),"#2F7A4D")
note(ax[1,2],"кожен пропущений LM1881 імпульс\nпідхоплює VCO у правильний момент —\nтому нема сходинок по 1.5 мкс, як у v5",(0.5,0.75),(0.03,0.15),"#2F7A4D")
fig.suptitle("Рис. 7. v6: частота VCO, джерело запуску рядка та екран у трьох сценаріях",fontsize=12.5,x=0.02,ha="left")
fig.tight_layout(); fig.savefig("results/FIG7_v6_hold_and_capture.png",dpi=120); plt.close(fig)
print("ok")
