# システム概要

## システムの目的

`BukkenAiSearch` は、不動産営業担当者が顧客のヒアリング内容をもとに、売買物件・収益物件の探索条件を整理し、候補物件の確認、比較、提案文作成を支援するAIチャット型Webアプリである。

当初は「ClaudeのProjectをBubble.ioからAPIで呼び出せるか」という検討から始まり、Claude Projectsそのものを直接使うのではなく、Bubble側で会話・プロジェクト設定・Knowledge資料・登記データを管理し、Claude APIへ必要な文脈を渡す構成に整理された。

## 想定ユーザー

主な利用者は不動産会社の営業担当者。

想定する業務は、賃貸物件探しではなく、売買物件・収益物件の探索支援。顧客から聞いた条件を入力し、AIが不足情報、確認事項、次に取るべき営業アクションを整理する。

## 業務フロー

1. 営業担当者がログインする
2. `AI Chat` で新規会話を開始する
3. 顧客ヒアリング内容を自然文で入力する
4. Bubbleがユーザー発言を `Message` として保存する
5. Bubbleが会話履歴を整形してClaude APIへ送信する
6. Claudeが条件整理・不足項目・営業アクションを返す
7. BubbleがClaude回答を `Message` として保存する
8. 会話一覧にはタイトル、Claude回答の抜粋、最終更新日時を表示する
9. 必要に応じて「条件として保存」「提案文を作成」「比較リストに追加」を行う
10. 将来的には登記データ・Knowledge資料を検索し、候補物件情報をClaudeに渡して比較・提案に活用する

# 現在の画面構成

## index / ダッシュボード

- 画面名: `index`
- 目的: ログイン後のホーム画面。最近の会話、保存済み条件、AIプロジェクト、Knowledge資料の概要を確認する
- 主な機能:
  - 統計カード表示
  - 最近の会話一覧
  - クイックチャット入力
  - `AIチャットを開く` 導線
- 実装状況:
  - Bubble AIにより画面生成済み
  - リンク系エラーを修正済み
  - 最近の会話カードから `ai_chat` に遷移するWorkflowを設定
  - `Data to send` に対象 `Conversation` を渡す形に修正済み

## ai_chat / AIチャット画面

- 画面名: `ai_chat`
- 目的: 顧客ヒアリング内容を入力し、Claudeから営業支援回答を得る中心画面
- 主な機能:
  - 左サイドバー
  - 会話一覧
  - 新規会話作成
  - チャットメッセージ表示
  - メッセージ入力
  - Claude API連携
  - 回答下のアクションボタン
- 実装状況:
  - `Type of content: Conversation` に設定済み
  - `Current page's Conversation` を前提にメッセージ一覧を表示
  - ユーザー発言とClaude回答を `role` により表示分岐
  - 会話履歴をClaude APIへ渡すよう修正済み
  - 入力欄のみ安全にクリアする対応済み
  - 左側一覧の抜粋をClaude回答にする対応済み
  - 新規会話を作らずPreviewから直接入力すると表示されない問題を確認し、`+ 新規` 経由を基本導線に整理

## search_conditions / 物件条件管理

- 画面名: `search_conditions`
- 目的: 保存済み物件探索条件を一覧・詳細管理する
- 主な機能:
  - 希望エリア
  - 予算
  - 駅距離
  - 面積
  - 特別条件
  - メモ
- 実装状況:
  - Bubble AIによりページ生成済み
  - Data Type `SearchCondition` は作成済み
  - 本格的な保存Workflowは今後調整予定

## ai_projects / AIプロジェクト設定

- 画面名: `ai_projects`
- 目的: Claude ProjectのようなAI設定をBubble内で管理する
- 主な機能:
  - プロジェクト名
  - model
  - system prompt
  - max tokens
  - temperature
  - active状態
- 実装状況:
  - ページ生成済み
  - Data Type `AiProject` は作成済み
  - API連携で `system_prompt` を動的に使う処理は未着手

## knowledge / Knowledge資料管理

- 画面名: `knowledge`
- 目的: AIが参照する資料を管理する
- 主な機能:
  - 資料タイトル
  - 要約
  - 本文
  - ファイル
  - active切替
- 実装状況:
  - ページ生成済み
  - Data Type `KnowledgeDocument` は作成済み
  - Claude Projectsのファイル相当として検討
  - ただし今回の登記PDF由来データは、単なるKnowledge資料ではなく登記物件DBとして扱う方針に変更

## login / signup

- 画面名: ログイン・サインアップ
- 目的: ユーザー認証
- 主な機能:
  - メールアドレス・パスワードによるログイン
  - サインアップ
  - ログアウト
- 実装状況:
  - Bubble AIにより基本生成済み
  - `User` Data Typeに `name` を追加
  - Privacy Rulesは要強化

# Data Types

## User

| 項目名 | データ型 | 用途 |
|---|---|---|
| `email` | text | Bubble標準のログイン用メール |
| `name` | text | 画面表示用ユーザー名 |
| `Created Date` | date | 作成日時 |
| `Modified Date` | date | 更新日時 |

## Conversation

| 項目名 | データ型 | 用途 |
|---|---|---|
| `owner_user` | User | 会話の所有者 |
| `title` | text | 会話一覧・ヘッダーに表示するタイトル |
| `last_message_at` | date | 最終更新日時 |
| `last_message_text` | text | 会話一覧に表示する抜粋。現在はClaude回答を入れる方針 |
| `project` | AiProject | 使用するAIプロジェクト設定。追加済みだが本格利用は未着手 |
| `Created Date` | date | 作成日時 |
| `Modified Date` | date | 更新日時 |

## Message

| 項目名 | データ型 | 用途 |
|---|---|---|
| `content` | text | メッセージ本文 |
| `conversation` | Conversation | 所属する会話 |
| `role` | text | `user` または `assistant` |
| `api_response_id` | text | Claude APIの応答ID保存用。任意 |
| `error_message` | text | APIエラー保存用。任意 |
| `token_count` | number | token使用量保存用。任意 |
| `Created Date` | date | メッセージ順序制御 |
| `Modified Date` | date | 更新日時 |

## AiProject

| 項目名 | データ型 | 用途 |
|---|---|---|
| `name` | text | AIプロジェクト名 |
| `model` | text | 利用モデル名 |
| `system_prompt` | text | Claudeへ渡すシステムプロンプト |
| `max_tokens` | number | 最大出力トークン |
| `temperature` | number | 生成の揺らぎ |
| `is_active` | yes/no | 利用中かどうか |
| `owner_user` | User | 所有者 |
| `Created Date` | date | 作成日時 |
| `Modified Date` | date | 更新日時 |

## KnowledgeDocument

| 項目名 | データ型 | 用途 |
|---|---|---|
| `title` | text | 資料タイトル |
| `summary` | text | 資料要約 |
| `content` | text | AIに渡す本文 |
| `document_file` | file | 元資料ファイル |
| `is_active` | yes/no | Claude参照対象にするか |
| `owner_user` | User | 所有者 |
| `Created Date` | date | 作成日時 |
| `Modified Date` | date | 更新日時 |

## SearchCondition

| 項目名 | データ型 | 用途 |
|---|---|---|
| `area` | text | 希望エリア |
| `budget_min` | number | 予算下限 |
| `budget_max` | number | 予算上限 |
| `floor_plan` | text | 間取り・物件種別など |
| `station_distance` | number | 駅距離 |
| `area_size` | number | 面積 |
| `building_age` | number | 築年数 |
| `special_requirements` | text | 譲れない条件・こだわり |
| `memo` | text | メモ |
| `owner_user` | User | 所有者 |
| `Created Date` | date | 作成日時 |
| `Modified Date` | date | 更新日時 |

## PropertyRegistry / 登記物件DB案

未実装だが、謄本一覧サンプルExcelを確認した結果、追加予定のData Type。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `area_group` | text | Excel列「地域」 |
| `registry_type` | text | 種別。建物・土地・地図 |
| `pdf_url` | text | PDFリンク |
| `property_number` | text | 不動産番号 |
| `location` | text | 所在 |
| `land_number` | text | 地番 |
| `building_number` | text | 家屋番号 |
| `building_name` | text | 建物の名称 |
| `land_category` | text | 地目 |
| `building_type` | text | 建物の種類 |
| `use_category` | text | 用途分類 |
| `income_rank` | text | 収益区分 |
| `is_condo_unit` | text / yes-no | 区分建物 |
| `structure` | text | 建物の構造 |
| `floors` | number | 階数 |
| `land_area_sqm` | number | 地積 |
| `building_area_sqm` | number | 建築面積 |
| `total_floor_area_sqm` | number | 延床面積 |
| `exclusive_area_sqm` | number | 専有面積 |
| `max_area_sqm` | number | 最大面積 |
| `ownership_rank` | number | 甲区_順位 |
| `ownership_purpose` | text | 甲区_目的 |
| `ownership_date` | text | 甲区_受付日 |
| `ownership_cause` | text | 甲区_原因 |
| `owner_name` | text | 甲区_所有者 |
| `owner_address` | text | 甲区_所有者住所 |
| `mortgage_status` | text | 乙区_状態 |
| `mortgage_rank` | number | 乙区_順位 |
| `mortgage_purpose` | text | 乙区_目的 |
| `mortgage_date` | text | 乙区_受付日 |
| `mortgage_cause` | text | 乙区_原因 |
| `mortgage_amount` | text | 乙区_債権額 |
| `mortgage_holder` | text | 乙区_抵当権者 |
| `issued_date` | text / date | 発行日 |

# Workflow一覧

## Button new-conversation-btn is clicked

- トリガー: `+ 新規` ボタン押下
- 処理内容:
  - `Conversation` を新規作成
  - `title = 新規会話`
  - `owner_user = Current User`
  - `last_message_at = Current date/time`
  - `ai_chat` ページへ遷移
  - `Data to send = Result of step 1`

## Button chat-send-btn is clicked

- トリガー: チャット送信ボタン押下
- 条件: `Current page's Conversation is not empty`
- 処理内容:
  - ユーザー発言を `Message` として保存
  - Claude API `Create Message` を実行
  - Claude回答を `Message` として保存
  - `Conversation` の `last_message_text` と `last_message_at` を更新
  - 会話タイトルが `新規会話` の場合、初回ユーザー発言からタイトルを生成
  - 入力欄を安全にクリア

## Group recent-card is clicked

- トリガー: ダッシュボードの最近の会話カードクリック
- 処理内容:
  - `ai_chat` へ遷移
  - `Data to send = Current cell's Conversation`

## Button AIチャットを開く is clicked

- トリガー: ダッシュボード等のAIチャット開始ボタン
- 処理内容:
  - 新規 `Conversation` 作成
  - `ai_chat` へ遷移
  - 作成した `Conversation` を渡す

## Button conv-item delete / delete modal workflows

- トリガー: 会話一覧の削除アイコン・削除確認モーダル
- 処理内容:
  - 削除対象会話を表示
  - 確認後に削除
- 実装状況:
  - Bubble AI生成済み
  - 詳細検証は未完了

## Assistant message action buttons

- トリガー:
  - `条件として保存`
  - `提案文を作成`
  - `比較リストに追加`
- 処理内容:
  - それぞれポップアップ表示やデータ作成に接続予定
- 実装状況:
  - UIは存在
  - 本格処理は未実装または仮実装

# API連携

## Anthropic Claude API

- 用途: 顧客ヒアリング内容をもとに、売買物件探索条件の整理、確認事項抽出、営業アクション提案を行う
- Bubble Plugin: API Connector
- API名: `Anthropic Claude`
- Call名: `Create Message`
- Method: `POST`
- URL: `https://api.anthropic.com/v1/messages`
- Use as: `Action`
- Data type: `JSON`
- Headers:
  - `x-api-key`
  - `anthropic-version: 2023-06-01`
  - `content-type: application/json`
- Model:
  - 現在は `claude-sonnet-4-6`
  - 古いモデル指定では `not_found_error` が発生したため変更済み
- 主なBody Parameters:
  - `user_message`
  - `conversation_history`
- 応答取得:
  - `Result of step 2's content:first item's text`

# 実装済み機能

- Bubble AIによる初期画面生成
- Data Typesの基本作成
- `ai_chat` ページを `Conversation` ページとして設定
- 会話一覧表示
- メッセージ一覧表示
- `role = user / assistant` による表示分岐
- 新規会話作成
- 会話ページへの `Data to send`
- Claude API Connector設定
- Claude API初期化成功
- ユーザー発言保存
- Claude回答保存
- 会話履歴をClaudeへ渡す処理
- 左側会話一覧の抜粋をClaude回答に変更
- 入力欄のみ安全にクリア
- 初回発言から会話タイトルを作成
- `Reset relevant inputs` による不具合回避
- 登記Excelサンプルの列構成確認

# 未実装機能

- `AiProject.system_prompt` をClaude APIへ動的に渡す処理
- AI Project設定画面の本格運用
- Knowledge資料のClaude連携
- 登記データ `PropertyRegistry` のBubble DB作成
- Excel/CSVからの登記データ取り込み
- 登記DB検索
- 検索結果をClaudeへ渡す処理
- 条件保存機能の完成
- 提案文作成機能の完成
- 比較リスト機能の完成
- Privacy Rulesの本格設計
- 個人情報を含む登記データの権限制御
- 本番デプロイ前のセキュリティ確認
- APIキーの安全管理確認

# Bubble AIへの主要プロンプト履歴

## 初期アプリ生成プロンプト

日本語のWebアプリとして `BukkenAiSearch` を作成。目的は、不動産物件探しをAIで支援するチャット型アプリ。ユーザーが希望条件を自然文で入力し、AIが条件整理、物件検索方針、確認事項、候補比較、問い合わせ文作成を支援する。画面は派手なLPではなく、ログイン後にすぐ使うダッシュボード型UIを希望。

## 画面生成後の追加方針

- メインダッシュボード
- AIチャット
- 物件条件管理
- AIプロジェクト設定
- Knowledge資料管理
- ログイン・サインアップ
- サイドバー付き業務アプリ構成

## 文言修正

当初は賃貸物件探しのような文言が混じっていたため、売買物件・収益物件探索支援へ修正。

例:
- `問い合わせ文を作成` → `提案文を作成`
- 入力例を「自己居住用」だけでなく、売買・収益物件でも使える内容へ調整
- `比較リストに追加` を採用

# 要件変更履歴

## Claude Projects直接利用からAPI再現へ変更

当初はClaudeのProjectをAPIで直接呼び出す発想だったが、Bubble側でProject相当の設定を持ち、Claude APIへsystem prompt・履歴・資料を渡す構成に変更。

## 賃貸物件支援から売買物件・不動産営業支援へ変更

初期画面に賃貸物件探しのニュアンスがあったが、実際の目的は不動産営業担当者が売買物件・収益物件を探す支援であると整理。

## Knowledge資料から登記物件DBへ拡張

Claude Projectsのファイル相当としてKnowledge資料を想定していたが、ユーザーが保有するデータは不動産登記PDF約9千件をExcel化したものだったため、単なるKnowledge資料ではなく検索可能な登記物件DBとして扱う方針に変更。

## 会話単発処理から履歴付きチャットへ変更

初期は現在入力だけをClaudeへ渡していたが、追加質問時に過去の質問・回答が無視される問題があり、`conversation_history` を追加して会話履歴を渡す構成に変更。

## 会話タイトル・抜粋の仕様変更

左側一覧のタイトルが常に `新規会話` になっていたため、初回ユーザー発言からタイトルを生成する仕様に変更。抜粋はユーザー発言ではなくClaude回答を表示する方針に変更。

## Reset relevant inputsの扱い変更

`Reset relevant inputs` が表示クリアや意図しない状態変化を起こす可能性があったため、入力欄だけを安全にクリアする方針に変更。

# 現在のシステム仕様（最新版）

`BukkenAiSearch` は、不動産営業担当者向けのAIチャット業務アプリである。営業担当者は顧客の希望条件やヒアリング内容を自然文で入力し、Claudeが売買物件・収益物件探索に必要な条件整理、未確認事項、営業担当者が次に取るべき行動を日本語で返す。

Bubble側では、ユーザー、会話、メッセージ、AIプロジェクト設定、Knowledge資料、保存条件をData Typeとして管理する。`ai_chat` ページは `Conversation` を受け取るページとして動作し、メッセージは `Message` に保存される。Claude APIには、今回のユーザー入力だけでなく、同じ会話に紐づく過去メッセージを整形した `conversation_history` を渡す。

Claude APIの回答は `Message` として保存され、会話一覧にはタイトル、Claude回答の抜粋、最終更新日時が表示される。新規会話は必ず `Conversation` を作成してから `ai_chat` に遷移する。Conversationが存在しない状態で送信しないよう、送信Workflowには条件を設定している。

今後の中核機能は、登記PDF約9千件をExcel化したデータを `PropertyRegistry` としてDB化し、顧客条件に応じてBubble側で候補を絞り込み、その候補だけをClaudeへ渡して、比較・営業コメント・提案文作成に活用することである。Knowledge資料は営業マニュアルや評価基準などの補助資料として扱い、登記データ本体は検索可能な物件DBとして分離する。
