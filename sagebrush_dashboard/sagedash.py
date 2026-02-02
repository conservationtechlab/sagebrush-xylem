from nicegui import ui, app

# Register static files
app.add_static_files('/assets', 'assets')
app.add_static_files('/css', 'css')

# Importing the page registers it with NiceGUI
# DO NOT call it manually
from src.ui.main_page import main_page  # noqa: F401

ui.run(
    title='SageBrush Dashboard',
    port=8081,
)
