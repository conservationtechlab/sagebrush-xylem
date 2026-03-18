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
    device_id = item.get('device_id', 'N/A')
    device_name = item.get('device_name') or device_id
    category = item.get('category', 'N/A')
    recorded_at = item.get('recorded_at', 'N/A')
    temperature = item.get('temperature')
    humidity = item.get('humidity')
    bat_v = item.get('bat_v')
    lat = item.get('lat', 'N/A')
    lon = item.get('lon', 'N/A')

    temperature_text = f"{temperature} °C" if temperature is not None else "N/A"
    humidity_text = f"{humidity} %" if humidity is not None else "N/A"
    battery_text = f"{bat_v} V" if bat_v is not None else "N/A"

    return (
        "<div style='min-width:240px;font-size:13px;line-height:1.5;font-family:Arial,sans-serif;'>"
        f"<div style='font-size:15px;font-weight:600;margin-bottom:8px;'>{device_name}</div>"
        f"<div><b>Device ID:</b> {device_id}</div>"
        f"<div><b>Category:</b> {category}</div>"
        f"<div><b>Recorded At:</b> {recorded_at}</div>"
        f"<div><b>Temperature:</b> {temperature_text}</div>"
        f"<div><b>Humidity:</b> {humidity_text}</div>"
        f"<div><b>Battery:</b> {battery_text}</div>"
        f"<div><b>Latitude:</b> {lat}</div>"
        f"<div><b>Longitude:</b> {lon}</div>"
        "</div>"
    )


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
    """
    Add a boundary polygon to the NiceGUI Leaflet map using generic_layer.

    IMPORTANT:
    This NiceGUI version expects args like:
      [":L.polygon", latlngs, options]
    not a single JS expression string.
    """
    latlngs_js = [[lat, lon] for lat, lon in latlngs]

    options = {
        "color": "#FF00FF",      # bright magenta so you can't miss it
        "weight": 6,
        "fill": True,
        "fillOpacity": 0.18,
    }

    return map_obj.generic_layer(name=name, args=[":L.polygon", latlngs_js, options])
