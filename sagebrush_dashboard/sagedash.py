from nicegui import ui, app
from config.device_loader import load_device_config

from src.scripts.data_arch import flatten_items, compute_center
from src.ui.main_page import main_page

app.add_static_files('/assets', 'assets')
app.add_static_files('/css', 'css')

cfg = load_device_config("config/devices.yaml")
items = flatten_items(cfg)
center_lat, center_lon = compute_center(items)

ui.run(title='SageBrush Dash')
