# Export Checklist

| Category | Preferred Format | Target Folder | Notes |
|---|---|---|---|
| Project summary | TXT/CSV/PDF text | exports/raw/project_info/ | PLC model, CPU, software version |
| Program source | ST/TXT/mnemonic CSV | exports/raw/programs/ | Preserve original names |
| Global labels | CSV | exports/raw/labels/ | Name, type, address, comment |
| Local labels | CSV | exports/raw/labels/ | Keep per-program context |
| Device comments | CSV | exports/raw/device_comments/ | Device, comment, language |
| CPU parameters | CSV/TXT/XML | exports/raw/parameters/ | Preserve raw names and values |
| Module parameters | CSV/TXT/XML | exports/raw/module_config/ | Slot, module model, parameter value |
| Network parameters | CSV/TXT/XML | exports/raw/network/ | CC-Link, Ethernet, station config |
| Cross reference | CSV/TXT | exports/raw/cross_reference/ | Read/write/use information |
| Compile report | TXT | exports/raw/reports/ | Warnings/errors |
