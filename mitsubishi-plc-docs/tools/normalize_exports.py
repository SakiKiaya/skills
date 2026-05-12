#!/usr/bin/env python3
"""
Mitsubishi PLC Export Normalizer

This script normalizes exported CSV/TXT/XML/ST/mnemonic files from GX Works
into structured JSON format.
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

def normalize_labels(csv_path):
    """Normalize labels CSV to JSON"""
    labels = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = {
                'name': row.get('Name', ''),
                'address': row.get('Address', ''),
                'data_type': row.get('DataType', ''),
                'scope': row.get('Scope', 'Global'),
                'comment': row.get('Comment', ''),
                'raw': row
            }
            labels.append(label)
    return labels

def normalize_devices(csv_path):
    """Normalize device comments CSV to JSON"""
    devices = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            device = {
                'address': row.get('Address', ''),
                'comment': row.get('Comment', ''),
                'raw': row
            }
            devices.append(device)
    return devices

def main():
    raw_dir = Path('exports/raw')
    normalized_dir = Path('exports/normalized')
    normalized_dir.mkdir(exist_ok=True)

    # Normalize labels
    labels_files = list(raw_dir.glob('labels/*.csv'))
    all_labels = []
    for f in labels_files:
        all_labels.extend(normalize_labels(f))

    with open(normalized_dir / 'labels.json', 'w', encoding='utf-8') as f:
        json.dump(all_labels, f, indent=2, ensure_ascii=False)

    # Normalize devices
    device_files = list(raw_dir.glob('device_comments/*.csv'))
    all_devices = []
    for f in device_files:
        all_devices.extend(normalize_devices(f))

    with open(normalized_dir / 'devices.json', 'w', encoding='utf-8') as f:
        json.dump(all_devices, f, indent=2, ensure_ascii=False)

    print("Normalization complete!")

if __name__ == '__main__':
    main()