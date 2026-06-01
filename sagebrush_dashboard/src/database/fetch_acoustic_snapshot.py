import json
import glob
import psycopg2
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).parent
NAS_BASE  = Path('/mnt/sagebase')

# Devices on NAS that have acoustic data
NAS_DEVICES = [
    'sagemic1_ac6',
    'sagemic3_ac2',
    'sagemic6_oll',
    'sagemic_boa_hills',
    'sagemic_ridge',
    'sagemic_lte_balcony',
    'birdnet',
]


def normalize_id(s: str) -> str:
    return (s or "").strip().upper()


def _get_conn():
    with open(BASE_DIR / "db_credentials.json") as f:
        creds = json.load(f)
    return psycopg2.connect(
        host=creds["host"], port=creds["port"],
        dbname=creds["database"], user=creds["user"],
        password=creds["password"], sslmode="prefer",
    )


def _parse_wav_filename(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Parse a WAV filename into its components.
    Format: {HH-MM-SS}_{Species Name}_{confidence}.wav
    Example: 16-07-38_Western Screech-Owl_0.18.wav
    """
    name = filepath.stem  # strip .wav
    # Split on _ but species name can contain spaces and hyphens
    # Format is: HH-MM-SS_Species Name_0.xx
    # First token is always time (HH-MM-SS), last token is confidence float
    parts = name.split('_')
    if len(parts) < 3:
        return None
    try:
        time_str   = parts[0]          # HH-MM-SS
        conf_str   = parts[-1]         # 0.18
        species    = '_'.join(parts[1:-1])  # everything between
        confidence = float(conf_str)
        hh, mm, ss = time_str.split('-')
        return {
            'time_str':   time_str,
            'species':    species,       # 'Western Screech-Owl'
            'confidence': confidence,
            'filepath':   str(filepath),
        }
    except Exception:
        return None


def get_acoustic_snapshot_at(target_timestamp) -> Dict[str, Dict[str, Any]]:
    """
    Return the most recent acoustic detection per device at or before target_timestamp.
    Reads directly from NAS filenames — does not rely on DB filepath column.
    """
    if isinstance(target_timestamp, str):
        target_timestamp = datetime.fromisoformat(target_timestamp)

    target_date = target_timestamp.date()
    result: Dict[str, Dict[str, Any]] = {}

    for device_name in NAS_DEVICES:
        device_folder = NAS_BASE / device_name
        if not device_folder.exists():
            continue

        best_file   = None
        best_dt     = None

        # Search today and up to 7 days back for the most recent detection
        for days_back in range(8):
            search_date   = target_date - timedelta(days=days_back)
            date_folder   = device_folder / search_date.strftime('%Y-%m-%d')
            if not date_folder.exists():
                continue

            wav_files = sorted(date_folder.glob('*.wav'), reverse=True)

            for wav in wav_files:
                parsed = _parse_wav_filename(wav)
                if not parsed:
                    continue
                try:
                    hh, mm, ss = parsed['time_str'].split('-')
                    file_dt = datetime(
                        search_date.year, search_date.month, search_date.day,
                        int(hh), int(mm), int(ss)
                    )
                except Exception:
                    continue

                if file_dt <= target_timestamp:
                    if best_dt is None or file_dt > best_dt:
                        best_dt   = file_dt
                        best_file = parsed
                        best_file['recorded_at'] = file_dt
                    break  # files are sorted desc, first match is best for this day

            if best_file:
                break  # found something, stop going back further

        if best_file:
            norm_id = normalize_id(device_name)
            result[norm_id] = {
                'device_id':   norm_id,
                'recorded_at': str(best_file['recorded_at']),
                'species':     best_file['species'],
                'confidence':  best_file['confidence'],
                'filepath':    best_file['filepath'],
            }

    print(f"[acoustic_nas] snapshot at {target_timestamp}: {len(result)} devices")
    return result


def get_acoustic_time_series(
    start_timestamp,
    end_timestamp,
) -> List[Dict[str, Any]]:
    """
    Return all NAS detections between start and end timestamps.
    """
    if isinstance(start_timestamp, str):
        start_timestamp = datetime.fromisoformat(start_timestamp)
    if isinstance(end_timestamp, str):
        end_timestamp = datetime.fromisoformat(end_timestamp)

    results: List[Dict[str, Any]] = []

    current_date = start_timestamp.date()
    end_date     = end_timestamp.date()

    while current_date <= end_date:
        for device_name in NAS_DEVICES:
            date_folder = NAS_BASE / device_name / current_date.strftime('%Y-%m-%d')
            if not date_folder.exists():
                continue

            for wav in date_folder.glob('*.wav'):
                parsed = _parse_wav_filename(wav)
                if not parsed:
                    continue
                try:
                    hh, mm, ss = parsed['time_str'].split('-')
                    file_dt = datetime(
                        current_date.year, current_date.month, current_date.day,
                        int(hh), int(mm), int(ss)
                    )
                except Exception:
                    continue

                if start_timestamp <= file_dt <= end_timestamp:
                    results.append({
                        'device_id':  normalize_id(device_name),
                        'start_time': file_dt,
                        'species':    parsed['species'],
                        'confidence': parsed['confidence'],
                        'filepath':   parsed['filepath'],
                    })

        current_date += timedelta(days=1)

    print(f"[acoustic_nas] time series {start_timestamp} -> {end_timestamp}: {len(results)} detections")
    return results


if __name__ == "__main__":
    now  = datetime.now()
    snap = get_acoustic_snapshot_at(now)
    print(f"\nSnapshot: {len(snap)} devices")
    for k, v in snap.items():
        print(f"  {k}: {v['species']} ({v['confidence']}) @ {v['recorded_at']}")
        print(f"    file: {v['filepath']}")
