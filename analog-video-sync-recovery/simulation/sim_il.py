#!/usr/bin/env python3
"""Injection-locked генератор (555 або 2-транзисторний мультивібратор) замість ФАПЧ.
Модель: вільний період T0 (трохи довший за рядок); фронт LM1881 у «вікні» (останні W мкс періоду)
запускає новий рядок негайно; поза вікном — ігнорується; якщо фронту нема — запуск по таймауту T0.
Метрики ті самі, що у sim_v4 (використовує його генератор CVBS і модель LM1881)."""
import sys, os, json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sim_v4 as S

def il_run(sig_edges_t, t_end, T0=65.5e-6, W=2.5e-6, t_sync=4.7e-6):
    """Повертає моменти запуску рядків (початки вставленого sync)."""
    starts=[]; t_next=T0; j=0; n=len(sig_edges_t)
    last=0.0
    while last < t_end:
        # шукаємо перший фронт у вікні [t_next-W, t_next)
        while j < n and sig_edges_t[j] < t_next - W: j += 1
        if j < n and sig_edges_t[j] < t_next:
            trig = sig_edges_t[j]; j += 1
        else:
            trig = t_next
        starts.append(trig); last = trig; t_next = trig + T0
    return np.array(starts)

def scenario(name, dur=0.30, line_period=S.H, snr_profile=None, dropout=None, silence=None, T0=65.5e-6, W=2.5e-6, seed=1):
    rng=np.random.default_rng(seed)
    n_lines=int(dur/line_period); v,starts=S.gen_cvbs(n_lines,line_period); t=np.arange(len(v))*S.DT
    amp=np.ones_like(v); 
    if snr_profile is None: snr_profile=lambda tt:35.0
    snr=np.array([snr_profile(tt) for tt in t[::1000]]); sigma=np.repeat(1.0/(10**(snr/20)),1000)[:len(v)].astype(np.float32)
    for a,b in (dropout or []):
        m=(t>=a)&(t<b); amp[m]=0; sigma[m]=0.30
    for a,b in (silence or []):
        m=(t>=a)&(t<b); amp[m]=0; sigma[m]=0
    vin=v*amp+rng.normal(0,1,len(v)).astype(np.float32)*sigma
    cs,s_idx,e_idx=S.lm1881(vin); sig=s_idx*S.DT+0.15e-6
    st=il_run(sig,dur,T0,W)
    m,err,ph=S.analyze(st,starts,line_period)
    m["false_edges_per_line"]=float(len(s_idx)/n_lines)
    # графік
    fig,ax=plt.subplots(3,1,figsize=(11,7.5),sharex=True)
    te=st[1:len(err)+1]*1e3
    ax[0].plot(te,err,lw=.6); ax[0].axhspan(-5,5,color="g",alpha=.08); ax[0].set_ylim(-12,12); ax[0].set_ylabel("похибка періоду, %"); ax[0].set_title(f"{name} (injection-locked, T0={T0*1e6:.1f} мкс, вікно {W*1e6:.1f} мкс)")
    ax[1].plot(st[:len(ph)]*1e3,ph,lw=.6); ax[1].axhspan(-1,2.3,color="g",alpha=.08); ax[1].set_ylim(-33,33); ax[1].set_ylabel("фаза vs справжній sync, мкс")
    tt=t[::100]*1e3; ax[2].plot(tt,sigma[::100]*1e3,lw=.8,label="σ шуму, мВ"); ax[2].plot(tt,amp[::100]*300,lw=.8,label="сигнал"); ax[2].legend(loc="upper right"); ax[2].set_xlabel("час, мс")
    fig.tight_layout(); os.makedirs("results",exist_ok=True); fig.savefig(f"results/IL_{name}.png",dpi=110); plt.close(fig)
    np.savez(f"results/IL_{name}.npz",vco_edges=st,err=err,ph=ph,f_log=np.array([]),dtl=0.0,sigma=sigma[::100],amp=amp[::100],t=t[::100],starts=starts,line_period=line_period)
    return m

SCEN={
 "A_clean":dict(), "B_dropout":dict(dropout=[(0.10,0.20)]), "C_snr_ramp":dict(snr_profile=lambda tt:35-32*min(tt/0.30,1.0)),
 "D_cam_64p3":dict(line_period=64.3e-6), "D_cam_65p0":dict(line_period=65.0e-6), "E_silence":dict(silence=[(0.10,0.20)]),
 "F_bursts":dict(dropout=[(0.08,0.12),(0.16,0.20),(0.24,0.28)]),
 "H_heavy_noise":dict(snr_profile=lambda tt:8.0),            # постійний сильний шум, сигнал є
 "W5_dropout":dict(dropout=[(0.10,0.20)],W=5e-6),           # ширше вікно — чутливіше до шуму
 "T0_67":dict(dropout=[(0.10,0.20)],T0=67e-6,W=4e-6),       # гірше підстроєний T0
}
if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    names=sys.argv[1:] or list(SCEN); rows=[]
    for nm in names:
        m=scenario(nm,**SCEN[nm]); rows.append((nm,m))
        print(f"{nm:14s} edges/line={m['false_edges_per_line']:.2f} err RMS/max={m['err_rms_pct']:.2f}/{m['err_max_pct']:.2f}% bad={m['bad_lines']} maxrun={m['max_bad_run']} blue={m['blue_events']} phase RMS/max={m['phase_rms_us']:.2f}/{m['phase_max_us']:.2f} мкс")
    with open("results/IL_summary.md","w") as f:
        f.write("| сценарій | хибних фронтів/рядок | похибка періоду RMS/max, % | поганих рядків (>5 %) | макс. серія | «синій екран» | фаза RMS/max, мкс |\n|---|---|---|---|---|---|---|\n")
        for nm,m in rows: f.write(f"| {nm} | {m['false_edges_per_line']:.2f} | {m['err_rms_pct']:.2f} / {m['err_max_pct']:.2f} | {m['bad_lines']} | {m['max_bad_run']} | {m['blue_events']} | {m['phase_rms_us']:.2f} / {m['phase_max_us']:.2f} |\n")
