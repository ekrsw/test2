# Knowledge Maintenance System Backend API

ナレッジメンテナンスサイトのバックエンドAPI（FastAPI + PostgreSQL + Redis）

## 機能概要

- **認証・認可**: JWT（RS256）とRedisによるトークン管理
- **ユーザー管理**: 一般ユーザー・SV・管理者の権限管理
- **提案管理**: 記事の修正・削除提案の作成・承認ワークフロー
- **統計機能**: 個人・グループ別の提案統計と集計

## 技術スタック

- **Backend**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **Cache/Session**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Authentication**: JWT (RS256) + Redis
- **Container**: Docker + Docker Compose

## セットアップ

### 1. JWTキーの生成

```bash
./generate_keys.sh
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# 必要に応じて.envファイルを編集
```

### 3. Docker Composeで起動

```bash
docker-compose up --build
```

これで以下のサービスが起動します：
- **API Server**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. API仕様書の確認

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## プロジェクト構成

```
app/
├── api/
│   └── v1/                 # API エンドポイント
│       ├── auth.py         # 認証
│       ├── users.py        # ユーザー管理
│       ├── groups.py       # グループ管理
│       ├── info_categories.py # 情報カテゴリ
│       ├── articles.py     # 記事管理
│       ├── proposals.py    # 提案管理
│       └── statistics.py   # 統計・集計
├── auth/                   # 認証システム
│   ├── jwt.py             # JWT処理
│   ├── password.py        # パスワード処理
│   └── redis.py           # Redis操作
├── models/                 # SQLAlchemyモデル
├── schemas/                # Pydanticスキーマ
├── config.py              # 設定
├── database.py            # DB接続
└── main.py                # FastAPIアプリ
```

## API エンドポイント

### 認証
- `POST /api/v1/auth/login` - ログイン

### ユーザー管理
- `GET /api/v1/users/` - ユーザー一覧（管理者のみ）
- `GET /api/v1/users/me` - 現在のユーザー情報
- `POST /api/v1/users/` - ユーザー作成（管理者のみ）
- `PUT /api/v1/users/{user_id}` - ユーザー更新
- `DELETE /api/v1/users/{user_id}` - ユーザー削除（管理者のみ）

### グループ管理
- `GET /api/v1/groups/` - グループ一覧
- `POST /api/v1/groups/` - グループ作成（管理者のみ）
- `PUT /api/v1/groups/{group_id}` - グループ更新（管理者のみ）
- `DELETE /api/v1/groups/{group_id}` - グループ削除（管理者のみ）

### 情報カテゴリ
- `GET /api/v1/info-categories/` - カテゴリ一覧
- `POST /api/v1/info-categories/` - カテゴリ作成（管理者のみ）
- `PUT /api/v1/info-categories/{category_id}` - カテゴリ更新（管理者のみ）
- `DELETE /api/v1/info-categories/{category_id}` - カテゴリ削除（管理者のみ）

### 記事管理
- `GET /api/v1/articles/` - 記事一覧
- `POST /api/v1/articles/` - 記事作成（管理者のみ）
- `PUT /api/v1/articles/{article_id}` - 記事更新（管理者のみ）
- `DELETE /api/v1/articles/{article_id}` - 記事削除（管理者のみ）

### 提案管理
- `GET /api/v1/proposals/` - 提案一覧
- `POST /api/v1/proposals/` - 提案作成
- `GET /api/v1/proposals/pending-approval` - 承認待ち提案（SV・管理者のみ）
- `GET /api/v1/proposals/{proposal_id}` - 提案詳細
- `PUT /api/v1/proposals/{proposal_id}` - 提案更新（作成者のみ、申請中のみ）
- `POST /api/v1/proposals/{proposal_id}/approve` - 提案承認・却下（SV・管理者のみ）
- `DELETE /api/v1/proposals/{proposal_id}` - 提案削除

### 統計・集計
- `GET /api/v1/statistics/user/monthly-proposals` - 月次提案数
- `GET /api/v1/statistics/user/approval-rate` - 承認率
- `GET /api/v1/statistics/user/proposal-summary` - 提案サマリー
- `GET /api/v1/statistics/group/proposal-counts` - グループ別提案数（管理者のみ）
- `GET /api/v1/statistics/monthly-trends` - 月次トレンド（SV・管理者のみ）
- `GET /api/v1/statistics/approval-statistics` - 承認統計（SV・管理者のみ）

## 権限設計

### 一般ユーザー
- 自分の提案の作成・参照・更新（申請中のみ）
- 自分の統計情報の参照

### SV（スーパーバイザー）
- 一般ユーザーの権限に加えて
- 担当グループの提案承認・却下
- 担当グループの統計情報参照

### 管理者
- 全ての機能へのアクセス
- ユーザー・グループ・カテゴリ・記事の管理
- 全体統計の参照

## データベース

詳細なテーブル設計は `docs/database-design.md` を参照してください。

### 主要テーブル
- **users**: ユーザー情報
- **groups**: 承認グループ
- **info_categories**: 情報カテゴリ
- **articles**: 記事マスタ
- **proposals**: 提案情報
- **proposals_before**: 修正前データ

## 開発

### ローカル開発環境

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/knowledge_maintenance"
export REDIS_URL="redis://localhost:6379"

# マイグレーション実行
alembic upgrade head

# 開発サーバー起動
uvicorn app.main:app --reload
```

### マイグレーション

```bash
# 新しいマイグレーション作成
alembic revision --autogenerate -m "Add new table"

# マイグレーション実行
alembic upgrade head
```

## ライセンス

MIT License