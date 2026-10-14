# Firmware

Not started. Arduino vs ESP-IDF still to decide.

Planned behaviour:

- Read /art/index.json from the SD card
- Pick today's image from the RTC date (days since a start date, modulo count)
- Decode the 800x480 baseline JPEG into PSRAM and draw it
- Draw title, artist and date in the 40 px strip at the bottom
- Backlight schedule from RTC time: off 23:00-06:00, ramp 06:00-08:00, full 08:00-23:00
- Apply /time.txt to the RTC on boot, rename it to time.done
- Show a "set time" notice if the RTC lost power
- WiFi stays off
