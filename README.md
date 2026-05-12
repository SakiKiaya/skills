# PLC Skills Kit - Skill 倉庫

## 📖 專案概覽

這是一個**PLC ( PLC) 文檔化 Skill 倉庫**，提供一套完整的 Claude Code / GitHub Copilot Agent Skills，用於自動化生成和處理 GX Works PLC 專案的技術文檔。

**主要用途**: 將 GX Works2 / GX Works3 匯出的原始數據（CSV、ST 程式、助記碼）轉換為版本控制友善的標準化 JSON 資料，進而自動產生 GitHub Markdown 文檔。

## 🎯 核心功能

- **匯出顧問** (`plc-export-advisor`) - 規劃最佳的 PLC 專案匯出策略
- **資料標準化** (`plc-project-normalizer`) - 將原始匯出文件轉換為標準 JSON 格式
- **文檔生成** (`plc-doc-generator`) - 從標準化資料自動產生 Markdown 文檔
- **參數說明** (`plc-parameter-explainer`) - 解釋 PLC 參數和變數定義
- **結構分析** (`plc-structure-analyzer`) - 分析 ST 程式和助記碼結構

## 📁 目錄結構

```
skills/
├── plc-skills-kit/              # 主要 Skill 倉庫
│   ├── README.md                # 詳細文檔
│   ├── requirements.txt          # Python 依賴
│   ├── .claude/skills/           # Claude Agent Skills 定義
│   ├── docs/                     # 文檔資源
│   ├── examples/                 # 使用範例
│   │   └── sample_exports/       # 範例匯出檔
│   └── exports/                  # 處理結果輸出目錄
│       ├── raw/                  # 原始數據
│       └── normalized/           # 標準化數據
```

## 🚀 快速開始

### 環境要求
- Python 3.7+
- Claude Code 或 GitHub Copilot

### 安裝依賴
```bash
cd plc-skills-kit
pip install -r requirements.txt
```

### 使用流程

1. **匯出 PLC 專案** - 使用 GX Works2/3 的匯出功能
2. **放置原始檔** - 將匯出的 CSV、ST 檔放入 `exports/raw/`
3. **標準化** - 使用 `plc-project-normalizer` Skill
4. **生成文檔** - 使用 `plc-doc-generator` Skill
5. **查看結果** - 在 `exports/normalized/` 中查看輸出

## 📚 詳細文檔

請查看 README.md 了解更多詳細信息。

## 📋 支援的格式

- **匯出格式**: CSV (全域標籤)、JSON (專案配置)、ST (結構化文本)、Mnemonic (助記碼)
- **輸出格式**: 標準化 JSON、Markdown 文檔、結構分析報告

## 🔧 核心 Skills

每個 Skill 都包含：
- `SKILL.md` - Skill 定義和使用方法
- `scripts/` - Python 實現腳本
- `references/` - 參考文檔和範例
- `assets/` - 輔助資源

## 📝 License

請查看 LICENSE 了解授權條款。

## 💡 主要特性

- ✅ 自動化文檔生成
- ✅ 版本控制友善的數據格式
- ✅ 模組化設計，每個 Skill 獨立可用
- ✅ 支援 Claude Code 和 GitHub Copilot
- ✅ 完整的範例和文檔

---

**技術棧**: Python 3.7+ | Claude Code Skills | GitHub Copilot Agent Skills |  GX Works
