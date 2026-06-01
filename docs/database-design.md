# BukkenAiSearch DB設計

## 0. 設計方針

`BukkenAiSearch` のDB設計は、CRMではなく「自然言語による `PropertyRegistry` 検索セッション」を中心に設計する。

中核方針は以下のとおり。

1. 登記データ本体は `PropertyRegistry` に保持する。
2. ユーザーの自然言語検索セッションは `Conversation` に保持する。
3. 検索条件は `Conversation.current_search_condition`、`SearchCondition`、`SearchConditionItem` に保持する。
4. 検索結果全件は `Conversation` に保存しない。
5. 検索結果一覧は、現在の検索条件をもとに毎回 `PropertyRegistry` を再検索して取得する。
6. Claudeとのやり取り、検索条件解釈、分析結果は `Message` に保存する。
7. 候補として明示保存した物件のみ `CandidateProperty` に保存する。
8. 管理者による登記データ全差し替え履歴は `ImportLog` に保存する。

## 1. Data Type一覧

| Data Type | 目的 | MVP |
|---|---|---|
| `User` | 社内ログインユーザー、管理者権限、利用停止管理 | 対象 |
| `PropertyRegistry` | 登記簿由来の物件・所有者・権利関係データ | 対象 |
| `Conversation` | 自然言語検索セッション | 対象 |
| `SearchCondition` | 1つのConversationに紐づく現在検索条件セット | 対象 |
| `SearchConditionItem` | 条件チップ単位の個別検索条件 | 対象 |
| `Message` | ユーザー入力、Claude解釈、分析結果 | 対象 |
| `CandidateProperty` | 営業担当者が保存した候補物件 | 対象 |
| `ImportLog` | 管理者によるPropertyRegistry全差し替え履歴 | 対象 |
| `InvestigationNote` | 調査メモ。MVPでは簡易 | 任意 |
| `AiProject` | Claude設定。MVPでは固定設定でも可 | MVP後 |
| `KnowledgeDocument` | 補助資料。MVPでは任意 | MVP後 |

## 2. User

| Field | Type | 説明 |
|---|---|---|
| `email` | text | Bubble標準ログイン用メール |
| `name` | text | 表示名 |
| `role` | text | 営業担当者/管理者など |
| `is_admin` | yes/no | 管理者画面アクセス可否 |
| `is_active` | yes/no | 利用停止判定 |
| `company_name` | text | 所属会社 |

## 3. PropertyRegistry

`PropertyRegistry` は自然言語検索対象となる中核Data Typeである。

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
| `ownership_rank` | number | 甲区順位 |
| `ownership_purpose` | text | 甲区目的 |
| `ownership_date` | text | 甲区受付日 |
| `ownership_cause` | text | 甲区原因 |
| `mortgage_status` | text | 乙区状態 |
| `has_mortgage` | yes/no | 抵当権有無 |
| `mortgage_rank` | number | 乙区順位 |
| `mortgage_purpose` | text | 乙区目的 |
| `mortgage_date` | text | 乙区受付日 |
| `mortgage_cause` | text | 乙区原因 |
| `mortgage_amount` | text | 債権額 |
| `mortgage_holder` | text | 抵当権者 |
| `issued_date` | text/date | 発行日 |

## 4. Conversation

`Conversation` は自然言語検索セッション本体である。検索結果全件は保持せず、現在条件と表示設定のみ保持する。

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

保持しないField:

| Field | 理由 |
|---|---|
| `current_search_results` | 検索結果全件を保存するとデータ量・鮮度・権限制御が複雑になるため。表示時に `PropertyRegistry` を再検索する |

## 5. SearchCondition

| Field | Type | 説明 |
|---|---|---|
| `owner_user` | User | 作成者 |
| `conversation` | Conversation | 紐づく検索セッション |
| `title` | text | 条件名 |
| `natural_language_query` | text | 初回検索文 |
| `current_condition_summary` | text | 現在条件の日本語要約 |
| `structured_query_json` | text | 現在条件JSON |
| `condition_history_json` | text | 追加・削除・更新履歴 |
| `last_refinement_text` | text | 最後の追加条件文 |
| `result_count` | number | 現在条件のヒット件数 |
| `display_fields` | list of text | この条件で表示する列 |
| `sort_instruction` | text | 並び替え・優先順位付け指示 |
| `memo` | text | 補足 |

## 6. SearchConditionItem

| Field | Type | 説明 |
|---|---|---|
| `search_condition` | SearchCondition | 親条件 |
| `field_name` | text | `PropertyRegistry` の対象Field |
| `operator` | text | contains / equals / in / is_empty / greater_or_equal など |
| `value_text` | text | テキスト値 |
| `value_number` | number | 数値条件 |
| `value_list_text` | list of text | 複数値条件 |
| `source_text` | text | 条件を生成した自然文 |
| `label` | text | 条件チップ表示名 |
| `is_active` | yes/no | 有効/無効 |
| `order_index` | number | 表示順 |
| `created_by_ai` | yes/no | Claude生成条件かどうか |

## 7. Message

| Field | Type | 説明 |
|---|---|---|
| `conversation` | Conversation | 所属Conversation |
| `role` | text | user / assistant |
| `content` | text | メッセージ本文 |
| `intent_type` | text | initial_search / refine_search / show_fields / analyze_results |
| `parsed_conditions_json` | text | Claudeが返した条件JSON |
| `search_result_count` | number | 処理後のヒット件数 |
| `referenced_properties` | list of PropertyRegistry | 分析に使った物件。必要最小限のみ |
| `api_response_id` | text | Claude API応答ID |
| `error_message` | text | APIエラー |
| `token_count` | number | token使用量 |

## 8. CandidateProperty

| Field | Type | 説明 |
|---|---|---|
| `owner_user` | User | 作成者 |
| `conversation` | Conversation | 保存元Conversation |
| `property` | PropertyRegistry | 候補物件 |
| `search_condition` | SearchCondition | 保存時の検索条件 |
| `priority` | number | 優先度 |
| `reason` | text | 候補保存理由 |
| `ai_summary` | text | Claude要約 |
| `next_research` | text | 次調査項目 |
| `status` | text | 未調査/調査中/有望/除外など |
| `memo` | text | メモ |

## 9. ImportLog

| Field | Type | 説明 |
|---|---|---|
| `uploaded_file` | file | アップロードExcel/CSV |
| `imported_count` | number | 登録件数 |
| `error_count` | number | エラー件数 |
| `executed_by` | User | 実行管理者 |
| `executed_at` | date | 実行日時 |
| `status` | text | running / completed / failed |
| `memo` | text | エラー内容・補足 |

## 10. Relation整理

| From | Field | To | 関係 |
|---|---|---|---|
| `Conversation` | `owner_user` | `User` | 多対1 |
| `Conversation` | `current_search_condition` | `SearchCondition` | 1対1 |
| `SearchCondition` | `conversation` | `Conversation` | 1対1 |
| `SearchConditionItem` | `search_condition` | `SearchCondition` | 多対1 |
| `Message` | `conversation` | `Conversation` | 多対1 |
| `CandidateProperty` | `conversation` | `Conversation` | 多対1 |
| `CandidateProperty` | `property` | `PropertyRegistry` | 多対1 |
| `CandidateProperty` | `search_condition` | `SearchCondition` | 多対1 |
| `ImportLog` | `executed_by` | `User` | 多対1 |

## 11. 検索結果の扱い

`PropertyRegistry` 検索結果は保存対象ではなく表示対象である。

| 項目 | 方針 |
|---|---|
| 初回検索結果 | `SearchConditionItem` を条件に `PropertyRegistry` を検索して表示 |
| 追加絞り込み後の結果 | 条件更新後に `PropertyRegistry` を再検索して表示 |
| Conversationへの保存 | 検索結果全件は保存しない |
| 保存する情報 | 検索条件、条件履歴、表示列、ヒット件数、Message |
| 候補保存 | ユーザーが明示保存した物件のみ `CandidateProperty` に保存 |
