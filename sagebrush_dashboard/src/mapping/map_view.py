from typing import Any, Dict, List, Tuple
from nicegui import ui


def create_map(center_lat, center_lon):
    """Create a Leaflet map using OpenStreetMap tiles (not topo)."""
    m = ui.leaflet(center=(center_lat, center_lon), zoom=15).classes('w-full h-full')
    # Use standard OSM tiles to match the target UI screenshot
    m.tile_layer(
        url_template='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        options={
            'maxZoom': 19,
            'attribution': '© OpenStreetMap contributors',
        },
    )
    return m


def get_marker_icon_js(category: str) -> str:
    """
    Return a :L.divIcon(...) string for use with m.run_layer_method(mk.id, 'setIcon', ...).
    Each category gets a teardrop-style pin with a sensor icon inside.
    """
    if category == "Temperature Sensors":
        bg_color = "#F97316"       # orange
        border_color = "#c2410c"
        icon_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="white" width="12" height="12">'
            '<path d="M12 2a5 5 0 00-5 5c0 3.5 5 11 5 11s5-7.5 5-11a5 5 0 00-5-5zm0 7a2 2 0 110-4 2 2 0 010 4z"/>'
            '</svg>'
        )
    elif category == "SageMic":
        bg_color = "#22C55E"       # green
        border_color = "#15803d"
        icon_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="white" width="12" height="12">'
            '<path d="M12 14a3 3 0 003-3V5a3 3 0 00-6 0v6a3 3 0 003 3zm-1 1.93V18H9v2h6v-2h-2v-2.07A7 7 0 0019 11h-2a5 5 0 01-10 0H5a7 7 0 006 6.93z"/>'
            '</svg>'
        )
    elif category == "scrubmic":
        bg_color = "#A855F7"       # purple
        border_color = "#7e22ce"
        icon_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="white" width="12" height="12">'
            '<path d="M12 14a3 3 0 003-3V5a3 3 0 00-6 0v6a3 3 0 003 3zm-1 1.93V18H9v2h6v-2h-2v-2.07A7 7 0 0019 11h-2a5 5 0 01-10 0H5a7 7 0 006 6.93z"/>'
            '</svg>'
        )
    else:
        bg_color = "#94A3B8"       # slate
        border_color = "#475569"
        icon_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="white" width="12" height="12">'
            '<circle cx="12" cy="12" r="5"/>'
            '</svg>'
        )

    # Teardrop pin shape: circle top with a point at bottom
    pin_html = (
        f"<div style='"
        f"width:28px;height:36px;position:relative;display:flex;"
        f"flex-direction:column;align-items:center;"
        f"'>"
        f"<div style='"
        f"width:28px;height:28px;"
        f"background:{bg_color};"
        f"border:2.5px solid {border_color};"
        f"border-radius:50% 50% 50% 0;"
        f"transform:rotate(-45deg);"
        f"box-shadow:0 3px 10px rgba(0,0,0,0.35);"
        f"display:flex;align-items:center;justify-content:center;"
        f"'>"
        f"<div style='transform:rotate(45deg);display:flex;align-items:center;justify-content:center;'>"
        f"{icon_svg}"
        f"</div>"
        f"</div>"
        f"</div>"
    )

    return (
        ":L.divIcon({"
        "className: '',"
        f"html: {pin_html!r},"
        "iconSize: [28, 36],"
        "iconAnchor: [14, 36],"
        "popupAnchor: [0, -38]"
        "})"
    )


def popup_html(item: Dict[str, Any]) -> str:
    """Generate styled HTML for a Leaflet marker popup."""

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

    # -------------------------------------------------------
    # Temperature Sensor popup — matches target screenshot
    # -------------------------------------------------------
    if category == "Temperature Sensors":
        temp_val = f"{round(temperature, 1)}°C" if temperature is not None else "--"
        hum_val = f"{round(humidity, 1)}%" if humidity is not None else "--"
        battery_val = f"{round(bat_v, 2)} V" if bat_v is not None else "--"

        return f"""
        <div style="
            min-width:240px;
            font-family: Inter, system-ui, -apple-system, sans-serif;
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 8px 24px rgba(15,23,42,0.18);
            overflow: hidden;
            color: #0f172a;
        ">
            <div style="
                background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
                padding: 10px 14px;
                color: white;
            ">
                <div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.9;">
                    Temperature Sensor
                </div>
                <div style="font-size:15px;font-weight:700;margin-top:2px;">{device_name}</div>
            </div>
            <div style="padding:12px;">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:10px;">
                    <div style="grid-column:span 2;background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:13px;margin-bottom:2px;">🌡️</div>
                        <div style="font-size:22px;font-weight:800;color:#c2410c;line-height:1;">{temp_val}</div>
                        <div style="font-size:10px;font-weight:700;color:#9a3412;margin-top:4px;letter-spacing:.06em;">TEMPERATURE</div>
                    </div>
                    <div style="grid-column:span 2;background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:13px;margin-bottom:2px;">💧</div>
                        <div style="font-size:22px;font-weight:800;color:#0369a1;line-height:1;">{hum_val}</div>
                        <div style="font-size:10px;font-weight:700;color:#075985;margin-top:4px;letter-spacing:.06em;">HUMIDITY</div>
                    </div>
                    <div style="grid-column:span 2;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:13px;margin-bottom:2px;">🔋</div>
                        <div style="font-size:18px;font-weight:700;color:#0f172a;line-height:1;">{battery_val}</div>
                        <div style="font-size:10px;font-weight:700;color:#475569;margin-top:4px;letter-spacing:.06em;">BATTERY</div>
                    </div>
                    <div style="grid-column:span 2;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:13px;margin-bottom:2px;">🕐</div>
                        <div style="font-size:11px;font-weight:600;color:#334155;line-height:1.3;">{recorded_at}</div>
                        <div style="font-size:10px;font-weight:700;color:#475569;margin-top:4px;letter-spacing:.06em;">LAST UPDATED</div>
                    </div>
                </div>
                <div style="background:#f8fafc;border-radius:8px;padding:6px 10px;font-size:11px;color:#64748b;display:flex;justify-content:space-between;">
                    <span style="font-weight:600;">ID</span>
                    <span style="word-break:break-all;text-align:right;max-width:160px;">{device_id}</span>
                </div>
            </div>
        </div>
        """

    # -------------------------------------------------------
    # Acoustic Sensor (SageMic / scrubmic) popup
    # -------------------------------------------------------
    if category in ("SageMic", "scrubmic"):
        battery_val = f"{round(bat_v, 2)} V" if bat_v is not None else "--"
        confidence_val = format_confidence_percent(confidence)
        acoustic_time_val = acoustic_recorded_at or "--"
        species_val = pretty_species_name(species)

        header_color = (
            "linear-gradient(135deg, #4ade80 0%, #16a34a 100%)"
            if category == "SageMic"
            else "linear-gradient(135deg, #c084fc 0%, #7e22ce 100%)"
        )
        label_text = "Acoustic Sensor (SageMic)" if category == "SageMic" else "Acoustic Sensor (ScrubMic)"

        filepath_block = ""
        if filepath:
            # Strip /mnt/sagebase prefix to build /audio/ URL served by NiceGUI
            clean_path = str(filepath).strip()
            for prefix in ['/mnt/sagebase/', '/mnt/sagebase']:
                if clean_path.startswith(prefix):
                    clean_path = clean_path[len(prefix):]
                    break
            clean_path = clean_path.lstrip('/')
            audio_url  = f"/audio/{clean_path}"
            filename   = clean_path.split('/')[-1]

            filepath_block = f"""
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:10px;margin-top:6px;">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                    <span style="font-size:14px;">🎵</span>
                    <span style="font-size:11px;font-weight:700;color:#166534;">Audio Recording</span>
                </div>
                <audio controls style="width:100%;height:36px;accent-color:#16a34a;" preload="none">
                    <source src="{audio_url}" type="audio/wav">
                    Your browser does not support audio.
                </audio>
                <div style="font-size:9px;color:#94a3b8;margin-top:4px;word-break:break-all;">{filename}</div>
            </div>
            """

        return f"""
        <div style="
            min-width:260px;
            font-family: Inter, system-ui, -apple-system, sans-serif;
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 8px 24px rgba(15,23,42,0.18);
            overflow: hidden;
            color: #0f172a;
        ">
            <div style="background:{header_color};padding:10px 14px;color:white;">
                <div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.9;">{label_text}</div>
                <div style="font-size:15px;font-weight:700;margin-top:2px;">{device_name}</div>
            </div>
            <div style="padding:12px;">
                <div style="display:flex;gap:8px;margin-bottom:10px;">
                    <div style="flex:1;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:15px;font-weight:800;color:#166534;line-height:1.2;word-break:break-word;">{species_val}</div>
                        <div style="font-size:10px;font-weight:700;color:#166534;margin-top:4px;letter-spacing:.06em;">SPECIES</div>
                    </div>
                    <div style="width:90px;background:#ecfeff;border:1px solid #a5f3fc;border-radius:10px;padding:10px;text-align:center;">
                        <div style="font-size:22px;font-weight:800;color:#155e75;line-height:1;">{confidence_val}</div>
                        <div style="font-size:10px;font-weight:700;color:#155e75;margin-top:4px;letter-spacing:.06em;">CONFIDENCE</div>
                    </div>
                </div>
                <div style="display:grid;gap:6px;font-size:11px;color:#475569;">
                    <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;">
                        <span style="font-weight:600;">🕐 Sensor Updated</span><span>{recorded_at}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;">
                        <span style="font-weight:600;">🎵 Acoustic Time</span><span>{acoustic_time_val}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;">
                        <span style="font-weight:600;">🔋 Battery</span><span>{battery_val}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;gap:10px;">
                        <span style="font-weight:600;">ID</span>
                        <span style="text-align:right;word-break:break-all;max-width:160px;">{device_id}</span>
                    </div>
                    {filepath_block}
                </div>
            </div>
        </div>
        """

    # -------------------------------------------------------
    # Generic fallback popup
    # -------------------------------------------------------
    battery_val = f"{round(bat_v, 2)} V" if bat_v is not None else "N/A"

    return f"""
    <div style="
        min-width:220px;
        font-family: Inter, system-ui, -apple-system, sans-serif;
        background: #ffffff;
        border-radius: 14px;
        box-shadow: 0 8px 24px rgba(15,23,42,0.18);
        overflow: hidden;
        color: #0f172a;
    ">
        <div style="background:linear-gradient(135deg,#94a3b8 0%,#64748b 100%);padding:10px 14px;color:white;">
            <div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.9;">Sensor</div>
            <div style="font-size:15px;font-weight:700;margin-top:2px;">{device_name}</div>
        </div>
        <div style="padding:12px;display:grid;gap:6px;font-size:11px;color:#475569;">
            <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;">
                <span style="font-weight:600;">Category</span><span>{category}</span>
            </div>
            <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;">
                <span style="font-weight:600;">🕐 Updated</span><span>{recorded_at}</span>
            </div>
            <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;">
                <span style="font-weight:600;">🔋 Battery</span><span>{battery_val}</span>
            </div>
            <div style="display:flex;justify-content:space-between;background:#f8fafc;border-radius:8px;padding:6px 10px;gap:10px;">
                <span style="font-weight:600;">ID</span>
                <span style="text-align:right;word-break:break-all;">{device_id}</span>
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
        "color": "#16a34a",
        "weight": 3,
        "fill": True,
        "fillOpacity": 0.08,
    }
    return map_obj.generic_layer(name=name, args=[":L.polygon", latlngs_js, options])
