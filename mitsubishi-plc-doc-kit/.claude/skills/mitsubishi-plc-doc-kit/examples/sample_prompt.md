# Sample Gemini CLI Prompts

## Export planning

```bash
gemini -p "Use skills/mitsubishi-plc-doc-kit/SKILL.md. I have a GX Works3 Mitsubishi PLC project and want Git version control. Tell me exactly what to export and create a folder layout."
```

## Documentation generation

```bash
gemini -p "Use skills/mitsubishi-plc-doc-kit/SKILL.md. Read exports/raw and generate exports/normalized JSON plus docs Markdown. Do not invent missing values."
```

## Parameter explanation

```bash
gemini -p "Use skills/mitsubishi-plc-doc-kit/SKILL.md. Explain all CPU, module, and network parameters under exports/raw/parameters and write docs/02_cpu_parameters.md, docs/03_module_parameters.md, and docs/04_network_parameters.md."
```
