from typing import Dict, Any, List
from statistics import mean

from nicegui import ui
from config.device_loader import load_device_config

from src.mapping.map_view import create_map, popup_html
from src.scripts.data_arch import flatten_items, make_time_range, fmt


@ui.page('/')
async def main_page():
    # ----------------------------
    # Load data
    # ----------------------------
    cfg = load_device_config('config/devices.yaml')
    items = flatten_items(cfg)

    coords = [(i['lat'], i['lon']) for i in items if i.get('lat') and i.get('lon')]
    center_lat, center_lon = (
        (mean(a for a, _ in coords), mean(b for _, b in coords))
        if coords else (33.095, -116.995)
    )

    # Page style
    ui.query('body').classes('bg-slate-900 m-0')

    times = make_time_range()
    idx = {'value': len(times) - 1}

    markers: Dict[str, Any] = {}
    map_ready = {'value': False}

    # ----------------------------
    # Group items by category
    # ----------------------------
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for it in items:
        cat = it.get('category', 'Other')
        grouped.setdefault(cat, []).append(it)

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
            markers[it['id']] = mk
            if map_ready['value']:
                m.run_layer_method(mk.id, 'bindPopup', popup_html(it))

        def remove_marker(it):
            mk = markers.pop(it['id'], None)
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
        # LAYERS BUTTON (TOP-RIGHT)
        # ----------------------------
        layers_button = ui.button(
            icon='layers',
            on_click=toggle_layers,
        ).props('flat').classes(
            'fixed right-4 top-4 z-[9999] '
            'bg-blue-400 text-white '
            'rounded-md shadow px-2 py-2 '
        ).tooltip('Open layer list')

        # ----------------------------
        # LAYERS PANEL (TOP-RIGHT)
        # ----------------------------
        layers_panel = ui.card().classes(
            'fixed right-4 top-4 z-[9998] w-80 '
            'bg-white shadow-xl rounded-lg p-3'
        )
        layers_panel.set_visibility(False)

        with layers_panel:
            with ui.row().classes('items-center justify-between mb-3'):
                ui.label('Layers').classes('text-lg font-semibold')
                ui.button('Close', on_click=toggle_layers).props('flat')

            for category, cat_items in grouped.items():
                with ui.expansion(category):
                    for it in cat_items:
                        chk = ui.checkbox(it.get('name', it['id']), value=True)

                        def _toggle(e, it=it):
                            add_marker(it) if e.value else remove_marker(it)

                        chk.on_value_change(_toggle)

        # ----------------------------
        # ALERTCalifornia-style bottom bar
        # ----------------------------
        playing = {'value': False}

        with ui.element('div').classes(
            'fixed bottom-0 left-0 right-0 z-[9999]'
        ):
            with ui.element('div').classes(
                'flex items-center gap-4 px-4 py-2 '
                'bg-slate-900/90 border-t border-slate-700 '
                'backdrop-blur'
            ):

                # ---- Playback controls ----
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

                # ---- Timeline ----
                time_label = ui.label(
                    fmt(times[idx['value']])
                ).classes('text-xs text-slate-200 w-48 text-center')

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

                # ---- Right dropdown ----

                ui.select(
                    options=['Live', 'Playback', 'Archive'],
                    value='Live',
                ).props(
                    'dark'
                ).classes(
                    'text-white font-semibold '
                    'bg-slate-900 '
                    'border border-slate-1000 '
                    'rounded-md '
                    'px-3 py-2 '
                    'text-sm '
                    'h-8'
                    'flex items-center'
                    'shadow-sm'
                )


    # ----------------------------
    # Finalize map (MUST stay inside async function)
    # ----------------------------
    await m.initialized()
    map_ready['value'] = True

    for it in items:
        add_marker(it)
