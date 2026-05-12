#!/usr/bin/env python3
"""
PLC Structured Text Parser

This script parses Structured Text (ST) files exported from GX Works.
"""

import re
import json
import sys
from pathlib import Path
from typing import Any

def parse_st_file(file_path: Path) -> dict[str, Any]:
    """Parse a single ST file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract function blocks, functions, programs, etc.
    functions = re.findall(r'(FUNCTION\s+\w+.*?END_FUNCTION)', content, re.DOTALL | re.IGNORECASE)
    function_blocks = re.findall(r'(FUNCTION_BLOCK\s+\w+.*?END_FUNCTION_BLOCK)', content, re.DOTALL | re.IGNORECASE)
    programs = re.findall(r'(PROGRAM\s+\w+.*?END_PROGRAM)', content, re.DOTALL | re.IGNORECASE)
    
    # Extract variable declarations
    var_declarations = re.findall(r'VAR.*?END_VAR', content, re.DOTALL | re.IGNORECASE)
    
    # Extract function/FB names
    func_names = [re.match(r'FUNCTION\s+(\w+)', f, re.IGNORECASE).group(1) for f in functions if re.match(r'FUNCTION\s+(\w+)', f, re.IGNORECASE)]
    fb_names = [re.match(r'FUNCTION_BLOCK\s+(\w+)', f, re.IGNORECASE).group(1) for f in function_blocks if re.match(r'FUNCTION_BLOCK\s+(\w+)', f, re.IGNORECASE)]
    prog_names = [re.match(r'PROGRAM\s+(\w+)', p, re.IGNORECASE).group(1) for p in programs if re.match(r'PROGRAM\s+(\w+)', p, re.IGNORECASE)]

    return {
        'filename': file_path.name,
        'functions': func_names,
        'function_blocks': fb_names,
        'programs': prog_names,
        'var_declarations': len(var_declarations),
        'total_size': len(content),
        'raw_content_size': len(content)
    }

def main():
    if len(sys.argv) > 2:
        programs_dir = Path(sys.argv[1])
        normalized_dir = Path(sys.argv[2])
    else:
        programs_dir = Path('exports/raw/programs')
        normalized_dir = Path('exports/normalized')
    
    normalized_dir.mkdir(exist_ok=True, parents=True)

    all_programs = []
    if programs_dir.exists():
        for st_file in programs_dir.glob('*.st'):
            parsed = parse_st_file(st_file)
            all_programs.append(parsed)

    with open(normalized_dir / 'st_programs.json', 'w', encoding='utf-8') as f:
        json.dump(all_programs, f, indent=2, ensure_ascii=False)

    print(f"ST parsing complete! Parsed {len(all_programs)} files.")

if __name__ == '__main__':
    main()