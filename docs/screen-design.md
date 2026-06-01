# BukkenAiSearch 画面設計

## 0. 本書の位置づけ

本書は、正式版 `requirements.md` と `database-design.md` を前提に、MVPで実装するBubble画面を設計するドキュメントである。

`BukkenAiSearch` はCRMではなく、営業担当者がClaudeに相談しながら、登記情報・物件情報をもとに候補物件探索、所有者確認、権利関係確認、アプローチ先整理、次調査項目の判断を行うAI相談型の登記・物件調査支援システムとして設計する。

MVPでは以下に絞る。

- AIチャット
- `PropertyRegistry` 最小版を使った物件検索
- 物件詳細からClaude相談
- 候補物件保存
- 会話履歴保存
- 最小限のログイン/ログアウト

## 1. 画面一覧

| No | Bubble page名 | 画面名 | 目的 | MVP |
|---:|---|---|---|---|
| 1 | `login` | ログイン画面 | 営業担当者がログインする | 対象 |
| 2 | `signup` | サインアップ画面 | 初回ユーザー登録を行う | 対象 |
| 3 | `index` | ダッシュボード | 最近の会話・候補物件・物件検索導線を表示する | 対象 |
| 4 | `property_search` | 物件検索画面 | `PropertyRegistry` から候補物件を検索する | 対象 |
| 5 | `property_detail` | 物件詳細画面 | 物件・所有者・権利関係を確認しClaudeへ相談する | 対象 |
| 6 | `ai_chat` | AIチャット画面 | Claudeと会話し、調査内容を整理する | 対象 |
| 7 | `candidate_properties` | 候補物件一覧画面 | 保存した候補物件を一覧・確認する | 対象 |
| 8 | `search_conditions` | 調査条件管理画面 | 物件検索条件を保存・再利用する | 簡易対象 |

### MVP対象外画面

以下はMVP後の拡張とする。

| Bubble page名 | 画面名 | 理由 |
|---|---|---|
| `knowledge` | Knowledge資料管理画面 | MVPではClaudeへ固定プロンプトを渡す運用で開始可能 |
| `ai_projects` | AIプロジェクト設定画面 | MVPでは既存active設定または固定設定で開始可能 |
| `registry_import` | 登記データ取込画面 | MVPでは手動投入またはBubble標準CSV投入で開始可能 |
| `investigation_notes` | 調査メモ一覧画面 | MVPでは物件詳細・候補物件内のメモ表示から開始可能 |

## 2. 画面遷移図

### 2.1 全体遷移

```text
[login]
   │ ログイン成功
   ▼
[index]
   ├─ 物件を探す ───────────────▶ [property_search]
   │                                  │ 検索結果クリック
   │                                  ▼
   │                             [property_detail]
   │                                  ├─ Claudeに相談 ─────▶ [ai_chat]
   │                                  ├─ 候補に追加 ───────▶ [candidate_properties]
   │                                  └─ 検索へ戻る ───────▶ [property_search]
   │
   ├─ AIチャット開始 ───────────▶ [ai_chat]
   │                                  ├─ 参照物件を開く ───▶ [property_detail]
   │                                  └─ 候補に追加 ───────▶ [candidate_properties]
   │
   ├─ 候補物件を見る ───────────▶ [candidate_properties]
   │                                  └─ 物件詳細 ─────────▶ [property_detail]
   │
   └─ 条件管理 ─────────────────▶ [search_conditions]
                                      └─ 条件で検索 ───────▶ [property_search]
```

### 2.2 物件検索からClaude相談までの主要導線

```text
[property_search]
   │ 条件入力・検索
   ▼
検索結果Repeating Group
   │ 物件詳細を開く
   ▼
[property_detail]
   │ Claudeにこの物件を相談
   ▼
Conversation作成または既存Conversation選択
   │ PropertyRegistry情報をプロンプト化
   ▼
[ai_chat]
   │ Claude回答保存
   ▼
Message / CandidateProperty / InvestigationNote
```

### 2.3 候補物件保存導線

```text
[property_search] または [property_detail] または [ai_chat]
   │ 候補に追加
   ▼
CandidateProperty作成
   │
   ▼
[candidate_properties]
   │ 物件詳細を確認
   ▼
[property_detail]
```

## 3. 共通UI構成

### 3.1 共通ヘッダー

全ログイン後画面に配置する。

| UI要素 | 種別 | 内容 |
|---|---|---|
| ロゴ/アプリ名 | Text/Group | `BukkenAiSearch` |
| グローバルナビ | Link/Button | ダッシュボード、物件検索、AIチャット、候補物件 |
| ユーザー表示 | Text | Current User's nameまたはemail |
| ログアウト | Button | ログアウトWorkflow |

### 3.2 共通のData Source方針

- ログイン後画面は `Current User is logged in` を前提とする
- ユーザー所有データは原則 `owner_user = Current User` で絞り込む
- `PropertyRegistry` はログインユーザーであれば検索可能とする
- `Conversation`、`Message`、`CandidateProperty`、`SearchCondition` はCurrent User所有データを表示する

## 4. 各画面のUI構成・Data Type・Workflow

## 4.1 `login` / ログイン画面

### 目的

営業担当者がメールアドレス・パスワードでログインする。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| メイン | Input email | メールアドレス入力 |
| メイン | Input password | パスワード入力 |
| メイン | Button login | ログイン実行 |
| メイン | Link signup | サインアップ画面へ遷移 |
| メイン | Alert/Text | ログインエラー表示 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `User` | Bubble標準ログイン認証 |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button login clicked | Log the user in |
| Login success | Go to page `index` |
| Login failed | エラーメッセージ表示 |
| Link signup clicked | Go to page `signup` |

## 4.2 `signup` / サインアップ画面

### 目的

初回ユーザー登録を行う。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| メイン | Input name | ユーザー名 |
| メイン | Input email | メールアドレス |
| メイン | Input password | パスワード |
| メイン | Button signup | 登録実行 |
| メイン | Link login | ログイン画面へ戻る |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `User` | 新規ユーザー作成、`name`設定 |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button signup clicked | Sign the user up |
| Signup success | Make changes to Current User: `name`, `role = 営業担当者`, `is_admin = no` |
| Signup success | Go to page `index` |
| Link login clicked | Go to page `login` |

## 4.3 `index` / ダッシュボード

### 目的

ログイン後の起点画面。最近のClaude相談、候補物件、物件検索導線を表示する。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 上部カード | Stat card | 登録物件数、候補物件数、進行中会話数 |
| メイン左 | Button property_search | 物件検索を開始 |
| メイン左 | Button new_chat | AIチャット開始 |
| メイン左 | Button candidates | 候補物件一覧へ |
| メイン中央 | RG recent_conversations | 最近のConversation一覧 |
| メイン右 | RG recent_candidates | 最近追加したCandidateProperty一覧 |
| メイン右 | RG recent_properties | 最近見たPropertyRegistry。MVPでは省略可 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `Conversation` | 最近のClaude相談表示 |
| `CandidateProperty` | 最近の候補物件表示 |
| `PropertyRegistry` | 登録物件数表示、物件導線 |
| `User` | Current User判定 |

### 表示条件・Data Source

| UI | Data Source |
|---|---|
| RG recent_conversations | Search for Conversations where `owner_user = Current User`, sort by `last_message_at desc` |
| RG recent_candidates | Search for CandidateProperties where `owner_user = Current User`, sort by Created Date desc |
| 登録物件数 | Search for PropertyRegistries:count |
| 候補物件数 | Search for CandidateProperties where `owner_user = Current User`:count |
| 進行中会話数 | Search for Conversations where `owner_user = Current User` and `status = 調査中`:count |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button property_search clicked | Go to page `property_search` |
| Button new_chat clicked | Create new `Conversation` → Go to page `ai_chat` with Data to send |
| Button candidates clicked | Go to page `candidate_properties` |
| RG recent_conversations cell clicked | Go to page `ai_chat`, Data to send = Current cell's Conversation |
| RG recent_candidates cell clicked | Go to page `property_detail`, Data to send = Current cell's CandidateProperty's property |

## 4.4 `property_search` / 物件検索画面

### 目的

`PropertyRegistry` から候補物件を検索し、詳細確認・Claude相談・候補保存につなげる。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 検索条件 | Input location | 所在/エリア検索 |
| 検索条件 | Input owner_name | 所有者名検索 |
| 検索条件 | Dropdown registry_type | 種別 |
| 検索条件 | Dropdown use_category | 用途分類 |
| 検索条件 | Dropdown income_rank | 収益区分 |
| 検索条件 | Dropdown mortgage_filter | 抵当権あり/なし |
| 検索条件 | Button search | 検索実行 |
| 検索条件 | Button clear | 条件クリア |
| 検索条件 | Button save_condition | 検索条件保存 |
| 結果 | RG property_results | 検索結果一覧 |
| 結果セル | Text location | 所在 |
| 結果セル | Text building_name | 建物名 |
| 結果セル | Text owner_name | 所有者 |
| 結果セル | Text mortgage_summary | 抵当権概要 |
| 結果セル | Button detail | 詳細 |
| 結果セル | Button add_candidate | 候補に追加 |
| 結果セル | Button ask_claude | Claudeに相談 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `PropertyRegistry` | 検索対象、結果表示 |
| `SearchCondition` | 条件保存 |
| `CandidateProperty` | 候補保存 |
| `Conversation` | Claude相談開始時に作成 |
| `Message` | Claude相談開始時の初期メッセージ保存 |
| `User` | owner_user設定 |

### Data Source

| UI | Data Source |
|---|---|
| RG property_results | Search for PropertyRegistries with filters |
| Dropdown registry_type | Option Set `RegistryType` またはPropertyRegistryの候補値 |
| Dropdown use_category | Option Setまたは手入力候補 |
| Dropdown income_rank | Option Setまたは手入力候補 |

### 検索条件

MVPでは以下を優先する。

- `location contains Input location's value`
- `owner_name contains Input owner_name's value`
- `registry_type = Dropdown registry_type's value`
- `use_category = Dropdown use_category's value`
- `income_rank = Dropdown income_rank's value`
- 抵当権あり: `mortgage_status is not empty` または `mortgage_holder is not empty`
- 抵当権なし: `mortgage_status is empty` and `mortgage_holder is empty`

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button search clicked | 検索結果RGの条件を更新 |
| Button clear clicked | 入力値をリセット |
| Button save_condition clicked | Create new `SearchCondition` |
| Button detail clicked | Go to page `property_detail`, Data to send = Current cell's PropertyRegistry |
| Button add_candidate clicked | Create new `CandidateProperty` with Current cell's PropertyRegistry |
| Button ask_claude clicked | Create new `Conversation` with `target_property` → Go to page `ai_chat` |

## 4.5 `property_detail` / 物件詳細画面

### 目的

1件の `PropertyRegistry` を詳細表示し、所有者・甲区・乙区・抵当権を確認してClaude相談や候補保存につなげる。

### Page Type

| 設定 | 値 |
|---|---|
| Type of content | `PropertyRegistry` |
| Data source | 前画面から渡された `PropertyRegistry` |

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 上部 | Text title | 建物名または所在地 |
| 上部 | Button ask_claude | Claudeにこの物件を相談 |
| 上部 | Button add_candidate | 候補に追加 |
| 上部 | Button back_search | 検索へ戻る |
| 基本情報 | Group basic_info | 地域、種別、PDFリンク、不動産番号、発行日 |
| 所在情報 | Group location_info | 所在、地番、家屋番号、建物名 |
| 土地情報 | Group land_info | 地目、地積 |
| 建物情報 | Group building_info | 建物種類、用途分類、収益区分、構造、階数、面積 |
| 所有者情報 | Group owner_info | 所有者名、所有者住所、甲区順位、目的、受付日、原因 |
| 抵当権情報 | Group mortgage_info | 乙区状態、順位、目的、受付日、原因、債権額、抵当権者 |
| 候補状況 | Group candidate_status | 既に候補保存済みかどうか |
| 関連会話 | RG related_conversations | この物件に紐づくConversation |
| 調査メモ | RG investigation_notes | この物件に紐づくInvestigationNote。MVPでは簡易表示 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `PropertyRegistry` | 画面の主Data Type |
| `CandidateProperty` | 候補保存状況、候補追加 |
| `Conversation` | 物件に紐づくClaude相談 |
| `Message` | Claude相談開始時の初期メッセージ |
| `InvestigationNote` | 調査メモ表示・保存。MVPでは簡易 |
| `User` | owner_user設定 |

### Data Source

| UI | Data Source |
|---|---|
| 画面全体 | Current page's PropertyRegistry |
| RG related_conversations | Search for Conversations where `owner_user = Current User` and `target_property = Current page's PropertyRegistry` |
| RG investigation_notes | Search for InvestigationNotes where `owner_user = Current User` and `property = Current page's PropertyRegistry` |
| candidate_status | Search for CandidateProperties where `owner_user = Current User` and `property = Current page's PropertyRegistry`:first item |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button ask_claude clicked | Create new `Conversation` with `target_property = Current page's PropertyRegistry` |
| Button ask_claude clicked | Create initial `Message` or set page state for prompt context |
| Button ask_claude clicked | Go to page `ai_chat`, Data to send = Result of Conversation creation |
| Button add_candidate clicked | Create new `CandidateProperty` if not already exists |
| Button add_candidate clicked | Show success alert / change button state |
| Button back_search clicked | Go to page `property_search` |
| RG related_conversations cell clicked | Go to page `ai_chat`, Data to send = Current cell's Conversation |

### Claude相談時に渡す文脈

物件詳細からClaude相談する場合、以下をプロンプトに含める。

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
- 甲区情報
- 乙区情報
- 抵当権者
- 債権額
- 発行日
- PDFリンク

## 4.6 `ai_chat` / AIチャット画面

### 目的

営業担当者がClaudeに相談し、登記・物件調査の論点整理、所有者確認、権利関係確認、次調査項目整理を行う。

### Page Type

| 設定 | 値 |
|---|---|
| Type of content | `Conversation` |
| Data source | 前画面から渡された `Conversation` |

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 左サイドバー | Button new_conversation | 新規相談開始 |
| 左サイドバー | RG conversations | 自分のConversation一覧 |
| 中央上部 | Text conversation_title | 会話タイトル |
| 中央上部 | Group target_property_summary | 対象物件サマリー |
| 中央 | RG messages | Message一覧 |
| Message cell | Text role_label | user / Claude |
| Message cell | Text content | メッセージ本文 |
| Message cell | Button save_note | 調査メモ保存。MVPでは任意 |
| Message cell | Button add_candidate | 参照物件を候補に追加 |
| 下部 | MultilineInput chat_input | ユーザー入力 |
| 下部 | Button send | 送信 |
| 下部 | Button open_property | 対象物件詳細を開く |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `Conversation` | 現在の会話 |
| `Message` | 会話履歴表示・保存 |
| `PropertyRegistry` | 対象物件・参照物件表示 |
| `CandidateProperty` | 候補保存 |
| `InvestigationNote` | Claude回答からメモ保存。MVPでは任意 |
| `AiProject` | Claude設定。MVPではactive設定または固定設定 |
| `KnowledgeDocument` | active資料参照。MVPでは任意 |
| `User` | owner_user判定 |

### Data Source

| UI | Data Source |
|---|---|
| 画面全体 | Current page's Conversation |
| RG conversations | Search for Conversations where `owner_user = Current User`, sort by `last_message_at desc` |
| RG messages | Search for Messages where `conversation = Current page's Conversation`, sort by Created Date asc |
| target_property_summary | Current page's Conversation's target_property |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button new_conversation clicked | Create new `Conversation` → Go to page `ai_chat` with Data to send |
| RG conversations cell clicked | Go to page `ai_chat`, Data to send = Current cell's Conversation |
| Button send clicked | Create new `Message` as user |
| Button send clicked | Build Claude API payload from conversation history and target property |
| Button send clicked | Call Claude API |
| Claude API success | Create new `Message` as assistant |
| Claude API success | Update `Conversation.last_message_text`, `last_message_at`, `title` if needed |
| Claude API error | Create or update error `Message` / show alert |
| Button open_property clicked | Go to page `property_detail`, Data to send = Current page's Conversation's target_property |
| Button add_candidate clicked | Create new `CandidateProperty` for referenced/target property |
| Button save_note clicked | Create new `InvestigationNote` from Claude response |

### Claude API送信時の文脈

MVPでは以下を渡す。

1. activeな`AiProject.system_prompt`または固定system prompt
2. 現在の`Conversation`に紐づく過去`Message`一覧
3. `Conversation.target_property` の主要フィールド
4. 必要に応じて `Conversation.related_properties`
5. ユーザーの今回入力

## 4.7 `candidate_properties` / 候補物件一覧画面

### 目的

保存済み候補物件を一覧表示し、優先度・ステータス・次調査項目を確認する。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 上部 | Filter status | ステータス絞り込み |
| 上部 | Sort priority | 優先度順/作成日順 |
| 上部 | Button property_search | 物件検索へ |
| 一覧 | RG candidates | CandidateProperty一覧 |
| セル | Text building_name | 候補物件名 |
| セル | Text location | 所在 |
| セル | Text owner_name | 所有者 |
| セル | Text status | ステータス |
| セル | Text priority | 優先度 |
| セル | Text next_research | 次調査項目 |
| セル | Button detail | 物件詳細へ |
| セル | Button chat | 関連会話へ、なければ新規相談 |
| セル | Button remove | 候補から削除 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `CandidateProperty` | 候補一覧の主Data Type |
| `PropertyRegistry` | 候補物件の詳細表示 |
| `Conversation` | 関連会話への導線 |
| `User` | owner_user判定 |

### Data Source

| UI | Data Source |
|---|---|
| RG candidates | Search for CandidateProperties where `owner_user = Current User`, sort by priority asc or Created Date desc |
| status filter | CandidateProperty.status |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button property_search clicked | Go to page `property_search` |
| Button detail clicked | Go to page `property_detail`, Data to send = Current cell's CandidateProperty's property |
| Button chat clicked | If conversation exists → Go to page `ai_chat` |
| Button chat clicked | If conversation empty → Create `Conversation` with property → Go to page `ai_chat` |
| Status changed | Make changes to Current cell's CandidateProperty.status |
| Priority changed | Make changes to Current cell's CandidateProperty.priority |
| Button remove clicked | Delete Current cell's CandidateProperty or set status = 除外 |

## 4.8 `search_conditions` / 調査条件管理画面

### 目的

物件検索条件を保存・再利用する。MVPでは簡易実装とし、物件検索画面への条件引き渡しを優先する。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 上部 | Button new_condition | 新規条件作成 |
| 一覧 | RG search_conditions | 保存済み条件一覧 |
| セル | Text title | 条件名 |
| セル | Text area | 対象エリア |
| セル | Text property_type | 物件種別 |
| セル | Text use_category | 用途分類 |
| セル | Button use_condition | この条件で検索 |
| セル | Button edit | 編集 |
| セル | Button delete | 削除 |
| Popup | Popup condition_form | 条件追加・編集フォーム |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `SearchCondition` | 保存済み検索条件 |
| `User` | owner_user判定 |

### Data Source

| UI | Data Source |
|---|---|
| RG search_conditions | Search for SearchConditions where `owner_user = Current User`, sort by Created Date desc |
| Popup condition_form | 作成時は空、編集時はCurrent cell's SearchCondition |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button new_condition clicked | Show Popup condition_form |
| Button save in popup clicked | Create new `SearchCondition` or Make changes |
| Button use_condition clicked | Go to page `property_search` with condition values via URL parameters or custom state |
| Button edit clicked | Show Popup condition_form with Current cell's SearchCondition |
| Button delete clicked | Delete Current cell's SearchCondition |

## 5. MVP画面別Data Type対応表

| 画面 | User | PropertyRegistry | Conversation | Message | CandidateProperty | SearchCondition | InvestigationNote | AiProject | KnowledgeDocument |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `login` | ○ |  |  |  |  |  |  |  |  |
| `signup` | ○ |  |  |  |  |  |  |  |  |
| `index` | ○ | ○ | ○ |  | ○ |  |  |  |  |
| `property_search` | ○ | ○ | ○ | ○ | ○ | ○ |  |  |  |
| `property_detail` | ○ | ○ | ○ | ○ | ○ |  | ○ |  |  |
| `ai_chat` | ○ | ○ | ○ | ○ | ○ |  | ○ | ○ | ○ |
| `candidate_properties` | ○ | ○ | ○ |  | ○ |  |  |  |  |
| `search_conditions` | ○ |  |  |  |  | ○ |  |  |  |

## 6. MVP画面別Workflow対応表

| 画面 | 主なWorkflow |
|---|---|
| `login` | ログイン、ログイン後ダッシュボード遷移 |
| `signup` | サインアップ、User追加情報保存、ダッシュボード遷移 |
| `index` | 新規会話作成、物件検索遷移、候補物件遷移、最近の会話再開 |
| `property_search` | 物件検索、検索条件保存、物件詳細遷移、候補追加、Claude相談開始 |
| `property_detail` | 物件情報表示、候補追加、Claude相談開始、関連会話表示 |
| `ai_chat` | Message保存、Claude API実行、Claude回答保存、候補追加、調査メモ保存 |
| `candidate_properties` | 候補一覧表示、ステータス更新、優先度更新、物件詳細遷移、関連会話遷移 |
| `search_conditions` | 条件作成、条件編集、条件削除、条件で物件検索 |

## 7. 実装優先順位

### Phase 1: 最小導線

1. `login` / `signup`
2. `index`
3. `property_search`
4. `property_detail`
5. `ai_chat`

### Phase 2: 候補管理

1. `CandidateProperty` 作成Workflow
2. `candidate_properties`
3. 候補から物件詳細・Claude相談への導線

### Phase 3: 条件・メモ

1. `search_conditions`
2. `InvestigationNote` の簡易保存
3. AI回答から調査メモ保存

## 8. 画面設計上の注意点

- CRMではないため、顧客詳細画面、商談詳細画面、追客履歴画面、契約管理画面はMVPでは作らない。
- `PropertyRegistry` の検索・詳細・Claude相談を最短導線にする。
- 所有者情報・抵当権情報は個人情報やセンシティブ情報を含む可能性があるため、Privacy Rulesとログイン必須制御を前提にする。
- Claude回答は法的判断ではなく、調査支援・論点整理として表示する。
- Bubbleではページ遷移時にData to sendを使い、`property_detail` は `PropertyRegistry`、`ai_chat` は `Conversation` をType of contentにする。
