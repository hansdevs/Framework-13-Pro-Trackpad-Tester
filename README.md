# Framework 13 Pro Trackpad Tester

Logs every physical trackpad click to a CSV with its position, pad zone and press duration. Built to document a trackpad corner that will not click, for a Framework warranty claim. Works on any Linux laptop with a touchpad. Not official, just used this for practicality. 

## Requirements

Python 3.14 (standard library only) on Linux. Needs sudo to read `/dev/input`.

## Run

```
sudo python3 touchpad_click_test.py
```

Click around the pad, then press Ctrl+C to stop.

## Output

Each click prints to the terminal and is saved to `touchpad_clicks_<date>_<time>.csv` next to the script:

```
click,time,zone,x_pct,y_pct,duration_ms
1,22:35:11,top right,99.2,4.1,358
2,22:35:16,top left,9.3,7.0,115
```

A healthy pad gives steady press durations (roughly 80 to 250 ms) in every zone. A failing area shows clicks that are missing, very short (under 50 ms) or very long because you had to force them.

Record a video while the test runs, so presses that never register are visible next to the log.
