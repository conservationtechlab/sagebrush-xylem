from __future__ import annotations

from typing import Dict, Any, List
from statistics import mean

from nicegui import ui
from config.device_loader import load_device_config

from src.mapping.map_view import create_map, popup_html, set_custom_icon
from src.scripts.data_arch import flatten_items, make_time_range, fmt


# ----------------------------
# Icon mapping (edit paths as needed)
# ----------------------------
ICON_URLS = {
    # Networking
    'lora gateways': '/static/icons/lora_gateway.png',
    'nanobeams': '/static/icons/nanobeam.png',

    # Sensors
    'sagecam': '/static/icons/sagecam.png',
    'sagemic': '/static/icons/sagemic.png',
    'scrubcam': '/static/icons/scrubcam.png',
    'scrubmic': '/static/icons/scrubmic.png',
    'camera trap': '/static/icons/camera_trap.png',

    # Fallbacks
    'networking': '/static/icons/networking.png',
    'sensors': '/static/icons/sensor.png',
    'default': '/static/icons/default.png',
}


def _norm(s: str | None) -> str:
    return (s or '').strip().lower()


def infer_subtype(item: Dict[str, Any]) -> str:
    text = ' '.join(
        _norm(str(item.get(k)))
        for k in ('type', 'subtype', 'device_type', 'name', 'id')
        if item.get(k)
    )

    if 'lora' in text:
        return 'LoRa gateways'
    if 'nanobeam' in text:
        return 'Nanobeams'
    if 'sagecam' in text:
        return 'SageCam'
    if 'sagemic' in text:
        return 'SageMic'
    if 'scrubcam' in text:
        return 'ScrubCam'
    if 'scrubmic' in text:
        return 'ScrubMic'
    if 'camera' in text or 'trap' in text:
        return 'Camera Trap'

    return 'Other'


def infer_category(subtype: str) -> str:
    s = _norm(subtype)
    if s in {'lora gateways', 'nanobeams'}:
        return 'Networking'
    if s in {'sagecam', 'sagemic', 'scrubcam', 'scrubmic', 'camera trap'}:
        return 'Sensors'
    return 'Other'


def icon_for(subtype: str, category: str) -> str:
    return (
        ICON_URLS.get(_norm(subtype))
        or ICON_URLS.get(_norm(category))
        or ICON_URLS['default']
    )


@ui.page('/')
async def main_page():
    # ----------------------------
    # Load + prepare data
    # ----------------------------
    cfg = load_device_config('config/devices.yaml')
    raw_items = flatten_items(cfg)

    items: List[Dict[str, Any]] = []
    for it in raw_items:
        st = infer_subtype(it)
        cat = infer_category(st)
        it2 = dict(it)
        it2['__subtype'] = st
        it2['__category'] = cat
        items.append(it2)

    coords = [(i['lat'], i['lon']) for i in items if i.get('lat') and i.get('lon')]
    center_lat, center_lon = (
        (mean(a for a, _ in coords), mean(b for _, b in coords))
        if coords else (33.095, -116.995)
    )

    # ----------------------------
    # Page styling
    # ----------------------------
    ui.query('body').classes('bg-slate-900 m-0')

    times = make_time_range()
    idx = {'value': len(times) - 1}

    markers: Dict[str, Any] = {}
    map_ready = {'value': False}

    # Group items for layer panel
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    subtype_enabled: Dict[str, bool] = {}

    for it in items:
        grouped.setdefault(it['__category'], {}).setdefault(it['__subtype'], []).append(it)
        subtype_enabled.setdefault(it['__subtype'], True)

    # ----------------------------
    # Map container
    # ----------------------------
    with ui.element('div').classes('relative w-full h-screen'):
        m = create_map(center_lat, center_lon)

        # ----------------------------
        # Marker helpers
        # ----------------------------
        def add_marker(it):
            if it['id'] in markers or not it.get('lat') or not it.get('lon'):
                return
            mk = m.marker(
                latlng=(float(it['lat']), float(it['lon'])),
                options={'title': it.get('name', it['id'])},
            )
            set_custom_icon(m, mk, icon_for(it['__subtype'], it['__category']))
            markers[it['id']] = mk
            if map_ready['value']:
                m.run_layer_method(mk.id, 'bindPopup', popup_html(it))

        def remove_marker(it):
            mk = markers.pop(it['id'], None)
            if mk:
                m.remove_layer(mk)

        def apply_subtype(st, visible):
            for cat in grouped.values():
                for it in cat.get(st, []):
                    add_marker(it) if visible else remove_marker(it)

        # ----------------------------
        # Layers panel state
        # ----------------------------
        layer_panel_open = {'value': False}

        def toggle_layers():
            layer_panel_open['value'] = not layer_panel_open['value']
            layers_panel.set_visibility(layer_panel_open['value'])
            layers_button.set_visibility(not layer_panel_open['value'])

        # ----------------------------
        # Layers button (icon + text)
        # ----------------------------
        layers_button = ui.button(
            'Layers',
            icon='layers',
            on_click=toggle_layers,
        ).classes(
            'fixed left-4 top-20 z-[9999] '
            'bg-white text-gray-800 rounded-lg shadow-lg px-3'
        )

        # ----------------------------
        # Layers panel (NOAA-style)
        # ----------------------------
        layers_panel = ui.card().classes(
            'fixed left-4 top-20 z-[9998] w-80 '
            'bg-white shadow-xl rounded-lg'
        )
        layers_panel.set_visibility(False)

        with layers_panel:
            with ui.row().classes('items-center justify-between mb-2'):
                ui.label('Layers').classes('text-lg font-semibold')
                ui.button(icon='close', on_click=toggle_layers).props('flat')

            for category, submap in grouped.items():
                with ui.expansion(category):
                    for st in sorted(submap.keys()):
                        chk = ui.checkbox(st, value=True)

                        def _toggle(e, st=st):
                            subtype_enabled[st] = bool(e.value)
                            apply_subtype(st, bool(e.value))

                        chk.on_value_change(_toggle)

        # ----------------------------
        # Bottom timeline + controls
        # ----------------------------
        with ui.element('div').classes(
            'fixed bottom-0 left-0 right-0 z-[9999] px-4 pb-4'
        ):
            with ui.card().classes(
                'w-full bg-slate-900/80 border border-slate-700 p-3'
            ):
                time_label = ui.label(fmt(times[idx['value']])).classes(
                    'text-xs text-slate-200 text-center'
                )

                with ui.row().classes('justify-center gap-4'):
                    def rewind():
                        idx['value'] = max(0, idx['value'] - 1)
                        slider.value = idx['value']
                        time_label.text = fmt(times[idx['value']])

                    ui.button(icon='fast_rewind', on_click=rewind).props('flat round')

                    playing = {'value': False}

                    async def play_loop():
                        while playing['value']:
                            if idx['value'] < len(times) - 1:
                                idx['value'] += 1
                                slider.value = idx['value']
                                time_label.text = fmt(times[idx['value']])
                            await ui.sleep(0.6)

                    def toggle_play():
                        playing['value'] = not playing['value']
                        play_btn.icon = 'pause' if playing['value'] else 'play_arrow'
                        if playing['value']:
                            ui.run_task(play_loop())

                    play_btn = ui.button(
                        icon='play_arrow',
                        on_click=toggle_play,
                    ).props('round')

                    def forward():
                        idx['value'] = min(len(times) - 1, idx['value'] + 1)
                        slider.value = idx['value']
                        time_label.text = fmt(times[idx['value']])

                    ui.button(icon='fast_forward', on_click=forward).props('flat round')

                def on_slider(v):
                    idx['value'] = int(v)
                    time_label.text = fmt(times[idx['value']])

                slider = ui.slider(
                    min=0,
                    max=len(times) - 1,
                    value=idx['value'],
                    step=1,
                    on_change=on_slider,
                ).classes('w-full')

    # ----------------------------
    # Finalize map
    # ----------------------------
    await m.initialized()
    map_ready['value'] = True

    for it in items:
        if subtype_enabled.get(it['__subtype'], True):
            add_marker(it)
