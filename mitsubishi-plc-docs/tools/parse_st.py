#!/usr/bin/env python3
"""
Mitsubishi PLC Structured Text Parser

This script parses Structured Text (ST) files exported from GX Works.
"""

import re
from pathlib import Path

def parse_st_file(file_path):
    """Parse a single ST file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic parsing - extract function blocks, functions, etc.
    functions = re.findall(r'(FUNCTION\s+\w+.*?END_FUNCTION)', content, re.DOTALL | re.IGNORECASE)
    function_blocks = re.findall(r'(FUNCTION_BLOCK\s+\w+.*?END_FUNCTION_BLOCK)', content, re.DOTALL | re.IGNORECASE)
    programs = re.findall(r'(PROGRAM\s+\w+.*?END_PROGRAM)', content, re.DOTALL | re.IGNORECASE)

    return {
        'functions': functions,
        'function_blocks': function_blocks,
        'programs': programs,
        'raw_content': content
    }

def main():
    programs_dir = Path('exports/raw/programs')
    normalized_dir = Path('exports/normalized')
    normalized_dir.mkdir(exist_ok=True)

    all_programs = []
    for st_file in programs_dir.glob('*.st'):
        parsed = parse_st_file(st_file)
        parsed['filename'] = st_file.name
        all_programs.append(parsed)

    with open(normalized_dir / 'programs.json', 'w', encoding='utf-8') as f:
        json.dump(all_programs, f, indent=2, ensure_ascii=False)

    print("ST parsing complete!")

if __name__ == '__main__':
    import json
    main()