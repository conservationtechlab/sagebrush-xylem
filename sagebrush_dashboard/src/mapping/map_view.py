from typing import Any, Dict, List, Tuple
from nicegui import ui


def create_map(center_lat, center_lon):
    m = ui.leaflet(center=(center_lat, center_lon), zoom=15).classes('w-full h-full')
    m.tile_layer(
        url_template='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        options={'maxZoom': 17},
    )
    return m


def popup_html(item: Dict[str, Any]) -> str:
    def pretty_species_name(name: Any) -> str:
        if not name:
            return "--"
        return str(name).replace("_", " ")

    def format_confidence_percent(value: Any) -> str:
        if value is None:
            return "--"
        try:
            return f"{round(float(value) * 100)}%"
        except Exception:
            return "--"

    device_id = item.get('device_id', 'N/A')
    device_name = item.get('device_name') or device_id
    category = item.get('category', 'N/A')
    recorded_at = item.get('recorded_at', 'N/A')
    temperature = item.get('temperature')
    humidity = item.get('humidity')
    bat_v = item.get('bat_v')

    acoustic_recorded_at = item.get('acoustic_recorded_at')
    species = item.get('species')
    confidence = item.get('confidence')
    filepath = item.get('filepath')

    if category == "Temperature Sensors":
        temp_val = f"{round(temperature, 1)}°C" if temperature is not None else "--"
        hum_val = f"{round(humidity, 1)}%" if humidity is not None else "--"
        battery_val = f"{round(bat_v, 2)} V" if bat_v is not None else "--"

        return f"""
        <div style="
            min-width:260px;
            font-family: Inter, system-ui, -apple-system, sans-serif;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
            overflow: hidden;
            color: #0f172a;
        ">
            <div style="
                background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
                padding: 12px 14px;
                color: white;
            ">
                <div style="
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    opacity: 0.95;
                ">
                    Temperature Sensor
                </div>
                <div style="
                    font-size: 16px;
                    font-weight: 700;
                    margin-top: 2px;
                    line-height: 1.2;
                ">
                    {device_name}
                </div>
            </div>

            <div style="padding: 14px;">
                <div style="
                    display: flex;
                    gap: 10px;
                    margin-bottom: 12px;
                ">
                    <div style="
                        flex: 1;
                        background: #fff7ed;
                        border: 1px solid #fed7aa;
                        border-radius: 14px;
                        padding: 12px;
                        text-align: center;
                    ">
                        <div style="
                            font-size: 28px;
                            font-weight: 800;
                            color: #c2410c;
                            line-height: 1;
                        ">
                            {temp_val}
                        </div>
                        <div style="
                            margin-top: 6px;
                            font-size: 11px;
                            font-weight: 700;
                            letter-spacing: 0.08em;
                            color: #9a3412;
                        ">
                            TEMP
                        </div>
                    </div>

                    <div style="
                        flex: 1;
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 14px;
                        padding: 12px;
                        text-align: center;
                    ">
                        <div style="
                            font-size: 28px;
                            font-weight: 800;
                            color: #0f172a;
                            line-height: 1;
                        ">
                            {hum_val}
                        </div>
                        <div style="
                            margin-top: 6px;
                            font-size: 11px;
                            font-weight: 700;
                            letter-spacing: 0.08em;
                            color: #475569;
                        ">
                            HUMIDITY
                        </div>
                    </div>
                </div>

                <div style="
                    display: grid;
                    gap: 8px;
                    font-size: 12px;
                    color: #475569;
                ">
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                    ">
                        <span style="font-weight: 600;">Updated</span>
                        <span>{recorded_at}</span>
                    </div>

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                    ">
                        <span style="font-weight: 600;">Battery</span>
                        <span>{battery_val}</span>
                    </div>

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                        gap: 12px;
                    ">
                        <span style="font-weight: 600;">ID</span>
                        <span style="text-align: right; word-break: break-word;">{device_id}</span>
                    </div>
                </div>
            </div>
        </div>
        """

    if category == "SageMic":
        battery_val = f"{round(bat_v, 2)} V" if bat_v is not None else "--"
        confidence_val = format_confidence_percent(confidence)
        acoustic_time_val = acoustic_recorded_at or "--"
        species_val = pretty_species_name(species)

        filepath_block = ""
        if filepath:
            filepath_block = f"""
            <div style="
                display: flex;
                flex-direction: column;
                background: #f8fafc;
                border-radius: 10px;
                padding: 8px 10px;
                gap: 4px;
            ">
                <span style="font-weight: 600;">File</span>
                <span style="
                    display: block;
                    max-height: 40px;
                    overflow-y: auto;
                    font-size: 11px;
                    line-height: 1.3;
                    color: #334155;
                    word-break: break-all;
                ">
                    {filepath}
                </span>
            </div>
            """

        return f"""
        <div style="
            min-width:280px;
            font-family: Inter, system-ui, -apple-system, sans-serif;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
            overflow: hidden;
            color: #0f172a;
        ">
            <div style="
                background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%);
                padding: 12px 14px;
                color: white;
            ">
                <div style="
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    opacity: 0.95;
                ">
                    Acoustic Sensor
                </div>
                <div style="
                    font-size: 16px;
                    font-weight: 700;
                    margin-top: 2px;
                    line-height: 1.2;
                ">
                    {device_name}
                </div>
            </div>

            <div style="padding: 14px;">
                <div style="
                    display: flex;
                    gap: 10px;
                    margin-bottom: 12px;
                ">
                    <div style="
                        flex: 1;
                        background: #f0fdf4;
                        border: 1px solid #bbf7d0;
                        border-radius: 14px;
                        padding: 12px;
                        text-align: center;
                    ">
                        <div style="
                            font-size: 16px;
                            font-weight: 800;
                            color: #166534;
                            line-height: 1.15;
                            word-break: break-word;
                        ">
                            {species_val}
                        </div>
                        <div style="
                            margin-top: 6px;
                            font-size: 11px;
                            font-weight: 700;
                            letter-spacing: 0.08em;
                            color: #166534;
                        ">
                            SPECIES
                        </div>
                    </div>

                    <div style="
                        width: 110px;
                        background: #ecfeff;
                        border: 1px solid #a5f3fc;
                        border-radius: 14px;
                        padding: 12px;
                        text-align: center;
                    ">
                        <div style="
                            font-size: 24px;
                            font-weight: 800;
                            color: #155e75;
                            line-height: 1;
                        ">
                            {confidence_val}
                        </div>
                        <div style="
                            margin-top: 6px;
                            font-size: 11px;
                            font-weight: 700;
                            letter-spacing: 0.08em;
                            color: #155e75;
                        ">
                            CONFIDENCE
                        </div>
                    </div>
                </div>

                <div style="
                    display: grid;
                    gap: 8px;
                    font-size: 12px;
                    color: #475569;
                ">
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                    ">
                        <span style="font-weight: 600;">Sensor Updated</span>
                        <span>{recorded_at}</span>
                    </div>

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                    ">
                        <span style="font-weight: 600;">Acoustic Time</span>
                        <span>{acoustic_time_val}</span>
                    </div>

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                    ">
                        <span style="font-weight: 600;">Battery</span>
                        <span>{battery_val}</span>
                    </div>

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        background: #f8fafc;
                        border-radius: 10px;
                        padding: 8px 10px;
                        gap: 12px;
                    ">
                        <span style="font-weight: 600;">ID</span>
                        <span style="text-align: right; word-break: break-word;">{device_id}</span>
                    </div>

                    {filepath_block}
                </div>
            </div>
        </div>
        """

    battery_val = f"{round(bat_v, 2)} V" if bat_v is not None else "N/A"

    return f"""
    <div style="
        min-width:240px;
        font-family: Inter, system-ui, -apple-system, sans-serif;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
        overflow: hidden;
        color: #0f172a;
    ">
        <div style="
            background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
            padding: 12px 14px;
            color: white;
        ">
            <div style="
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                opacity: 0.95;
            ">
                Sensor
            </div>
            <div style="
                font-size: 16px;
                font-weight: 700;
                margin-top: 2px;
                line-height: 1.2;
            ">
                {device_name}
            </div>
        </div>

        <div style="padding: 14px; display:grid; gap:8px; font-size:12px; color:#475569;">
            <div style="display:flex; justify-content:space-between; background:#f8fafc; border-radius:10px; padding:8px 10px;">
                <span style="font-weight:600;">Category</span>
                <span>{category}</span>
            </div>
            <div style="display:flex; justify-content:space-between; background:#f8fafc; border-radius:10px; padding:8px 10px;">
                <span style="font-weight:600;">Updated</span>
                <span>{recorded_at}</span>
            </div>
            <div style="display:flex; justify-content:space-between; background:#f8fafc; border-radius:10px; padding:8px 10px;">
                <span style="font-weight:600;">Battery</span>
                <span>{battery_val}</span>
            </div>
            <div style="display:flex; justify-content:space-between; background:#f8fafc; border-radius:10px; padding:8px 10px; gap:12px;">
                <span style="font-weight:600;">ID</span>
                <span style="text-align:right; word-break:break-word;">{device_id}</span>
            </div>
        </div>
    </div>
    """


def set_custom_icon(map_obj, marker, icon_path: str):
    icon_url = "/" + icon_path.lstrip("/")
    html = (
        "<div style='width:34px;height:34px;"
        "border-radius:8px;overflow:hidden;"
        "border:2px solid rgba(255,255,255,0.9);"
        "box-shadow:0 6px 14px rgba(0,0,0,0.35);'>"
        f"<img src=\"{icon_url}\" style='width:100%;height:100%;object-fit:cover;'/>"
        "</div>"
    )

    js_icon = (
        ":L.divIcon({"
        "className: '',"
        f"html: {html!r},"
        "iconSize: [34,34],"
        "iconAnchor: [17,34],"
        "popupAnchor: [0,-34]"
        "})"
    )

    map_obj.run_layer_method(marker.id, "setIcon", js_icon)


def add_boundary_polygon(map_obj, name: str, latlngs: List[Tuple[float, float]]):
    latlngs_js = [[lat, lon] for lat, lon in latlngs]

    options = {
        "color": "#FF00FF",
        "weight": 6,
        "fill": True,
        "fillOpacity": 0.18,
    }

    return map_obj.generic_layer(name=name, args=[":L.polygon", latlngs_js, options])
