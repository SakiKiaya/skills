#!/usr/bin/env python3
"""
Mitsubishi PLC Mnemonic Parser

This script parses mnemonic CSV files exported from GX Works ladder programs.
"""

import csv
import re
from pathlib import Path

def parse_mnemonic_csv(file_path):
    """Parse a mnemonic CSV file"""
    instructions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            instruction = {
                'step': row.get('Step', ''),
                'instruction': row.get('Instruction', ''),
                'operand': row.get('Operand', ''),
                'comment': row.get('Comment', ''),
                'raw': row
            }
            instructions.append(instruction)

    # Extract device usage
    devices = set()
    for inst in instructions:
        operand = inst.get('operand', '')
        # Simple regex to find device addresses like X0, Y1, M100, D200, etc.
        device_matches = re.findall(r'\b([X-Y|M|D|L|F|T|C|S|B|W|ZR|LZ|RD|SD|SW|Z|U|G|V]\d+(?:\.\d+)?)\b', operand)
        devices.update(device_matches)

    return {
        'instructions': instructions,
        'devices_used': list(devices)
    }

def main():
    programs_dir = Path('exports/raw/programs')
    normalized_dir = Path('exports/normalized')
    normalized_dir.mkdir(exist_ok=True)

    all_mnemonics = []
    for csv_file in programs_dir.glob('*mnemonic*.csv'):
        parsed = parse_mnemonic_csv(csv_file)
        parsed['filename'] = csv_file.name
        all_mnemonics.append(parsed)

    with open(normalized_dir / 'mnemonics.json', 'w', encoding='utf-8') as f:
        json.dump(all_mnemonics, f, indent=2, ensure_ascii=False)

    print("Mnemonic parsing complete!")

if __name__ == '__main__':
    import json
    main()