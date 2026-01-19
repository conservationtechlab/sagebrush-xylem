from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, List, Tuple

from config.device_loader import load_device_config

from nicegui import ui, app

app.add_static_files('/assets', 'assets')

cfg = load_device_config("config/devices.yaml")


def flatten_items(cfg_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten cfg into a list of items with category/subgroup attached."""
    flat: List[Dict[str, Any]] = []
    for category_key in ("networking", "sensors"):
        groups = cfg_dict.get(category_key, {}) or {}
        for subgroup, items in groups.items():
            for item in (items or []):
                flat.append({
                    "category": category_key,
                    "subgroup": str(subgroup),
                    "id": str(item.get("id", "")),
                    "name": str(item.get("name", item.get("id", ""))),
                    "lat": item.get("lat", None),
                    "lon": item.get("lon", None),
                    "icon": item.get("icon", None),  # e.g. assets/icons/zoo.jpg
                    "enabled": bool(item.get("enabled", True)),
                })
    return flat


ITEMS = flatten_items(cfg)


def make_time_range():
    end = datetime.now()
    start = end - timedelta(days=1)
    times = []
    t = start
    while t <= end:
        times.append(t)
        t += timedelta(minutes=30)
    return times


def fmt(dt: datetime) -> str:
    return dt.strftime('%d %B %Y, %I:%M %p')


@ui.page('/')
async def main_page():
    ui.query('body').classes('bg-slate-900 m-0')
    ui.add_head_html("""
    <style>
    /* Hide Leaflet default zoom (+ / -) buttons */
    .leaflet-control-zoom {
    display: none !important;
    }
    </style>
    """)


    coords = [
        (i["lat"], i["lon"])
        for i in ITEMS
        if i.get("lat") is not None and i.get("lon") is not None
    ]
    if coords:
        center_lat = mean(float(a) for a, _ in coords)
        center_lon = mean(float(b) for _, b in coords)
    else:
        center_lat, center_lon = 33.095, -116.995

    times = make_time_range()
    idx = {'value': len(times) - 1}

    layer_state: Dict[str, bool] = {}   # key -> enabled
    markers: Dict[str, Any] = {}        # device_id -> leaflet marker
    map_ready = {"value": False}

    item_lookup: Dict[Tuple[str, str, str], Dict[str, Any]] = {
        (i["category"], i["subgroup"], i["id"]): i for i in ITEMS
    }

    with ui.element('div').classes('relative w-full h-screen'):
        m = ui.leaflet(center=(center_lat, center_lon), zoom=13).classes('w-full h-full')
        m.tile_layer(
            url_template='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            options={'maxZoom': 17},
        )


        def popup_html_for(item: Dict[str, Any]) -> str:
            return (
                "<div style=\"font-size:13px;line-height:1.4;\">"
                f"<b>{item.get('name','')}</b><br>"
                f"Category: {item.get('category','')}<br>"
                f"Group: {item.get('subgroup','')}<br>"
                f"ID: {item.get('id','')}"
                "</div>"
            )

        # ---------- Task 5: custom icon (DivIcon) applied via setIcon ----------
        def show_marker(item: Dict[str, Any]) -> None:
            dev_id = item["id"]
            if dev_id in markers:
                return

            if item.get("lat") is None or item.get("lon") is None:
                ui.notify(f"No location for '{item.get('name', dev_id)}' yet", type='warning')
                return

            # Create marker first
            mk = m.marker(
                latlng=(float(item["lat"]), float(item["lon"])),
                options={'title': item.get("name", dev_id)},
            )
            markers[dev_id] = mk

            # Then force icon (most compatible across NiceGUI Leaflet versions)
            if item.get("icon"):
                # YAML uses: assets/icons/zoo.jpg -> URL: /assets/icons/zoo.jpg
                icon_url = "/" + str(item["icon"]).lstrip("/")

                # Plain string (no backticks/template literals)
                html = (
                    "<div style='width:34px;height:34px;"
                    "border-radius:8px;overflow:hidden;"
                    "border:2px solid rgba(255,255,255,0.9);"
                    "box-shadow:0 6px 14px rgba(0,0,0,0.35);"
                    "background:rgba(0,0,0,0.15);'>"
                    f"<img src=\"{icon_url}\" style='width:100%;height:100%;object-fit:cover;'/>"
                    "</div>"
                )

                # Use Python repr to guarantee valid JS string quoting
                js_icon = (
                    ":L.divIcon({"
                    "className: '',"
                    f"html: {html!r},"
                    "iconSize: [34,34],"
                    "iconAnchor: [17,34],"
                    "popupAnchor: [0,-34]"
                    "})"
                )

                m.run_layer_method(mk.id, "setIcon", js_icon)

            if map_ready["value"]:
                m.run_layer_method(mk.id, 'bindPopup', popup_html_for(item))

        def hide_marker(item: Dict[str, Any]) -> None:
            dev_id = item["id"]
            mk = markers.pop(dev_id, None)
            if mk:
                # Reliable removal
                m.run_map_method('removeLayer', mk.id)

        def apply_visibility(item: Dict[str, Any], visible: bool) -> None:
            if visible:
                show_marker(item)
            else:
                hide_marker(item)

        # ---- Layers panel (Task 3) ----
        panel_visible = {"value": True}

        def toggle_panel():
            panel_visible["value"] = not panel_visible["value"]
            layers_panel.set_visibility(panel_visible["value"])
            layers_btn.set_text("Layers" if panel_visible["value"] else "Show Layers")

        layers_btn = ui.button("Layers", on_click=toggle_panel).props("dense").classes(
            "fixed left-4 top-4 z-[9999]"
        )

        layers_panel = ui.card().classes(
            "fixed left-4 top-16 z-[9999] w-80 max-h-[80vh] overflow-auto shadow-lg "
            "bg-slate-900/90 border border-slate-700"
        )

        def render_category(title: str, category_key: str, category_data: Dict[str, Any]) -> None:
            with ui.expansion(title, value=True).classes("w-full text-white"):
                if not category_data:
                    ui.label("No items").classes("text-sm text-slate-300")
                    return

                for subgroup, subgroup_items in (category_data or {}).items():
                    with ui.expansion(str(subgroup), value=True).classes("w-full text-white"):
                        if not subgroup_items:
                            ui.label("No items").classes("text-sm text-slate-300")
                            continue

                        for it in subgroup_items:
                            dev_id = str(it.get("id", ""))
                            name = str(it.get("name", dev_id))
                            enabled = bool(it.get("enabled", True))

                            key = f"{category_key}/{subgroup}/{dev_id}"
                            layer_state[key] = enabled

                            full_item = item_lookup.get((category_key, str(subgroup), dev_id))

                            def on_toggle(e, k=key, item=full_item):
                                layer_state[k] = bool(e.value)
                                if item:
                                    apply_visibility(item, layer_state[k])

                            with ui.row().classes("items-center justify-between w-full"):
                                ui.label(name).classes("text-sm text-slate-100")
                                ui.switch(value=enabled).props("dense").on_value_change(on_toggle)

        with layers_panel:
            ui.label("Layers").classes("text-lg font-semibold text-white")
            render_category("Networking", "networking", cfg.get("networking", {}))
            render_category("Sensors", "sensors", cfg.get("sensors", {}))

        # ---- Title chip ----
        ui.html(
            """
            <div style="
                position:absolute;
                top:14px; left:120px;
                background:#0b2d5f;
                color:white;
                padding:10px 14px;
                border-radius:14px;
                font-weight:600;
                font-size:14px;
                box-shadow:0 8px 18px rgba(0,0,0,.25);
                display:flex;
                gap:10px;
                align-items:center;
                z-index:9999;
            ">
                <div style="
                    width:26px;height:26px;border-radius:999px;
                    background:white;
                    display:flex;align-items:center;justify-content:center;
                    color:#0b2d5f;font-weight:800;
                ">S</div>
                <div>SageBRUSH Dash</div>
            </div>
            """,
            sanitize=False,
        )

        # ---- Left controls ----
        with ui.column().classes('absolute right-4 top-20 z-[9999] gap-2'):
            def zoom_in():
                m.run_map_method('zoomIn')

            def zoom_out():
                m.run_map_method('zoomOut')

            def home():
                m.run_map_method('setView', [center_lat, center_lon], 13)

            btn_cls = 'w-10 h-10 bg-slate-800/90 border border-slate-700 text-white rounded-lg shadow'
            ui.button('+', on_click=zoom_in).classes(btn_cls)
            ui.button('−', on_click=zoom_out).classes(btn_cls)
            ui.button('⌂', on_click=home).classes(btn_cls)

        # ---- Top-right mini map placeholder ----
        ui.html(
            """
            <div style="
                position:absolute;
                top:14px; right:160px;
                width:170px; height:120px;
                background: rgba(255,255,255,.08);
                border:1px solid rgba(255,255,255,.15);
                border-radius:10px;
                overflow:hidden;
                box-shadow:0 8px 18px rgba(0,0,0,.25);
                z-index:9999;
            ">
                <div style="
                    height:100%;
                    background: linear-gradient(135deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
                    display:flex;align-items:center;justify-content:center;
                    color:rgba(255,255,255,.65);
                    font-size:12px;
                ">
                    Mini Map (placeholder)
                </div>
            </div>
            """,
            sanitize=False,
        )

        # ---- Bottom slider ----
        with ui.element('div').classes('fixed bottom-0 left-0 right-0 z-[9999] px-4 pb-4'):
            with ui.card().classes('w-full bg-slate-900/75 border border-slate-700 backdrop-blur p-3'):
                time_label = ui.label(fmt(times[idx['value']])).classes('text-xs text-slate-200')

                def on_time_change(value):
                    idx['value'] = int(value)
                    time_label.text = fmt(times[idx['value']])

                ui.slider(
                    min=0,
                    max=len(times) - 1,
                    value=idx['value'],
                    step=1,
                    on_change=on_time_change,
                ).classes('w-full')

    await m.initialized()
    map_ready["value"] = True

    # Render all enabled markers at startup
    for item in ITEMS:
        if item.get("enabled", True):
            apply_visibility(item, True)


ui.run(title='SageBrush Dash (Map UI Overlay)')
