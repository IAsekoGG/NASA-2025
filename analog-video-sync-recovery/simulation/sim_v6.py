#!/usr/bin/env python3
"""v6 = 555 injection-locked (як v5) + CD4046 як пам'ять частоти:
PC2 порівнює ВИХІД 555 (один фронт на рядок) з VCO; VCO_OUT через затримку kick_delay також штовхає 555.
Справжній sync (якщо є і потрапив у вікно) завжди випереджає поштовх VCO; без сигналу 555 запускає VCO
з вивченим періодом камери. RC-період 555 (T0) — лише страховка, довший за все."""
import sys, os, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sim_v4 as S

def hybrid_run(sig_edges_t, t_end, fmin=15.3e3, fmax=16.3e3, R3=22e3, R4=10e3, C=1e-6,
               T0=66.5e-6, W=5e-6, kick_delay=0.8e-6, VDD=5.0, v9_init=None, phase_init=None, bleed_tau=1.0):
    dt=0.1e-6; n=int(t_end/dt)
    sig=np.zeros(n+1,bool); idx=(sig_edges_t/dt).astype(int); idx=idx[(idx>=0)&(idx<n)]; sig[idx]=True
    vkick=np.zeros(n+100,bool); kd=int(kick_delay/dt)
    if v9_init is None: v9_init=float(np.clip(VDD*(1/S.H-fmin)/(fmax-fmin),0,VDD))
    vc=v9_init; f0=fmin+(fmax-fmin)*vc/VDD
    phase=((1.0-f0*float(sig_edges_t[0])) % 1.0) if (phase_init is None and len(sig_edges_t)) else (phase_init or 0.0)
    up=down=False; T0s=int(T0/dt); Ws=int(W/dt); next_rc=T0s
    starts=[]; nl=(n+99)//100; f_log=np.zeros(nl,np.float32); v9_log=np.zeros(nl,np.float32)
    src=[]  # що запустило рядок: 0 таймаут, 1 sync, 2 VCO
    for i in range(n):
        if up:     v9=vc+(VDD-vc)*R4/(R3+R4)
        elif down: v9=vc+(0.0-vc)*R4/(R3+R4)
        else:      v9=vc
        f=fmin+(fmax-fmin)*min(max(v9/VDD,0.0),1.0)
        phase+=f*dt; comp=False
        if phase>=1.0:
            phase-=1.0; comp=True; vkick[i+kd]=True
        # 555
        trig=0
        if i>=next_rc: trig=3
        elif i>=next_rc-Ws:
            if sig[i]: trig=1
            elif vkick[i]: trig=2
        if trig:
            starts.append(i*dt); src.append(trig); next_rc=i+T0s; up=True   # вихід 555 = SIG_IN PC2
        if comp: down=True
        if up and down: up=down=False
        if up:   vc+=(VDD-vc)/(R3+R4)*dt/C
        elif down: vc+=(0.0-vc)/(R3+R4)*dt/C
        vc-=vc*dt/bleed_tau            # R_bleed || C8: VCO повільно «сповзає» вниз → sync завжди випереджає поштовх VCO
        if i%100==0: f_log[i//100]=f; v9_log[i//100]=v9
    return np.array(starts), np.array(src), f_log, dt*100

def scenario(name, dur=0.30, line_period=S.H, snr_profile=None, dropout=None, silence=None, seed=1, **kw):
    rng=np.random.default_rng(seed); n_lines=int(dur/line_period)
    v,starts=S.gen_cvbs(n_lines,line_period); t=np.arange(len(v))*S.DT
    amp=np.ones_like(v)
    if snr_profile is None: snr_profile=lambda tt:35.0
    snr=np.array([snr_profile(tt) for tt in t[::1000]]); sigma=np.repeat(1.0/(10**(snr/20)),1000)[:len(v)].astype(np.float32)
    for a,b in (dropout or []): m=(t>=a)&(t<b); amp[m]=0; sigma[m]=0.30
    for a,b in (silence or []): m=(t>=a)&(t<b); amp[m]=0; sigma[m]=0
    vin=v*amp+rng.normal(0,1,len(v)).astype(np.float32)*sigma
    cs,s_idx,e_idx=S.lm1881(vin); sig=s_idx*S.DT+0.15e-6
    st,src,f_log,dtl=hybrid_run(sig,dur,**kw)
    m,err,ph=S.analyze(st,starts,line_period)
    m["false_edges_per_line"]=float(len(s_idx)/n_lines); m["vco_f_min_kHz"]=float(f_log.min()/1e3); m["vco_f_max_kHz"]=float(f_log.max()/1e3)
    good=0; m["lock_ms"]=None
    for k in range(min(len(ph),len(src))):
        good = good+1 if (src[k]==1 and abs(ph[k]-0.65)<1.0) else 0
        if good>=50: m["lock_ms"]=float(st[k]*1e3); break
    m["src_sync_pct"]=float((src==1).mean()*100); m["src_vco_pct"]=float((src==2).mean()*100); m["src_timeout_pct"]=float((src==3).mean()*100)
    fig,ax=plt.subplots(4,1,figsize=(11,9.5),sharex=True)
    tl=np.arange(len(f_log))*dtl*1e3
    ax[0].plot(tl,f_log/1e3,lw=1); ax[0].axhline(1/S.H/1e3,color="k",ls="--",lw=.7); ax[0].axhspan(1/S.H/1e3*.95,1/S.H/1e3*1.05,color="g",alpha=.08); ax[0].set_ylabel("VCO, кГц"); ax[0].set_title(f"{name} (v6: 555 + 4046 як пам'ять частоти)")
    te=st[1:len(err)+1]*1e3; ax[1].plot(te,err,lw=.6); ax[1].axhspan(-5,5,color="g",alpha=.08); ax[1].set_ylim(-12,12); ax[1].set_ylabel("похибка періоду, %")
    ax[2].plot(st[:len(ph)]*1e3,ph,lw=.6); ax[2].axhspan(-1,2.3,color="g",alpha=.08); ax[2].set_ylim(-33,33); ax[2].set_ylabel("фаза vs sync, мкс")
    tt=t[::100]*1e3; ax[3].plot(tt,sigma[::100]*1e3,lw=.8,label="σ шуму, мВ"); ax[3].plot(tt,amp[::100]*300,lw=.8,label="сигнал"); ax[3].legend(loc="upper right"); ax[3].set_xlabel("час, мс")
    fig.tight_layout(); fig.savefig(f"results/V6_{name}.png",dpi=110); plt.close(fig)
    np.savez(f"results/V6_{name}.npz",vco_edges=st,err=err,ph=ph,f_log=f_log,dtl=dtl,sigma=sigma[::100],amp=amp[::100],t=t[::100],starts=starts,line_period=line_period,src=src)
    return m

SCEN={
 "A_clean":dict(), "B_dropout":dict(dropout=[(0.10,0.20)]), "B_long_dropout":dict(dur=0.8,dropout=[(0.10,0.60)]),
 "C_snr_ramp":dict(snr_profile=lambda tt:35-32*min(tt/0.30,1.0)), "D_cam_64p3":dict(line_period=64.3e-6), "D_cam_65p0":dict(line_period=65.0e-6),
 "E_silence":dict(silence=[(0.10,0.20)]), "F_bursts":dict(dropout=[(0.08,0.12),(0.16,0.20),(0.24,0.28)]),
 "H_heavy_noise":dict(snr_profile=lambda tt:8.0), "M_medium_noise":dict(snr_profile=lambda tt:14.0),
 "G_acquire_fast":dict(dur=1.5,phase_init=0.5,v9_init=3.0),
 "P_trap":dict(dur=0.6,dropout=[(0.05,0.10)],line_period=64.2e-6),  # після пропадання камера повільніша за вивчене   # VCO стартує швидшим за камеру (пастка «VCO виграє»)
 "G_acquire_slow":dict(dur=1.5,phase_init=0.5,v9_init=1.0),
}
if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__))); names=sys.argv[1:] or list(SCEN); rows=[]
    for nm in names:
        m=scenario(nm,**SCEN[nm]); rows.append((nm,m))
        print(f"{nm:16s} edges/l={m['false_edges_per_line']:.2f} VCO={m['vco_f_min_kHz']:.2f}-{m['vco_f_max_kHz']:.2f} err={m['err_rms_pct']:.2f}/{m['err_max_pct']:.2f}% bad={m['bad_lines']} blue={m['blue_events']} ph={m['phase_rms_us']:.2f}/{m['phase_max_us']:.1f} запуск: sync {m['src_sync_pct']:.0f}% / VCO {m['src_vco_pct']:.0f}% / RC {m['src_timeout_pct']:.0f}% lock@{m['lock_ms']}", flush=True)
    with open("results/V6_summary.md","w") as f:
        f.write("| сценарій | VCO min–max, кГц | похибка періоду RMS/max, % | поганих | «синій» | фаза RMS/max, мкс | запуск рядка: sync / VCO / RC, % | lock, мс |\n|---|---|---|---|---|---|---|---|\n")
        for nm,m in rows: f.write(f"| {nm} | {m['vco_f_min_kHz']:.2f}–{m['vco_f_max_kHz']:.2f} | {m['err_rms_pct']:.2f} / {m['err_max_pct']:.2f} | {m['bad_lines']} | {m['blue_events']} | {m['phase_rms_us']:.2f} / {m['phase_max_us']:.1f} | {m['src_sync_pct']:.0f} / {m['src_vco_pct']:.0f} / {m['src_timeout_pct']:.0f} | {'' if m['lock_ms'] is None else round(m['lock_ms'])} |\n")
