import sys,json
for line in sys.stdin:
    if ' {' not in line: print(line.strip()); continue
    nm,js=line.split(' ',1); m=json.loads(js)
    r=lambda x,d=1: None if x is None else round(x,d)
    print(f"{nm:16s} lock {m['locked_pct']:5.1f}% coast {m['coast_pct']:4.1f}% first {m['first_lock_ms']} relock {r(m['relock_ms'])} blue {m['blue_events']} bad {m['bad_lines']} errmax {m['err_max_pct']:.2f} jit {r(m['jitter_us_locked'],3)} Tppm {r(m['T_est_err_ppm'],0)} dc {round(m['dc_err_mV_max_locked'])} V {m['v_locks']}/{m['v_resync']} edges {m['edges_per_line']}")
