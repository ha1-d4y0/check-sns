# Multi-Platform SNS & Gaming Activity Monitor

Discord、Steam、Xbox などの複数プラットフォームから指定ユーザーのオンラインステータスやプレイ中のゲーム、最終アクティブ日時などの情報を集約し、コンソール上に美しく整形して表示する CLI ツールです。

## 🌟 特徴

* **マルチプラットフォーム対応**: Discord, Steam, Xbox Live のステータスを一覧で確認可能。
* **2つの表示モード**:
  * `status` モード: リアルタイムの稼働状況やプレイ中のタイトルを表示。
  * `all` モード: アカウント作成日時や詳細な環境設定を含む包括的なレポートを表示。
* **タイムゾーン自動補正**: JST (日本標準時) に最適化された日時フォーマット。
* **バッチファイル対応**: Windows 環境であればダブルクリック操作でモード選択＆実行が可能。

## 📁 構成ファイル

```text
.
├── check-sns.py      # メインの実行スクリプト
├── run.bat           # Windows向け実行用バッチファイル
├── .env.example      # 環境変数のサンプルファイル
└── README.md         # 本ドキュメント
```

## 📋 動作環境・必要ライブラリ

* **Python 3.8+**
* **依存パッケージ**:
  * `discord.py`
  * `requests`
  * `python-dotenv`
  * `tabulate`

---

## 🚀 使い方

### 1. リポジトリのクローンと依存パッケージのインストール

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

pip install discord.py requests python-dotenv tabulate
```

### 2. 環境変数の設定 (`.env`)

`.env.example` をコピーして `.env` ファイルを作成し、各種 API キーおよびターゲット ID を設定してください。

```ini
DISCORD_TOKEN=your-discord-token
STEAM_API_KEY=your-steam-api-key
TARGET_DISCORD_ID=target-discord-id
TARGET_STEAM_ID=target-steam-id
XBOX_API_KEY=your-xbox-api-key
TARGET_XBOX_GAMERTAG=target-xbox-gamertag
```

> **注意**: Discord Bot を作成する際、Discord Developer Portal にて **Server Members Intent** および **Presence Intent** を有効にする必要があります。

---

### 3. スクリプトの実行

#### ■ Windows の場合（バッチファイルを使用）
`run.bat` をダブルクリックすると、メニューからモードを選択して簡単に実行できます。

#### ■ コマンドラインから実行する場合

**リアルタイムステータスの取得（デフォルト）**
```bash
python check-sns.py status
# または
python check-sns.py
```

**総合レポートの取得**
```bash
python check-sns.py all
```

---

## 📊 出力例 (`status` モード)

```text
🚀 [ 取得時刻: 2026-10-29 07:50:00 ]
┌──────────┬─────────────┬────────────────┐
│ Source   │ Item        │ Current Value  │
├──────────┼─────────────┼────────────────┤
│ Discord  │ Status      │ 🟢 Online      │
│ Discord  │ Playing     │ Apex Legends   │
│ Discord  │ Active On   │ Desktop        │
│ Steam    │ Status      │ 🔵 Online      │
│ Steam    │ Playing     │ Counter-Strike │
│ Xbox     │ Status      │ Online         │
└──────────┴─────────────┴────────────────┘
```

## ⚙️ ライセンス

MIT License