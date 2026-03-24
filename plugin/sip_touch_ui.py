# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Touch-first station runner plugin for SIP."""

import ast
import io
import json
import time

import gv
from helpers import run_once, stop_stations
from sip import template_render
from urls import urls
import web
from webpages import ProtectedPage


urls.extend(
    [
        u"/touch-ui",
        u"plugins.sip_touch_ui.touch_ui_page",
        u"/touch-ui/run",
        u"plugins.sip_touch_ui.touch_ui_run",
        u"/touch-ui/stop",
        u"plugins.sip_touch_ui.touch_ui_stop",
        u"/touch-ui/status",
        u"plugins.sip_touch_ui.touch_ui_status",
    ]
)

gv.plugin_menu.append([_(u"Touch UI"), u"/touch-ui"])
gv.plugin_scripts.append(u"sip_touch_ui.js")


DURATION_OPTIONS = [
    {u"label": u"10s", u"seconds": 10},
    {u"label": u"20s", u"seconds": 20},
    {u"label": u"30s", u"seconds": 30},
    {u"label": u"1m", u"seconds": 60},
    {u"label": u"2m", u"seconds": 120},
    {u"label": u"3m", u"seconds": 180},
    {u"label": u"4m", u"seconds": 240},
    {u"label": u"5m", u"seconds": 300},
    {u"label": u"6m", u"seconds": 360},
    {u"label": u"7m", u"seconds": 420},
    {u"label": u"8m", u"seconds": 480},
    {u"label": u"9m", u"seconds": 540},
    {u"label": u"10m", u"seconds": 600},
    {u"label": u"15m", u"seconds": 900},
    {u"label": u"20m", u"seconds": 1200},
]

ALLOWED_SECONDS = [item[u"seconds"] for item in DURATION_OPTIONS]


def duration_label(seconds):
    if seconds < 60:
        return _(u"{seconds}s").format(seconds=seconds)
    minutes, remainder = divmod(seconds, 60)
    if remainder:
        return _(u"{minutes}m {seconds}s").format(minutes=minutes, seconds=remainder)
    return _(u"{minutes}m").format(minutes=minutes)


def relative_time_label(timestamp):
    elapsed = max(0, int(time.time()) - int(timestamp))
    if elapsed < 60:
        return _(u"just now")
    if elapsed < 3600:
        minutes = elapsed // 60
        return _(u"{minutes}m ago").format(minutes=minutes)
    if elapsed < 86400:
        hours = elapsed // 3600
        return _(u"{hours}h ago").format(hours=hours)
    if elapsed < 604800:
        days = elapsed // 86400
        return _(u"{days}d ago").format(days=days)
    return time.strftime("%d %b %Y", time.localtime(timestamp))


def read_log_records():
    try:
        with io.open(u"./data/log.json", u"r", encoding="utf-8") as logf:
            return logf.readlines()
    except IOError:
        return []


def station_last_runs():
    results = {}
    records = read_log_records()
    for line in records:
        try:
            parsed = json.loads(line)
            event = ast.literal_eval(parsed)
        except (ValueError, SyntaxError):
            try:
                event = json.loads(line)
            except ValueError:
                continue

        try:
            station_index = int(event[u"station"])
        except (KeyError, TypeError, ValueError):
            continue

        if station_index in results:
            continue

        duration_text = event.get(u"duration", u"")
        duration_seconds = 0
        try:
            parts = [int(part) for part in duration_text.split(":")]
            if len(parts) == 2:
                duration_seconds = parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                duration_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        except (TypeError, ValueError):
            duration_seconds = 0

        try:
            started = time.strptime(
                event[u"date"] + u" " + event[u"start"], u"%Y-%m-%d %H:%M:%S"
            )
            timestamp = int(time.mktime(started))
        except (KeyError, TypeError, ValueError):
            timestamp = None

        results[station_index] = {
            u"relative": relative_time_label(timestamp) if timestamp else _(u"unknown"),
            u"duration": duration_label(duration_seconds) if duration_seconds else _(u"unknown"),
        }

    return results


def visible_stations():
    last_runs = station_last_runs()
    stations = []
    for bid in range(gv.sd[u"nbrd"]):
        for s in range(8):
            sid = bid * 8 + s
            if sid >= gv.sd[u"nst"]:
                continue
            if sid + 1 == gv.sd[u"mas"]:
                continue
            show = (gv.sd[u"show"][bid] >> s) & 1
            if not show:
                continue
            stations.append(
                {
                    u"index": sid,
                    u"number": sid + 1,
                    u"name": gv.snames[sid],
                    u"board": bid + 1,
                    u"bit": s,
                    u"last_run": last_runs.get(
                        sid,
                        {u"relative": _(u"never"), u"duration": u""},
                    ),
                }
            )
    return stations


def current_mode_label():
    if gv.sd[u"mm"]:
        return _(u"Manual")
    if gv.sd[u"seq"]:
        return _(u"Sequential")
    return _(u"Concurrent")


def active_station_indexes():
    active = []
    for sid, value in enumerate(gv.srvals):
        if not value:
            continue
        if sid + 1 == gv.sd[u"mas"]:
            continue
        active.append(sid)
    return active


def status_payload():
    active = active_station_indexes()
    return {
        u"ok": True,
        u"mode": current_mode_label(),
        u"enabled": bool(gv.sd[u"en"]),
        u"busy": bool(gv.sd[u"bsy"]),
        u"active": active,
        u"count": len(active),
    }


class touch_ui_page(ProtectedPage):
    """Mobile-friendly station runner page."""

    def GET(self):
        return template_render.sip_touch_ui(visible_stations(), DURATION_OPTIONS, status_payload())


class touch_ui_run(ProtectedPage):
    """Start a single station for a fixed duration using SIP's native run-once flow."""

    def POST(self):
        web.header(u"Content-Type", u"application/json")
        qdict = web.input(station=None, seconds=None)

        if not gv.sd[u"en"]:
            return json.dumps({u"ok": False, u"message": _(u"SIP is disabled.")})

        try:
            station_index = int(qdict[u"station"])
            seconds = int(qdict[u"seconds"])
        except (TypeError, ValueError):
            return json.dumps({u"ok": False, u"message": _(u"Invalid request payload.")})

        if seconds not in ALLOWED_SECONDS:
            return json.dumps({u"ok": False, u"message": _(u"Unsupported duration.")})

        stations = visible_stations()
        station_map = {station[u"index"]: station for station in stations}
        if station_index not in station_map:
            return json.dumps({u"ok": False, u"message": _(u"Station is not available.")})

        gv.rovals = [0] * gv.sd[u"nst"]
        gv.rovals[station_index] = seconds
        run_once()

        return json.dumps(
            {
                u"ok": True,
                u"message": _(u"Started {name} for {seconds} seconds.").format(
                    name=station_map[station_index][u"name"],
                    seconds=seconds,
                ),
                u"status": status_payload(),
            }
        )


class touch_ui_stop(ProtectedPage):
    """Stop all running stations."""

    def POST(self):
        web.header(u"Content-Type", u"application/json")
        stop_stations()
        return json.dumps(
            {
                u"ok": True,
                u"message": _(u"Stopped all running stations."),
                u"status": status_payload(),
            }
        )


class touch_ui_status(ProtectedPage):
    """Return current touch UI status as JSON."""

    def GET(self):
        web.header(u"Content-Type", u"application/json")
        return json.dumps(status_payload())
