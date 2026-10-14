# Hardware notes

## Pinned (to handle when we reach hardware)

- **Power wiring.** Power for the board and the DS3231 module has to be adapted. Decide which rail feeds the RTC (3.3V), how USB-C reaches the board, and where the module sits in the frame.
- **RTC battery.** Use a CR2032 with the charge resistor (200 ohm) or diode removed from the DS3231 module. At 3.3V the module's charge circuit barely charges anything, so a LIR2032 is not worth it.
- **Backlight control.** Check on the exact board whether the backlight can be dimmed (PWM) or only switched on/off. If it is behind an I/O expander, the 06:00-08:00 ramp needs a workaround.

## To determine

- Exact board model and link
- Budget check (target about 45 EUR total)
- Number of days the SD card covers
- Landscape or portrait mounting
- Frame size

## Dimensions (approximate, verify against the datasheet)

- Visible screen area: about 15.4 x 8.6 cm
- Board outline: about 16.5 x 10 cm
- Caption strip: 40 px, about 0.7 cm
- Art area: 800x440 px, about 7.9 cm tall

## Decisions made

- Fully offline: no WiFi, no NTP, no WiFiManager
- RTC set from time.txt on the SD card, applied on boot then renamed to time.done
- RTC stores local time, DST ignored
- If the RTC reports lost power, show a "set time" notice
- Caption in a dedicated strip, not an overlay
- Source images filtered to ratio 1.2 to 2.0 by default (adjustable)
- Baseline JPEG only, pre-sized to exactly 800x480
