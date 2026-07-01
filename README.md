# Stock App

プチ株（単元未満株）を前提にした、株式投資の意思決定支援アプリです。

通常の株価表示アプリではなく、ユーザーが「いつ買うか」「待つか」「売るか」を判断するために、始値を重視したバックテスト、タグ分析、売買ログを組み合わせて使うことを目的にしています。

## 目的

プチ株は通常の株取引と比べて、売買タイミングに制約があります。

- 売買タイミングが前場・後場の始値中心になる
- デイトレードがしにくい
- 細かい注文条件を指定しにくい

そのため、このアプリでは「寄り付き（始値）」を重視し、過去データから以下のような判断材料を得ることを目指します。

- この条件では勝率が高いか
- このテーマやタグは最近強いか弱いか
- 自分はどのパターンで負けやすいか
- すぐ買うべきか、待つべきか

## 主な機能

### 株価チャート

銘柄コードを入力すると、yfinance から株価データを取得し、ローソク足チャートを表示します。

- 日本株コードは `7203` のように入力すると `7203.T` として扱います
- 移動平均線の期間を指定できます
- 生成したチャート画像は `static/charts/` に保存されます

### お気に入り銘柄

よく見る銘柄をお気に入りに登録できます。

- お気に入り追加
- お気に入り一覧
- お気に入り削除

### 売買ログ

ユーザー自身のトレードを記録できます。

保存する主な内容:

- 銘柄コード
- 購入日
- 購入価格
- 売却日
- 売却価格
- 損益
- メモ
- タグ

### タグ分析

売買ログにタグを付けて、タグごとの成績を分析できます。

現在確認できる指標:

- 回数
- 勝率
- 平均利益
- タグの組み合わせ別分析

タグの例:

- 決算
- 半導体
- AI
- 金利上昇
- 割安
- 初動
- 期待先行

### バックテスト

指定した銘柄・期間・保有日数で、始値ベースのバックテストを実行できます。

現在の基本ロジック:

```text
指定日の始値で買う
指定した保有日数後の始値で売る
```

算出する指標:

- 勝率
- 平均リターン
- 最大ドローダウン
- 最大連敗数
- 検証回数

画面:

```text
/backtest
/backtest-ui
```

API:

```text
GET /api/data/prices/{symbol}
GET /api/data/backtest/{symbol}?hold_days=3&start=2022-01-01&end=2023-01-01
```

## 技術構成

- Python
- FastAPI
- Jinja2
- SQLite
- yfinance
- pandas
- mplfinance
- Bootstrap

## ディレクトリ構成

```text
stock_app/
├── main.py
├── db.py
├── init_db.py
├── requirements.txt
├── database/
│   └── stock.db
├── router/
│   ├── auth.py
│   ├── stock.py
│   ├── favorites.py
│   ├── data.py
│   ├── trade.py
│   ├── trade_view.py
│   └── tag.py
├── services/
│   ├── price_service.py
│   ├── backtest.py
│   └── tag_analysis.py
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── stock.html
│   ├── favorites.html
│   ├── trade.html
│   ├── trades.html
│   ├── tag_analysis.html
│   ├── tag_combo_analysis.html
│   └── backtest.html
└── static/
    └── charts/
```

## 起動方法

このプロジェクトは WSL 側の仮想環境で動かす想定です。

```bash
source venv/bin/activate
uvicorn main:app --reload
```

ブラウザで開きます。

```text
http://127.0.0.1:8000
```

## 初期ログイン

現在の実装では、起動時に以下のユーザーが作成されます。

```text
ユーザー名: admin
パスワード: password
```

本番利用する場合は、固定パスワードの初期ユーザー作成は削除または変更してください。

## 主要URL

```text
/login                 ログイン
/register              新規登録
/                      ホーム
/stock                 株価チャート
/favorites             お気に入り一覧
/trade                 売買ログ登録
/trades                売買ログ一覧
/tag-analysis          タグ別分析
/tag-combo-analysis    タグ組み合わせ分析
/backtest              バックテスト画面
```

## API

```text
GET  /api/data/prices/{symbol}
GET  /api/data/backtest/{symbol}

GET  /api/trades/
POST /api/trades/
POST /api/trades/delete/{trade_id}

GET  /api/tags/
POST /api/tags/
POST /api/tags/assign
GET  /api/tags/analysis
GET  /api/tags/analysis/combo

##　画面イメージ



## 今後の拡張方針

このアプリの最終形は、単なる株価確認ではなく、投資判断の傾向分析です。

今後追加したい機能:

- バックテスト結果のDB保存
- 戦略パターンの選択
- 公式タグとユーザータグの分離
- 銘柄・日付単位のイベントタグ管理
- タグ別バックテスト
- 売買ログとバックテスト結果の比較
- AIによる傾向分析
- ニュース取得と自動タグ付け

AI分析は株価予測ではなく、以下のような振り返り用途を想定しています。

- どのタグで勝率が高いか
- どのテーマで負けやすいか
- 高値掴みしやすい傾向があるか
- 特定銘柄とテーマの相性が良いか

## 注意点

- yfinance のデータ取得に失敗すると、バックテストやチャート生成ができない場合があります
- バックテストは過去データの検証であり、将来の利益を保証するものではありません
- 現在のバックテストには手数料、税金、スリッページは含まれていません
- プチ株の実際の約定仕様は証券会社によって異なるため、実運用前に確認が必要です


