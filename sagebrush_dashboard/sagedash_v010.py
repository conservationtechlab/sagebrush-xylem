from datetime import datetime, timedelta
from statistics import mean

from nicegui import ui

SENSORS = [
    {'name': 'BDR North Tower', 'type': 'BirdNET-Pi', 'lat': 33.100, 'lon': -116.995,
     'temperature': 24.3, 'humidity': 51, 'last_seen': '2025-12-17 13:45'},
    {'name': 'BDR South Weather Station', 'type': 'Weather Sensor', 'lat': 33.090, 'lon': -117.005,
     'temperature': 27.1, 'humidity': 43, 'last_seen': '2025-12-17 13:50'},
    {'name': 'Camera Trap 07', 'type': 'Cell Camera Trap', 'lat': 33.095, 'lon': -116.990,
     'temperature': 22.8, 'humidity': 58, 'last_seen': '2025-12-17 13:40'},
]

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

    center_lat = mean(s['lat'] for s in SENSORS)
    center_lon = mean(s['lon'] for s in SENSORS)

    times = make_time_range()
    idx = {'value': len(times) - 1}

    with ui.element('div').classes('relative w-full h-screen'):
        m = ui.leaflet(center=(center_lat, center_lon), zoom=13).classes('w-full h-full')
        m.tile_layer(
            url_template='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            options={'maxZoom': 19},
        )

        marker_list = []
        for i, sensor in enumerate(SENSORS):
            mk = m.marker(
                latlng=(sensor['lat'], sensor['lon']),
                options={'title': sensor['name']},
            )
            marker_list.append((i, mk, sensor))

        # Top-left title chip
        ui.html(
            """
            <div style="
                position:absolute;
                top:14px; left:14px;
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

        # Left toolbar controls
        with ui.column().classes('absolute left-4 top-20 z-[9999] gap-2'):
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

        # Top-right minimap placeholder (visual)
        ui.html(
            """
            <div style="
                position:absolute;
                top:14px; right:14px;
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
                    background: linear-gradient(135deg, rgba(255,255,255,.08), rgba(255,255,255,.02));
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

        # Bottom time slider overlay
        with ui.element('div').classes('absolute bottom-5 left-1/2 -translate-x-1/2 z-[9999] w-[520px]'):
            with ui.card().classes('w-full bg-slate-900/75 border border-slate-700 backdrop-blur-md'):
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

    # Popups after map init
    await m.initialized()
    for i, mk, sensor in marker_list:
        popup_html = f"""
        <div style="font-size:13px;line-height:1.4;">
            <b>{sensor['name']}</b><br>
            Type: {sensor['type']}<br>
            Temperature: {sensor['temperature']}°C<br>
            Humidity: {sensor['humidity']}%<br>
            Last seen: {sensor['last_seen']}
        </div>
        """
        m.run_layer_method(mk.id, 'bindPopup', popup_html)

ui.run(title='SageBRUSH Dash (Map UI Overlay)')
