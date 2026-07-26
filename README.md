# 🚀 StockVision Engine v2.5 - 台灣頂級 AI 股票研究平台

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Markets-TW%20%7C%20US-brightgreen.svg)]()

> **Institutional Commercial Edition & Retail EZ Mode**
> 
> StockVision Pro 是一款專為台股 (上市/上櫃) 與美股打造的機構級 AI 股票診斷與估值共識引擎。結合 **6 大內在估值模型**、**10 項全方位投資檢核**、**五維健康星圖**、**100 次 Monte Carlo 隨機模擬** 與 **雙模式 (EZ 新手 / Pro 機構) 介面**，提供全自動且具高度說服力的投資診斷。

---

## 🌟 核心特色功能 (Key Features)

### 1. 🔰 雙模式一鍵切換 (EZ Mode vs Pro Mode)
- **🔰 EZ 新手導引模式**：第一屏資訊簡化 35%~50%，將複雜財務數據轉化為直覺的 4 大速覽卡（全域建議、估值目標價區間、護城河強度、健康總分），並輔以 3 步驟導覽與金融白話 Tooltips。
- **🏛️ Pro 機構研報模式**：完整展示 8 階段機構研報流程、Model Card 2.5 演算法規格、95% 統計信賴區間與全量指標。

### 2. ⚖️ 6 大估值模型內在價值共識 (Fair Value Consensus)
整合多重無偏估值模型，避免單一指標的估值盲點：
- **DCF 自由現金流折現模型** (30%)
- **歷史本益比 (PE) 估值** (20%)
- **歷史股價淨值比 (PB) 估值** (15%)
- **PEG 成長性估值模型** (15%)
- **EV/EBITDA 企業價值估值** (10%)
- **RIM 剩餘收益模型** (10%)

### 3. 📋 10 項全方位投資檢核清單與 StockVision 護城河
- **黃金護城河 (Golden Moats)**：自動檢核超額利差 (\(\text{ROIC} - \text{WACC} \ge 5\%\))、高定價權 (毛利率 \(\ge 40\%\))、自由現金流率 (\(\ge 10\%\)) 與規模壁壘。
- **10 項定量檢核**：覆蓋盈利、成長、資產效率、負債比與技術面多頭排列。

### 4. 💎 五維企業健康星圖 (5-Pillar Health Matrix)
雷達圖量化企業 5 大維度健康度（總分 30 分）：
`Valuation (估值)` | `Future Growth (成長)` | `Past Performance (績效)` | `Financial Health (財務健康)` | `Dividend (股利回報)`

### 5. 🎯 100 次 Monte Carlo 隨機模擬 (95% CI)
針對 CAPM WACC、永續成長率與營收波動進行 100 次隨機抽樣，計算 95% 統計信賴區間 (\(\text{Score} \pm 3.5 \text{分}\))，避免單一數值的過度擬合。

### 6. ⚡ 7 大風險熱圖與調評觸發進度 (Trigger Progress)
設有連續 2~4 季過慮門檻的調評觸發器（上調/降級條件），搭配地緣政治、庫存週期與客戶集中度 7 大風險維度熱圖。

### 7. 📈 5 年歷史回測實績與主動風險指標
提供 Sharpe Ratio (夏普比率)、Sortino Ratio、Calmar Ratio、Information Ratio、Beta 與歷史最大回撤 (Max Drawdown) 驗證。

---

## 📁 專案架構 (Project Architecture)

```
StockVision-Pro/
├── main.py                  # FastAPI Web Server 與 API 端點 routing
├── config.py                # 全局參數設定 (WACC, DCF, 伺服器 Host/Port)
├── requirements.txt         # Python 套件依賴清單
├── .gitignore               # Git 忽略設定檔
├── .env.example             # 環境變數範本
├── LICENSE                  # MIT 授權條款
│
├── analyzers/               # 核心分析引擎
│   ├── fundamental.py       # 基本面分析器 (ROE, ROIC, 利潤率)
│   ├── technical.py         # 技術面分析器 (RSI, MACD, 均線排列)
│   ├── valuation.py         # 6 大模型內在估值共識引擎
│   ├── risk.py              # 7 大風險維度與 Alt-Z / Piotroski
│   ├── moat.py              # StockVision 護城河與 10 項投資檢核
│   ├── snowflake.py         # 五維健康星圖分析器
│   ├── industry.py          # 動態產業基準與動態權重配置
│   └── peer.py              # 同業標竿對比矩陣
│
├── scoring/                 # 評分與策略決策層
│   ├── score_engine.py      # 特徵歸一化與指標計分器
│   ├── decision.py          # 5 大策略 (Value, Growth, Quality, Momentum, Balanced)
│   ├── weights.py           # 產業特化動態加權矩陣
│   └── knowledge.py         # 知識庫與理由生成
│
├── data/                    # 資料載入與快取層
│   ├── loader.py            # yfinance / FinMind 資料整合器 (支援任意台股/美股)
│   ├── processor.py         # 財報與日線特徵工程對齊
│   ├── cache.py             # SQLite 本地高效快取
│   └── mock_generator.py    # 容錯 Mock 數據生成器
│
├── reports/                 # 研報與可解釋性生成器
│   ├── report.py            # Markdown 8 階段機構研報全文生成器
│   └── explainability.py    # 樹狀決策可解釋性拆解
│
├── backtest/                # 策略回測引擎
│   └── engine.py            # 5 年歷史 Alpha 超額報酬與權重優化
│
└── static/                  # 前端視覺 UI (Glassmorphism + Responsive)
    └── index.html           # 單頁 Web 應用程式 (含 EZ Mode / Pro Mode 切換)
```

---

## 🛠️ 快速開始 (Quick Start)

### 1. 複製專案庫 (Clone Repository)
```bash
git clone https://github.com/yourusername/StockVision-Pro.git
cd StockVision-Pro
```

### 2. 安裝依賴套件 (Install Dependencies)
建議建立並啟用 Python 虛擬環境：
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 啟動 Web 服務 (Run Application)
```bash
python main.py
```
控制台將顯示：
```text
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 4. 開啟瀏覽器體驗 (Open Browser)
於瀏覽器開啟 [http://127.0.0.1:8000](http://127.0.0.1:8000) 即可開始分析任意台股與美股！

---

## 📡 REST API 說明 (API Reference)

### 1. 個股全方位診斷評估 API
```http
GET /api/evaluate?ticker={ticker}&force={force}
```
* **參數**：
  * `ticker` (string, 必填)：台股代號 (如 `2330`, `2454`, `2603`) 或美股代碼 (如 `NVDA`, `AAPL`)。
  * `force` (boolean, 選填)：是否強制跳過快取並刷新資料 (預設 `false`)。
* **範例**：
  ```bash
  curl http://127.0.0.1:8000/api/evaluate?ticker=2330
  ```

### 2. 策略歷史回測 API
```http
GET /api/backtest?ticker={ticker}&strategy={strategy}
```
* **參數**：
  * `strategy`：`Value` | `Growth` | `Quality` | `Momentum` | `Balanced`

### 3. 策略權重優化 API
```http
GET /api/optimize?ticker={ticker}&strategy={strategy}
```

---

## 💡 貢獻與授權 (License)

本專案採 [MIT License](LICENSE) 授權開放。歡迎 Submit Issue 或 Pull Request！
