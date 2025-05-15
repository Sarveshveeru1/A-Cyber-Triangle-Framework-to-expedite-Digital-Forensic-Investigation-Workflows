# analyzer/timeline_generator.py

import json
import os
from datetime import datetime, timezone
from dateutil import parser

def load_events_from_logs(file_path, source):
    events = []
    if not os.path.exists(file_path):
        return events

    with open(file_path, "r") as f:
        data = json.load(f)
        for entry in data:
            timestamp = entry.get("timestamp")
            if timestamp:
                events.append({
                    "time": timestamp,
                    "event": f"{source}: Event ID {entry.get('event_id')}",
                    "source": source
                })
    return events

def load_boot_time(system_info_path="output/system_info.json"):
    if not os.path.exists(system_info_path):
        return []

    with open(system_info_path) as f:
        info = json.load(f)
        return [{
            "time": info.get("boot_time"),
            "event": "System Boot",
            "source": "System Info"
        }] if info.get("boot_time") else []

def generate_timeline(
    system_info_path="output/system_info.json",
    log_paths=[
        ("output/security_log_summary.json", "Security Log"),
        ("output/app_log_summary.json", "Application Log"),
        ("output/system_log_summary.json", "System Log")
    ],
    output_path="output/timeline.json"
):
    all_events = []

    # Add boot time
    all_events.extend(load_boot_time(system_info_path))

    # Add events from logs
    for path, label in log_paths:
        all_events.extend(load_events_from_logs(path, label))

    # Sort events by parsed and normalized datetime
    def sort_key(event):
        try:
            dt = parser.isoparse(event["time"])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    sorted_events = sorted(all_events, key=sort_key)

    with open(output_path, "w") as f:
        json.dump(sorted_events, f, indent=4)

    print(f"✅ Timeline generated with {len(sorted_events)} events at {output_path}")
    return output_path
