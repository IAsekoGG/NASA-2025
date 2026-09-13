---
type: source
lang: en
date: 2026-09-13
tags: [source, report, cvbs, sync-separator]
method: "Compiled from ~50 web-search snippets; direct page fetches were blocked by the network proxy. [V] = value seen verbatim in a snippet of the cited source; [U] = standard textbook value, not verified this session."
---
# Report: CVBS sync structure and sync extraction in noisy conditions (EN)

Українські витяги: [[Структура сигналу CVBS]], [[Сепаратори синхроімпульсів]], [[Flywheel синхронізація]].

## 1. Timing and levels

### 1.1 Horizontal (line) timing
| Parameter | PAL 625/50 | NTSC 525/60 | Sources |
|---|---|---|---|
| Line period | 64.000 µs [U] | 63.556 µs [V] | [SMPTE EG27](https://pub.smpte.org/latest/eg27/eg0027-2004_stable2010.pdf), [Hinner PAL](https://martin.hinner.info/vga/pal.html) |
| Line blanking | 12.05 ± 0.25 µs [V] | 10.9 µs [V] | [NESdev PAL](https://www.nesdev.org/wiki/PAL_video), [NESdev NTSC](https://www.nesdev.org/wiki/NTSC_video), [batsocks](http://www.batsocks.co.uk/readme/video_timing.htm) |
| Front porch | 1.65 ± 0.1 µs [V] | 1.5 µs [V] | same |
| H-sync width | 4.7 ± 0.1 µs [V] | 4.7 µs [V] | [ITU-R BT.470-6](https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.470-6-199811-S!!PDF-E.pdf) |
| Back porch | ≈ 5.7 µs (derived) | 4.7 µs [V] | [diyAudio thread](https://www.diyaudio.com/community/threads/pal-amp-ntsc-composite-video-timings.58386/) |
| Breezeway | ≈ 0.9 µs | 0.6 µs [U] | derived |
| Burst start from sync leading edge | 5.6 ± 0.1 µs [V] | 5.3 µs ≈ 19 cycles [U] | [NESdev PAL](https://www.nesdev.org/wiki/PAL_video) |
| Burst length | 10 ± 1 cycles ≈ 2.25 µs [V] | 9 cycles ≈ 2.5 µs [V] | [Wikipedia Color burst](https://en.wikipedia.org/wiki/Color_burst) |
| Subcarrier | 4.43361875 MHz [V] | 3.579545 MHz [V] | [Skyworks AN377](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN377.pdf) |
| Active line | 52 µs [V] | 52.6 µs [V] | Hinner, NESdev |

### 1.2 Vertical (field) timing
| Parameter | PAL | NTSC | Sources |
|---|---|---|---|
| Lines per frame / field | 625 / 312.5 [U] | 525 / 262.5 [U] | — |
| Field / frame rate | 50 Hz / 25 Hz [U] | 59.94 Hz / 29.97 Hz [U] | — |
| Field blanking | 25 lines ≈ 1.6 ms [V] | 20–21 lines [U] | BT.470 |
| Pre-equalising | 5 pulses / 2.5 H [V] | 6 / 3 H [V] | [US 4,169,659](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4169659), [SMPTE ST 244](https://pub.smpte.org/pub/st244/st0244-2003.pdf) |
| Broad (serrated) pulses | 5 / 2.5 H [V] | 6 / 3 H [V] | same |
| Post-equalising | 5 / 2.5 H [V] | 6 / 3 H [V] | same |
| Equalising pulse width | 2.35 ± 0.1 µs [V] | 2.3 µs [U] | BT.470, [US 4,535,353](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4535353) |
| Broad pulse width | 27.3 ± 0.1 µs [V] | ≈ 27 µs [V] | same |
| Pulse rate in VBI | 2 H [V] | 2 H [V] | US 4,169,659 |
| Odd/even | half-line offset of the pulse train between fields [V] | same | US 4,169,659, [LM1881 DS](https://www.ti.com/lit/gpn/lm1881) |

Why: serrations keep H running through V; equalising pulses at 2H equalise the RC-integrator charge between fields so interlace is preserved ([TV Tech](https://www.tvtechnology.com/miscellaneous/analog-video-synchronization), [US 5,844,626](https://patents.google.com/patent/US5844626A/en)).

### 1.3 Voltage levels (1 Vpp / 75 Ω)
| Level | PAL | NTSC | Sources |
|---|---|---|---|
| Sync tip | −300 mV [V] | −40 IRE = −286 mV [V] | [Wikipedia Blanking level](https://en.wikipedia.org/wiki/Blanking_level) |
| Blanking | 0 mV | 0 IRE | |
| Black | 0 mV | 7.5 IRE ≈ 54 mV [V] | [Maxim Tutorial 734](https://www.maximintegrated.com/en/design/technical-documents/tutorials/7/734.html) |
| White | +700 mV | 100 IRE = 714 mV | [EBU Tech 3280](https://tech.ebu.ch/docs/tech/tech3280.pdf) |

## 2. Sync separator ICs
| Part | Status | Slice | Outputs | Noise notes | Price |
|---|---|---|---|---|---|
| LM1881 (TI) | active; clones exist | sync tip + 70 mV [V], 0.5–2 Vpp | CSYNC, VSYNC, BP, O/E | "assumed clean and relatively noise-free"; 620 Ω + 510 pF LPF recommended [V]; RSET 680 kΩ → 64 µs V default | DigiKey $3.19–4.92; LCSC clones $0.36–0.5 |
| LMH1980 (TI) | "Transferred"? | 50 % | CS, HS, VS, BP, O/E | small CIN; RC LPF; not hot-plug tolerant ([SNLA255](https://www.ti.com/lit/pdf/snla255)) | LCSC $2.55 |
| LMH1981 (TI) | active | 50 % | CS, HS, VS, BP, O/E, format | HS delay variation < ±3 ns | DigiKey $12–17 |
| EL1883 (Renesas) | obsolete 2022 | 70 mV | CS, VS, BP, H | Macrovision tolerant | — |
| EL4581/EL4583 (Renesas) | EL4583CSZ still listed | 50 % from two S/H | CS, VS, filter, BP, H, no-signal, level, O/E | "hum and noise rejection", built-in chroma filter, default V when no serrations | Mouser $10 |
| ISL59885 (Renesas) | active | auto-adjusting | HOUT, VOUT, CSYNC, SD/HD | non-standard tolerant | $2.7–8 |
| GS1881/4881/4981 (Gennum) | obsolete | sync tip | CS, VS, BP, O/E | "noise immune back porch pulse" | — |
| GS4882/4982 | obsolete | precision 50 % | | ±5 ns, "superior noise immunity" | — |
| MAX7450/51/52 (ADI) | conditioner | DC restore, AGC ±6 dB, BP clamp, fault detect | | | — |

Datasheets: [LM1881](https://www.ti.com/lit/gpn/lm1881), [LMH1980](https://www.ti.com/lit/pdf/snls263), [LMH1981](https://datasheet.octopart.com/LMH1981MT-National-Semiconductor-datasheet-10846906.pdf), [EL1883](https://www.renesas.com/en/document/dst/el1883-datasheet), [EL4583](https://www.farnell.com/datasheets/65607.pdf), [ISL59885](https://docs.rs-online.com/774d/0900766b80e2c788.pdf), [GS1881](https://www.mouser.com/datasheet/2/761/GS1881_GS4881_GS4981_Datasheet-769183.pdf), [EL1883 EOL](https://www.renesas.com/en/document/eln/plc21035-end-life-notice), [LM1881 DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/LM1881M-NOPB/148116), [LCSC clones](https://lcsc.com/product-detail/Interface-Specialized_HGSEMI-LM1881M-TR_C518922.html).

Key distinction: none of these has a flywheel. Video decoders do: [TVP5150A](https://www.ti.com/product/TVP5150A) "patented technology for locking to weak, noisy, or unstable signals"; [ADV7180](https://www.analog.com/media/en/technical-documentation/data-sheets/ADV7180.pdf) "HSYNC processor is designed to filter incoming HSYNCs that have been corrupted by noise".

## 3. Clamp / DC restoration
- Why: AC-coupled video DC level varies with scene content ([LT AN57](https://www.analog.com/media/en/technical-documentation/application-notes/an57fa.pdf)).
- Types ([Maxim Tutorial 3303](https://www.maximintegrated.com/en/design/technical-documents/tutorials/3/3303.html)): diode sync-tip clamp, keyed clamp (sync tip or back porch), DC restore.
- Noise: sync-tip clamp "rides on the negative sync tip noise" ([US 5,798,802](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5798802)); back-porch clamp noise → streaking ([US 7,126,645](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7126645)).
- Buffers with clamp: [THS7314](https://www.ti.com/lit/ds/symlink/ths7314.pdf) / [THS7316](https://www.ti.com/lit/gpn/THS7316) (6 dB, LPF, transparent sync-tip clamp), [THS7303](https://www.ti.com/lit/ds/symlink/ths7303.pdf) (active STC, 135 mV), [MAX4090](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX4090-MAX4090A.pdf) (6 dB, sync-tip clamp, SOT23).
- App notes: [ADI AN-1603](https://www.analog.com/media/en/technical-documentation/application-notes/an-1603.pdf), [Renesas AN9514](https://www.renesas.com/en/document/apn/an9514-video-amplifier-sync-stripper-and-dc-restore), [Renesas AN9752 sync stripper/inserter](https://www.renesas.com/en/document/apn/an9752-sync-stripper-and-sync-inserter-composite-video-hfa1115-hfa1135?language=en), [Embedded.com](https://www.embedded.com/component-and-rgb-video-routing-clamping-and-sync-extraction/).

## 4. Flywheel / AFC in TV receivers
- Dual time constant PLL, coincidence detector decides ([US 5,621,485](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5621485), [EP 0504209](https://patents.google.com/patent/EP0504209A1/en)).
- History: [GE Techni-Talk 1950 "Horizontal AFC Systems"](https://www.worldradiohistory.com/Archive-Company-Publications/GE-Techni-Talk/GE-Techni-Talk-1950-04-05.pdf), [Gernsback 1963](https://www.worldradiohistory.com/BOOKSHELF-ARH/Technology/Gernsback/Gernsback-Horizontal-Sweep-Servicing-Handbook-Darr-1963.pdf), [US 2,702,348](https://patents.google.com/patent/US2702348), [US 3,497,620](https://patents.google.com/patent/US3497620).
- ICs: [TDA2593](https://eandc.ru/pdf/import/tda2593.pdf) (gated φ1, noise separator, coincidence detector, time-constant switch), [TDA2595](https://www.alldatasheet.com/datasheet-pdf/pdf/143335/PHILIPS/TDA2595.html) (adaptive sync separator, double-slope V integrator, φ3 coincidence → auto time-constant), [TDA2579](http://www.elektronikjk.pl/elementy_czynne/IC/TDA2579.pdf) (triple current source), [LM1391](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/48/LM1391datasheet.PDF) (H PLL, ~300 Hz pull-in).
- Gain scheduling within field: [US 5,561,354](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5561354), [US 4,482,869](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4482869).

## 5. Noise on sync — countermeasures
1. Noise gating / inversion ([US 4,254,435](https://patents.google.com/patent/US4254435A/en), [US 3,582,551](https://patents.google.com/patent/US3582551), [CA 1,130,914](https://patents.google.com/patent/CA1130914A/en)).
2. Phase-detector gating / sync window; digital: disable H detector for a duration after valid H, "free-wheel" when missing ([US 6,833,875](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6833875)).
3. Pulse-width discrimination: e.g. "≥ 80 consecutive samples below −20 IRE" (US 6,833,875); analog ([US 4,400,733](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4400733)).
4. Vertical integration; 10–15 µs constants for poor tapes ([US 4,467,358](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4467358)).
5. Flywheel averaging / dual time constant (Section 4).
6. Majority voting across lines — not found named; decoders use lock counters instead.

Front-end idea: 75 Ω → 620 Ω/510 pF LPF → 50 % slicer (LMH1981/EL4583) or LM1881 → MCU/FPGA PLL with ±1–2 µs window; slow loop when locked, fast when not; V by integrating gated sync; keyed back-porch clamp.

## 6. Reading list
- [ITU-R BT.470-6](https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.470-6-199811-S!!PDF-E.pdf) · [BT.1700](https://www.itu.int/rec/R-REC-BT.1700) · [SMPTE EG 27](https://pub.smpte.org/latest/eg27/eg0027-2004_stable2010.pdf) · [SMPTE ST 244](https://pub.smpte.org/pub/st244/st0244-2003.pdf) · [EBU Tech 3280](https://tech.ebu.ch/docs/tech/tech3280.pdf)
- [Maxim 734 Video Basics](https://www.maximintegrated.com/en/design/technical-documents/tutorials/7/734.html) · [Maxim 3303 Clamps](https://www.maximintegrated.com/en/design/technical-documents/tutorials/3/3303.html) · [ADI Understanding analog video](https://www.analog.com/media/en/technical-documentation/tech-articles/understanding-analog-video-signals--maxim-integrated.pdf)
- [TI SNLA097A](https://www.ti.com/lit/an/snla097a/snla097a.pdf) · [TI AN-861](https://www.ti.com/lit/an/snoa268/snoa268.pdf) · [Renesas TB368](https://www.renesas.com/en/document/tcb/tb368-understanding-video-timing-digital-video-encoders)
- Keith Jack, *Video Demystified* ([Elsevier](https://shop.elsevier.com/books/video-demystified/jack/978-0-7506-8395-1))
- [Retroleum PAL timing](http://blog.retroleum.co.uk/electronics-articles/pal-tv-timing-and-voltages/) · [Hinner PAL](https://martin.hinner.info/vga/pal.html) · [NESdev PAL](https://www.nesdev.org/wiki/PAL_video) / [NTSC](https://www.nesdev.org/wiki/NTSC_video)

## Unverified
NTSC breezeway/burst start/eq/broad widths, burst amplitudes; TDA/LM1391 numeric time constants; ISL59885 slice method; current prices of LMH1980/EL4583/ISL59885.
