# 📈 Stock Analysis App

株価データの取得・バックテスト・自分のトレード分析までできる  
シンプルな株分析Webアプリです。

---

## 🚀 機能

### ✅ フェーズ1（基盤）

- 株価データ取得（yfinance）
- データベース保存（SQLite）
- バックテスト機能
  - 勝率
  - 平均リターン
  - 最大ドローダウン
- 保有日数を指定した検証
  - 例：翌日 / 2日後 / 5日後

---

### ✅ トレード管理

- トレード登録（UIフォーム）
- トレード一覧表示
- トレード削除
- 利益の自動計算

---

### ✅ フェーズ2（分析）

- タグ機能
  - トレードに複数タグ付与可能
- タグによる分析基盤
  - AI / 決算 / 半導体 などで分類

---

## 🧠 コンセプト

このアプリは単なる株価表示ツールではなく、

👉 **「何が正しいか」**
👉 **「自分はどうズレているか」**

を分析するためのツールです。

---

## 🛠 技術スタック

- Python（FastAPI）
- SQLite
- Jinja2（テンプレート）
- Bootstrap（UI）
- yfinance（株価取得）

---

## 📂 ディレクトリ構成

stock_app/
│
├── main.py
├── db.py
├── init_db.py
│
├── router/
│   ├── auth.py
│   ├── data.py
│   ├── trade.py
│   └── trade_view.py
│
├── services/
│   ├── price_service.py
│   └── backtest.py
│
├── templates/
│   ├── index.html
│   ├── trade.html
│   └── trades.html
│
└── database/
└── stock.db

---

## ⚙️ セットアップ

### ① 仮想環境作成

```bash
python -m venv venv
source venv/bin/activate

### ② ライブラリインストール

pip install fastapi uvicorn yfinance panda

### ③　サーバー起動

uvicorn main:app --reload
``
### ④　アクセス

http://127.0.0.1:8000

主なAPI
株価データ保存
GET /api/data/prices/{symbol}

例：
/api/data/prices/7203.T


バックテスト
GET /api/data/backtest/{symbol}?hold_days=1


トレード一覧
GET /trades


##📊 これからの拡張

タグ分析画面
勝率・収益の可視化
市場全体 × タグ分析
グラフ（収益推移）
AIによる戦略分析


##🎯 今後のビジョン

感覚ではなくデータで投資判断する
自分のトレードの癖を分析する
勝ちパターンを再現可能にする


##📝 メモ

本アプリは学習・研究目的です
投資判断は自己責任で行ってください


##👤 Author

GitHub: https://github.com/momonga5454
