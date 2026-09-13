---
type: prior-art
status: researched
tags: [prior-art, opensource, rp2040, fpga]
---
# DIY та open-source проєкти, з яких можна брати код і схеми

## Найближчий за духом: PicoSync (RP2040)
https://github.com/Adewotta/PicoSync (форк https://github.com/mackieks/PicoSync-PS2)
- Проблема, яку розв'язує: при XNOR-об'єднанні H і V губиться один H-фронт у VBI → дорогі монітори (Sony BVM) не синхронізуються.
- Рішення: **PIO спостерігає за CSYNC і вставляє відсутній спадний фронт, якщо його немає; якщо є — пропускає без змін.** Це буквально режим PASS/REPLACE нашого [[Блок 5 - Вставка sync (аналоговий ключ)]], тільки для TTL-sync і однієї детермінованої вади.
- Обмеження: TTL-рівні, без 75 Ω, без LM1881 на вході; окремі H/V прибрали, бо софтверне об'єднання було нестабільним → винесли в апаратний XNOR. Урок: **критичні за часом речі — в PIO/залізо, не в переривання.**
- Протестовано на 240p/480i/480p/720p/1080i.

## Точний захват фронтів на RP2040 (ключова техніка)
Cornell ECE4760 «PIO input capture»: RP2040 не має апаратного input capture, тому дві PIO-машини зі зсувом на пів такту дають часову мітку фронту з роздільністю **16 нс на 62.5 MHz (8 нс на 125 MHz)** у FIFO. — https://people.ece.cornell.edu/land/courses/ece4760/RP2040/C_SDK_PIO_control/Input_capture/index_pio_control.html
Це основа [[Блок 3 - Трекер таймінгу (flywheel PLL)]] на Pico. Альтернатива — STM32 з апаратним таймерним capture + DMA (простіше і надійніше, якщо є досвід).

## Генерація точного композитного sync на MCU (для Блоку 4)
| Проєкт | Що корисно |
|---|---|
| pico-composite-PAL-colour (guruthree) — https://github.com/guruthree/pico-composite-PAL-colour | PIO-генерація повного PAL із кольором; таблиці таймінгів рядка/поля, готова структура VBI |
| pico-composite8 (obstruse) — https://github.com/obstruse/pico-composite8 | NTSC interlaced 640×480, R2R DAC |
| pico-composite-video (alanpreed) — https://github.com/alanpreed/pico-composite-video | простий приклад |
| PicoVGA (Nemecek / codaris) — https://codaris.github.io/picovga-cmake/ | зріла бібліотека з детермінованим таймінгом |
| mac-se-video-converter (guruthree) — https://github.com/guruthree/mac-se-video-converter | `videoinput.pio`: **захват зовнішнього sync у PIO + перегенерація таймінгу на вихід** — скелет нашого пристрою |
| bitluni ESP32CompositeVideo — https://github.com/bitluni/ESP32CompositeVideo | генерація на ESP32 (I2S/DMA) — якщо обрати ESP32 |
| STM32 | готового проєкту з equalizing/serration не знайдено — писати самим на TIM + DMA |

## FPGA / CPLD (якщо A не вистачить точності або підемо у C)
- **RGBtoHDMI** (hoglet67): CPLD семплює sync із роздільністю 10.4 нс, «leading sync edge triggering», VHDL відкритий — https://github.com/hoglet67/RGBtoHDMI
- **OSSC**: вбудований «sync filter & separator» у ADC-фронтенді, порядкова обробка без буфера кадру (near-zero latency) — https://github.com/ManuFerHi/OSSC , https://consolemods.org/wiki/AV:Open_Source_Scan_Converter_(OSSC)
- **GBS-Control**: «output runs independent from input, sync to display never drops» — принцип відв'язки вихідного sync від входу — https://github.com/ramapcsx2/gbs-control
- MiSTer analog IO — лише вихідна сторона, мало корисне.

## Алгоритми пошуку sync у шумі: ld-decode / vhs-decode
https://github.com/happycube/ld-decode , https://github.com/oyvindln/vhs-decode (wiki: Technical-Code-Breakdowns)
Конвеєр: `getpulses()` → `refinepulses()` (класифікація H/V/eq за шириною й позицією) → `computeLineLen()` (очікувана довжина рядка) → `getLine0()` → `get_first_hsync_loc()` → `valid_pulses_to_linelocs()`.
Що переносимо у прошивку:
- підтримувати **очікувану довжину рядка** й шукати імпульс лише у вікні навколо прогнозу;
- класифікувати імпульси за **шириною** (4.7 / 2.35 / 27.3 мкс);
- якщо у вікні нічого валідного — ставити рядок за прогнозом (coasting);
- опція vhs-decode: використовувати **задній (висхідний) фронт** H-sync, бо передній частіше спотворений на поганому сигналі — цікаво перевірити для FM-шуму приймача.

## Тест-генератори і захват (для [[Тестовий стенд]])
- RP2040-TestPatternGenerator (nmur) — https://github.com/nmur/RP2040-TestPatternGenerator ; ESP32 варіант — https://github.com/nmur/ESP32-TestPatternGenerator
- pico-pattern (sharpie7) — https://github.com/sharpie7/pico-pattern
- Adafruit QT Py ESP32 NTSC test pattern — https://learn.adafruit.com/video-nub-shank-esp32-qt-py-composite-video-injector/ntsc-test-pattern-generator
- Elektor/Hackaday кишеньковий CRT pattern generator (12/2025) — https://hackaday.com/2025/12/26/pocket-sized-test-pattern-generator-helps-check-those-crts/
- Жоден не має «керованих пропадань» — додамо самі (модифікація pico-composite: за командою по UART гасити/спотворювати sync на N рядків, додавати шум з ЦАП).
- Захват: EasyCap UTV007 ($10–15) для логів; але його власний декодер теж «бланкує» — не еталон. Еталон — осцилограф з відео-тригером або логічний аналізатор на виході сепаратора.

## Висновок
Готового «FPV sync regenerator» немає ні англійською, ні російською, ні українською. Є всі цеглини: PicoSync (патерн вставки), Cornell capture (мітки часу), pico-composite (таймінг генерації), vhs-decode (алгоритм), AN9752/стабілізатори (аналогова вставка). Це оригінальна робота зі збірки перевірених частин.
