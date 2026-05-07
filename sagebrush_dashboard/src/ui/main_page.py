import asyncio
from typing import Dict, Any, List
from statistics import mean
from collections import Counter
from datetime import datetime, timedelta

from nicegui import ui

from src.database.fetch_site_boundary import get_site_boundary_feature
from src.database.fetch_device_coordinates import get_devices, categorize_devices
from src.database.fetch_latest_sensor_data import get_latest_sensor_data
from src.database.fetch_sensor_snapshot import get_sensor_snapshot_at
from src.database.fetch_acoustic_snapshot import get_acoustic_snapshot_at
from src.mapping.map_view import create_map, popup_html
from src.scripts.data_arch import make_time_range, fmt


@ui.page('/')
async def main_page():

    # ── Data ────────────────────────────────────────────────────────────
    devices            = get_devices()
    latest_sensor_data = get_latest_sensor_data()
    categorized_layers = categorize_devices(devices)

    selected_sensor_data   = {'value': latest_sensor_data}
    selected_acoustic_data = {'value': {}}

    device_category_map: Dict[str, str] = {}
    for category, devs in categorized_layers.items():
        for d in devs:
            device_category_map[d['device_id']] = category

    items: List[Dict[str, Any]] = []
    for layer_devices in categorized_layers.values():
        items.extend(layer_devices)

    coords = [(i['lat'], i['lon']) for i in items
              if i.get('lat') is not None and i.get('lon') is not None]
    center_lat, center_lon = (
        (mean(a for a, _ in coords), mean(b for _, b in coords))
        if coords else (33.095, -116.995)
    )

    # ── Global state ────────────────────────────────────────────────────
    time_range_options = {
        'Last 24 hours': 24,
        'Last 7 days':   24 * 7,
        'Last 30 days':  24 * 30,
    }
    selected_time_range = {'value': 'Last 24 hours'}
    times   = make_time_range(hours=time_range_options[selected_time_range['value']])
    idx     = {'value': len(times) - 1}
    playing = {'value': False}
    markers: Dict[str, Any] = {}
    heatmap_layers = {
        'temperature': {'visible': False},
        'humidity':    {'visible': False},
    }

    # ── Boundary ────────────────────────────────────────────────────────
    SITE_CODE       = "SDZWA Safari Park"
    boundary_feature = get_site_boundary_feature(SITE_CODE)

    def extract_outer_ring_latlngs(feature):
        if not feature:
            return []
        geom   = feature.get("geometry") or {}
        gtype  = geom.get("type")
        coords_ = geom.get("coordinates")
        if not coords_:
            return []
        if gtype == "Polygon":
            ring = coords_[0]
        elif gtype == "MultiPolygon":
            ring = coords_[0][0]
        else:
            return []
        return [[lat, lon] for lon, lat in ring]

    boundary_latlngs = extract_outer_ring_latlngs(boundary_feature)

    # ── Pure helpers ────────────────────────────────────────────────────
    # BirdNET stores scientific names (e.g. "Corvus_corax").
    # Map scientific name (lowercase, spaces) -> common name for display.
    SCIENTIFIC_TO_COMMON = {
        "corvus corax":           "Common Raven",
        "corvus brachyrhynchos":  "American Crow",
        "haemorhous mexicanus":   "House Finch",
        "sayornis nigricans":     "Black Phoebe",
        "sayornis saya":          "Say's Phoebe",
        "melanerpes formicivorus":"Acorn Woodpecker",
        "aphelocoma californica": "California Scrub-Jay",
        "chamaea fasciata":       "Wrentit",
        "toxostoma redivivum":    "California Thrasher",
        "pipilo maculatus":       "Spotted Towhee",
        "pipilo crissalis":       "California Towhee",
        "zonotrichia leucophrys": "White-crowned Sparrow",
        "melospiza melodia":      "Song Sparrow",
        "spinus psaltria":        "Lesser Goldfinch",
        "cardellina pusilla":     "Wilson's Warbler",
        "setophaga coronata":     "Yellow-rumped Warbler",
        "vireo cassinii":         "Cassin's Vireo",
        "buteo jamaicensis":      "Red-tailed Hawk",
        "buteo lineatus":         "Red-shouldered Hawk",
        "accipiter cooperii":     "Cooper's Hawk",
        "falco peregrinus":       "Peregrine Falcon",
        "geococcyx californianus":"Greater Roadrunner",
        "calypte anna":           "Anna's Hummingbird",
        "selasphorus sasin":      "Allen's Hummingbird",
        "zenaida macroura":       "Mourning Dove",
        "columba livia":          "Rock Pigeon",
        "cathartes aura":         "Turkey Vulture",
        "ardea herodias":         "Great Blue Heron",
        "ardea alba":             "Great Egret",
        "egretta thula":          "Snowy Egret",
        "phalacrocorax auritus":  "Double-crested Cormorant",
        "pelecanus occidentalis": "Brown Pelican",
        "turdus migratorius":     "American Robin",
        "sialia mexicana":        "Western Bluebird",
        "myadestes townsendi":    "Townsend's Solitaire",
        "polioptila californica": "California Gnatcatcher",
        "baeolophus inornatus":   "Oak Titmouse",
        "psaltriparus minimus":   "Bushtit",
        "sitta carolinensis":     "White-breasted Nuthatch",
        "troglodytes pacificus":  "Pacific Wren",
        "thryomanes bewickii":    "Bewick's Wren",
        "cistothorus palustris":  "Marsh Wren",
        "icteria virens":         "Yellow-breasted Chat",
        "icterus cucullatus":     "Hooded Oriole",
        "icterus bullockii":      "Bullock's Oriole",
        "sturnella neglecta":     "Western Meadowlark",
        "agelaius phoeniceus":    "Red-winged Blackbird",
        "molothrus ater":         "Brown-headed Cowbird",
        "passer domesticus":      "House Sparrow",
        "sturnus vulgaris":       "European Starling",
        "mimus polyglottos":      "Northern Mockingbird",
    }

    def scientific_to_common(raw_name: str) -> str:
        """Convert BirdNET class_id (scientific name) to common name for display."""
        if not raw_name:
            return "--"
        key = raw_name.replace("_", " ").strip().lower()
        return SCIENTIFIC_TO_COMMON.get(key, raw_name.replace("_", " ").title())

    def pretty_species_name(name):
        """Return display name — converts scientific to common if known."""
        if not name:
            return "--"
        return scientific_to_common(name)

    def get_bird_image_url(raw_species: str) -> str:
        """
        Return a bird image URL for display.
        raw_species is the class_id from BirdNET (scientific name like Corvus_corax).
        Uses Cornell Lab's Macaulay Library via species-specific known asset IDs,
        falling back to a Wikipedia Commons thumbnail via the species name.
        """
        if not raw_species:
            return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Blackbird_2.jpg/400px-Blackbird_2.jpg"

        # Cornell Macaulay Library asset IDs for common San Diego species
        cornell_assets = {
            "corvus corax":           "203485001",
            "corvus brachyrhynchos":  "202984001",
            "haemorhous mexicanus":   "307954711",
            "sayornis nigricans":     "303880101",
            "melanerpes formicivorus":"304692671",
            "aphelocoma californica": "303542521",
            "calypte anna":           "312630701",
            "zenaida macroura":       "303517581",
            "buteo jamaicensis":      "303552231",
            "mimus polyglottos":      "303533021",
            "thryomanes bewickii":    "303528101",
            "toxostoma redivivum":    "303531571",
            "pipilo maculatus":       "303534741",
            "spinus psaltria":        "304689251",
            "icterus cucullatus":     "303556761",
            "turdus migratorius":     "303516661",
            "cathartes aura":         "303546311",
            "ardea herodias":         "303546861",
            "geococcyx californianus":"303563121",
        }
        key = raw_species.replace("_", " ").strip().lower()
        asset_id = cornell_assets.get(key)
        if asset_id:
            return f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset_id}/900"

        # Fallback: generic bird image
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Blackbird_2.jpg/400px-Blackbird_2.jpg"

    def enrich_device_with_sensor_data(device, sensor_data, acoustic_data):
        enriched     = dict(device)
        sensor_row   = sensor_data.get(device['device_id'])
        latest_row   = latest_sensor_data.get(device['device_id'])
        acoustic_row = acoustic_data.get(device['device_id'])
        base_row     = sensor_row or {}
        fallback     = latest_row or {}

        enriched['device_name'] = (base_row.get('device_name') or
                                   fallback.get('device_name') or
                                   device.get('device_id'))
        enriched['recorded_at'] = base_row.get('recorded_at') or fallback.get('recorded_at')
        for key in ('humidity', 'bat_v', 'temperature'):
            enriched[key] = (base_row.get(key) if base_row.get(key) is not None
                             else fallback.get(key))
        enriched['lat'] = (base_row.get('latitude') if base_row.get('latitude') is not None
                           else fallback.get('latitude') if fallback.get('latitude') is not None
                           else device.get('lat'))
        enriched['lon'] = (base_row.get('longitude') if base_row.get('longitude') is not None
                           else fallback.get('longitude') if fallback.get('longitude') is not None
                           else device.get('lon'))
        if acoustic_row:
            enriched['acoustic_recorded_at'] = acoustic_row.get('recorded_at')
            enriched['species']   = acoustic_row.get('species')
            enriched['confidence'] = acoustic_row.get('confidence')
            enriched['filepath']  = acoustic_row.get('filepath')
        else:
            enriched['acoustic_recorded_at'] = None
            enriched['species']   = None
            enriched['confidence'] = None
            enriched['filepath']  = None
        return enriched

    def load_sensor_snapshot(ts):
        try:
            snap = get_sensor_snapshot_at(ts)
            print(f"[sensor] {len(snap)} rows at {ts}")
            return snap
        except Exception as e:
            print(f"[sensor] failed: {e}")
            return latest_sensor_data

    def load_acoustic_snapshot(ts):
        try:
            snap = get_acoustic_snapshot_at(ts)
            print(f"[acoustic] {len(snap)} rows at {ts}")
            return snap
        except Exception as e:
            print(f"[acoustic] failed: {e}")
            return {}

    def build_birdnet_summary(acoustic_data):
        species_list, confidences, latest_time = [], [], None
        for row in acoustic_data.values():
            sp  = row.get('species')
            con = row.get('confidence')
            rat = row.get('recorded_at')
            if sp:  species_list.append(sp)
            if con is not None: confidences.append(con)
            if rat and (latest_time is None or rat > latest_time):
                latest_time = rat
        counts = Counter(species_list)
        return {
            'total_detections': len(species_list),
            'unique_species':   len(counts),
            'top_species':      [(pretty_species_name(s), c) for s, c in counts.most_common(3)],
            'avg_confidence':   round(sum(confidences)/len(confidences)*100) if confidences else None,
            'latest_time':      latest_time,
        }

    def normalize_heat_value(value, lo, hi):
        try:
            v = float(value)
        except Exception:
            return None
        if hi == lo:
            return 0.6
        return max(0.1, min(1.0, (v - lo) / (hi - lo)))

    # ── CSS ─────────────────────────────────────────────────────────────
    ui.query('body').classes('bg-slate-900 m-0')
    ui.add_head_html('''
    <script>
/*
 (c) 2014, Vladimir Agafonkin
 simpleheat, a tiny JavaScript library for drawing heatmaps with Canvas
 https://github.com/mourner/simpleheat
*/
!function(){"use strict";function t(i){return this instanceof t?(this._canvas=i="string"==typeof i?document.getElementById(i):i,this._ctx=i.getContext("2d"),this._width=i.width,this._height=i.height,this._max=1,void this.clear()):new t(i)}t.prototype={defaultRadius:25,defaultGradient:{.4:"blue",.6:"cyan",.7:"lime",.8:"yellow",1:"red"},data:function(t,i){return this._data=t,this},max:function(t){return this._max=t,this},add:function(t){return this._data.push(t),this},clear:function(){return this._data=[],this},radius:function(t,i){i=i||15;var a=this._circle=document.createElement("canvas"),s=a.getContext("2d"),e=this._r=t+i;return a.width=a.height=2*e,s.shadowOffsetX=s.shadowOffsetY=200,s.shadowBlur=i,s.shadowColor="black",s.beginPath(),s.arc(e-200,e-200,t,0,2*Math.PI,!0),s.closePath(),s.fill(),this},gradient:function(t){var i=document.createElement("canvas"),a=i.getContext("2d"),s=a.createLinearGradient(0,0,0,256);i.width=1,i.height=256;for(var e in t)s.addColorStop(e,t[e]);return a.fillStyle=s,a.fillRect(0,0,1,256),this._grad=a.getImageData(0,0,1,256).data,this},draw:function(t){this._circle||this.radius(this.defaultRadius),this._grad||this.gradient(this.defaultGradient);var i=this._ctx;i.clearRect(0,0,this._width,this._height);for(var a,s=0,e=this._data.length;e>s;s++)a=this._data[s],i.globalAlpha=Math.max(a[2]/this._max,t||.05),i.drawImage(this._circle,a[0]-this._r,a[1]-this._r);var n=i.getImageData(0,0,this._width,this._height);return this._colorize(n.data,this._grad),i.putImageData(n,0,0),this},_colorize:function(t,i){for(var a,s=3,e=t.length;e>s;s+=4)a=4*t[s],a&&(t[s-3]=i[a],t[s-2]=i[a+1],t[s-1]=i[a+2])}},window.simpleheat=t}(),/*
 (c) 2014, Vladimir Agafonkin
 Leaflet.heat, a tiny and fast heatmap plugin for Leaflet.
 https://github.com/Leaflet/Leaflet.heat
*/
L.HeatLayer=(L.Layer?L.Layer:L.Class).extend({initialize:function(t,i){this._latlngs=t,L.setOptions(this,i)},setLatLngs:function(t){return this._latlngs=t,this.redraw()},addLatLng:function(t){return this._latlngs.push(t),this.redraw()},setOptions:function(t){return L.setOptions(this,t),this._heat&&this._updateOptions(),this.redraw()},redraw:function(){return!this._heat||this._frame||this._map._animating||(this._frame=L.Util.requestAnimFrame(this._redraw,this)),this},onAdd:function(t){this._map=t,this._canvas||this._initCanvas(),t._panes.overlayPane.appendChild(this._canvas),t.on("moveend",this._reset,this),t.options.zoomAnimation&&L.Browser.any3d&&t.on("zoomanim",this._animateZoom,this),this._reset()},onRemove:function(t){t.getPanes().overlayPane.removeChild(this._canvas),t.off("moveend",this._reset,this),t.options.zoomAnimation&&t.off("zoomanim",this._animateZoom,this)},addTo:function(t){return t.addLayer(this),this},_initCanvas:function(){var t=this._canvas=L.DomUtil.create("canvas","leaflet-heatmap-layer leaflet-layer"),i=L.DomUtil.testProp(["transformOrigin","WebkitTransformOrigin","msTransformOrigin"]);t.style[i]="50% 50%";var a=this._map.getSize();t.width=a.x,t.height=a.y;var s=this._map.options.zoomAnimation&&L.Browser.any3d;L.DomUtil.addClass(t,"leaflet-zoom-"+(s?"animated":"hide")),this._heat=simpleheat(t),this._updateOptions()},_updateOptions:function(){this._heat.radius(this.options.radius||this._heat.defaultRadius,this.options.blur),this.options.gradient&&this._heat.gradient(this.options.gradient),this.options.max&&this._heat.max(this.options.max)},_reset:function(){var t=this._map.containerPointToLayerPoint([0,0]);L.DomUtil.setPosition(this._canvas,t);var i=this._map.getSize();this._heat._width!==i.x&&(this._canvas.width=this._heat._width=i.x),this._heat._height!==i.y&&(this._canvas.height=this._heat._height=i.y),this._redraw()},_redraw:function(){var t,i,a,s,e,n,h,o,r,d=[],_=this._heat._r,l=this._map.getSize(),m=new L.Bounds(L.point([-_,-_]),l.add([_,_])),c=void 0===this.options.max?1:this.options.max,u=void 0===this.options.maxZoom?this._map.getMaxZoom():this.options.maxZoom,f=1/Math.pow(2,Math.max(0,Math.min(u-this._map.getZoom(),12))),g=_/2,p=[],v=this._map._getMapPanePos(),w=v.x%g,y=v.y%g;for(t=0,i=this._latlngs.length;i>t;t++)if(a=this._map.latLngToContainerPoint(this._latlngs[t]),m.contains(a)){e=Math.floor((a.x-w)/g)+2,n=Math.floor((a.y-y)/g)+2;var x=void 0!==this._latlngs[t].alt?this._latlngs[t].alt:void 0!==this._latlngs[t][2]?+this._latlngs[t][2]:1;r=x*f,p[n]=p[n]||[],s=p[n][e],s?(s[0]=(s[0]*s[2]+a.x*r)/(s[2]+r),s[1]=(s[1]*s[2]+a.y*r)/(s[2]+r),s[2]+=r):p[n][e]=[a.x,a.y,r]}for(t=0,i=p.length;i>t;t++)if(p[t])for(h=0,o=p[t].length;o>h;h++)s=p[t][h],s&&d.push([Math.round(s[0]),Math.round(s[1]),Math.min(s[2],c)]);this._heat.data(d).draw(this.options.minOpacity),this._frame=null},_animateZoom:function(t){var i=this._map.getZoomScale(t.zoom),a=this._map._getCenterOffset(t.center)._multiplyBy(-i).subtract(this._map._getMapPanePos());L.DomUtil.setTransform?L.DomUtil.setTransform(this._canvas,a,i):this._canvas.style[L.DomUtil.TRANSFORM]=L.DomUtil.getTranslateString(a)+" scale("+i+")"}}),L.heatLayer=function(t,i){return new L.HeatLayer(t,i)};
    </script>
    <style>
    html, body { height: 100%; overflow: hidden; }
    .sidebar-scroll { overflow-y: auto; }
    .sidebar-scroll::-webkit-scrollbar { width: 4px; }
    .sidebar-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 2px; }
    .mode-select .q-field__control { background: transparent !important; min-height: 32px !important; height: 32px !important; padding: 0 8px !important; border: none !important; }
    .mode-select .q-field__native, .mode-select .q-field__input,
    .mode-select .q-icon, .mode-select .q-select__dropdown-icon { color: #fff !important; }
    .mode-select .q-field__native span { color: #fff !important; font-weight: 700 !important; }
    .mode-select .q-field__control-container { padding-top: 0 !important; }
    .mode-select-menu .q-item { color: #0f172a !important; }
    </style>
    ''')

    # ════════════════════════════════════════════════════════════════════
    # LAYOUT  —  top-bar + sidebar + map all in one pass
    # Widget refs that jump_to / refresh_* will need are declared here
    # so closures can capture them properly.
    # ════════════════════════════════════════════════════════════════════

    # ── Top bar ─────────────────────────────────────────────────────────
    with ui.element('div').style(
        'position:fixed;top:0;left:0;right:0;height:48px;z-index:9999;'
        'background:#0f172a;border-bottom:1px solid #334155;'
        'display:flex;align-items:center;padding:0 16px;gap:10px;'
    ):
        with ui.element('a').style(
            'display:flex;align-items:center;gap:8px;text-decoration:none;cursor:pointer;'
        ).props('href="/" '):
            ui.icon('eco').classes('text-green-400').style('font-size:22px')
            ui.label('SageBRUSH Dashboard').style('color:#fff;font-weight:700;font-size:15px;')
        ui.element('div').style('flex:1')
        ui.label('Wildlife & Sensor Monitoring').style('color:#94a3b8;font-size:13px;')

    # ── Page body (sidebar + map) ────────────────────────────────────────
    with ui.element('div').style(
        'position:fixed;top:48px;left:0;right:0;bottom:52px;display:flex;'
    ):

        # ── LEFT SIDEBAR ─────────────────────────────────────────────────
        with ui.element('div').style(
            'width:272px;flex-shrink:0;background:#0f172a;'
            'border-right:1px solid #1e293b;'
            'display:flex;flex-direction:column;overflow:hidden;z-index:100;'
        ):
            # scrollable content
            with ui.element('div').classes('sidebar-scroll').style(
                'flex:1;min-height:0;padding:10px 10px 4px 10px;'
                'display:flex;flex-direction:column;gap:10px;'
            ):

                # BirdNET Summary card
                with ui.element('div').style(
                    'background:#1e293b;border-radius:12px;padding:12px;'
                ):
                    with ui.element('div').style('display:flex;align-items:center;gap:8px;margin-bottom:6px;'):
                        ui.icon('spatial_audio_off').style('color:#4ade80;font-size:18px;')
                        ui.label('BirdNET Summary').style('color:#fff;font-weight:700;font-size:13px;')

                    summary_time = ui.label('--').style('color:#64748b;font-size:11px;margin-bottom:8px;display:block;')

                    with ui.element('div').style('display:grid;grid-template-columns:1fr 1fr;gap:8px;'):
                        with ui.element('div').style('background:#14532d44;border-radius:8px;padding:8px;text-align:center;'):
                            total_label = ui.label('0').style('color:#4ade80;font-size:20px;font-weight:800;display:block;')
                            ui.label('Detections').style('color:#94a3b8;font-size:11px;')
                        with ui.element('div').style('background:#0e7490aa;border-radius:8px;padding:8px;text-align:center;'):
                            unique_label = ui.label('0').style('color:#22d3ee;font-size:20px;font-weight:800;display:block;')
                            ui.label('Unique species').style('color:#94a3b8;font-size:11px;')

                    with ui.element('div').style('background:#78350f44;border-radius:8px;padding:8px;text-align:center;margin-top:8px;'):
                        avg_conf_label = ui.label('--').style('color:#fbbf24;font-size:20px;font-weight:800;display:block;')
                        ui.label('Avg confidence').style('color:#94a3b8;font-size:11px;')

                    ui.element('div').style('height:1px;background:#334155;margin:8px 0;')
                    ui.label('TOP SPECIES').style('color:#64748b;font-size:10px;font-weight:700;letter-spacing:.08em;')
                    top_species_column = ui.column().classes('w-full').style('gap:4px;margin-top:4px;')



                # Temperature legend
                with ui.element('div').style('background:#1e293b;border-radius:12px;padding:10px;'):
                    ui.label('Temperature (°C)').style('color:#cbd5e1;font-size:11px;font-weight:600;display:block;margin-bottom:4px;')
                    ui.element('div').style(
                        'width:100%;height:10px;border-radius:4px;'
                        'background:linear-gradient(to right,#2563EB,#22D3EE,#22C55E,#FACC15,#EF4444);'
                    )
                    with ui.element('div').style('display:flex;justify-content:space-between;margin-top:3px;'):
                        ui.label('0°C').style('color:#64748b;font-size:10px;')
                        ui.label('45°C').style('color:#64748b;font-size:10px;')

                # Humidity legend
                with ui.element('div').style('background:#1e293b;border-radius:12px;padding:10px;'):
                    ui.label('Humidity (%)').style('color:#cbd5e1;font-size:11px;font-weight:600;display:block;margin-bottom:4px;')
                    ui.element('div').style(
                        'width:100%;height:10px;border-radius:4px;'
                        'background:linear-gradient(to right,#FACC15,#22C55E,#22D3EE,#2563EB,#1e3a5f);'
                    )
                    with ui.element('div').style('display:flex;justify-content:space-between;margin-top:3px;'):
                        ui.label('0%').style('color:#64748b;font-size:10px;')
                        ui.label('100%').style('color:#64748b;font-size:10px;')

    # ── BOTTOM BAR (full width, fixed) ───────────────────────────────────
    # Defined here so widgets exist before jump_to / toggle_play reference them

        # ── MAP AREA ──────────────────────────────────────────────────────
        with ui.element('div').style('flex:1;position:relative;overflow:hidden;'):
            m = create_map(center_lat, center_lon)

            # Bird dialog
            bird_dialog = ui.dialog()
            with bird_dialog:
                with ui.card().classes('w-[420px] max-w-[90vw] p-4'):
                    bird_title = ui.label('').classes('text-xl font-bold text-slate-800')
                    bird_img   = ui.image('https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Blackbird_2.jpg/400px-Blackbird_2.jpg').classes('w-full h-64 object-cover rounded-lg mt-3')
                    bird_link  = ui.link('View on Wikipedia', '#', new_tab=True).classes('text-blue-600 text-sm mt-3')
                    ui.button('Close', on_click=bird_dialog.close).classes('mt-4')

            def open_bird_popup(species_name):
                if not species_name: return
                common_name = scientific_to_common(species_name)
                # Use scientific name for Wikipedia (most reliable page)
                sci_wiki    = species_name.replace(" ", "_").replace("_", "_")
                wiki_url    = f"https://en.wikipedia.org/wiki/{sci_wiki}"
                # Cornell Lab of Ornithology All About Birds — reliable image + info
                cornell_url = f"https://www.allaboutbirds.org/guide/{sci_wiki}"
                bird_title.text = common_name
                # Use Wikimedia thumbnail for the species scientific name page
                sci_clean = species_name.replace(" ", "_")
                bird_img.set_source(get_bird_image_url(species_name))
                bird_link.text  = f"View {common_name} on All About Birds"
                bird_link._props['href'] = cornell_url
                bird_dialog.open()

            # Layers panel
            panel_open   = {'value': True}
            layers_button = ui.button(icon='layers', on_click=lambda: toggle_layers()).props('flat').style(
                'position:absolute;right:12px;top:12px;z-index:9999;'
                'background:#fff;color:#334155;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,.2);'
            )
            layers_panel = ui.card().style(
                'position:absolute;right:12px;top:12px;z-index:9998;width:240px;'
                'background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.15);'
                'padding:12px;max-height:80vh;overflow-y:auto;'
            )

            with layers_panel:
                with ui.row().classes('items-center justify-between').style('margin-bottom:8px;'):
                    ui.label('Layers').style('font-weight:700;font-size:14px;color:#0f172a;')
                    ui.button('CLOSE', on_click=lambda: toggle_layers()).props('flat dense').style('color:#3b82f6;font-size:11px;')

                ui.element('div').style('height:1px;background:#e2e8f0;margin:10px 0;')
                ui.label('SENSORS').style('color:#94a3b8;font-size:10px;font-weight:700;letter-spacing:.08em;')

                for category, cat_items in categorized_layers.items():
                    if category == "Temperature Sensors":
                        icon_color, icon_name = "#F97316", "thermostat"
                    elif category == "SageMic":
                        icon_color, icon_name = "#22C55E", "mic"
                    else:
                        icon_color, icon_name = "#94A3B8", "sensors"

                    child_checkboxes: List[Any] = []

                    with ui.row().classes('items-center').style('gap:6px;margin-top:8px;'):
                        ui.icon(icon_name).style(f'color:{icon_color};font-size:16px;')
                        group_checkbox = ui.checkbox(category, value=True).style('font-weight:600;font-size:13px;')

                    def make_group_toggle(cat_items, child_checkboxes):
                        def fn(e):
                            for it in cat_items:
                                add_marker(it) if e.value else remove_marker(it)
                            for chk in child_checkboxes:
                                chk.value = e.value
                        return fn
                    group_checkbox.on_value_change(make_group_toggle(cat_items, child_checkboxes))

                    with ui.column().style('margin-left:20px;gap:0;'):
                        for it in cat_items:
                            chk = ui.checkbox(it['device_id'], value=True).style('font-size:11px;')
                            child_checkboxes.append(chk)
                            def make_child_toggle(it):
                                def fn(e):
                                    add_marker(it) if e.value else remove_marker(it)
                                return fn
                            chk.on_value_change(make_child_toggle(it))

                ui.element('div').style('height:1px;background:#e2e8f0;margin:10px 0;')
                ui.label('BOUNDARIES').style('color:#94a3b8;font-size:10px;font-weight:700;letter-spacing:.08em;')
                with ui.row().classes('items-center').style('gap:6px;margin-top:6px;'):
                    ui.icon('park').style('color:#16a34a;font-size:16px;')
                    boundary_checkbox = ui.checkbox('Park Boundary', value=True).style('font-weight:600;font-size:13px;color:#15803d;')

                def on_boundary_toggle(e):
                    action = 'addLayer' if e.value else 'removeLayer'
                    ui.run_javascript(f"""
                    (function(){{
                        const map = window._leafletMapRef;
                        if (map && window._boundaryLayer) map.{action}(window._boundaryLayer);
                    }})();
                    """)
                boundary_checkbox.on_value_change(on_boundary_toggle)

            def toggle_layers():
                panel_open['value'] = not panel_open['value']
                layers_panel.set_visibility(panel_open['value'])
                layers_button.set_visibility(not panel_open['value'])

            # Temperature legend card (bottom-right of map)
            with ui.element('div').style(
                'position:absolute;right:12px;bottom:12px;z-index:500;'
                'background:#fff;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.15);'
                'padding:10px 12px;width:180px;'
            ):
                ui.label('Temperature (°C)').style('font-size:11px;font-weight:700;color:#334155;display:block;margin-bottom:4px;')
                ui.element('div').style(
                    'width:100%;height:8px;border-radius:3px;'
                    'background:linear-gradient(to right,#2563EB,#22D3EE,#22C55E,#FACC15,#EF4444);'
                )
                with ui.element('div').style('display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-top:4px;'):
                    for lbl, col in [('< 15','#2563EB'),('15–20','#22D3EE'),
                                     ('20–25','#22C55E'),('25–30','#86EFAC'),
                                     ('30–35','#FACC15'),('35–40','#F97316'),('>40','#EF4444')]:
                        with ui.element('div').style('display:flex;align-items:center;gap:3px;'):
                            ui.element('div').style(f'width:9px;height:9px;border-radius:2px;background:{col};flex-shrink:0;')
                            ui.label(lbl).style('font-size:10px;color:#475569;')

            # ── Marker & heatmap functions ───────────────────────────────
            def add_marker(it):
                if it['device_id'] in markers or it.get('lat') is None or it.get('lon') is None:
                    return
                category   = device_category_map.get(it['device_id'], 'Other')
                popup_item = enrich_device_with_sensor_data(it, selected_sensor_data['value'],
                                                            selected_acoustic_data['value'])
                popup_item['category'] = category
                mk = m.marker(
                    latlng=(float(popup_item['lat']), float(popup_item['lon'])),
                    options={'title': it['device_id']},
                )
                markers[it['device_id']] = mk
                html = popup_html(popup_item)
                m.run_layer_method(mk.id, 'bindPopup', html)
                print(f"[marker] added {it['device_id']}")

            def remove_marker(it):
                mk = markers.pop(it['device_id'], None)
                if mk:
                    m.remove_layer(mk)

            def refresh_marker_popups():
                for it in items:
                    mk = markers.get(it['device_id'])
                    if not mk: continue
                    category   = device_category_map.get(it['device_id'], 'Other')
                    popup_item = enrich_device_with_sensor_data(it, selected_sensor_data['value'],
                                                                selected_acoustic_data['value'])
                    popup_item['category'] = category
                    html = popup_html(popup_item)
                    # bindPopup updates content for next open;
                    # setPopupContent updates it if the popup is currently visible
                    m.run_layer_method(mk.id, 'bindPopup', html)
                    m.run_layer_method(mk.id, 'setPopupContent', html)

            def remove_heatmap_layer(kind):
                ui.run_javascript(f"""
                (function(){{
                    const key = '{kind}HeatLayer';
                    const map = window._leafletMapRef;
                    if (map && window[key]) {{ map.removeLayer(window[key]); window[key]=null; }}
                }})();
                """)

            def refresh_heatmap_layer(kind):
                rows = []
                for device in items:
                    did = device.get('device_id')
                    row = (selected_sensor_data['value'].get(did) or
                           latest_sensor_data.get(did) or {})
                    lat   = row.get('latitude')   if row.get('latitude')   is not None else device.get('lat')
                    lon   = row.get('longitude')  if row.get('longitude')  is not None else device.get('lon')
                    value = row.get(kind)
                    if lat is None or lon is None or value is None: continue
                    rows.append({'lat': float(lat), 'lon': float(lon), 'value': float(value)})

                print(f"[heatmap] {kind}: {len(rows)} points")
                if not rows: return

                lo = min(r['value'] for r in rows)
                hi = max(r['value'] for r in rows)
                pts = [[r['lat'], r['lon'], normalize_heat_value(r['value'], lo, hi)] for r in rows]

                ui.run_javascript(f"""
                (function(){{
                    let map = window._leafletMapRef;
                    if (!map) {{
                        try {{ const el = getElement('{m.id}'); map = el && (el.map || el._map); if(map) window._leafletMapRef=map; }} catch(e){{}}
                    }}
                    if (!map) {{ console.warn('heatmap: no map'); return; }}
                    if (!L.heatLayer) {{ console.warn('heatmap: plugin missing'); return; }}
                    const key = '{kind}HeatLayer';
                    const pts = {pts};
                    if (!map.getPane('heatPane')) {{
                        map.createPane('heatPane');
                        map.getPane('heatPane').style.zIndex = 650;
                        map.getPane('heatPane').style.pointerEvents = 'none';
                    }}
                    if (window[key]) {{ map.removeLayer(window[key]); window[key]=null; }}
                    window[key] = L.heatLayer(pts, {{
                        pane:'heatPane', radius:120, blur:55,
                        maxZoom:18, minOpacity:0.6, max:1.0,
                        gradient:{{0:'#2563EB',0.25:'#22D3EE',0.5:'#22C55E',0.75:'#FACC15',1:'#EF4444'}}
                    }}).addTo(map);
                }})();
                """)



            # ── BirdNET summary refresh ──────────────────────────────────
            def refresh_birdnet_summary():
                s = build_birdnet_summary(selected_acoustic_data['value'])
                total_label.text    = str(s['total_detections'])
                unique_label.text   = str(s['unique_species'])
                avg_conf_label.text = f"{s['avg_confidence']}%" if s['avg_confidence'] is not None else '--'
                summary_time.text   = f"Latest: {s['latest_time'] or '--'}"
                top_species_column.clear()
                with top_species_column:
                    if s['top_species']:
                        for sp, cnt in s['top_species']:
                            with ui.element('div').style(
                                'display:flex;align-items:center;justify-content:space-between;'
                                'background:#1e293b;border-radius:6px;padding:4px 8px;'
                            ):
                                ui.button(sp, on_click=lambda s=sp: open_bird_popup(s)).props('flat dense').style(
                                    'color:#60a5fa;font-size:12px;text-transform:none;'
                                )
                                ui.label(str(cnt)).style('color:#94a3b8;font-size:12px;font-weight:600;')
                    else:
                        ui.label('No acoustic detections').style('color:#64748b;font-size:12px;')



    # ── FIXED BOTTOM BAR ─────────────────────────────────────────────────
    with ui.element('div').style(
        'position:fixed;bottom:0;left:0;right:0;z-index:9999;'
        'background:#0f172a;border-top:1px solid #334155;'
        'padding:8px 16px;display:flex;align-items:center;gap:10px;'
    ):
        # Play controls
        play_btn = ui.button(icon='play_arrow', on_click=lambda: toggle_play()).props('flat round dense').style(
            'background:#1d4ed8;color:#fff;width:36px;height:36px;flex-shrink:0;'
        )
        stop_btn = ui.button(icon='stop', on_click=lambda: stop_play()).props('flat round dense').style(
            'color:#94a3b8;flex-shrink:0;'
        )
        back_btn = ui.button(icon='skip_previous', on_click=lambda: jump_to(idx['value'] - 1)).props('flat round dense').style(
            'color:#94a3b8;flex-shrink:0;'
        )
        fwd_btn = ui.button(icon='skip_next', on_click=lambda: jump_to(idx['value'] + 1)).props('flat round dense').style(
            'color:#94a3b8;flex-shrink:0;'
        )

        def make_step(delta_h):
            def _fn():
                target  = times[idx['value']] + timedelta(hours=delta_h)
                closest = min(range(len(times)), key=lambda i: abs((times[i] - target).total_seconds()))
                jump_to(closest)
            return _fn

        for lbl, dh in [('-1H', -1), ('+1H', 1), ('-1D', -24)]:
            ui.button(lbl, on_click=make_step(dh)).props('flat dense').style(
                'color:#94a3b8;font-size:11px;padding:0 6px;min-height:32px;flex-shrink:0;'
            )

        # Current time label
        current_time_label = ui.label(fmt(times[idx['value']])).style(
            'color:#f97316;font-size:11px;font-weight:700;white-space:nowrap;flex-shrink:0;min-width:140px;text-align:center;'
        )

        # Slider — takes all remaining space
        timeline = ui.slider(
            min=0, max=len(times) - 1, value=idx['value'], step=1,
        ).style('flex:1;min-width:0;')

        # Start / end labels
        start_label = ui.label(fmt(times[0])).style('color:#475569;font-size:10px;white-space:nowrap;flex-shrink:0;')
        end_label   = ui.label(fmt(times[-1])).style('color:#475569;font-size:10px;white-space:nowrap;flex-shrink:0;')

        # Time range selector
        time_range_select = ui.select(
            options=list(time_range_options.keys()),
            value=selected_time_range['value'],
        ).props('borderless dense popup-content-class=mode-select-menu').classes('mode-select').style(
            'background:#1e293b;color:#fff;border-radius:6px;min-width:130px;flex-shrink:0;'
        )

    # ════════════════════════════════════════════════════════════════════
    # Playback / jump functions  (all widgets are now defined above)
    # ════════════════════════════════════════════════════════════════════
    def jump_to(new_index: int):
        idx['value'] = max(0, min(len(times) - 1, new_index))
        timeline.value = idx['value']
        current_time_label.text = fmt(times[idx['value']])

        selected_sensor_data['value']   = load_sensor_snapshot(times[idx['value']])
        selected_acoustic_data['value'] = load_acoustic_snapshot(times[idx['value']])

        refresh_marker_popups()
        refresh_birdnet_summary()

        if heatmap_layers['temperature']['visible']:
            refresh_heatmap_layer('temperature')
        if heatmap_layers['humidity']['visible']:
            refresh_heatmap_layer('humidity')

    def stop_play():
        playing['value'] = False
        play_btn.props('icon=play_arrow')

    async def play_loop():
        while playing['value'] and idx['value'] < len(times) - 1:
            jump_to(idx['value'] + 1)
            await asyncio.sleep(0.8)
        playing['value'] = False
        play_btn.props('icon=play_arrow')

    def toggle_play():
        playing['value'] = not playing['value']
        play_btn.props('icon=pause' if playing['value'] else 'icon=play_arrow')
        if playing['value']:
            asyncio.create_task(play_loop())

    # Debounce: wait 300ms after last slider move before querying DB
    _slider_task = {'task': None}

    async def _debounced_jump(new_idx: int):
        await asyncio.sleep(0.3)
        jump_to(new_idx)

    def on_slider_change(e):
        if _slider_task['task'] is not None:
            _slider_task['task'].cancel()
        _slider_task['task'] = asyncio.create_task(_debounced_jump(int(e.value)))

    timeline.on_value_change(on_slider_change)

    def on_time_range_change(e):
        selected_time_range['value'] = e.value
        new_times = make_time_range(hours=time_range_options[e.value])
        times.clear()
        times.extend(new_times)
        idx['value'] = len(times) - 1
        timeline.max   = len(times) - 1
        timeline.value = idx['value']
        start_label.text        = fmt(times[0])
        end_label.text          = fmt(times[-1])
        current_time_label.text = fmt(times[idx['value']])
        selected_sensor_data['value']   = load_sensor_snapshot(times[idx['value']])
        selected_acoustic_data['value'] = load_acoustic_snapshot(times[idx['value']])
        refresh_marker_popups()
        refresh_birdnet_summary()
        if heatmap_layers['temperature']['visible']: refresh_heatmap_layer('temperature')
        if heatmap_layers['humidity']['visible']:    refresh_heatmap_layer('humidity')

    time_range_select.on_value_change(on_time_range_change)

    # ════════════════════════════════════════════════════════════════════
    # Finalize — wait for map, add markers, draw boundary
    # ════════════════════════════════════════════════════════════════════
    await m.initialized()

    # Cache map reference immediately so heatmap toggles always work
    ui.run_javascript(f"""
    (function(){{
        const el = getElement('{m.id}');
        const map = el && (el.map || el._map);
        if (map) {{ window._leafletMapRef = map; console.log('[map] cached _leafletMapRef'); }}
        else {{ console.warn('[map] could not cache ref at init'); }}
    }})();
    """)

    selected_sensor_data['value']   = load_sensor_snapshot(times[idx['value']])
    selected_acoustic_data['value'] = load_acoustic_snapshot(times[idx['value']])

    for it in items:
        add_marker(it)

    refresh_birdnet_summary()

    if boundary_latlngs:
        ui.run_javascript(f"""
        (function(){{
            const el  = getElement('{m.id}');
            const map = el && (el.map || el._map);
            if (!map) {{ console.warn('boundary: no map'); return; }}
            window._leafletMapRef = map;
            const latlngs = {boundary_latlngs};
            window._boundaryLayer = L.polygon(latlngs, {{
                color:'#16a34a', weight:3, fill:true, fillOpacity:0.08
            }}).addTo(map);
            // Small delay ensures tiles are loaded before fitBounds
            setTimeout(function() {{ map.fitBounds(window._boundaryLayer.getBounds(), {{padding:[20,20]}}); }}, 300);
        }})();
        """)
        print(f"[boundary] {SITE_CODE} ({len(boundary_latlngs)} pts)")
    else:
        ui.run_javascript(f"""
        (function(){{
            const el = getElement('{m.id}');
            const map = el && (el.map || el._map);
            if (map) window._leafletMapRef = map;
        }})();
        """)
