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
    return (
        "<div style='font-size:13px;line-height:1.4;'>"
        f"<b>{item.get('name')}</b><br>"
        f"Category: {item.get('category')}<br>"
        f"Group: {item.get('subgroup')}<br>"
        f"ID: {item.get('id')}"
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
