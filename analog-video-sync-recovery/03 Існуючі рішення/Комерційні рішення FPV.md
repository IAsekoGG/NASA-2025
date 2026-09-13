---
type: prior-art
status: researched
tags: [prior-art, fpv, rapidfire, clearview]
---
# Комерційні рішення у FPV (prior art)

| Продукт | Що заявляє | Що відомо про механізм | Затримка | Урок для нас |
|---|---|---|---|---|
| **ImmersionRC rapidFIRE** («Analog Plus») | «fuses images from two receivers, predicts noise before it is visible, rebuilds analog signals to avoid tearing, rolling, dropped DVR frames, zero added latency» | Teardown-ів немає. Firmware 1.2.7 додало налаштування **Sync Lock time**; 1.3.2 прибрало його, зафіксувавши «short» — «eliminates rolling even with marginal systems». Це прямий доказ, що всередині є трекер sync із налаштовуваним часом захоплення/утримання | «zero added» (ймовірно ≤ 1 рядок) | Час lock/coast — параметр, який доведеться підбирати; «short» виграв у виробника |
| **Iftron ClearView** | «Digitally Enhanced Video Receiver… stabilizes the picture, reduces noise in real time… eliminates glitches, dropouts, rolling, tearing… latency-free», «Patents Pending» | Патентів під ім'ям Iftron у Google Patents не знайдено. Механізм не розкрито | «latency-free» | Робиться на рівні приймача, де є доступ до RSSI/демодулятора — у нас цього немає, ми працюємо лише з CVBS |
| **TBS Fusion** | «active video fusion» двох входів (обробка BrainFPV) «without color deterioration or video desync» | Деталей немає | — | Diversity + regeneration — окрема тема; наш пристрій може стояти після будь-якого приймача |
| **Walksnail Goggles X + аналоговий модуль** | Показує **сніг замість синього екрана** при втраті | Оцифровує аналог (тому 10–20 ms затримки) | 10–20 ms | Доказ, що «сніг замість синього» — бажана поведінка; але цифровий шлях коштує затримки |
| **Lilliput 664/W «No Blue Screen»** | Монітор, який не бланкує «від 100 до 2000 м» | Ймовірно, відключений no-signal детектор скейлера | 0 | Деякі монітори це вміють «з коробки»; варто перевірити сервісне меню свого монітора |
| **Hawkeye Firefly Little Pilot** | «anti blue screen / anti black screen technology» | Не розкрито | 0 | Те саме |
| **Feelworld** | Меню «No Signal»: Blue/Red/Green/Black/White screen | Це лише колір заставки, **не** відключення бланкування | — | Не плутати з «no blue screen» |

## Спільнота (DIY-спроби до нас)
- IntoFPV «Removing Blue screen on monitor»: пропуск через **MAX7456** або DVR дає сніг замість синього. — https://intofpv.com/t-removing-blue-screen-on-monitor
- RCGroups «FPV monitor no blue screen» (2011+): «dummy» MinimOSD як регенератор — в одного не спрацював; TBC за $200 — працює. — https://www.rcgroups.com/forums/showthread.php?1494699-FPV-monitor-no-blue-screen
- fpvlab «Advice needed: Anti LCD Bluescreen device», Arduino Forum «Help coming up with Anti-BLUESCREEN device» (2012): пропонували LM1881 як основу; готового завершеного проєкту не знайдено. — https://fpvlab.com/forums/showthread.php?3672 , https://forum.arduino.cc/t/help-coming-up-with-anti-bluescreen-device/120874

**Висновок:** задача давно відома, комерційно вирішена всередині приймачів/окулярів, а як **окрема коробка між приймачем і монітором** у DIY — обговорювалась, але завершеного відкритого проєкту не знайдено. Ніша вільна.

## Джерела
- https://www.immersionrc.com/fpv-products/rapidfire/
- https://intofpv.com/t-rapidfire-calibration?page=2 (changelog Sync Lock)
- https://clearview-direct.com/discover/ , https://www.getfpv.com/iftron-clearview-goggle-receiver-module.html
- https://www.team-blacksheep.com/products/prod:tbs_fusion
- https://oscarliang.com/walksnail-goggle-x-extension-module/
- https://www.amazon.com/Lilliput-664-1280x800-Receiver-Photography/dp/B00F2O3PY2
- https://www.manualslib.com/manual/2063052/Feelworld-Fw759.html
