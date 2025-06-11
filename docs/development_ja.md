# 開発ガイド

## はじめに

### 前提条件

- Python 3.11 以上
- PostgreSQL 13+（本番環境用）
- Redis 6+（キャッシュとバックグラウンドタスク用）
- Git
- uv（推奨）または pip

### インストール

1. **リポジトリをクローン：**
   ```bash
   git clone https://github.com/mugipan-en/fastapi-ddd-template.git
   cd fastapi-ddd-template
   ```

2. **uv をインストール（推奨）：**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **仮想環境を作成し、依存関係をインストール：**
   ```bash
   uv venv
   source .venv/bin/activate  # Windows の場合: .venv\Scripts\activate
   uv pip install -e ".[dev,lint,security]"
   ```

4. **環境設定：**
   ```bash
   cp .env.example .env
   # .env ファイルを設定で編集
   ```

5. **データベース設定：**
   ```bash
   # データベーステーブルを作成
   make migrate

   # サンプルデータを投入（オプション）
   make seed
   ```

6. **アプリケーションを実行：**
   ```bash
   make dev
   ```

アプリケーションは `http://localhost:8000` で利用できます。

## プロジェクト構造

```
fastapi-ddd-template/
├── app/                    # アプリケーションコード
│   ├── core/              # コアユーティリティ（設定、データベース、セキュリティ）
│   ├── domain/            # ドメイン層（エンティティ、リポジトリ、サービス）
│   ├── application/       # アプリケーション層（ユースケース）
│   ├── infrastructure/    # インフラストラクチャ層（リポジトリ、外部サービス）
│   ├── presentation/      # プレゼンテーション層（API、スキーマ）
│   └── main.py           # アプリケーションエントリーポイント
├── tests/                 # テストファイル
├── alembic/              # データベースマイグレーション
├── docs/                 # ドキュメント
├── docker/               # Docker 設定
├── scripts/              # ユーティリティスクリプト
├── .env.example          # 環境変数テンプレート
├── pyproject.toml        # プロジェクト設定
└── Makefile              # 開発用コマンド
```

## 開発ワークフロー

### 1. 変更を行う

1. **フィーチャーブランチを作成：**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **コーディング標準に従って変更を行う**

3. **テストを実行：**
   ```bash
   make test
   ```

4. **リンティングとフォーマットを実行：**
   ```bash
   make lint
   make format
   ```

### 2. データベース変更

1. **マイグレーションを作成：**
   ```bash
   make migration message="新しいテーブルを追加"
   ```

2. **マイグレーションを適用：**
   ```bash
   make migrate
   ```

3. **必要に応じてロールバック：**
   ```bash
   alembic downgrade -1
   ```

### 3. テスト

```bash
# すべてのテストを実行
make test

# カバレッジ付きで実行
make test-cov

# 特定のテストファイルを実行
pytest tests/test_auth_api.py

# 特定のテストを実行
pytest tests/test_auth_api.py::TestAuthAPI::test_login_success
```

### 4. コード品質

```bash
# コードをリント
make lint

# コードをフォーマット
make format

# 型チェック
make typecheck

# セキュリティチェック
make security
```

## 利用可能な Make コマンド

| コマンド | 説明 |
|---------|------|
| `make setup` | 開発環境をセットアップ |
| `make dev` | 開発サーバーを実行 |
| `make test` | テストを実行 |
| `make test-cov` | カバレッジ付きでテストを実行 |
| `make lint` | リンティングを実行 |
| `make format` | コードをフォーマット |
| `make typecheck` | 型チェックを実行 |
| `make security` | セキュリティチェックを実行 |
| `make migrate` | データベースマイグレーションを実行 |
| `make migration` | 新しいマイグレーションを作成 |
| `make seed` | サンプルデータを投入 |
| `make clean` | キャッシュとビルドファイルをクリーン |
| `make build` | Docker イメージをビルド |
| `make docker-dev` | Docker Compose で実行 |

## 環境変数

### 必須変数

```bash
# セキュリティ
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# データベース
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379
```

### オプション変数

```bash
# アプリケーション
APP_NAME=FastAPI DDD Template
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# メール（メール機能を使用する場合）
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

## IDE 設定

### VS Code

推奨拡張機能：
- Python
- Pylance
- Python Test Explorer
- GitLens
- Thunder Client（API テスト用）

ワークスペース設定（`.vscode/settings.json`）：
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. Python インタープリターを `.venv/bin/python` に設定
2. Black を使用するようにコードスタイルを設定
3. pytest をテストランナーとして有効化
4. Python Requirements プラグインをインストール

## デバッグ

### VS Code デバッグ

起動設定（`.vscode/launch.json`）：
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/uvicorn",
            "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

### ログ

アプリケーションは構造化ログを使用します。デバッグ情報は以下の設定で有効化できます：
```bash
LOG_LEVEL=DEBUG
```

## API ドキュメント

開発モードで実行時、インタラクティブ API ドキュメントが利用できます：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## データベース管理

### Alembic コマンド

```bash
# マイグレーション生成
alembic revision --autogenerate -m "マイグレーションメッセージ"

# マイグレーション適用
alembic upgrade head

# ロールバック
alembic downgrade -1

# マイグレーション履歴表示
alembic history

# 現在のリビジョン表示
alembic current
```

### データシード

```bash
# サンプルデータ投入
python scripts/seed_data.py

# または make を使用
make seed
```

## パフォーマンス監視

### ローカル監視

```bash
# メトリクスエンドポイントにアクセス
curl http://localhost:8000/metrics

# ヘルスチェック
curl http://localhost:8000/health
```

### プロファイリング

パフォーマンスプロファイリングには以下を使用できます：
```bash
pip install py-spy
py-spy top --pid <process-id>
```

## トラブルシューティング

### よくある問題

1. **ポートが既に使用中：**
   ```bash
   # ポート 8000 を使用しているプロセスを検索
   lsof -i :8000
   # プロセスを終了
   kill -9 <pid>
   ```

2. **データベース接続エラー：**
   - PostgreSQL が実行中か確認
   - .env の DATABASE_URL を確認
   - データベースが存在するか確認

3. **マイグレーションエラー：**
   - データベース接続を確認
   - 競合するマイグレーションがないか確認
   - マイグレーションファイルを確認

4. **インポートエラー：**
   - 仮想環境がアクティブか確認
   - すべての依存関係がインストールされているか確認
   - PYTHONPATH を確認

### ヘルプの取得

1. ドキュメントを確認
2. GitHub Issues で類似の問題を検索
3. 以下の情報を含む新しい Issue を作成：
   - Python バージョン
   - OS 詳細
   - エラーメッセージ
   - 再現手順

## コントリビューション

コードオブコンダクトとプルリクエストの送信プロセスの詳細については、[コントリビューションガイド](contributing_ja.md)をお読みください。
