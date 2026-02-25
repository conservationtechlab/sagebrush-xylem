# main_page.py
"""
Main dashboard page — dynamic layer integration.

Prerequisites:
- NiceGUI installed (your project already uses it)
- src/database/fetch_device_coordinates.py provides:
    - get_devices()
    - categorize_devices(devices) -> (layers_dict, unclassified_list)

How it works:
- /layers.json endpoint returns categorized layers with device objects { device_id, lat, lon }.
- The UI uses Leaflet (loaded via CDN) and plain JS to fetch /layers.json,
  render markers, and toggle layers on/off.
"""
from src.database.fetch_device_coordinates import get_devices, categorize_devices
from nicegui import ui, app
from fastapi import Response
import json
from pathlib import Path
import time

devices = get_devices()
layers, unclassified = categorize_devices(devices)
print("Layer counts:", {k: len(v) for k, v in layers.items()})
if unclassified:
    print("Unclassified:", [d for d in sorted(unclassified)])

# Import your DB helper functions (make sure this file exists)
try:
    from src.database.fetch_device_coordinates import get_devices, categorize_devices
except Exception as e:
    # Helpful error if import fails
    raise RuntimeError(
        "Failed to import get_devices / categorize_devices from src.database.fetch_device_coordinates. "
        "Make sure that file exists and is correct. Original error: " + str(e)
    )

BASE_DIR = Path(__file__).parent


# ---------------------------
# Server endpoint returning JSON layers
# ---------------------------
@app.get('/layers.json')
def layers_endpoint():
    """
    Returns JSON:
    {
      "generated_at": 1234567890,
      "layers": {
        "Temperature Sensors": [ {device}, ... ],
        "scrubmic": [...],
        "SageMic": [...]
      },
      "unclassified": [ {device}, ...]
    }
    """
    devices = get_devices()
    layers, unclassified = categorize_devices(devices)

    # Convert to JSON-safe structure if anything odd
    payload = {
        "generated_at": int(time.time()),
        "layers": layers,
        "unclassified": unclassified
    }
    return payload


# ---------------------------
# Frontend page
# ---------------------------
def create_dashboard_page():
    ui.markdown("# Device Layers Dashboard")

    with ui.row():
        with ui.column().style("width: 300px; padding-right: 12px;"):
            ui.markdown("### Layers")
            # Container for checkboxes — we'll populate with JS after fetching /layers.json
            checkbox_container = ui.html('<div id="layer-checkboxes">Loading layers...</div>')

            ui.markdown("### Controls")
            ui.button("Refresh layers", on_click=lambda: ui.run_javascript("refreshLayers();"))
            ui.label("Tip: toggle categories to show/hide markers on the map.")

        with ui.column().style("flex:1;"):
            # Map container
            ui.html(
                """
                <div id="map" style="width: 100%; height: 70vh; border: 1px solid #ddd;"></div>

                <script>
                // Load Leaflet CSS + JS dynamically
                (function loadLeaflet() {
                    if (window.L) return initMap();
                    const css = document.createElement('link');
                    css.rel = 'stylesheet';
                    css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
                    document.head.appendChild(css);

                    const script = document.createElement('script');
                    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
                    script.onload = initMap;
                    document.head.appendChild(script);
                })();

                let map, markersByLayer = {};

                function initMap() {
                    if (map) return;
                    map = L.map('map').setView([33.1, -116.98], 12); // default view — adjust as needed
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '© OpenStreetMap'
                    }).addTo(map);

                    refreshLayers();
                }

                async function refreshLayers() {
                    try {
                        const res = await fetch('/layers.json');
                        const json = await res.json();
                        const layers = json.layers || {};
                        buildLayerCheckboxes(layers);
                        renderLayers(layers);
                    } catch (err) {
                        console.error('failed to fetch layers:', err);
                        document.getElementById('layer-checkboxes').innerText = 'Failed to load layers';
                    }
                }

                function clearAllMarkers() {
                    for (const key of Object.keys(markersByLayer)) {
                        for (const marker of markersByLayer[key]) {
                            map.removeLayer(marker);
                        }
                    }
                    markersByLayer = {};
                }

                function renderLayers(layers) {
                    clearAllMarkers();
                    for (const [layerName, devices] of Object.entries(layers)) {
                        markersByLayer[layerName] = [];
                        for (const d of devices) {
                            if (d.lat == null || d.lon == null) continue;
                            const marker = L.marker([d.lat, d.lon]).bindPopup(`<b>${d.device_id}</b><br>${layerName}`);
                            markersByLayer[layerName].push(marker);
                        }
                    }
                    // Show markers for checked layers only (checkbox UI will call toggleLayer)
                    // default: show all
                    document.querySelectorAll('.layer-checkbox').forEach(cb => {
                        if (cb.checked) toggleLayer(cb.dataset.layer, cb.checked);
                    });
                }

                function buildLayerCheckboxes(layers) {
                    const container = document.getElementById('layer-checkboxes');
                    container.innerHTML = ''; // reset

                    for (const layerName of Object.keys(layers)) {
                        const id = 'cb_' + layerName.replace(/\\s+/g, '_');
                        const wrapper = document.createElement('div');

                        const cb = document.createElement('input');
                        cb.type = 'checkbox';
                        cb.id = id;
                        cb.className = 'layer-checkbox';
                        cb.dataset.layer = layerName;
                        cb.checked = true; // default show
                        cb.onchange = (e) => toggleLayer(layerName, e.target.checked);

                        const label = document.createElement('label');
                        label.htmlFor = id;
                        label.style.marginLeft = '8px';
                        label.innerText = `${layerName} (${layers[layerName].length})`;

                        wrapper.appendChild(cb);
                        wrapper.appendChild(label);
                        container.appendChild(wrapper);
                    }
                }

                function toggleLayer(layerName, show) {
                    const arr = markersByLayer[layerName] || [];
                    for (const m of arr) {
                        if (show) {
                            m.addTo(map);
                        } else {
                            map.removeLayer(m);
                        }
                    }
                }
                </script>
                """,
                sanitize=False,
            )

    # small footer
    ui.markdown("---")
    ui.label("Layers are fetched dynamically from the database. Refresh after DB updates.")

# register the page on app start
create_dashboard_page()

# Start NiceGUI app if this file is run directly
if __name__ == "__main__":
    ui.run(title='Device Layers Dashboard', host='0.0.0.0', port=8081)
