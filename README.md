# art-frame

Offline daily art display frame. One public domain artwork per day, shown on an 800x480 screen with a caption strip at the bottom. No WiFi, time comes from a DS3231 RTC, images come from a microSD card.

## Layout

```
art-frame/
  tools/             Python fetcher (Met API -> JPEG + JSON on a folder)
  firmware/          ESP32-S3 firmware (not started)
  sdcard_sample/     what the SD card should look like
  docs/              hardware notes, decisions, pinned items
  README.md
```

## SD card layout

```
/art/0001.jpg    800x480 baseline JPEG (art area 800x440, bottom 40 px reserved for caption)
/art/0001.json   {"title": "...", "artist": "...", "date": "..."}
/art/index.json  list of entries, used by the firmware
/time.txt        optional, "YYYY-MM-DD HH:MM", applied to the RTC on boot then renamed to time.done
```

## Fetcher usage

```bash
pip install -r tools/requirements.txt
python tools/fetch_art.py --count 365 --out out
```

Then copy the content of `out/` to the root of the SD card (FAT32).

## Status

- [x] Repo skeleton
- [x] Fetcher script (untested against the live API)
- [ ] Hardware decisions (see docs/hardware.md)
- [ ] Firmware
