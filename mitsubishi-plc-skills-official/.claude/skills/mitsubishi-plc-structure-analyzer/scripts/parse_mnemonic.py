#!/usr/bin/env python3
"""
Mitsubishi PLC Mnemonic Parser

This script parses mnemonic CSV files exported from GX Works ladder programs.
"""

import csv
import re
import json
import sys
from pathlib import Path
from typing import Any

def parse_mnemonic_csv(file_path: Path) -> dict[str, Any]:
    """Parse a mnemonic CSV file"""
    instructions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            instruction = {
                'step': row.get('Step', ''),
                'instruction': row.get('Instruction', ''),
                'operand': row.get('Operand', ''),
                'comment': row.get('Comment', '')
            }
            instructions.append(instruction)

    # Extract device usage
    devices = set()
    for inst in instructions:
        operand = inst.get('operand', '')
        # Find device addresses like X0, Y1, M100, D200, etc.
        # Pattern: Device letter (X, Y, M, D, L, F, T, C, S, B, W, etc.) followed by numbers and optional decimal
        device_matches = re.findall(r'\b([X-Y|M|D|L|F|T|C|S|B|W|ZR|LZ|RD|SD|SW|Z|U|G|V]\d+(?:\.\d+)?)\b', operand)
        devices.update(device_matches)

    return {
        'filename': file_path.name,
        'total_instructions': len(instructions),
        'devices_used': sorted(list(devices)),
        'device_count': len(devices),
        'instructions': instructions
    }

def main():
    if len(sys.argv) > 2:
        programs_dir = Path(sys.argv[1])
        normalized_dir = Path(sys.argv[2])
    else:
        programs_dir = Path('exports/raw/programs')
        normalized_dir = Path('exports/normalized')
    
    normalized_dir.mkdir(exist_ok=True, parents=True)

    all_mnemonics = []
    if programs_dir.exists():
        for csv_file in programs_dir.glob('*mnemonic*.csv'):
            parsed = parse_mnemonic_csv(csv_file)
            all_mnemonics.append(parsed)

    # Save full data
    with open(normalized_dir / 'mnemonics.json', 'w', encoding='utf-8') as f:
        json.dump(all_mnemonics, f, indent=2, ensure_ascii=False)

    # Save summary (without full instruction list for readability)
    summary = []
    for m in all_mnemonics:
        summary.append({
            'filename': m['filename'],
            'total_instructions': m['total_instructions'],
            'devices_used': m['devices_used'],
            'device_count': m['device_count']
        })
    
    with open(normalized_dir / 'mnemonics_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Mnemonic parsing complete! Parsed {len(all_mnemonics)} files.")

if __name__ == '__main__':
    main()