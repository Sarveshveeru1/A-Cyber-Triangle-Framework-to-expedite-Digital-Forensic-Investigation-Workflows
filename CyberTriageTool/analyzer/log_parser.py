# analyzer/log_parser.py

import os
import json
from Evtx.Evtx import Evtx
import xml.etree.ElementTree as ET

def extract_event_data(xml_data):
    try:
        root = ET.fromstring(xml_data)
        ns = {'e': 'http://schemas.microsoft.com/win/2004/08/events/event'}

        system = root.find('e:System', ns)
        event_id = system.find('e:EventID', ns).text
        time_created = system.find('e:TimeCreated', ns).attrib['SystemTime']
        computer = system.find('e:Computer', ns).text

        return {
            "event_id": event_id,
            "timestamp": time_created,
            "computer": computer
        }
    except Exception as e:
        return {"error": str(e)}

def parse_evtx_file(file_path, output_path="output/log_summary.json", filter_ids=["4624", "4625", "6005", "6006"]):
    results = []

    with Evtx(file_path) as log:
        for record in log.records():
            data = extract_event_data(record.xml())
            if data.get("event_id") in filter_ids:
                results.append(data)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✅ Parsed {len(results)} events. Saved to {output_path}")
    return output_path
