# 🚀 FastAPI DDD Template

[![CI](https://github.com/mugipan-en/fastapi-ddd-template/actions/workflows/ci.yml/badge.svg)](https://github.com/mugipan-en/fastapi-ddd-template/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mugipan-en/fastapi-ddd-template/branch/main/graph/badge.svg)](https://codecov.io/gh/mugipan-en/fastapi-ddd-template)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00C7B7.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**プロダクション対応のFastAPI + ドメイン駆動設計(DDD) テンプレート**

即戦力のAPI開発テンプレートで、設計からデプロイまでのベストプラクティスを網羅。

## 🏗️ アーキテクチャ

```
app/
├── domain/          # ドメイン層 (ビジネスロジック)
│   ├── entities/    # エンティティ
│   ├── repositories/# リポジトリインターフェース
│   └── services/    # ドメインサービス
├── application/     # アプリケーション層 (ユースケース)
│   └── use_cases/   # ユースケース実装
├── infrastructure/  # インフラ層 (データベース、外部API)
│   ├── database/    # DB設定・マイグレーション
│   ├── repositories/# リポジトリ実装
│   └── external/    # 外部API クライアント
└── presentation/    # プレゼンテーション層 (API エンドポイント)
    ├── api/         # APIルーター
    ├── schemas/     # レスポンス・リクエスト スキーマ
    └── dependencies/# 依存性注入
```

## 🚀 クイックスタート

### 1. 環境構築

```bash
# リポジトリをクローン
git clone https://github.com/mugipan-en/fastapi-ddd-template.git
cd fastapi-ddd-template

# uvをインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
make setup
```

### 2. データベースセットアップ

```bash
# PostgreSQL起動 (Docker)
docker-compose up -d postgres

# マイグレーション実行
make migrate

# 初期データ投入
make seed
```

### 3. アプリケーション起動

```bash
# 開発サーバー起動
make dev

# API仕様確認
open http://localhost:8000/docs
```

## 📋 主な機能

### ✅ 実装済み
- **認証・認可**: JWT + Role-based Access Control
- **ユーザー管理**: CRUD操作 + プロフィール管理
- **データベース**: PostgreSQL + SQLModel + Alembic
- **バリデーション**: Pydantic v2
- **テスト**: pytest + coverage 90%+
- **セキュリティ**: CORS, Rate Limiting, Input Validation
- **ドキュメント**: OpenAPI/Swagger 自動生成
- **監視**: Prometheus メトリクス
- **ロギング**: 構造化ログ (JSON)

### 🔧 DevOps
- **CI/CD**: GitHub Actions
- **コード品質**: Black, Ruff, mypy
- **セキュリティ**: Safety, Bandit
- **コンテナ**: Docker + Docker Compose
- **環境管理**: .env ファイル

## 🗄️ データベース設計

### ER図
```mermaid
erDiagram
    Users {
        int id PK
        string email UK
        string hashed_password
        string first_name
        string last_name
        enum role
        datetime created_at
        datetime updated_at
    }

    Posts {
        int id PK
        int user_id FK
        string title
        text content
        enum status
        datetime created_at
        datetime updated_at
    }

    Users ||--o{ Posts : "creates"
```

## 🔧 開発コマンド

```bash
# セットアップ
make setup          # 依存関係インストール
make setup-dev      # 開発用依存関係も含む

# 開発
make dev            # 開発サーバー起動
make test           # テスト実行
make test-cov       # カバレッジ付きテスト
make lint           # コード品質チェック
make fmt            # コードフォーマット

# データベース
make migrate        # マイグレーション実行
make migrate-auto   # 自動マイグレーション生成
make seed           # 初期データ投入

# デプロイ
make build          # Dockerイメージビルド
make deploy         # 本番環境デプロイ
```

## 📁 ディレクトリ構成

```
fastapi-ddd-template/
├── app/
│   ├── __init__.py
│   ├── main.py                    # アプリケーションエントリーポイント
│   ├── core/                      # 共通設定
│   │   ├── config.py             # 設定管理
│   │   ├── security.py           # セキュリティ設定
│   │   └── database.py           # DB接続設定
│   ├── domain/                    # ドメイン層
│   ├── application/               # ユースケース層
│   ├── infrastructure/            # インフラ層
│   └── presentation/              # API層
├── tests/                         # テストコード
├── alembic/                       # DBマイグレーション
├── docker/                        # Docker設定
├── scripts/                       # ユーティリティスクリプト
├── docs/                          # ドキュメント
├── .github/workflows/             # GitHub Actions
├── pyproject.toml                 # Python設定
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## 🔐 環境変数

`.env`ファイルを作成し、以下の値を設定：

```env
# アプリケーション
APP_NAME=FastAPI DDD Template
DEBUG=True
SECRET_KEY=your-secret-key-here

# データベース
DATABASE_URL=postgresql://user:password@localhost/dbname
TEST_DATABASE_URL=sqlite:///./test.db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

## 🧪 テスト

```bash
# 全テスト実行
make test

# 特定のテストファイル実行
pytest tests/test_users.py

# カバレッジレポート
make test-cov
open htmlcov/index.html
```

## 📊 API仕様

### 認証エンドポイント
- `POST /api/v1/auth/login` - ログイン
- `POST /api/v1/auth/register` - ユーザー登録
- `POST /api/v1/auth/refresh` - トークン更新

### ユーザー管理
- `GET /api/v1/users/me` - 現在のユーザー情報
- `PUT /api/v1/users/me` - プロフィール更新
- `GET /api/v1/users/{id}` - ユーザー詳細

### 投稿管理
- `GET /api/v1/posts` - 投稿一覧
- `POST /api/v1/posts` - 投稿作成
- `GET /api/v1/posts/{id}` - 投稿詳細
- `PUT /api/v1/posts/{id}` - 投稿更新
- `DELETE /api/v1/posts/{id}` - 投稿削除

## 🚀 デプロイ

### Docker
```bash
# イメージビルド
docker build -t fastapi-ddd-template .

# コンテナ起動
docker run -p 8000:8000 fastapi-ddd-template
```

### Docker Compose
```bash
# 全サービス起動
docker-compose up -d

# ログ確認
docker-compose logs -f app
```

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. コミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

## 📄 ライセンス

MIT License. 詳細は [LICENSE](LICENSE) を参照。

## 🙏 謝辞

- [FastAPI](https://fastapi.tiangolo.com/) - モダンなPython Web フレームワーク
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL データベース操作
- [Pydantic](https://pydantic-docs.helpmanual.io/) - データバリデーション

---

**⭐ 気に入ったらスターをお願いします！**
