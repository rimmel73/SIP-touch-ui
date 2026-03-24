# SIP Touch UI

AI vibe coded Touch-first SIP plugin for fast station runs from a phone.

## What It Does

- shows large, thumb-friendly buttons for visible stations
- offers fixed run times from 10 seconds to 10 minutes
- asks for confirmation before starting a station
- provides a single stop button for all running stations
- reuses SIP's native `run_once()` and `stop_stations()` flow
- leaves SIP's current controller mode intact instead of forcing a custom mode

## Plugin Files

- `plugin/sip_touch_ui.py`: SIP plugin entry point and API endpoints
- `plugin/sip_touch_ui.manifest`: plugin manager install manifest
- `templates/sip_touch_ui.html`: mobile-first SIP page template
- `static/sip_touch_ui.js`: injects a `Touch UI` shortcut into SIP's top nav
- `scripts/install-to-sip.ps1`: copies the plugin into a SIP checkout

## How It Integrates With SIP

The plugin registers these routes:

- `/touch-ui`: touch control page
- `/touch-ui/run`: start one station using SIP's run-once scheduling
- `/touch-ui/stop`: stop all running stations
- `/touch-ui/status`: lightweight status polling for the page

Under the hood it:

- reads station names and visibility from `gv`
- excludes the master station from the touch page
- fills `gv.rovals` with just one selected station duration
- calls `run_once()` exactly like SIP's own run-once flow
- calls `stop_stations()` for the stop action

## Installation Into SIP

Copy these files into your SIP install:

- `plugin/sip_touch_ui.py` -> `SIP/plugins/sip_touch_ui.py`
- `plugin/sip_touch_ui.manifest` -> `SIP/plugins/manifests/sip_touch_ui.manifest`
- `templates/sip_touch_ui.html` -> `SIP/templates/sip_touch_ui.html`
- `static/sip_touch_ui.js` -> `SIP/static/scripts/sip_touch_ui.js`

Then enable the plugin in SIP's plugin manager and restart SIP if needed.

Or, if you have a local SIP checkout, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-to-sip.ps1
```

## Next Step

Install it into your Pi's SIP instance and test:

1. open `/touch-ui`
2. pick a duration
3. tap a station
4. confirm the action
5. verify the stop button halts active stations
