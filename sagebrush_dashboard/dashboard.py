"""
dashboard.py
--------------

Brief Description:
    Demo dashboard for the SageBRUSH digital twin project.

Author:           Grace Coleman
Date Created:     2025-07-30
Last Modified:    2025-07-30
Version:          0.9.9

Usage:
    streamlit dashboard.py

Dependencies:
    - See environment.yml
    - SageBase access

Notes:
    - See SageBase schema for database.
    - For questions, contact arichardson@sdzwa.org

"""

import glob
import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import psycopg
import pydeck as pdk
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="SAGEBASE",
    layout="wide"
)

CACHE_TTL = 3600
TEMPERATURE_THRESHOLD = 50
SENSORS = ['boa_hills_temp_sensor', 'ridge_gateway_temp_sensor_6', 'ridge_gateway_temp_sensor_3']
MAP_CONFIG = {
    'latitude': 33.095295,
    'longitude': -116.979037,
    'zoom': 14,
    'pitch': 0,
}

@dataclass
class ColorConfig:
    """Color configuration for visualizations"""
    TEMP_MAX = 45
    HUMIDITY_MAX = 100
    TEMP_BASE_COLOR = (220, 0, 0)
    HUMIDITY_BASE_COLOR = (0, 200, 0)

class DatabaseManager:
    """Handles database connections and queries"""

    def __init__(self, secrets_file: str = "secrets.json"):
        self.secrets_file = secrets_file
        self._connection_params = None

    def _load_secrets(self) -> Dict[str, str]:
        """Load database secrets from JSON file"""
        if self._connection_params is None:
            with open(self.secrets_file, encoding="utf-8") as file:
                secrets = json.load(file)
                self._connection_params = {
                    'host': secrets["host"],
                    'port': secrets["port"],
                    'user': "sage_user",
                    'password': secrets["password"],
                    'dbname': "sagebase"
                }
        return self._connection_params

    @st.cache_data(ttl=CACHE_TTL)
    def get_sensor_data(_self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch and process sensor data from database"""
        params = _self._load_secrets()

        query = """
        SELECT deployment_id, recorded_at, temperature, humidity, latitude, longitude
        FROM v_field_sensor_lat_long
        WHERE temperature < %s;
        """

        try:
            with psycopg.connect(**params) as conn:
                sensor_data = pd.read_sql_query(
                    query,
                    conn,
                    params=[TEMPERATURE_THRESHOLD]
                )
        except psycopg.Error as err:
            st.error(f"Database error: {err}")

            empty_df = pd.DataFrame(columns=['deployment_id','recorded_at', 'temperature',
                                             'humidity', 'latitude', 'longitude'])
            empty_long = pd.DataFrame(columns=['recorded_at', 'variable', 'value', 'hour', 'day'])
            return empty_df, empty_long

        if sensor_data.empty:
            empty_df = pd.DataFrame(columns=['deployment_id', 'recorded_at', 'temperature',
                                             'humidity', 'latitude', 'longitude'])
            empty_long = pd.DataFrame(columns=['recorded_at', 'variable', 'value', 'hour', 'day'])
            return empty_df, empty_long

        sensor_data['timestamp'] = pd.to_datetime(sensor_data['recorded_at'])
        sensor_data['recorded_at'] = sensor_data['recorded_at'].dt.floor('h')

        sensor_data_avgs = (
            sensor_data
            .groupby('recorded_at')
            .agg({'temperature': 'mean', 'humidity': 'mean'})
            .reset_index()
        )

        sensor_data_long = sensor_data_avgs.melt(
            id_vars='recorded_at',
            value_vars=['temperature', 'humidity'],
            var_name='variable',
            value_name='value'
        )

        sensor_data_long["hour"] = sensor_data_long["recorded_at"].dt.hour
        sensor_data_long["day"] = sensor_data_long["recorded_at"].dt.date

        return sensor_data, sensor_data_long

class BirdDataProcessor:
    """Handles bird detection data processing"""

    def __init__(self, data_path: str = "birdnet/"):
        self.data_path = data_path
        self.filename_pattern = re.compile(
            r"(?P<species>.+?)-\d{1,4}-(?P<date>\d{4}-\d{2}-\d{2})-birdnet-(?P<time>\d{2}[:：]\d{2}[:：]\d{2})\.mp3.png"
        )

    @st.cache_data(ttl=CACHE_TTL)
    def get_bird_data(_self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process bird detection files and return structured data"""
        files = glob.glob(os.path.join(_self.data_path, "**", "*.png"), recursive=True)
        file_names = [os.path.basename(f) for f in files]

        birds_data = []
        for filename in file_names:
            bird_info = _self._parse_filename(filename)
            if bird_info:
                birds_data.append(bird_info)

        if not birds_data:
            empty_birds = pd.DataFrame(columns=['timestamp', 'day_folder', 'day',
                                                'hour', 'minute', 'species', 'png_key', 'mp3_key'])
            empty_counts = pd.DataFrame(columns=['day', 'hour', 'count'])
            return empty_birds, empty_counts

        birds_df = pd.DataFrame(birds_data).sort_values("timestamp")

        hourly_counts = (
            birds_df
            .groupby([
                birds_df["timestamp"].dt.date.rename("day"),
                birds_df["timestamp"].dt.hour.rename("hour")
            ])
            .size()
            .reset_index(name="count")
        )

        return birds_df, hourly_counts

    def _parse_filename(self, filename: str) -> Optional[Dict]:
        """Parse bird detection filename to extract metadata"""
        match = self.filename_pattern.search(filename)
        if not match:
            return None

        time_str = match.group('time').replace("：", ":")
        dt_str = f"{match.group('date')} {time_str}"

        try:
            timestamp = pd.to_datetime(dt_str, utc=True)
            timestamp = timestamp.tz_convert("America/Los_Angeles")
        except:
            return None

        return {
            "timestamp": timestamp,
            "day_folder": match.group("date"),
            "day": timestamp.date(),
            "hour": timestamp.hour,
            "minute": timestamp.minute,
            "species": match.group("species"),
            "png_key": match.group(0),
            "mp3_key": match.group(0).replace(".png", "")
        }

class ColorUtils:
    """Utility functions for color calculations"""

    @staticmethod
    def humidity_to_color(humidity: float) -> List[int]:
        """Convert humidity to RGB color"""
        normalized = min(humidity / ColorConfig.HUMIDITY_MAX, 1.0)
        red = int(225 * (1 - normalized))
        green = int(220 - (220 * normalized) / 2)
        blue = 0
        return [red, green, blue, 160]

    @staticmethod
    def temp_to_color(temperature: float) -> List[int]:
        """Convert temperature to RGB color"""
        normalized = min(temperature / ColorConfig.TEMP_MAX, 1.0)
        red = 220
        green = 0
        blue = int(255 * normalized)
        return [red, green, blue, 160]

class MapVisualizer:
    """Handles map visualization logic"""

    def __init__(self):
        self.tooltip = {
            "html": "<b>Sensor:</b> {deployment_id} <br/>"
                   "<b>Temperature:</b> {temperature} °C <br/>"
                   "<b>Humidity:</b> {humidity}% <br/>",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "fontSize": "12px"
            }
        }

    def create_map(self, sensor_data: pd.DataFrame, selected_time: datetime) -> None:
        """Create and display map with sensor data"""
        filtered_data = self._filter_sensor_data(sensor_data, selected_time)

        if filtered_data.empty:
            st.info("No sensor data available for selected time")
            return

        filtered_data["hum_color"] = filtered_data["humidity"].apply(ColorUtils.humidity_to_color)
        filtered_data["temp_color"] = filtered_data["temperature"].apply(ColorUtils.temp_to_color)

        filtered_data['longitude'] = pd.to_numeric(filtered_data['longitude'], errors='coerce')
        filtered_data['latitude'] = pd.to_numeric(filtered_data['latitude'], errors='coerce')

        filtered_data = filtered_data.dropna(subset=['longitude', 'latitude'])

        if filtered_data.empty:
            st.info("No valid sensor locations for selected time")
            return

        layers = self._create_map_layers(filtered_data)

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=pdk.ViewState(**MAP_CONFIG),
                map_style="mapbox://styles/mapbox/light-v9",
                tooltip=self.tooltip
            )
        )

    def _filter_sensor_data(self, sensor_data: pd.DataFrame,
                            selected_time: datetime) -> pd.DataFrame:
        """Filter sensor data for the selected time window"""
        if sensor_data.empty:
            return pd.DataFrame(columns=['deployment_id', 'temperature',
                                         'humidity', 'latitude', 'longitude'])

        time_window_start = selected_time - timedelta(hours=1)
        filtered_sensors = []

        for sensor in SENSORS:
            sensor_subset = sensor_data[sensor_data['deployment_id'] == sensor]
            if sensor_subset.empty:
                continue

            time_filtered = sensor_subset[
                (sensor_subset['timestamp'] >= time_window_start) &
                (sensor_subset['timestamp'] <= selected_time)
            ]

            if not time_filtered.empty:
                latest_time = time_filtered['timestamp'].max()
                latest_data = time_filtered[time_filtered['timestamp'] == latest_time]
                filtered_sensors.append(latest_data)

        if not filtered_sensors:
            return pd.DataFrame(columns=['deployment_id', 'temperature',
                                         'humidity', 'latitude', 'longitude'])

        return pd.concat(filtered_sensors, ignore_index=True)

    def _create_map_layers(self, data: pd.DataFrame) -> List[pdk.Layer]:
        """Create map layers for temperature and humidity"""
        return [
            pdk.Layer(
                "ScatterplotLayer",
                data=data,
                get_position='[longitude, latitude]',
                get_fill_color='hum_color',
                get_radius=120,
                pickable=True,
                opacity=1,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=data,
                get_position='[longitude, latitude]',
                get_fill_color='temp_color',
                get_radius=80,
                pickable=True,
                opacity=1,
            )
        ]

class BirdVisualizer:
    """Handles bird detection visualizations"""

    def create_timeline(self, birds: pd.DataFrame, selected_time: datetime) -> None:
        """Create timeline visualization for bird calls"""
        filtered_birds = self._filter_birds_by_time(birds, selected_time)

        if filtered_birds.empty:
            return

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_birds['minute'],
            y=[1] * len(filtered_birds),
            mode='markers',
            marker={"size": 10, "color": 'green'},
            name="Bird Calls"
        ))

        fig.update_layout(
            height=100,
            xaxis=dict(
                range=[0, 59],
                title="Minutes",
                showgrid=True
            ),
            yaxis={"visible": False},
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    def display_bird_detections(self, birds: pd.DataFrame, selected_time: datetime) -> None:
        """Display bird detection details for selected time"""
        filtered_birds = self._filter_birds_by_time(birds, selected_time)

        if filtered_birds.empty:
            st.info("No bird detections for that hour.")
            return

        species_found = sorted({
            s.replace("_", " ").title()
            for s in filtered_birds["species"].unique()
        })
        st.text(", ".join(species_found))

        for _, detection in filtered_birds.iterrows():
            self._display_single_detection(detection)

    def _filter_birds_by_time(self, birds: pd.DataFrame, selected_time: datetime) -> pd.DataFrame:
        """Filter birds by selected time"""
        if birds.empty:
            return pd.DataFrame()
        return birds[
            (birds["day"] == selected_time.date()) &
            (birds["hour"] == selected_time.hour)
        ]

    def _display_single_detection(self, detection: pd.Series) -> None:
        """Display a single bird detection"""
        timestamp = detection["timestamp"]
        species = detection["species"]
        day_folder = detection["day_folder"]

        with st.container():
            st.markdown("---")
            header = f"{timestamp.strftime('%I:%M:%S %p')} - {species.replace('_', ' ').title()}"
            st.subheader(header)

            icon_path = f"bird_pics/{species.lower().replace('-', '_')}.png"
            mp3_path = f"birdnet/{day_folder}/{species}/{detection['mp3_key']}"
            png_path = f"birdnet/{day_folder}/{species}/{detection['png_key']}"

            try:
                if os.path.exists(icon_path):
                    st.image(icon_path, use_container_width=False)
                if os.path.exists(mp3_path):
                    st.audio(mp3_path, format="audio/mp3")
                if os.path.exists(png_path):
                    st.image(png_path, caption=species.replace("_", " ").title())
            except Exception:
                st.warning(f"Missing file for: {species}")

class ChartVisualizer:
    """Handles chart visualizations"""

    @st.cache_data(ttl=CACHE_TTL)
    def create_timeline_chart(_self, sensor_data: pd.DataFrame,
                              min_time: datetime, selected_time: datetime) -> go.Figure:
        """Create historical timeline chart"""
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if sensor_data.empty:
            fig.update_layout(
                height=300,
                title="No data available",
                margin={"t": 20, "b": 20, "l": 0, "r": 0}
            )
            return fig

        time_filtered = sensor_data[sensor_data['recorded_at'] >= min_time]

        fig.add_trace(
            go.Bar(
                x=time_filtered['recorded_at'],
                y=time_filtered['count'],
                name='Bird Calls',
                marker_color='orange',
                opacity=0.3
            ),
            secondary_y=True
        )

        colors = {'temperature': 'red', 'humidity': 'green'}
        line_styles = {'temperature': 'solid', 'humidity': 'dash'}

        for variable in ['temperature', 'humidity']:
            var_data = time_filtered[time_filtered['variable'] == variable]
            fig.add_trace(
                go.Scatter(
                    x=var_data['recorded_at'],
                    y=var_data['value'],
                    mode='lines',
                    name=variable.title(),
                    line={
                        "color": colors[variable],
                        "dash": line_styles[variable]
                    }
                ),
                secondary_y=False
            )

        fig.add_vline(x=selected_time, line_width=2, line_color="#DA2C43")

        fig.update_layout(
            height=300,
            xaxis=dict(title='', showgrid=True),
            legend=dict(
                orientation="h",
                x=0.5, y=1.1,
                xanchor="center",
                font={"size": 12}
            ),
            margin={"t": 20, "b": 20, "l": 0, "r": 0},
            yaxis={"title": '', "showticklabels": False, "showgrid": False},
            yaxis2={"title": '', "showticklabels": False, "showgrid": False}
        )

        return fig

def create_legend_html(min_val: str, max_val: str, gradient: str) -> str:
    """Create HTML for color legends"""
    return f"""
    <div style="display: flex; align-items: center; margin-top: 5px;">
        <span style="margin-right: 10px;">{min_val}</span>
        <div style="flex: 1; height: 20px; background: {gradient}; border: 1px solid #ccc;"></div>
        <span style="margin-left: 10px;">{max_val}</span>
    </div>
    """

def main():
    """Main application logic"""
    db_manager = DatabaseManager()
    bird_processor = BirdDataProcessor()
    map_viz = MapVisualizer()
    bird_viz = BirdVisualizer()
    chart_viz = ChartVisualizer()

    try:
        sensor_data, sensor_data_long = db_manager.get_sensor_data()
        birds, hourly_counts = bird_processor.get_bird_data()

        if not sensor_data_long.empty and not hourly_counts.empty:
            sensor_data_long = pd.merge(
                sensor_data_long, hourly_counts,
                on=["hour", "day"], how="left"
            )
            sensor_data_long["count"] = sensor_data_long["count"].fillna(0)
        else:
            sensor_data_long["count"] = 0

    except Exception as exc:
        st.error(f"Error loading data: {exc}")
        st.stop()

    st.title("SageBRUSH Dash")

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    yesterday = now - timedelta(days=1)
    min_time = now - timedelta(days=7)
    time_range = pd.date_range(min_time, yesterday, freq='h')

    if "animate" not in st.session_state:
        st.session_state.animate = False
    if "anim_time_index" not in st.session_state:
        st.session_state.anim_time_index = len(time_range) - 1

    col1, col2, col3 = st.columns([1, 70, 4])
    with col2:
        slider_ph = st.empty()

    selected_time = slider_ph.slider(
        "Time",
        min_value=min_time,
        max_value=now,
        value=time_range[min(st.session_state.anim_time_index,
                            len(time_range) - 1)].to_pydatetime(),
        step=timedelta(hours=1),
        format="MM/DD/YYYY hh:mm A"
    )

    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        if st.button("animate"):
            st.session_state.animate = True
            try:
                st.session_state.anim_time_index = time_range.get_loc(selected_time)
            except ValueError:
                st.session_state.anim_time_index = 0
    with col2:
        if st.button("stop"):
            st.session_state.animate = False
            selected_time = time_range[st.session_state.anim_time_index]

    if not st.session_state.animate:
        fig = chart_viz.create_timeline_chart(sensor_data_long, min_time, selected_time)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns([1, 3])

        with col1:
            st.subheader("Identified Bird Calls")
            bird_viz.create_timeline(birds, selected_time)
            bird_viz.display_bird_detections(birds, selected_time)

        with col2:
            st.subheader("Temperature")
            st.markdown(
                create_legend_html(
                    "0°C", "45°C",
                    "linear-gradient(to left, rgb(220,0,0), rgb(255, 0, 255))"
                ),
                unsafe_allow_html=True
            )

            st.subheader("Humidity")
            st.markdown(
                create_legend_html(
                    "0%", "100%",
                    "linear-gradient(to right, rgb(0, 200, 0), rgb(255, 255, 0))"
                ),
                unsafe_allow_html=True
            )

            st.text(" ")
            map_viz.create_map(sensor_data, selected_time)

    else:
        st.session_state.start_time = time.time()
        selected_time = slider_ph.slider(
            "Time",
            min_value=min_time,
            max_value=yesterday,
            value=time_range[st.session_state.anim_time_index].to_pydatetime(),
            step=timedelta(hours=1),
            format="MM/DD/YYYY hh:mm A",
            key="slider_anim"
        )
        selected_time = time_range[st.session_state.anim_time_index]
        st.session_state.anim_time_index += 1
        if st.session_state.anim_time_index >= len(time_range):
            st.session_state.animate = False
        else:
            time.sleep(0.5)
            fig = chart_viz.create_timeline_chart(sensor_data_long, min_time, selected_time)
            st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns([1, 3])

            with col1:
                st.subheader("Identified Bird Calls")
                bird_viz.create_timeline(birds, selected_time)
                bird_viz.display_bird_detections(birds, selected_time)

            with col2:
                st.subheader("Temperature")
                st.markdown(
                    create_legend_html(
                        "0°C", "45°C",
                        "linear-gradient(to left, rgb(220,0,0), rgb(255, 0, 255))"
                    ),
                    unsafe_allow_html=True
                )

                st.subheader("Humidity")
                st.markdown(
                    create_legend_html(
                        "0%", "100%",
                        "linear-gradient(to right, rgb(0, 200, 0), rgb(255, 255, 0))"
                    ),
                    unsafe_allow_html=True
                )

                st.text(" ")
                map_viz.create_map(sensor_data, selected_time)
            st.rerun()

if __name__ == "__main__":
    main()

