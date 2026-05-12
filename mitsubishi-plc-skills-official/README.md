# Mitsubishi PLC Skills Pack

這是一組符合 Claude Code / Agent Skills 目錄慣例的 Mitsubishi PLC 文件化 Skills Pack。

## 官方相容目錄結構

每個 Skill 都是獨立資料夾，並且每個資料夾內都有自己的 `SKILL.md`：

```text
.claude/
└── skills/
    ├── mitsubishi-plc-export-advisor/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── scripts/
    │   └── assets/
    ├── mitsubishi-plc-project-normalizer/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── scripts/
    │   └── assets/
    ├── mitsubishi-plc-doc-generator/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── scripts/
    │   └── assets/
    ├── mitsubishi-plc-parameter-explainer/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── scripts/
    │   └── assets/
    └── mitsubishi-plc-structure-analyzer/
        ├── SKILL.md
        ├── references/
        ├── scripts/
        └── assets/
```

## 建議工作流程

1. `/mitsubishi-plc-export-advisor`：規劃 GX Works2 / GX Works3 應匯出的文本資料。
2. `/mitsubishi-plc-project-normalizer`：將 `exports/raw/` 內的 CSV / TXT / ST / mnemonic 轉成 `exports/normalized/*.json`。
3. `/mitsubishi-plc-doc-generator`：根據 normalized JSON 產生 `docs/*.md`。
4. `/mitsubishi-plc-parameter-explainer`：產生 CPU / Module / Network 參數說明。
5. `/mitsubishi-plc-structure-analyzer`：產生程式結構、Device/Label 使用關係與 Mermaid 圖。

## Claude Code 安裝

專案層級：

```bash
cp -r .claude/skills/<skill-name> /path/to/your-project/.claude/skills/
```

個人層級：

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/
```

## Gemini CLI 使用方式

Gemini CLI 不一定會自動掃描 Claude Skills，因此建議明確要求它讀取某個 `SKILL.md`：

```bash
gemini -p "Read .claude/skills/mitsubishi-plc-export-advisor/SKILL.md and plan GX Works export files for a Mitsubishi PLC documentation workflow."
```

```bash
gemini -p "Read .claude/skills/mitsubishi-plc-project-normalizer/SKILL.md. Normalize files under exports/raw into exports/normalized. Do not invent missing values."
```

## 重要限制

此套件不假設可以直接解析 `.gx3`、`.gxw`、`.gppw` 等 proprietary project file。建議先由 GX Works 匯出 CSV / TXT / XML / ST / mnemonic / report，再由 Skills 解析。
