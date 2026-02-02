from typing import Dict, Any
from statistics import mean

from nicegui import ui
from config.device_loader import load_device_config

from src.mapping.map_view import create_map, popup_html, set_custom_icon
from src.scripts.data_arch import flatten_items, make_time_range, fmt


@ui.page('/')
async def main_page():
    # ----------------------------
    # Load data
    # ----------------------------
    cfg = load_device_config("config/devices.yaml")
    items = flatten_items(cfg)

    coords = [
        (i["lat"], i["lon"])
        for i in items
        if i.get("lat") is not None and i.get("lon") is not None
    ]

    if coords:
        center_lat = mean(a for a, _ in coords)
        center_lon = mean(b for _, b in coords)
    else:
        center_lat, center_lon = 33.095, -116.995

    # ----------------------------
    # UI setup
    # ----------------------------
    ui.query('body').classes('bg-slate-900 m-0')

    times = make_time_range()
    idx = {'value': len(times) - 1}

    markers: Dict[str, Any] = {}
    map_ready = {"value": False}

    with ui.element('div').classes('relative w-full h-screen'):
        m = create_map(center_lat, center_lon)

        def show_marker(item):
            if item["id"] in markers:
                return

            if item["lat"] is None or item["lon"] is None:
                return

            mk = m.marker(
                latlng=(float(item["lat"]), float(item["lon"])),
                options={'title': item["name"]},
            )
            markers[item["id"]] = mk

            if item.get("icon"):
                set_custom_icon(m, mk, item["icon"])

            if map_ready["value"]:
                m.run_layer_method(mk.id, 'bindPopup', popup_html(item))

        # ---- Bottom time slider (FIXED) ----
        with ui.element('div').classes(
            'fixed bottom-0 left-0 right-0 z-[9999] px-4 pb-4'
        ):
            with ui.card().classes(
                'w-full bg-slate-900/75 border border-slate-700 p-3'
            ):
                label = ui.label(
                    fmt(times[idx['value']])
                ).classes('text-xs text-slate-200')

                def on_change(v):
                    idx['value'] = int(v)
                    label.text = fmt(times[idx['value']])

                ui.slider(
                    min=0,
                    max=len(times) - 1,
                    value=idx['value'],
                    step=1,
                    on_change=on_change,
                ).classes('w-full')

    await m.initialized()
    map_ready["value"] = True

    for item in items:
        if item.get("enabled", True):
            show_marker(item)
