# BukkenAiSearch 要件定義

## システム概要
> 本要件定義は、全体像整理案を正式採用した版である。
> `BukkenAiSearch` はCRMではなく、自然言語で登記データベース `PropertyRegistry` を検索・絞り込みするためのAI支援システムとして設計する。

`BukkenAiSearch` は、不動産会社の営業担当者が顧客ヒアリング内容を入力し、売買物件・収益物件の探索条件整理、確認事項抽出、候補物件比較、提案文作成を支援するAIチャット型Webアプリである。
## 0. 要件サマリー

従来の賃貸店舗向け物件検索ではなく、売買物件・収益物件を扱う不動産営業支援システムとして設計する。
本ドキュメントは、`BukkenAiSearch` の正式な要件定義として、自然言語による対話型 `PropertyRegistry` 検索システムを実装するための前提、データ構造、API、画面、Workflow、MVP範囲を整理する。

## 想定ユーザー
採用する基本方針は以下のとおり。

1. CRMではなく、自然言語による対話型登記DB検索システムとして定義する
2. 中核目的は、営業担当者がClaudeへ自然文で検索指示を行い、`PropertyRegistry` を検索・追加絞り込みできることとする
3. Claudeの主な役割は、自然文を `PropertyRegistry` の検索条件に変換し、既存条件へ追加・削除・更新することである
4. `PropertyRegistry` を中核データとし、検索結果を会話の文脈として保持する
5. 必要に応じてClaudeが検索結果を要約・比較・優先順位付けする
6. 顧客管理・商談管理・追客管理・契約管理は主目的にしない
7. MVPは、自然言語検索セッション、`PropertyRegistry` 最小版、検索結果表示、追加絞り込み、候補物件保存、管理者画面までとする

Bubble実装では、要件確認、DB設計、API設計、画面設計、Workflow設計の順で具体化する。

## 1. システム概要

`BukkenAiSearch` は、不動産営業担当者がClaudeへ自然文で検索指示を行い、登記データベース `PropertyRegistry` を検索・追加絞り込み・再検索できるAI支援型の登記DB検索システムである。

本システムはCRMではなく、SQLや複雑な検索フォームを使わずに、自然言語で `PropertyRegistry` を検索できる対話型検索アプリとして設計する。

主目的は、営業担当者が以下を効率的に行えるようにすることである。

- 自然文で `PropertyRegistry` を検索する
- 前回検索結果に対して追加条件を自然文で指定し、既存条件に追加して再検索する
- 検索条件と検索結果を会話型検索セッションとして保持する
- 検索結果から所有者、土地、建物、収益区分、抵当権などを確認する
- 必要に応じて検索結果をClaudeに要約・比較・優先順位付けさせる
- 有望な検索結果を候補物件として保存する

## 2. CRMではないことの定義

`BukkenAiSearch` は、一般的なCRMのように顧客・商談・追客・契約を中心に管理するシステムではない。

### 主目的にしないこと

- 顧客管理
- 商談ステータス管理
- 追客管理
- 架電履歴管理
- メール配信管理
- 契約管理
- 営業担当者の活動KPI管理
- 顧客とのやり取りの一元管理

これらは将来的に外部CRM等と連携する可能性はあるが、少なくとも本システムの中核機能・MVP範囲には含めない。

## 3. 想定ユーザー

### 3.1 メインユーザー

- 不動産会社の営業担当者
- 営業管理者
- 物件情報・登記データを管理する社内担当者

## 主な利用シーン
### 3.2 補助ユーザー

1. 営業担当者が顧客から希望条件をヒアリングする
2. ヒアリング内容を自然文でAIチャットに入力する
3. AIが条件整理、不足情報、確認事項、次の営業アクションを提示する
4. 必要に応じて条件を保存し、候補物件の検索・比較・提案文作成に利用する
5. 将来的には登記物件DBから候補を抽出し、AI回答に連携する
- 営業管理者
- 登記情報・物件情報を整備する社内担当者

## 開発環境・主要サービス
## 4. 開発環境・主要サービス

- Bubble.io
- Anthropic Claude API
- GitHub
- Codex

## 主要機能
## 5. システムの基本構成

本システムでは、Bubble側で `PropertyRegistry`、検索セッション、検索条件、検索結果、候補物件、AI設定を管理し、Claude APIには自然文の検索意図解析と検索結果分析に必要な文脈を渡す。

```text
営業担当者の自然文検索指示
        ↓
Claudeが検索意図を解析し、PropertyRegistry検索条件へ変換
        ↓
BubbleがPropertyRegistryを検索
        ↓
検索結果をConversation / SearchConditionの文脈として保持
        ↓
営業担当者が追加条件を自然文で指定
        ↓
Claudeが既存条件に追加・削除・更新して再検索
        ↓
必要に応じてClaudeが結果を要約・比較・優先順位付け
```

登記データ本体はKnowledge資料ではなく、検索可能な構造化DBである `PropertyRegistry` として扱う。AIチャットと `PropertyRegistry` 検索は分離せず、同一の `Conversation` に検索指示、検索条件、検索結果、分析結果を保持する。

## 6. ユーザーの利用シナリオ

### 6.1 自然文で初回検索する

営業担当者が、検索フォームではなく自然文で `PropertyRegistry` を検索する。

例:

| 自然文 | Claudeが解釈する検索条件 |
|---|---|
| 「〇〇さんの土地と建物を探して」 | `owner_name contains 〇〇`、`registry_type in 土地, 建物` |
| 「中区で収益物件を一覧表示して」 | `location contains 中区`、`income_rank = 収益物件` |
| 「抵当権がある物件を出して」 | `mortgage_status is not empty` または `has_mortgage = yes` |

### 6.2 前回検索結果に追加条件を与えて絞り込む

営業担当者は、検索結果を見ながら追加条件を自然文で指定する。

例:

| 追加自然文 | 追加される条件 |
|---|---|
| 「その中で100坪以上に絞って」 | 既存条件 + 面積条件 |
| 「抵当権があるものを除外して」 | 既存条件 + `mortgage_status is empty` |
| 「法人所有だけにして」 | 既存条件 + `owner_type = 法人所有` |
| 「所有者を表示して」 | 現在の検索結果に `owner_name` / `owner_address` を表示 |

### 6.3 検索条件と検索結果を会話文脈として保持する

1つの検索セッションは `Conversation` として管理し、初回検索条件、追加絞り込み条件、検索結果、Claudeの解釈結果を保持する。

- 初回検索: `SearchCondition` を作成
- 追加絞り込み: 既存 `SearchCondition` に条件を追加・更新
- 検索結果: `Conversation.current_search_results` または関連フィールドに保持
- ユーザー自然文とClaude解釈: `Message` として保存

### 6.4 検索結果を分析する

検索結果が表示された後、営業担当者は必要に応じてClaudeへ分析を依頼する。

例:

| 自然文 | Claudeの処理 |
|---|---|
| 「この中で有望そうな順に並べて」 | 現在の検索結果を要約し、優先順位を提示 |
| 「所有者ごとにまとめて」 | 検索結果を `owner_name` ごとにグルーピング |
| 「土地と建物が同じ所有者のものを優先して」 | 検索結果を比較し、条件に合う候補を抽出 |

### 6.5 候補物件として保存する

検索結果やClaudeの分析結果を見て、有望な物件を `CandidateProperty` として保存する。

## 7. Claudeの役割

### AIチャット営業支援
Claudeは営業相談の相手である以前に、自然文を `PropertyRegistry` の検索条件へ変換し、検索セッションを前進させる検索アシスタントとして位置づける。

顧客ヒアリング内容を自然文で入力し、AIが営業支援回答を返す。
### 7.1 Claudeが優先して行うこと

| 役割 | 内容 |
|---|---|
| 自然文検索条件変換 | ユーザーの自然文を `PropertyRegistry` の検索条件JSONへ変換する |
| 追加絞り込み解釈 | 前回条件に対する「その中で」「さらに」などの追加条件を解釈する |
| 条件マージ | 既存 `SearchCondition` に追加・削除・更新条件を反映する |
| 条件説明 | 現在の検索条件を営業担当者に分かる日本語で説明する |
| 表示項目制御 | 「所有者を表示して」など、検索結果表示に必要な列を判断する |
| 結果分析 | 必要に応じて検索結果を要約・比較・優先順位付けする |
| 曖昧条件確認 | 条件が曖昧な場合、検索前に確認質問を返す |

### 7.2 Claudeが補助的に行うこと

- 検索結果から所有者や権利関係の注意点を要約する
- 複数物件の比較観点を整理する
- 有望そうな候補を理由付きで提示する
- 次に調べるべき事項を提案する

### 7.3 Claudeが行わないこと

Claudeは以下を最終判断しない。

- 法的判断の確定
- 権利関係の法的保証
- 不動産価格の確定評価
- 売却可否の断定
- 所有者の意思の推定
- 個人情報の不適切な利用判断
- CRM上の商談管理

### 7.4 BubbleとClaudeの役割分担

| 領域 | Bubbleの役割 | Claudeの役割 |
|---|---|---|
| 自然言語検索 | 検索セッション、条件、結果を保存する | 自然文を検索条件へ変換する |
| 条件マージ | `SearchCondition` を更新する | 追加・削除・更新すべき条件を返す |
| DB検索 | `PropertyRegistry` を実際に検索する | 検索条件JSONを生成する |
| 検索結果表示 | Repeating Groupに結果を表示する | 表示項目や分析観点を提案する |
| 結果分析 | 分析対象の結果をClaudeへ渡す | 要約・比較・優先順位付けする |
| セキュリティ | Privacy Rules/APIキー管理を行う | 渡された情報の範囲で回答する |

## 8. 主要機能

### 8.1 自然言語PropertyRegistry検索

営業担当者が自然文で検索指示を行い、Claudeが検索条件に変換し、Bubbleが `PropertyRegistry` を検索する。

主な出力内容:

- 顧客希望条件の整理
- 不足している確認事項
- 売買物件・収益物件探索の方針
- 候補物件比較時の観点
- 営業担当者が次に取るべきアクション
- 顧客向け提案文のたたき台
- 自然文から変換した検索条件
- 既存条件へ追加・削除・更新した絞り込み条件
- 現在の検索条件の日本語要約
- `PropertyRegistry` 検索結果
- 検索結果に表示すべき項目
- 必要に応じた検索結果の要約・比較・優先順位付け

### 会話管理
### 8.2 会話型検索セッション管理

- 新規会話の作成
- 会話履歴の保存
- ユーザー発言とAI回答の保存
- ユーザー発言とClaude回答の保存
- 会話タイトルの管理
- 最終更新日時の管理
- 会話一覧からの再開
- 不要な会話の削除
- 会話と対象物件・候補物件の紐づけ
- 会話と現在の `SearchCondition` の紐づけ
- 会話に現在の検索結果を保持
- 初回検索と追加絞り込みの履歴保存

### 物件条件管理
### 8.3 PropertyRegistry / 登記物件DB

顧客ごとの探索条件を保存・管理する。
登記PDF由来のExcel/CSVデータを検索可能な構造化DBとして管理する。

主な項目:
`PropertyRegistry` は本システムの中核データであり、自然言語検索、追加絞り込み、候補物件探索、所有者確認、権利関係確認、Claudeによる結果分析の入力文脈として利用する。

### 8.4 会話型PropertyRegistry検索

`PropertyRegistry` を対象に、営業担当者が自然文で調査対象となる物件を検索し、同一検索セッション内で追加条件を重ねて絞り込む。

主な検索観点:

- 希望エリア
- 予算下限・上限
- 駅距離
- 面積
- 築年数
- 物件種別・間取り等
- 特別条件
- エリア/所在
- 地番
- 家屋番号
- 建物名
- 物件種別
- 用途分類
- 収益区分
- 土地面積
- 建物面積
- 所有者名
- 所有者住所
- 抵当権有無
- 抵当権者
- 発行日

### 8.5 物件詳細確認

1物件について、基本情報、登記情報、所有者情報、権利関係、抵当権情報、PDFリンク、調査メモを確認する。

物件詳細から現在または新規の検索セッションへ接続できる導線を設け、対象物件の情報を同一 `Conversation` の分析文脈として渡す。

### 8.6 候補物件保存

営業担当者が有望と判断した物件を候補として保存し、後で比較・再確認できるようにする。

主な管理項目:

- 候補物件
- 候補にした理由
- 優先度
- Claude要約
- 次調査項目
- ステータス
- メモ

### AIプロジェクト設定管理
### 8.7 調査メモ管理

物件ごと、または会話ごとに調査メモを保存する。

調査メモはCRMの活動履歴ではなく、物件調査の記録として扱う。

### 8.8 AIプロジェクト設定管理

Claude Projects 相当のAI設定をBubble側で管理する。

主な項目:

- プロジェクト名
- 利用モデル
- system prompt
- 最大出力トークン
- temperature
- active状態

### Knowledge資料管理
### 8.9 Knowledge資料管理

AIが参照する補助資料を管理する。
Claudeが参照する補助資料を管理する。

対象例:

- 営業マニュアル
- 登記情報の読み方ガイド
- 物件調査チェックリスト
- 評価基準
- 提案文テンプレート
- アプローチ方針
- 社内ルール
- 物件調査に関する補足資料
- 調査手順

登記データ本体はKnowledge資料ではなく、検索可能な物件DBとして分離して扱う。
登記データ本体はKnowledge資料ではなく、`PropertyRegistry` として分離して扱う。

### 登記物件DB連携
## 9. データ要件

将来的に、登記PDF由来のExcel/CSVデータを `PropertyRegistry` としてDB化し、売買物件・収益物件探索に利用する。

主な項目候補:
主なData Type:

- 地域
- 種別
- PDFリンク
- 不動産番号
- 所在
- 地番
- 家屋番号
- 建物名
- 地目
- 建物種別
- 用途分類
- 収益区分
- 構造
- 階数
- 土地面積
- 建物面積
- 延床面積
- 専有面積
- 所有者情報
- 権利関係
- 抵当権情報
- 発行日
- `User`
- `Conversation`
- `Message`
- `PropertyRegistry`
- `CandidateProperty`
- `SearchCondition`
- `SearchConditionItem`
- `InvestigationNote`
- `AiProject`
- `KnowledgeDocument`
- `ImportLog`

### 9.1 User

| 項目名 | データ型 | 用途 |
|---|---|---|
| `email` | text | Bubble標準のログイン用メール |
| `name` | text | 画面表示用ユーザー名 |
| `role` | text | 営業担当者/管理者など |
| `company_name` | text | 所属会社 |
| `is_admin` | yes/no | 管理者判定 |
| `is_active` | yes/no | 利用停止フラグ |

### 9.2 Conversation

| 項目名 | データ型 | 用途 |
|---|---|---|
| `owner_user` | User | 会話の所有者 |
| `title` | text | 会話一覧・ヘッダーに表示するタイトル |
| `investigation_theme` | text | 調査テーマ |
| `target_area` | text | 対象エリア |
| `target_property` | PropertyRegistry | 主対象物件 |
| `related_properties` | list of PropertyRegistry | 関連候補物件 |
| `last_message_at` | date | 最終更新日時 |
| `last_message_text` | text | 会話一覧に表示する抜粋 |
| `project` | AiProject | 使用するAIプロジェクト設定 |
| `status` | text | 調査中/保留/完了など |
| `current_search_condition` | SearchCondition | 現在の検索条件 |
| `current_search_results` | list of PropertyRegistry | 現在の検索結果 |

### 9.3 Message

| 項目名 | データ型 | 用途 |
|---|---|---|
| `content` | text | メッセージ本文 |
| `conversation` | Conversation | 所属する会話 |
| `role` | text | `user` または `assistant` |
| `intent_type` | text | initial_search / refine_search / analyze_results / show_fields など |
| `parsed_conditions_json` | text | Claudeが自然文から変換した検索条件JSON |
| `search_result_count` | number | このメッセージ処理後の検索結果件数 |
| `referenced_properties` | list of PropertyRegistry | 回答時に参照した物件 |
| `api_response_id` | text | Claude APIの応答ID保存用 |
| `error_message` | text | APIエラー保存用 |
| `token_count` | number | token使用量保存用 |

### 9.4 PropertyRegistry / 登記物件DB

`PropertyRegistry` は、登記情報・物件情報を検索可能な形で管理する中核Data Typeである。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `area_group` | text | 地域 |
| `registry_type` | text | 種別。建物・土地・地図など |
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
| `is_condo_unit` | yes/no | 区分建物かどうか |
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
| `owner_type` | text | 法人所有/個人所有などの所有者種別 |
| `mortgage_status` | text | 乙区_状態 |
| `has_mortgage` | yes/no | 抵当権有無の検索用フラグ |
| `mortgage_rank` | number | 乙区_順位 |
| `mortgage_purpose` | text | 乙区_目的 |
| `mortgage_date` | text | 乙区_受付日 |
| `mortgage_cause` | text | 乙区_原因 |
| `mortgage_amount` | text | 乙区_債権額 |
| `mortgage_holder` | text | 乙区_抵当権者 |
| `issued_date` | text / date | 発行日 |

### 9.5 CandidateProperty

検索結果から営業担当者が気になる物件を保存するためのData Typeである。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `owner_user` | User | 作成者 |
| `conversation` | Conversation | 関連会話 |
| `property` | PropertyRegistry | 候補物件 |
| `search_condition` | SearchCondition | 元になった検索条件 |
| `priority` | number | 優先度 |
| `reason` | text | 候補にした理由 |
| `ai_summary` | text | Claudeによる要約 |
| `next_research` | text | 次に調査すべきこと |
| `status` | text | 未調査/調査中/有望/除外など |
| `memo` | text | 営業担当者メモ |

### 9.6 SearchCondition

物件探索時の条件を保存・再利用するためのData Typeである。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `owner_user` | User | 作成者 |
| `title` | text | 条件名 |
| `area` | text | 対象エリア |
| `property_type` | text | 土地/建物/区分/収益物件など |
| `budget_min` | number | 予算下限。必要な場合のみ使用 |
| `budget_max` | number | 予算上限。必要な場合のみ使用 |
| `land_area_min` | number | 土地面積下限 |
| `building_area_min` | number | 建物面積下限 |
| `use_category` | text | 用途分類 |
| `income_rank` | text | 収益区分 |
| `rights_filter` | text | 権利関係条件 |
| `conversation` | Conversation | 関連する検索セッション |
| `natural_language_query` | text | 初回検索の自然文 |
| `current_condition_summary` | text | 現在の検索条件の日本語要約 |
| `structured_query_json` | text | 現在の検索条件JSON |
| `condition_history_json` | text | 追加絞り込み履歴JSON |
| `last_refinement_text` | text | 最後の追加条件自然文 |
| `result_count` | number | 現在条件での検索件数 |
| `memo` | text | 調査メモ |

### 9.7 SearchConditionItem

`SearchConditionItem` は、会話型検索セッション内で追加・削除・更新される個別検索条件を保持するData Typeである。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `search_condition` | SearchCondition | 親となる検索条件 |
| `field_name` | text | `PropertyRegistry` の検索対象Field |
| `operator` | text | contains / equals / in / is_empty / greater_or_equal など |
| `value_text` | text | テキスト条件値 |
| `value_number` | number | 数値条件値 |
| `value_list_text` | list of text | in条件用の値一覧 |
| `source_text` | text | この条件を生成した自然文 |
| `label` | text | 画面表示用条件ラベル |
| `is_active` | yes/no | 条件が有効かどうか |
| `order_index` | number | 条件表示順 |
| `created_by_ai` | yes/no | Claudeが生成した条件かどうか |

### 9.8 InvestigationNote

物件ごと、または会話ごとに調査メモを保存するData Typeである。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `owner_user` | User | 作成者 |
| `property` | PropertyRegistry | 対象物件 |
| `conversation` | Conversation | 関連会話 |
| `note_type` | text | 所有者確認/権利関係/現地確認/価格調査など |
| `content` | text | メモ本文 |
| `ai_generated` | yes/no | Claude生成かどうか |
| `next_action` | text | 次アクション |
| `due_date` | date | 調査期限がある場合 |

### 9.9 AiProject

| 項目名 | データ型 | 用途 |
|---|---|---|
| `name` | text | AIプロジェクト名 |
| `model` | text | 利用モデル名 |
| `system_prompt` | text | Claudeへ渡すシステムプロンプト |
| `max_tokens` | number | 最大出力トークン |
| `temperature` | number | 生成の揺らぎ |
| `is_active` | yes/no | 利用中かどうか |
| `owner_user` | User | 所有者 |

### 9.10 KnowledgeDocument

| 項目名 | データ型 | 用途 |
|---|---|---|
| `title` | text | 資料タイトル |
| `summary` | text | 資料要約 |
| `content` | text | AIに渡す本文 |
| `document_file` | file | 元資料ファイル |
| `is_active` | yes/no | Claude参照対象にするか |
| `owner_user` | User | 所有者 |

### 9.11 ImportLog

`ImportLog` は、管理者による `PropertyRegistry` 全レコード差し替え更新の履歴を保存するData Typeである。

| 項目名 | データ型 | 用途 |
|---|---|---|
| `uploaded_file` | file | アップロードされたExcel/CSV |
| `imported_count` | number | インポート成功件数 |
| `error_count` | number | エラー件数 |
| `executed_by` | User | 実行した管理者 |
| `executed_at` | date | 実行日時 |
| `status` | text | running / completed / failed |
| `memo` | text | エラー内容、補足メモ |

## 10. API要件

### 10.1 Claude API

### 候補物件検索・比較
- Bubble API ConnectorからClaude APIを呼び出す
- ユーザーの現在入力だけでなく、同一会話の検索条件・検索結果・メッセージ履歴を渡す
- 自然文検索時は、Claudeに検索条件JSONのみを返させる
- 追加絞り込み時は、既存 `SearchCondition` と追加自然文を渡し、マージ後の条件JSONを返させる
- 必要に応じて `PropertyRegistry` の対象物件情報を渡す
- 必要に応じて候補物件一覧を渡す
- 必要に応じて active なKnowledge資料を補助文脈として渡す
- Claude回答を `Message` として保存する
- APIエラー時はエラー内容を記録し、ユーザーに分かる形で通知する

登記物件DB連携後、顧客条件に合う候補をBubble側で絞り込み、AIへ候補情報を渡して比較・営業コメント生成に利用する。
### 10.2 Claudeへ渡す相談テンプレート

主な検索・比較観点:
物件詳細からClaudeに相談する場合、以下のような構造で文脈を渡す。

- エリア
- 予算
- 土地面積
- 建物面積
- 築年数
- 駅距離
- 用途分類
- 収益区分
- 権利関係
- 抵当権等の注意点
```text
あなたは不動産営業担当者の調査支援AIです。
以下の登記情報・物件情報をもとに、営業担当者が次に判断すべきことを整理してください。

### 提案文作成
# 物件情報
...

AI回答や候補物件情報をもとに、営業担当者が顧客へ送る提案文の作成を支援する。
# 所有者情報
...

## 画面要件
# 権利関係
...

### ダッシュボード
# 出力してほしい内容
1. 物件概要
2. 所有者確認ポイント
3. 権利関係の注意点
4. 営業上の有望度
5. 次に調査すべきこと
6. アプローチ前の確認事項
```

- 最近の会話一覧を表示する
- 保存済み条件の概要を表示する
- AIプロジェクト、Knowledge資料への導線を表示する
- AIチャット開始導線を表示する
## 11. 画面要件

### AIチャット画面
### 11.1 ダッシュボード

- 会話一覧を表示する
- チャットメッセージを表示する
- ユーザー発言を入力できる
- Claude APIからの回答を表示・保存する
- 回答下に以下のアクション導線を表示する
  - 条件として保存
  - 提案文を作成
  - 比較リストに追加
- 最近の自然言語検索セッションを表示する
- 最近見た物件を表示する
- 保存した候補物件を表示する
- 調査中の物件を表示する
- 未確認の権利関係がある物件を表示する
- 新規検索セッション開始導線を表示する
- 物件検索導線を表示する

### 物件条件管理画面
### 11.2 検索セッション会話画面

- 保存済み条件を一覧表示する
- `Conversation` 単位で自然言語検索の会話履歴を表示する
- ユーザーの検索指示、追加絞り込み指示、表示・分析指示を入力できる
- Claude APIによる検索条件解釈、条件要約、分析結果を表示・保存する
- 現在の `SearchCondition` と `SearchConditionItem` を条件チップとして表示する
- 現在の検索結果件数と `Conversation.current_search_results` を表示する
- 回答下に以下のアクション導線を表示する
  - 条件を解除して再検索
  - 候補物件に追加
  - 調査メモとして保存
  - 物件詳細を開く

### 11.3 会話型PropertyRegistry検索画面

- 自然文入力から `PropertyRegistry` を検索する
- 初回検索指示をClaudeが構造化検索条件へ変換する
- 前回検索結果に対する追加絞り込み指示を受け付ける
- 既存の `SearchCondition` に条件を追加・削除・更新して再検索する
- 所在、所有者名、種別、用途分類、収益区分、面積、抵当権有無などを自然文から条件化できる
- 現在条件を日本語要約と条件チップで表示する
- 検索結果を同一 `Conversation` の文脈として保持する
- 検索結果から物件詳細へ遷移できる
- 検索結果の要約・比較・優先順位付けをClaudeへ依頼できる
- 検索結果から候補物件に追加できる

### 11.4 物件詳細画面

- 物件基本情報を表示する
- 所在情報を表示する
- 土地情報を表示する
- 建物情報を表示する
- 所有者情報を表示する
- 甲区情報を表示する
- 乙区情報を表示する
- PDFリンクを表示する
- 発行日を表示する
- Claude要約を表示する
- 調査メモを表示する
- Claudeにこの物件を相談できる
- 候補物件に追加できる
- 調査メモを追加できる

### 11.5 候補物件リスト画面

- 候補物件一覧を表示する
- 優先度を表示・編集できる
- 候補にした理由を表示・編集できる
- Claude要約を表示する
- 所有者情報を表示する
- 権利関係注意点を表示する
- 次調査項目を表示する
- ステータスを表示・編集できる
- 複数物件をClaudeに比較させる導線を表示する

### 11.6 調査条件管理画面

- 保存済み物件探索条件を一覧表示する
- 条件詳細を確認できる
- 条件の追加・編集・削除を行える
- 条件を使って `PropertyRegistry` を検索できる

### AIプロジェクト設定画面
### 11.7 AIプロジェクト設定画面

- AI設定を一覧表示する
- system prompt 等の設定を管理できる
- active な設定を切り替えられる
- system prompt等の設定を管理できる
- activeな設定を切り替えられる
- 用途別のClaude設定を管理できる
  - 自然文から `PropertyRegistry` 検索条件へ変換する用途
  - 前回条件への追加絞り込み・除外条件マージ用
  - 検索結果の要約・比較・優先順位付け用
  - 登記読み取り補助用
  - 調査タスク抽出用

### Knowledge資料管理画面
### 11.8 Knowledge資料管理画面

- 資料を一覧表示する
- 資料タイトル、要約、本文、ファイルを管理できる
- AI参照対象にするかを切り替えられる

### ログイン・サインアップ画面
### 11.9 登記データ取込画面

- メールアドレスとパスワードでログインできる
- 新規ユーザー登録ができる
- ログアウトできる
MVP後の拡張画面として、Excel/CSVから `PropertyRegistry` に登記データを取り込む画面を検討する。

## データ要件
- CSVアップロード
- カラムマッピング
- 取り込みプレビュー
- 重複チェック
- インポート実行
- インポート履歴確認

主なData Type:
### 11.10 ログイン画面

- `User`
- `Conversation`
- `Message`
- `AiProject`
- `KnowledgeDocument`
- `SearchCondition`
- `PropertyRegistry`
- 管理者が作成した社内ユーザーがメールアドレスとパスワードでログインできる
- 一般ユーザーによるサインアップは提供しない
- アカウントが必要な場合は管理者へ連絡する旨を表示する
- ログアウトできる

## API要件
### 11.11 admin / 管理者画面

管理者がログインユーザー管理と物件データベース更新を行う。

主な機能:

- ユーザー一覧表示
- 新規ユーザー登録
- ユーザー削除
- ユーザー名変更
- メールアドレス管理
- 管理者権限の付与/解除
- 利用停止フラグの管理
- Claude Codeで不動産登記簿謄本から抽出したExcel/CSVデータのアップロード
- `PropertyRegistry` の全レコード差し替え更新
- Excel/CSVカラムと `PropertyRegistry` Fieldのマッピング
- インポート件数、エラー件数、実行日時の記録
- `ImportLog` による物件データベース更新履歴の確認

## 12. Workflow要件

### 12.1 新規検索セッション作成

- `Conversation` を新規作成する
- `owner_user = Current User` を設定する
- 初期タイトルを設定する
- `current_search_condition` は空で開始する
- `current_search_results` は空で開始する
- 会話型PropertyRegistry検索画面へ遷移する
- 作成した `Conversation` を渡す

### 12.2 自然言語検索メッセージ送信

- ユーザーの自然文を `Message` として保存する
- 現在の `Conversation.current_search_condition` と過去メッセージを取得する
- Claude APIへ自然文、既存検索条件、現在の検索結果概要を送信する
- Claudeから `intent_type` と検索条件JSONを受け取る
- `intent_type = initial_search` の場合、新規 `SearchCondition` と `SearchConditionItem` を作成する
- `intent_type = refine_search` の場合、既存 `SearchCondition` に条件を追加・削除・更新する
- Bubbleが更新後の条件で `PropertyRegistry` を検索する
- 検索結果を `Conversation.current_search_results` として保持する
- 検索件数を `SearchCondition.result_count` と `Message.search_result_count` に保存する
- Claudeの条件解釈・条件要約を `Message` として保存する
- `Conversation` の `last_message_text` と `last_message_at` を更新する
- APIエラー時はエラーメッセージを保存・表示する

### 12.3 検索結果分析

- ユーザーが「有望そうな順に並べて」「所有者を表示して」など分析・表示指示を入力する
- 現在の `Conversation.current_search_results` を取得する
- 表示項目変更の場合は、検索結果一覧の表示列を変更する
- 要約・比較・優先順位付けの場合は、現在の検索結果をClaude APIへ送信する
- Claude回答を `Message` として保存する
- 必要に応じて推奨物件を `CandidateProperty` として保存できる導線を表示する

### Claude API
### 12.4 物件詳細から検索セッション分析

- Bubble API ConnectorからClaude APIを呼び出す
- ユーザーの現在入力だけでなく、同一会話の履歴を渡す
- 対象の `PropertyRegistry` を取得する
- 既存の `Conversation` がある場合は、その検索条件・検索結果文脈に対象物件を追加する
- 既存の `Conversation` がない場合は、新規検索セッションを作成して対象物件を `target_property` に設定する
- 物件情報、所有者情報、甲区情報、乙区情報をClaude API payloadへ差し込む
- Claude回答を `Message` として保存する
- APIエラー時はエラー内容を記録し、ユーザーに分かる形で通知する
- 必要に応じて `Conversation.current_search_results` に対象物件を含める

## 権限・セキュリティ要件
### 12.5 候補物件保存

- ユーザーは自分が作成した会話、条件、資料を閲覧・編集できる
- 管理者は必要に応じて全体管理を行える
- 登記データや顧客情報を扱うため、Privacy Rulesを本番運用前に必ず設計・検証する
- APIキーはクライアント側に露出しない形で管理する
- 個人情報を含むデータのアクセス制御を明確にする
- 対象の `PropertyRegistry` を `CandidateProperty` として保存する
- `owner_user`、関連 `Conversation`、候補理由、優先度、ステータスを設定する
- 必要に応じてClaude要約や次調査項目を保存する

### 12.6 調査メモ保存

## 実装優先度
- 対象物件または会話に紐づく `InvestigationNote` を作成する
- メモ種別、本文、次アクション、期限を保存する
- Claude回答から保存する場合は `ai_generated = yes` を設定する

### 優先度 高
### 12.7 管理者によるユーザー管理

- AIチャットの安定運用
- 会話履歴管理
- Claude API連携
- 条件保存機能
- `admin` 画面表示時に `Current User's is_admin = yes` を確認する
- 非管理者の場合は `index` へリダイレクトする
- 管理者が新規ユーザーを登録する
- 管理者がユーザー名、メールアドレス、role、is_admin、is_activeを編集する
- 管理者が不要なユーザーを削除する

### 12.8 管理者によるPropertyRegistry全差し替え更新

- 管理者がClaude Codeで不動産登記簿謄本から抽出したExcel/CSVデータをアップロードする
- Excel/CSVカラムを `PropertyRegistry` Fieldへマッピングする
- 全差し替え前に確認ダイアログを表示する
- 確認後、既存 `PropertyRegistry` を全削除する
- アップロードデータを新しい `PropertyRegistry` レコードとしてインポートする
- インポート件数、エラー件数、実行者、実行日時、ステータスを `ImportLog` に保存する

## 13. 権限・セキュリティ要件

- ユーザーは自分が作成した会話、候補物件、調査メモ、検索条件、資料を閲覧・編集できる
- 管理者は必要に応じて全体管理を行える
- 登記データ、所有者情報、顧客に関連し得る情報を扱うため、Privacy Rulesを本番運用前に必ず設計・検証する
- APIキーはクライアント側に露出しない形で管理する
- 個人情報を含むデータのアクセス制御を明確にする
- Claudeに送信する情報の範囲を必要最小限にする
- 法的判断や権利関係の確定判断は専門家確認が必要である旨を画面・プロンプト上で明確にする
- `admin` 画面は `Current User's is_admin = yes` のユーザーのみアクセス可能とする
- 非管理者が `admin` 画面にアクセスした場合は `index` にリダイレクトする
- 一般ユーザーによるサインアップは提供しない
- ユーザーアカウントは管理者が作成・削除・管理する
- `User.is_active = no` のユーザーは利用停止扱いとする
- 物件DB全差し替えは管理者のみ実行可能とする
- 物件DB全差し替え前に確認画面を必ず表示する
- 物件データベース更新履歴を `ImportLog` として保存する

## 14. Bubble実装の優先順位

### 優先度 高 / MVP範囲

- 会話型自然言語検索の安定運用
- 検索セッション履歴管理
- Claude APIによる自然文→検索条件変換
- `admin` 管理者画面
- `ImportLog` 作成
- `PropertyRegistry` 最小版の作成
- 会話型PropertyRegistry検索画面
- `SearchCondition` / `SearchConditionItem` 作成・更新
- 物件詳細画面
- 検索結果のClaude要約・比較・優先順位付け
- 候補物件保存
- Privacy Rules設計
- APIキー管理確認

### 優先度 中

- 調査メモ管理
- 複数候補物件のClaude比較
- AIプロジェクト設定の本格利用
- Knowledge資料のClaude連携
- 提案文作成機能
- 比較リスト機能
- 検索条件保存の強化

### 優先度 低〜将来対応
### 優先度 低 / 将来対応

- 登記Excel/CSVの取り込み
- `PropertyRegistry` DB作成
- 登記DB検索
- 検索結果のClaude連携
- Excel/CSV取込画面の完全実装
- インポート履歴管理
- 高度なスコアリング
- 高度な提案文作成
- 外部CRM連携
- LINE連携
- 契約管理

## 15. MVP範囲

MVPのゴールは、営業担当者が自然文で `PropertyRegistry` を検索し、前回検索結果に追加条件を重ねながら絞り込み、必要に応じてClaudeに検索結果の要約・比較・優先順位付けを依頼できる状態にすることである。

### 15.1 MVPに含めるもの

## 現時点の未実装・要確認項目
#### 会話型自然言語検索セッション

- 新規検索セッション作成
- 自然文検索入力
- `Message` 保存
- Claude APIによる検索条件変換
- `SearchCondition` / `SearchConditionItem` 保存
- `PropertyRegistry` 検索結果表示
- 追加絞り込み条件のマージ
- 検索結果を会話文脈として保持

#### PropertyRegistry最小版

MVPでは、以下の項目を優先して実装する。

- 所在
- 地番
- 家屋番号
- 建物名
- 種別
- 用途分類
- 収益区分
- 土地面積
- 建物面積
- 所有者名
- 所有者住所
- 抵当権状態
- 債権額
- 抵当権者
- PDFリンク
- 発行日

#### 物件検索

- 自然文による初回検索
- 前回検索結果への追加絞り込み
- 条件チップ表示
- 現在条件の日本語要約表示
- 所有者名、所在地、用途分類、収益区分、抵当権有無などの検索条件化
- 検索結果に対する所有者表示、要約、比較、優先順位付け

#### 物件詳細・検索結果分析

- 物件詳細画面から対象物件を現在の検索セッション文脈に追加できる
- 対象物件の登記情報をプロンプトに含める
- Claudeに以下を回答させる
  1. 物件概要
  2. 所有者確認ポイント
  3. 権利関係の注意点
  4. 営業上の有望度
  5. 次に調査すべきこと
  6. アプローチ前の確認事項

#### 候補物件保存

- 候補に追加
- 候補一覧表示
- メモ
- 優先度
- Claude要約
- 次調査項目

#### 管理者画面

- ログインユーザー管理
- 新規ユーザー登録
- ユーザー削除
- 管理者権限の付与/解除
- 利用停止フラグ管理
- `PropertyRegistry` 全レコード差し替え更新
- インポート履歴の `ImportLog` 保存

### 15.2 MVPに含めないもの

- CRM的な顧客管理
- 商談ステータス管理
- 追客管理
- 架電履歴管理
- メール配信
- 契約管理
- LINE連携
- 高度な提案文作成
- 差分更新方式のPropertyRegistryインポート
- 複雑な権限管理
- 複数部署・複数会社対応
- 高度なスコアリング
- 不動産価格査定機能

## 16. 現時点の未実装・要確認項目

- `PropertyRegistry` のBubble DB作成
- `ImportLog` のBubble DB作成
- `admin` 画面の作成
- `PropertyRegistry` 最小項目の確定
- 登記Excel/CSVの初期投入方法
- 同一物件に複数所有者・複数抵当権がある場合のデータ構造
- 物件検索画面の作成
- 物件詳細画面の作成
- 物件詳細から現在の検索セッションへ対象物件情報を渡す処理
- 候補物件保存機能
- 調査メモ保存機能
- `AiProject.system_prompt` をClaude APIへ動的に渡す処理
- Knowledge資料のClaude連携
- 登記データ `PropertyRegistry` のBubble DB作成
- Excel/CSVからの登記データ取り込み
- 登記DB検索
- 検索結果をClaudeへ渡す処理
- 条件保存機能の完成
- 提案文作成機能の完成
- 比較リスト機能の完成
- Privacy Rulesの本格設計
- 本番デプロイ前のセキュリティ確認
