# Skill: mitsubishi-plc-project-normalizer

## Purpose
解析 GX Works2 / GX Works3 匯出的文字檔、CSV、XML、ST、mnemonic CSV，轉換成統一 JSON 結構，供文件產生器與差異分析使用。

## Supported input
- CSV: labels, device comments, parameters, cross reference
- TXT: compile report, print report, parameter report
- ST: Structured Text program
- XML: 若 GX Works 或相關工具可匯出 XML，需保留原始節點與屬性
- Mnemonic CSV: Ladder 轉 mnemonic 後的指令表

## Output schema
```json
{
  "project": {
    "name": "",
    "plc_series": "",
    "cpu_model": "",
    "software": "",
    "exported_at": ""
  },
  "programs": [],
  "labels": [],
  "devices": [],
  "parameters": [],
  "modules": [],
  "networks": [],
  "diagnostics": []
}
```

## Parsing rules

* 保留原始欄位名稱。
* 另外產生標準欄位，例如 name, address, data_type, scope, comment。
* 無法判斷的欄位放入 raw。
* 不要刪除未知欄位。
* 所有解析錯誤需輸出到 diagnostics。