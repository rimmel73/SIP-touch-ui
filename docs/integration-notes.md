# Integration Notes

## Current Wiring

This plugin is now aligned with the cloned SIP codebase in this workspace.

Confirmed integration points:

- native run-once page entry: `webpages.change_runonce`
- native run-once scheduler: `helpers.run_once`
- native stop action: `helpers.stop_stations`
- plugin route pattern: import-time `urls.extend(...)`
- plugin menu pattern: `gv.plugin_menu.append(...)`

## Important Behavior Choice

The plugin intentionally uses SIP's existing run-once flow instead of manual station toggling.

That gives us:

- station timing managed by SIP itself
- no custom scheduler logic in the plugin
- no forced change to manual mode
- behavior that stays close to the built-in run-once page

## Deployment Notes

Files should be copied into the SIP install as:

- `plugins/sip_touch_ui.py`
- `plugins/manifests/sip_touch_ui.manifest`
- `templates/sip_touch_ui.html`

## First Pi Test Checklist

1. Install the three files into SIP.
2. Enable the plugin in the plugins page.
3. Open `/touch-ui` from a phone.
4. Confirm only visible, non-master stations are shown.
5. Run one short test station for 10 seconds.
6. Verify stop works.
7. Verify controller mode before and after remains what SIP already reports.
