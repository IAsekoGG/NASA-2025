import sim_v6 as V, os
os.chdir(os.path.dirname(os.path.abspath(V.__file__)))
for W,R3,bt in [(6e-6,47e3,2.0),(6e-6,22e3,2.0),(5e-6,22e3,1.0)]:
    print(f"--- W={W*1e6:.0f}us R3={R3/1e3:.0f}k bleed={bt}s")
    for nm,kw in [("A_clean",{}),("D_cam_64p3",dict(line_period=64.3e-6)),("B_dropout",dict(dropout=[(0.10,0.20)])),("P_trap",dict(dur=0.6,dropout=[(0.05,0.10)],line_period=64.2e-6)),("M_medium_noise",dict(snr_profile=lambda tt:14.0)),("C_snr_ramp",dict(snr_profile=lambda tt:35-32*min(tt/0.30,1.0)))]:
        m=V.scenario("try_"+nm, W=W, R3=R3, bleed_tau=bt, **kw)
        print(f"{nm:14s} err={m['err_rms_pct']:.2f}/{m['err_max_pct']:.2f}% bad={m['bad_lines']} blue={m['blue_events']} ph={m['phase_rms_us']:.2f} sync%={m['src_sync_pct']:.0f} lock@{m['lock_ms']}", flush=True)
