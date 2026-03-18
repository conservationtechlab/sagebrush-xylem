from typing import Dict, Any, List
from statistics import mean

from nicegui import ui

from src.database.fetch_site_boundary import get_site_boundary_feature
from src.database.fetch_device_coordinates import get_devices, categorize_devices
from src.database.fetch_latest_sensor_data import get_latest_sensor_data
from src.mapping.map_view import create_map, popup_html
from src.scripts.data_arch import make_time_range, fmt


@ui.page('/')
async def main_page():

    # ----------------------------
    # Load devices from DB
    # ----------------------------
    devices = get_devices()
    latest_sensor_data = get_latest_sensor_data()
    categorized_layers = categorize_devices(devices)

    # Build a robust map: device_id -> category
    device_category_map: Dict[str, str] = {}
    for category, devs in categorized_layers.items():
        for d in devs:
            device_category_map[d['device_id']] = category

    # Flatten all devices for global marker handling
    items: List[Dict[str, Any]] = []
    for layer_devices in categorized_layers.values():
        items.extend(layer_devices)

    coords = [(i['lat'], i['lon']) for i in items if i.get('lat') and i.get('lon')]
    center_lat, center_lon = (
        (mean(a for a, _ in coords), mean(b for _, b in coords))
        if coords else (33.095, -116.995)
    )

    ui.query('body').classes('bg-slate-900 m-0')

    times = make_time_range()
    idx = {'value': len(times) - 1}

    markers: Dict[str, Any] = {}
    map_ready = {'value': False}

    grouped = categorized_layers

    def enrich_device_with_latest_data(device: Dict[str, Any]) -> Dict[str, Any]:
        enriched = dict(device)
        latest = latest_sensor_data.get(device['device_id'])

        if latest:
            enriched['device_name'] = latest.get('device_name')
            enriched['recorded_at'] = latest.get('recorded_at')
            enriched['humidity'] = latest.get('humidity')
            enriched['bat_v'] = latest.get('bat_v')
            enriched['temperature'] = latest.get('temperature')

            if latest.get('latitude') is not None:
                enriched['lat'] = latest.get('latitude')
            if latest.get('longitude') is not None:
                enriched['lon'] = latest.get('longitude')
        else:
            enriched['device_name'] = None
            enriched['recorded_at'] = None
            enriched['humidity'] = None
            enriched['bat_v'] = None
            enriched['temperature'] = None

        return enriched

    # ----------------------------
    # Boundary: fetch from DB
    # ----------------------------
    SITE_CODE = "SDZWA Safari Park"
    boundary_feature = get_site_boundary_feature(SITE_CODE)

    def extract_outer_ring_latlngs(feature: Dict[str, Any]) -> List[List[float]]:
        """Return outer ring as [[lat, lon], ...] for Leaflet."""
        if not feature:
            return []
        geom = feature.get("geometry") or {}
        gtype = geom.get("type")
        coords_ = geom.get("coordinates")
        if not coords_:
            return []

        if gtype == "Polygon":
            ring = coords_[0]
        elif gtype == "MultiPolygon":
            ring = coords_[0][0]
        else:
            print(f"[boundary] Unsupported geometry type: {gtype}")
            return []

        return [[lat, lon] for lon, lat in ring]  # GeoJSON [lon,lat] -> Leaflet [lat,lon]

    boundary_latlngs = extract_outer_ring_latlngs(boundary_feature)

    # ----------------------------
    # Colored marker icon helper (guaranteed)
    # ----------------------------
    def build_colored_div_icon(category: str) -> str:
        # Temperature Sensors -> orange, scrubmic -> green, SageMic -> yellow
        if category == "Temperature Sensors":
            color = "#F97316"  # orange
        elif category == "scrubmic":
            color = "#22C55E"  # green
        elif category == "SageMic":
            color = "#EAB308"  # yellow
        else:
            color = "#94A3B8"  # gray

        html = (
            "<div style='width:16px;height:16px;"
            f"background:{color};"
            "border:2px solid white;"
            "border-radius:50%;"
            "box-shadow:0 2px 8px rgba(0,0,0,0.35);"
            "transform: translate(-50%, -50%);'></div>"
        )

        return (
            ":L.divIcon({"
            "className: '',"
            f"html: {html!r},"
            "iconSize: [16,16],"
            "iconAnchor: [8,8]"
            "})"
        )

    # ----------------------------
    # Map container
    # ----------------------------
    with ui.element('div').classes('relative w-full h-screen'):

        m = create_map(center_lat, center_lon)

        # ----------------------------
        # Marker helpers
        # ----------------------------
        def add_marker(it):
            if it['device_id'] in markers or not it.get('lat') or not it.get('lon'):
                return

            category = device_category_map.get(it['device_id'], 'Other')
            popup_item = enrich_device_with_latest_data(it)
            popup_item['category'] = category

            mk = m.marker(
                latlng=(float(popup_item['lat']), float(popup_item['lon'])),
                options={'title': it['device_id']},
            )
            markers[it['device_id']] = mk

            html = popup_html(popup_item)
            m.run_layer_method(mk.id, 'bindPopup', html)

            print(f"[popup] bound popup for {it['device_id']}")

        def remove_marker(it):
            mk = markers.pop(it['device_id'], None)
            if mk:
                m.remove_layer(mk)

        # ----------------------------
        # Layers panel state
        # ----------------------------
        panel_open = {'value': False}

        def toggle_layers():
            panel_open['value'] = not panel_open['value']
            layers_panel.set_visibility(panel_open['value'])
            layers_button.set_visibility(not panel_open['value'])

        # ----------------------------
        # LAYERS BUTTON
        # ----------------------------
        layers_button = ui.button(
            icon='layers',
            on_click=toggle_layers,
        ).props('flat').classes(
            'fixed right-4 top-4 z-[9999] '
            'bg-blue-400 text-white '
            'rounded-md shadow px-2 py-2'
        ).tooltip('Open layer list')

        # ----------------------------
        # LAYERS PANEL
        # ----------------------------
        layers_panel = ui.card().classes(
            'fixed right-4 top-16 z-[9998] w-80 '
            'bg-white shadow-xl rounded-lg p-3 '
            'max-h-[80vh] overflow-y-auto'
        )
        layers_panel.set_visibility(False)

        with layers_panel:

            with ui.row().classes('items-center justify-between mb-3'):
                ui.label('Layers').classes('text-lg font-semibold')
                ui.button('Close', on_click=toggle_layers).props('flat')

            # ----------------------------
            # GROUP + CHILD TOGGLES
            # ----------------------------
            for category, cat_items in grouped.items():

                group_checkbox = ui.checkbox(category, value=True).classes('font-semibold')
                child_checkboxes: List[Any] = []

                def make_group_toggle(cat_items, child_checkboxes):
                    def on_group_toggle(e):
                        for it in cat_items:
                            if e.value:
                                add_marker(it)
                            else:
                                remove_marker(it)

                        for chk in child_checkboxes:
                            chk.value = e.value
                    return on_group_toggle

                group_checkbox.on_value_change(make_group_toggle(cat_items, child_checkboxes))

                with ui.column().classes('ml-6'):
                    for it in cat_items:
                        chk = ui.checkbox(it['device_id'], value=True)
                        child_checkboxes.append(chk)

                        def make_child_toggle(it):
                            def on_child_toggle(e):
                                if e.value:
                                    add_marker(it)
                                else:
                                    remove_marker(it)
                            return on_child_toggle

                        chk.on_value_change(make_child_toggle(it))

        # ----------------------------
        # Bottom bar
        # ----------------------------
        playing = {'value': False}

        with ui.element('div').classes('fixed bottom-0 left-0 right-0 z-[9999]'):
            with ui.element('div').classes(
                'flex items-center gap-4 px-4 py-2 '
                'bg-slate-900/90 border-t border-slate-700 '
                'backdrop-blur'
            ):

                def rewind():
                    idx['value'] = max(0, idx['value'] - 1)
                    timeline.value = idx['value']
                    time_label.text = fmt(times[idx['value']])

                def forward():
                    idx['value'] = min(len(times) - 1, idx['value'] + 1)
                    timeline.value = idx['value']
                    time_label.text = fmt(times[idx['value']])

                async def play_loop():
                    while playing['value']:
                        if idx['value'] < len(times) - 1:
                            idx['value'] += 1
                            timeline.value = idx['value']
                            time_label.text = fmt(times[idx['value']])
                        await ui.sleep(0.5)

                def toggle_play():
                    playing['value'] = not playing['value']
                    play_btn.text = '⏸' if playing['value'] else '▶'
                    if playing['value']:
                        ui.run_task(play_loop())

                ui.button('⏮', on_click=rewind).classes('text-white')
                play_btn = ui.button('▶', on_click=toggle_play).classes('text-white')
                ui.button('⏭', on_click=forward).classes('text-white')

                time_label = ui.label(fmt(times[idx['value']])).classes('text-xs text-slate-200 w-48 text-center')

                def on_timeline_change(v):
                    idx['value'] = int(v)
                    time_label.text = fmt(times[idx['value']])

                timeline = ui.slider(
                    min=0,
                    max=len(times) - 1,
                    value=idx['value'],
                    step=1,
                    on_change=on_timeline_change,
                ).classes('flex-1')

                ui.select(
                    options=['Live', 'Playback', 'Archive'],
                    value='Live',
                ).props('dark').classes(
                    'text-white font-semibold '
                    'bg-slate-900 rounded-md px-3 py-2 text-sm h-8 '
                    'flex items-center shadow-sm'
                )

    # ----------------------------
    # Finalize map
    # ----------------------------
    await m.initialized()
    map_ready['value'] = True

    # Add all markers initially
    for it in items:
        add_marker(it)

    # ----------------------------
    # Draw boundary using Leaflet JS (guaranteed)
    # ----------------------------
    if boundary_latlngs:
        js = f"""
        (function() {{
            const el = getElement('{m.id}');
            if (!el || !el.map) {{
                console.warn('Leaflet element or map not found', el);
                return;
            }}
            const map = el.map;

            const latlngs = {boundary_latlngs};
            const poly = L.polygon(latlngs, {{
                color: '#0000FF',
                weight: 3,
                fill: true,
                fillOpacity: 0.18
            }}).addTo(map);

            map.fitBounds(poly.getBounds());
        }})();
        """
        ui.run_javascript(js)
        print(f"[boundary] Sent boundary JS for {SITE_CODE} ({len(boundary_latlngs)} points)")
