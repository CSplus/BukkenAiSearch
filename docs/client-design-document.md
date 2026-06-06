# BukkenAiSearch クライアント提示用設計書

| 項目 | 内容 |
|---|---|
| 文書名 | BukkenAiSearch クライアント提示用設計書 |
| 対象システム | 不動産営業向けAI自然言語物件検索支援システム |
| 作成日 | 2026年6月6日 |
| 開発基盤 | Bubble.io |
| 対象フェーズ | MVP設計・Bubble AI生成後のIssues修正フェーズ |

## 1. 要件確認

### 1.1 システムの目的

`BukkenAiSearch` は、不動産会社の営業担当者が顧客ヒアリング内容を自然文で入力し、登記データ由来の物件データベース `PropertyRegistry` を検索・絞り込み・比較し、候補物件の保存やAI分析を行うための営業支援システムである。

本システムはCRMではなく、登記データを検索可能な物件DBとして扱い、自然言語検索セッションを中心に営業活動を支援する。

### 1.2 想定ユーザー

| ユーザー | 主な利用目的 |
|---|---|
| 営業担当者 | 顧客条件の入力、物件検索、候補保存、AI分析依頼、提案準備 |
| 管理者 | ユーザー管理、登記データのCSV/Excel取り込み、インポート履歴確認 |

### 1.3 業務上の前提

- 対象は賃貸物件探しではなく、売買物件・収益物件の探索支援である。
- 登記PDF由来のExcel/CSVデータを `PropertyRegistry` としてDB化する。
- ユーザーは自然文で条件を入力し、AIが条件整理・不足項目・次アクションを返す。
- 検索結果全件は会話データへ保存せず、画面表示時に `PropertyRegistry` を都度検索する。
- 候補として明示保存した物件のみ `CandidateProperty` として保存する。

### 1.4 MVP対象範囲

| 分類 | MVPで実装する内容 |
|---|---|
| 認証 | ログイン、ログアウト。サインアップ導線は作らない |
| ダッシュボード | 最近の会話、候補、検索開始導線 |
| AI検索 | 自然言語入力、条件表示、物件検索結果表示、会話表示、候補保存 |
| 物件詳細 | 登記情報、所有者情報、権利関係、PDFリンク等の確認 |
| 候補一覧 | 保存済み候補物件の一覧・状態確認 |
| 管理 | PropertyRegistryのCSV/Excel取り込み、ImportLog管理 |

### 1.5 MVP対象外

| 対象外項目 | 理由 |
|---|---|
| CRM機能 | 顧客管理ではなく物件探索支援に集中するため |
| signup画面 | 社内ユーザー前提のため、管理者登録を想定する |
| property_searchページ | 検索機能は `ai_search` に統合するため |
| search_conditionsページ | 条件管理は `ai_search` 内のConversation/SearchConditionで扱うため |
| Conversation.current_search_results | 検索結果全件保存はデータ量・鮮度・権限制御の観点で避けるため |

### 1.6 現在の実装状況

Bubble AI App Generatorにより、以下のMVP主要ページは生成済みである。

- `login`
- `index`
- `ai_search`
- `property_detail`
- `candidate_properties`
- `admin`

現在は、生成済みアプリのIssues修正フェーズであり、特に `ai_search` のRepeating Group、`PropertyRegistry` 参照、`CandidateProperty` 保存、`Message` 作成Workflowを優先して修正する。

## 2. DB設計

### 2.1 DB設計方針

DBは、自然言語による物件検索セッションを中心に設計する。

1. 登記データ本体は `PropertyRegistry` に保持する。
2. 検索セッションは `Conversation` に保持する。
3. 検索条件は `SearchCondition` と `SearchConditionItem` に保持する。
4. 会話・AI応答・分析結果は `Message` に保持する。
5. 候補として保存した物件のみ `CandidateProperty` に保持する。
6. 検索結果全件は保存せず、必要時に `PropertyRegistry` を再検索する。

### 2.2 Data Type一覧

| Data Type | 目的 | MVP対象 |
|---|---|---|
| `User` | 社内ユーザー、管理者権限、利用停止管理 | 対象 |
| `PropertyRegistry` | 登記簿由来の物件・所有者・権利関係データ | 対象 |
| `Conversation` | 自然言語検索セッション | 対象 |
| `SearchCondition` | 1つのConversationに紐づく現在検索条件セット | 対象 |
| `SearchConditionItem` | 条件チップ単位の個別検索条件 | 対象 |
| `Message` | ユーザー入力、AI解釈、分析結果 | 対象 |
| `CandidateProperty` | 営業担当者が保存した候補物件 | 対象 |
| `ImportLog` | 管理者によるPropertyRegistry全差し替え履歴 | 対象 |

### 2.3 User

| Field | Type | 説明 |
|---|---|---|
| `email` | text | Bubble標準ログイン用メール |
| `name` | text | 表示名 |
| `role` | text | 営業担当者/管理者など |
| `is_admin` | yes/no | 管理者画面アクセス可否 |
| `is_active` | yes/no | 利用停止判定 |
| `company_name` | text | 所属会社 |

### 2.4 PropertyRegistry

`PropertyRegistry` は本システムの中核検索対象である。

| Field | Type | 説明 |
|---|---|---|
| `area_group` | text | 地域 |
| `registry_type` | text | 土地/建物/区分建物など |
| `pdf_url` | text | 登記PDFリンク |
| `property_number` | text | 不動産番号 |
| `location` | text | 所在 |
| `land_number` | text | 地番 |
| `building_number` | text | 家屋番号 |
| `building_name` | text | 建物名 |
| `land_category` | text | 地目 |
| `building_type` | text | 建物種類 |
| `use_category` | text | 用途分類 |
| `income_rank` | text | 収益区分 |
| `land_area_sqm` | number | 土地面積 |
| `building_area_sqm` | number | 建物面積 |
| `total_floor_area_sqm` | number | 延床面積 |
| `exclusive_area_sqm` | number | 専有面積 |
| `max_area_sqm` | number | 検索用最大面積 |
| `owner_name` | text | 所有者名 |
| `owner_address` | text | 所有者住所 |
| `owner_type` | text | 法人所有/個人所有など |
| `mortgage_status` | text | 乙区状態 |
| `has_mortgage` | yes/no | 抵当権有無 |
| `mortgage_amount` | text | 債権額 |
| `mortgage_holder` | text | 抵当権者 |
| `issued_date` | text/date | 発行日 |

### 2.5 Conversation

| Field | Type | 説明 |
|---|---|---|
| `owner_user` | User | セッション所有者 |
| `title` | text | セッションタイトル |
| `current_search_condition` | SearchCondition | 現在の検索条件 |
| `current_result_count` | number | 現在条件のヒット件数 |
| `current_display_fields` | list of text | 検索結果一覧に表示する列 |
| `target_property` | PropertyRegistry | 詳細画面から戻る場合などの主対象物件 |
| `related_properties` | list of PropertyRegistry | 分析対象にした関連物件 |
| `last_message_text` | text | 一覧表示用抜粋 |
| `last_message_at` | date | 最終更新日時 |
| `status` | text | active / archived など |

### 2.6 SearchCondition / SearchConditionItem

| Data Type | Field | Type | 説明 |
|---|---|---|---|
| `SearchCondition` | `owner_user` | User | 作成者 |
| `SearchCondition` | `conversation` | Conversation | 紐づく検索セッション |
| `SearchCondition` | `title` | text | 条件名 |
| `SearchCondition` | `natural_language_query` | text | 初回検索文 |
| `SearchCondition` | `summary` | text | 現在条件の日本語要約 |
| `SearchConditionItem` | `search_condition` | SearchCondition | 親条件 |
| `SearchConditionItem` | `field` | text | PropertyRegistryの検索対象Field |
| `SearchConditionItem` | `operator` | text | contains / equals / greater_or_equal 等 |
| `SearchConditionItem` | `value` | text | テキスト条件値 |
| `SearchConditionItem` | `is_active` | yes/no | 有効/無効 |
| `SearchConditionItem` | `label` | text | 条件チップ表示名 |

Bubble AIが生成したField名を正として使い、正式設計名と異なる場合でも重複Fieldは作らない。

### 2.7 Message

| Field | Type | 説明 |
|---|---|---|
| `conversation` | Conversation | 所属Conversation |
| `role` | text | user / assistant |
| `content` | text | メッセージ本文 |
| `intent_type` | text | initial_search / refine_search / show_fields / analyze_results |
| `parsed_conditions_json` | text | AIが返した条件JSON |
| `search_result_count` | number | 処理後のヒット件数 |
| `referenced_properties` | list of PropertyRegistry | 分析に使った物件 |
| `api_response_id` | text | API応答ID |
| `error_message` | text | APIエラー |

### 2.8 CandidateProperty

| Field | Type | 説明 |
|---|---|---|
| `user` | User | 作成者。正式設計の `owner_user` 相当 |
| `conversation` | Conversation | 保存元Conversation |
| `property_registry` | PropertyRegistry | 候補物件。正式設計の `property` 相当 |
| `search_condition` | SearchCondition | 保存時の検索条件 |
| `priority` | number | 優先度 |
| `reason` | text | 候補保存理由 |
| `ai_summary` | text | AI要約 |
| `next_research` | text | 次調査項目 |
| `status` | text | 未調査/調査中/有望/除外など |
| `memo` | text | メモ |

### 2.9 ImportLog

| Field | Type | 説明 |
|---|---|---|
| `uploaded_file` | file | アップロードExcel/CSV |
| `imported_count` | number | 登録件数 |
| `error_count` | number | エラー件数 |
| `imported_by_user` | User | 実行管理者。正式設計の `executed_by` 相当 |
| `executed_at` | date | 実行日時 |
| `status` | text | running / completed / failed |
| `error_detail` | text | エラー内容・補足 |

### 2.10 主なリレーション

| From | Field | To | 関係 |
|---|---|---|---|
| `Conversation` | `owner_user` | `User` | 多対1 |
| `Conversation` | `current_search_condition` | `SearchCondition` | 1対1 |
| `SearchCondition` | `conversation` | `Conversation` | 1対1 |
| `SearchConditionItem` | `search_condition` | `SearchCondition` | 多対1 |
| `Message` | `conversation` | `Conversation` | 多対1 |
| `CandidateProperty` | `conversation` | `Conversation` | 多対1 |
| `CandidateProperty` | `property_registry` | `PropertyRegistry` | 多対1 |
| `CandidateProperty` | `search_condition` | `SearchCondition` | 多対1 |
| `ImportLog` | `imported_by_user` | `User` | 多対1 |

## 3. API設計

### 3.1 API設計方針

AI連携は、Bubble側で会話・条件・検索対象物件を管理し、必要な文脈のみをAI APIへ渡す構成とする。

- 会話履歴は `Message` から取得する。
- 現在条件は `Conversation.current_search_condition` と `SearchConditionItem` から取得する。
- 検索結果全件は保存せず、AI分析時に必要な件数のみ整形して渡す。
- APIキーはクライアント側に露出しないよう、BubbleのAPI Connector/Backend Workflow側で管理する。

### 3.2 Claude API連携

| 項目 | 内容 |
|---|---|
| API種別 | Claude API |
| 主な用途 | 条件解釈、検索条件JSON生成、検索結果分析、提案文作成 |
| 送信元 | Bubble Workflow / API Connector |
| 保存先 | AI回答は `Message` に保存 |

### 3.3 自然言語検索API payload案

| 項目 | 内容 |
|---|---|
| `conversation_id` | 対象Conversation ID |
| `user_message` | ユーザーが入力した自然文 |
| `conversation_history` | 同一ConversationのMessage履歴 |
| `current_condition_summary` | 現在条件の要約 |
| `active_conditions` | 有効なSearchConditionItem一覧 |
| `visible_results_summary` | 画面に表示中または上位N件のPropertyRegistry概要 |

### 3.4 AI応答形式案

AIからは、Bubble Workflowで扱いやすいJSON形式で受け取る。

| 項目 | 内容 |
|---|---|
| `intent_type` | initial_search / refine_search / show_fields / analyze_results |
| `condition_summary` | 日本語の条件要約 |
| `conditions` | SearchConditionItem化する条件配列 |
| `display_fields` | 表示列変更がある場合のField一覧 |
| `assistant_message` | ユーザーへ表示するAI回答 |
| `recommended_actions` | 次に確認すべき営業アクション |

### 3.5 インポートAPI/Workflow方針

CSV/Excelからの `PropertyRegistry` 登録は、管理者画面のアップロードWorkflowで行う。

1. 管理者がCSV/Excelをアップロードする。
2. インポート開始時に `ImportLog` を作成する。
3. 既存 `PropertyRegistry` を全削除する。
4. アップロードデータを新しい `PropertyRegistry` として登録する。
5. 登録件数・エラー件数・ステータスを `ImportLog` に保存する。

## 4. 画面設計

### 4.1 画面一覧

| 画面 | 目的 | MVP対象 |
|---|---|---|
| `login` | 社内ユーザー認証 | 対象 |
| `index` | ダッシュボード、検索開始導線、最近の会話・候補表示 | 対象 |
| `ai_search` | 自然言語検索、条件表示、検索結果、会話、候補保存を統合 | 対象 |
| `property_detail` | 物件詳細・登記情報確認 | 対象 |
| `candidate_properties` | 保存済み候補物件一覧 | 対象 |
| `admin` | 物件データ取り込み、インポート履歴確認 | 対象 |

### 4.2 login

| 要素 | 内容 |
|---|---|
| メール入力 | 社内ユーザーのメールアドレス |
| パスワード入力 | ログインパスワード |
| ログインボタン | 認証成功後 `index` へ遷移 |
| パスワード再設定 | `reset_pw` へ遷移 |

### 4.3 index

| エリア | 内容 |
|---|---|
| 統計カード | 登録物件数、最近の候補数、検索セッション数など |
| 最近のConversation | 直近の検索セッション一覧 |
| 最近の候補 | 保存済みCandidatePropertyの一部表示 |
| 新規検索ボタン | 新規Conversationを作成し `ai_search` へ遷移 |

### 4.4 ai_search

`ai_search` はMVPの中心画面である。

| エリア | UI要素 | 内容 |
|---|---|---|
| 左サイド | Conversation一覧 | 自分の検索セッションを表示 |
| 中央上部 | セッションタイトル | 現在のConversationタイトル |
| 中央上部 | 条件要約 | 現在のSearchCondition summary |
| 中央上部 | 条件チップ | 有効なSearchConditionItem一覧 |
| 中央 | RG property_results | 現在条件で検索したPropertyRegistry一覧 |
| 結果セル | 詳細ボタン | `property_detail` へ遷移 |
| 結果セル | 候補保存ボタン | CandidatePropertyを作成 |
| 結果セル | 分析ボタン | 選択物件の分析Messageを作成 |
| 下部 | Message一覧 | ユーザー入力・AI回答を時系列表示 |
| 下部 | 自然言語入力 | 顧客条件や分析依頼を入力 |

`ai_search` のPage Typeは `Conversation` とし、すべての遷移元から `Data to send = 対象Conversation` を渡す。

### 4.5 property_detail

| エリア | 内容 |
|---|---|
| 基本情報 | 所在、建物名、用途、面積、不動産番号 |
| 所有者情報 | 所有者名、住所、所有者種別 |
| 権利情報 | 甲区、乙区、抵当権有無、債権額、抵当権者 |
| PDFリンク | 登記PDFの参照 |
| アクション | AI検索へ戻る、候補保存、現在Conversationで分析 |

### 4.6 candidate_properties

| エリア | 内容 |
|---|---|
| フィルター | ステータス別絞り込み |
| 候補一覧 | CandidateProperty一覧 |
| セル表示 | 建物名、所在地、所有者、ステータス、優先度、次調査項目 |
| アクション | 詳細表示、関連Conversationを開く、候補削除 |

### 4.7 admin

| エリア | 内容 |
|---|---|
| ファイルアップロード | PropertyRegistry登録用CSV/Excel |
| インポート実行 | 全差し替え更新の実行 |
| ImportLog一覧 | 実行日時、実行者、件数、エラー内容、ステータス表示 |

## 5. Workflow設計

### 5.1 ログインWorkflow

1. ユーザーがメールアドレス・パスワードを入力する。
2. Bubble標準認証でログインする。
3. 認証成功後、`index` へ遷移する。
4. 利用停止ユーザーの場合はアクセスを制御する。

### 5.2 新規検索セッション作成Workflow

1. `Conversation` を新規作成する。
2. `owner_user = Current User` を設定する。
3. 初期タイトルを設定する。
4. `current_result_count = 0` を設定する。
5. 必要に応じて空の `SearchCondition` を作成し、Conversationへ紐づける。
6. `ai_search` へ遷移し、作成したConversationを `Data to send` で渡す。

### 5.3 自然言語検索Message送信Workflow

1. ユーザーが自然文を入力する。
2. `Message` を作成し、`conversation = Current page Conversation`、`role = user`、`content = 入力文` を保存する。
3. 現在のSearchCondition、SearchConditionItem、会話履歴を取得する。
4. AI APIへ自然文と現在文脈を送信する。
5. AI応答の `intent_type` に応じてSearchCondition/SearchConditionItemを作成・更新する。
6. 更新後の条件で `PropertyRegistry` を再検索する。
7. ヒット件数を `Conversation.current_result_count`、`SearchCondition.result_count`、`Message.search_result_count` に保存する。
8. AI回答を `Message` として保存する。
9. `Conversation.last_message_text` と `last_message_at` を更新する。

### 5.4 検索結果表示Workflow

1. `RG property_results` は `PropertyRegistry` 型で構成する。
2. Data sourceは `Search for PropertyRegistries` とする。
3. 条件変換実装後、有効なSearchConditionItemに基づく制約を追加する。
4. 検索結果全件はConversationへ保存しない。
5. 結果セル内は `Parent group's PropertyRegistry` を参照して所在地、建物名、所有者、用途、面積、抵当権情報を表示する。

### 5.5 候補保存Workflow

1. ユーザーが `ai_search` または `property_detail` で候補保存ボタンを押す。
2. `CandidateProperty` を作成する。
3. `property_registry = Parent group's PropertyRegistry` または `Current page PropertyRegistry` を設定する。
4. `user = Current User` を設定する。
5. `conversation = Current page Conversation` を設定する。
6. `status = 未調査` を設定する。
7. 必要に応じて重複保存を防止する。

### 5.6 選択物件AI分析Workflow

1. ユーザーが検索結果セルの分析ボタンを押す。
2. `Message` を作成し、`conversation = Current page Conversation` を必ず設定する。
3. `role = user`、`intent_type = analyze_results`、`content = この物件を分析して` を保存する。
4. 将来API接続後、選択物件の所在地・所有者・用途・面積・抵当権情報をAIへ送信する。
5. AI回答を `Message` として保存する。

### 5.7 物件詳細Workflow

1. ユーザーが検索結果の詳細ボタンを押す。
2. `property_detail` へ遷移する。
3. `Data to send = Parent group's PropertyRegistry` を設定する。
4. 必要に応じてConversation IDをURL parameter等で渡す。
5. 詳細画面からAI検索へ戻る場合は、既存Conversationを優先して `ai_search` へ戻す。

### 5.8 管理者インポートWorkflow

1. 管理者がCSV/Excelをアップロードする。
2. `ImportLog` を作成し、`status = running` を設定する。
3. 既存 `PropertyRegistry` を削除する。
4. アップロードデータを新規 `PropertyRegistry` として登録する。
5. 登録件数、エラー件数、エラー詳細を保存する。
6. 完了時に `ImportLog.status = completed`、失敗時に `failed` を設定する。

## 6. セキュリティ・運用設計

### 6.1 アクセス制御

- `Conversation`、`Message`、`SearchCondition`、`SearchConditionItem`、`CandidateProperty` は原則として作成者本人のデータのみ閲覧・編集できる。
- 管理者は `admin` 画面にアクセスできる。
- `PropertyRegistry` は営業担当者の検索対象として閲覧可能とするが、本番運用前にPrivacy Rulesを検証する。
- APIキーはクライアント側へ露出しない。

### 6.2 データ管理

- 登記データはCSV/Excelから全差し替え更新する。
- 更新履歴は `ImportLog` に保存する。
- 検索結果全件は保存せず、保存対象は検索条件・会話・明示保存された候補物件に限定する。

### 6.3 エラー対応

| エラー | 対応 |
|---|---|
| AI API失敗 | `Message.error_message` に保存し、画面に通知する |
| インポート失敗 | `ImportLog.error_detail` に保存し、管理者画面に表示する |
| Conversation未設定 | ai_search遷移時に必ずData to sendを渡す設計で防止する |
| CandidatePropertyの物件未設定 | 結果セル内で `Parent group's PropertyRegistry` を使う設計で防止する |

## 7. 現在の優先修正事項

Bubble AI生成後のIssues修正では、以下を優先する。

1. `ai_search` Page Typeを `Conversation` にする。
2. すべての `ai_search` 遷移でConversationを渡す。
3. `RG property_results` を `PropertyRegistry` 型にする。
4. 結果セル内の参照を `Parent group's PropertyRegistry` に統一する。
5. number型・yes/no型をText表示する場合は `:formatted as text` を使う。
6. `CandidateProperty` 作成時に `property_registry`、`user`、`conversation` を必ず設定する。
7. `Message` 作成時に `conversation = Current page Conversation` を必ず設定する。

## 8. 今後の実装ステップ

| 優先度 | 内容 |
|---|---|
| 1 | `ai_search` の型・参照・Workflow Issues修正 |
| 2 | SearchConditionItemからPropertyRegistry検索条件への変換実装 |
| 3 | Claude API Connector設定 |
| 4 | 自然言語からSearchConditionItem生成Workflow |
| 5 | CSV/ExcelインポートWorkflowの安定化 |
| 6 | Privacy Rules設計・検証 |
| 7 | 管理者向けインポート確認UX改善 |

## 9. まとめ

`BukkenAiSearch` は、Bubble.io上で構築する不動産営業向けのAI自然言語物件検索支援システムである。MVPでは、`ai_search` を中心に自然言語入力、検索条件管理、`PropertyRegistry` 検索、候補保存、AI分析の流れを1画面に統合する。

システム設計上の最重要ポイントは、検索結果全件をConversationへ保存せず、検索条件のみを保存して `PropertyRegistry` を都度再検索することである。これにより、データ鮮度、権限制御、処理負荷のバランスを保ちつつ、営業担当者が候補物件を効率的に発見・保存・分析できる構成とする。
