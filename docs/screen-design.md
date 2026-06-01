# BukkenAiSearch 画面設計

## 0. 本書の位置づけ

本書は、正式版 `requirements.md` を前提に、MVPで実装するBubble画面を設計するドキュメントである。

`BukkenAiSearch` はCRMではなく、登記データベース `PropertyRegistry` を自然言語で検索し、対話しながら絞り込みを行う営業支援システムとして設計する。

本システムの中核は「AIチャット」単体ではなく、`Conversation` を単位とする「自然言語による `PropertyRegistry` 検索セッション」である。

MVPでは以下に絞る。

- `ai_search` による自然言語検索セッション
- 初回検索条件のClaude解釈
- 追加条件による絞り込み
- 現在条件での `PropertyRegistry` 再検索
- 検索結果一覧表示
- 検索結果に対するClaude分析
- 候補物件保存
- 物件詳細確認
- 社内ユーザー向けログイン/ログアウト
- 管理者によるログインユーザー管理
- 管理者による `PropertyRegistry` 全レコード差し替え更新

一般ユーザーによるサインアップは提供しない。ユーザーアカウントは管理者が `admin` 画面から作成・削除・管理する。

## 1. 画面一覧

MVP画面は以下の6画面とする。

| No | Bubble page名 | 画面名 | 目的 | MVP |
|---:|---|---|---|---|
| 1 | `login` | ログイン画面 | 管理者が作成した社内ユーザーがログインする | 対象 |
| 2 | `index` | ダッシュボード | 検索セッション開始、最近のConversation、候補物件、管理者画面導線を表示する | 対象 |
| 3 | `ai_search` | 自然言語PropertyRegistry検索セッション画面 | 自然言語検索、追加絞り込み、検索結果表示、Claudeとの会話、候補保存を1画面で行う | 対象 |
| 4 | `property_detail` | 物件詳細画面 | 物件・所有者・権利関係を確認し、現在のConversationへ戻って分析できる | 対象 |
| 5 | `candidate_properties` | 候補物件一覧画面 | 保存した候補物件を一覧・確認する | 対象 |
| 6 | `admin` | 管理者画面 | 管理者がログインユーザー管理と物件データベース更新を行う | 対象 |

### 1.1 削除する画面

以下の画面は不要とし、MVP画面一覧から削除する。

| 削除するBubble page名 | 削除理由 |
|---|---|
| `property_search` | 検索機能は `ai_search` に統合するため |
| `search_conditions` | 検索条件は `Conversation` に紐づく `SearchCondition` / `SearchConditionItem` で保持し、独立画面を作らないため |

### 1.2 MVP対象外画面

以下はMVP後の拡張とする。

| Bubble page名 | 画面名 | 理由 |
|---|---|---|
| `knowledge` | Knowledge資料管理画面 | MVPではClaudeへ固定プロンプトを渡す運用で開始可能 |
| `ai_projects` | AIプロジェクト設定画面 | MVPでは既存active設定または固定設定で開始可能 |
| `investigation_notes` | 調査メモ一覧画面 | MVPでは物件詳細・候補物件内のメモ表示から開始可能 |

## 2. 画面遷移図

### 2.1 全体遷移

```text
[login]
   │ ログイン成功
   ▼
[index]
   ├─ 新規検索セッション ─────▶ [ai_search]
   │                                  │ 検索結果クリック
   │                                  ▼
   │                             [property_detail]
   │                                  ├─ 現在の検索へ戻る ─▶ [ai_search]
   │                                  └─ 候補に追加 ───────▶ [candidate_properties]
   │
   ├─ 最近のConversation再開 ─▶ [ai_search]
   │
   ├─ 候補物件を見る ─────────▶ [candidate_properties]
   │                                  └─ 物件詳細 ─────────▶ [property_detail]
   │
   └─ 管理者画面 ※is_adminのみ ─▶ [admin]
                                      ├─ ユーザー管理
                                      └─ PropertyRegistry全差し替え更新
```

### 2.2 自然言語検索セッションの主要導線

```text
[ai_search]
   │ ユーザー: 「中区で収益物件を探して」
   ▼
Claudeが検索条件へ変換
   │ location contains 中区 / income_rank = 収益物件
   ▼
BubbleがPropertyRegistryを検索
   │
   ▼
検索結果一覧 + 条件チップ + ヒット件数を表示
   │ ユーザー: 「その中で100坪以上」
   ▼
既存SearchConditionに面積条件を追加
   │
   ▼
BubbleがPropertyRegistryを再検索
   │ ユーザー: 「法人所有だけ」
   ▼
owner_type条件を追加して再検索
   │ ユーザー: 「所有者を表示」
   ▼
表示列を変更
   │
   ├─ 詳細表示 ─────────────▶ [property_detail]
   ├─ 候補保存 ─────────────▶ CandidateProperty作成
   └─ Claude分析 ───────────▶ 同一[ai_search]内に分析Messageを表示
```

### 2.3 候補物件保存導線

```text
[ai_search] または [property_detail]
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
| グローバルナビ | Link/Button | ダッシュボード、AI検索、候補物件 |
| 管理者導線 | Link/Button | `Current User's is_admin = yes` の場合のみ `admin` を表示 |
| ユーザー表示 | Text | Current User's nameまたはemail |
| ログアウト | Button | Log the user out |

### 3.2 共通アクセス制御

| 条件 | 動作 |
|---|---|
| Current User is logged out | `login` へ遷移 |
| Current User's is_active is no | ログアウトまたは利用停止メッセージを表示 |
| admin画面で Current User's is_admin is no | `index` へ遷移 |

### 3.3 共通Data Type方針

- `Conversation`、`Message`、`CandidateProperty`、`SearchCondition`、`SearchConditionItem` はCurrent User所有データを表示する。
- `ai_search` は `Conversation` をType of contentにし、自然言語検索、会話、検索結果表示を統合する。
- 検索条件は `Conversation.current_search_condition`、`SearchCondition`、`SearchConditionItem` に保持する。
- 検索結果全件は `Conversation` に保存しない。
- 検索結果一覧は、現在の `SearchConditionItem` を条件として毎回 `PropertyRegistry` を再検索して取得する。

## 4. 各画面設計

## 4.1 `login` / ログイン画面

### 目的

管理者が作成した社内ユーザーのみがログインする。一般ユーザーによるサインアップ導線は設けない。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| 中央 | Text title | BukkenAiSearch |
| 中央 | Input email | メールアドレス |
| 中央 | Input password | パスワード |
| 中央 | Button login | ログイン |
| 中央 | Text account_notice | アカウントが必要な場合は管理者へ連絡する旨 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `User` | Bubble標準ログイン、is_active判定 |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button login clicked | Log the user in |
| Login success | If Current User's is_active is yes → Go to page `index` |
| Login success | If Current User's is_active is no → Log the user out and show alert |
| Login error | Show error alert |

## 4.2 `index` / ダッシュボード

### 目的

ログイン後の起点画面。新規検索セッション開始、最近のConversation再開、候補物件、管理者画面導線を表示する。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 上部カード | Stat card | 登録物件数、候補物件数、進行中Conversation数 |
| メイン左 | Button new_ai_search | 新規自然言語検索セッションを開始 |
| メイン左 | Button candidates | 候補物件一覧へ |
| メイン左 | Button admin | 管理者画面へ。is_adminのみ表示 |
| メイン中央 | RG recent_conversations | 最近のConversation一覧 |
| メイン右 | RG recent_candidates | 最近追加したCandidateProperty一覧 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `Conversation` | 最近の検索セッション表示 |
| `CandidateProperty` | 最近の候補表示 |
| `PropertyRegistry` | 登録物件数表示 |
| `User` | Current User、権限表示 |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Page is loaded | If logged out → Go to page `login` |
| Button new_ai_search clicked | Create new `Conversation` with `owner_user = Current User` |
| Button new_ai_search clicked | Create empty `SearchCondition` and set to `Conversation.current_search_condition` |
| Button new_ai_search clicked | Go to page `ai_search`, Data to send = Result of Conversation creation |
| RG recent_conversations cell clicked | Go to page `ai_search`, Data to send = Current cell's Conversation |
| Button candidates clicked | Go to page `candidate_properties` |
| Button admin clicked | Go to page `admin` only when Current User's is_admin = yes |

## 4.3 `ai_search` / 自然言語PropertyRegistry検索セッション画面

### 目的

従来の `ai_chat` と `property_search` を統合したMVPの中心画面。自然言語検索、追加条件による絞り込み、検索結果表示、Claudeとの会話、候補保存を1画面で実現する。

### Page Type

| 設定 | 値 |
|---|---|
| Type of content | `Conversation` |
| Data source | 新規作成または既存の検索セッションConversation |

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| 左サイド | RG conversations | 自分のConversation一覧 |
| 左サイド | Button new_conversation | 新規検索セッション開始 |
| 中央上部 | Text session_title | Conversationタイトル |
| 中央上部 | Group current_condition | 現在の検索条件の日本語要約 |
| 中央上部 | RG condition_chips | 有効な `SearchConditionItem` を条件チップ表示 |
| 中央上部 | Button remove_condition | 条件チップを無効化して再検索 |
| 中央上部 | Text hit_count | 現在のヒット件数 |
| 中央 | RG property_results | 現在条件で都度検索した `PropertyRegistry` 一覧 |
| 結果セル | Text location | 所在 |
| 結果セル | Text building_name | 建物名 |
| 結果セル | Text owner_name | 所有者 |
| 結果セル | Text registry_type | 種別 |
| 結果セル | Text use_category | 用途分類 |
| 結果セル | Text area | 面積。土地/建物面積を用途に応じて表示 |
| 結果セル | Text mortgage_status | 抵当権有無 |
| 結果セル | Button detail | 詳細表示 |
| 結果セル | Button add_candidate | 候補保存 |
| 結果セル | Button analyze_row | Claude分析 |
| 下部 | RG messages | 自然文検索、Claude解釈、分析結果のMessage一覧 |
| 下部 | MultilineInput natural_language_input | 自然言語入力欄 |
| 下部 | Button send | 送信 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `Conversation` | 検索セッション本体 |
| `Message` | 自然文入力、Claude解釈、分析結果の保存 |
| `PropertyRegistry` | 検索対象、結果表示 |
| `SearchCondition` | 現在の検索条件セット |
| `SearchConditionItem` | 条件チップ、追加絞り込み条件 |
| `CandidateProperty` | 候補保存 |
| `User` | owner_user設定 |

### Data Source

| UI | Data Source |
|---|---|
| 画面全体 | Current page's Conversation |
| RG conversations | Search for Conversations where `owner_user = Current User`, sort by `last_message_at desc` |
| current_condition | Current page's Conversation's current_search_condition's current_condition_summary |
| RG condition_chips | Search for SearchConditionItems where `search_condition = Current page's Conversation's current_search_condition` and `is_active = yes` |
| hit_count | Current page's Conversation's `current_result_count` or current RG result count |
| RG property_results | Search for PropertyRegistries using active SearchConditionItems. 検索結果全件はConversationへ保存しない |
| RG messages | Search for Messages where `conversation = Current page's Conversation`, sort by Created Date asc |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button send clicked | Create user `Message` with natural language input |
| Button send clicked | Send message, current `SearchCondition`, active `SearchConditionItem` list, and visible result summary to Claude |
| Claude returns `intent_type = initial_search` | Create/update `SearchCondition` and create `SearchConditionItem` records |
| Claude returns `intent_type = refine_search` | Add/update/remove `SearchConditionItem` records on the current `SearchCondition` |
| Claude returns `intent_type = show_fields` | Update `Conversation.current_display_fields` and RG display state |
| Claude returns `intent_type = analyze_results` | Search current `PropertyRegistry` results, send visible/top results to Claude, save analysis `Message` |
| Search condition changed | Search for `PropertyRegistry` again using active condition items |
| Search condition changed | Save only hit count to `Conversation.current_result_count`, `SearchCondition.result_count`, and `Message.search_result_count` |
| Search condition changed | Do not save all result records to `Conversation` |
| Button remove_condition clicked | Set selected `SearchConditionItem.is_active = no` and re-search `PropertyRegistry` |
| Button detail clicked | Go to page `property_detail`, Data to send = Current cell's PropertyRegistry. 現在Conversation IDをURL parameter等で渡す |
| Button add_candidate clicked | Create new `CandidateProperty` with Current cell's PropertyRegistry and Current page's Conversation |
| Button analyze_row clicked | Send selected property plus current condition summary to Claude and save assistant `Message` |

### 代表的な自然言語入力と処理

| ユーザー入力 | Claudeの解釈 | Bubble処理 |
|---|---|---|
| 中区で収益物件を探して | `location contains 中区` + `income_rank = 収益物件` | `SearchConditionItem` 作成、`PropertyRegistry` 検索 |
| その中で100坪以上 | 既存条件 + 面積条件 | 条件追加、再検索 |
| 法人所有だけ | 既存条件 + `owner_type = 法人所有` | 条件追加、再検索 |
| 所有者を表示 | 表示列に所有者を追加 | `current_display_fields` 更新 |
| 抵当権があるものを除外 | 既存条件 + `has_mortgage = no` | 条件追加、再検索 |

## 4.4 `property_detail` / 物件詳細画面

### 目的

1件の `PropertyRegistry` を詳細表示し、所有者・甲区・乙区・抵当権を確認する。`Claude分析` または `検索へ戻る` を押した場合は、新規Conversation作成ではなく、現在のConversationへ戻ることを優先する。

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
| 上部 | Button back_ai_search | 現在の検索へ戻る |
| 上部 | Button analyze_in_current_conversation | 現在のConversationでClaude分析 |
| 上部 | Button add_candidate | 候補に追加 |
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
| `Conversation` | 現在の検索セッションまたは関連会話 |
| `Message` | 分析結果の保存 |
| `InvestigationNote` | 調査メモ表示・保存。MVPでは簡易 |
| `User` | owner_user設定 |

### Data Source

| UI | Data Source |
|---|---|
| 画面全体 | Current page's PropertyRegistry |
| current_conversation | URL parameter `conversation_id` またはカスタムステートで保持したConversation |
| RG related_conversations | Search for Conversations where `owner_user = Current User` and `related_properties contains Current page's PropertyRegistry` or `target_property = Current page's PropertyRegistry` |
| RG investigation_notes | Search for InvestigationNotes where `owner_user = Current User` and `property = Current page's PropertyRegistry` |
| candidate_status | Search for CandidateProperties where `owner_user = Current User` and `property = Current page's PropertyRegistry`:first item |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Button back_ai_search clicked | If current_conversation exists → Go to page `ai_search`, Data to send = current_conversation |
| Button back_ai_search clicked | If current_conversation empty → Create `Conversation` with `target_property` and go to `ai_search` |
| Button analyze_in_current_conversation clicked | Prefer current_conversation; if empty, create a new Conversation |
| Button analyze_in_current_conversation clicked | Add Current page's PropertyRegistry to `related_properties` if needed |
| Button analyze_in_current_conversation clicked | Create user/assistant `Message` in the current Conversation with selected property context |
| Button analyze_in_current_conversation clicked | Go to page `ai_search`, Data to send = current_conversation |
| Button add_candidate clicked | Create new `CandidateProperty` if not already exists |
| Button add_candidate clicked | Show success alert / change button state |

## 4.5 `candidate_properties` / 候補物件一覧画面

### 目的

保存済み候補物件を一覧表示し、優先度・ステータス・次調査項目を確認する。

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | 共通ヘッダー | 主要画面への導線 |
| 上部 | Filter status | ステータス絞り込み |
| 上部 | Sort priority | 優先度順/作成日順 |
| 上部 | Button ai_search | AI検索へ |
| 一覧 | RG candidates | CandidateProperty一覧 |
| セル | Text building_name | 候補物件名 |
| セル | Text location | 所在 |
| セル | Text owner_name | 所有者 |
| セル | Text status | ステータス |
| セル | Text priority | 優先度 |
| セル | Text next_research | 次調査項目 |
| セル | Button detail | 物件詳細へ |
| セル | Button open_conversation | 関連Conversationへ、なければ新規検索セッション |
| セル | Button remove | 候補から削除 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `CandidateProperty` | 候補一覧の主Data Type |
| `PropertyRegistry` | 候補物件の詳細表示 |
| `Conversation` | 関連Conversationへの導線 |
| `User` | owner_user判定 |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Page is loaded | Search for CandidateProperties where `owner_user = Current User` |
| Filter status changed | Update RG candidates filter |
| Button ai_search clicked | Create or open Conversation → Go to page `ai_search` |
| Button detail clicked | Go to page `property_detail`, Data to send = Current cell's CandidateProperty's property |
| Button open_conversation clicked | If conversation exists → Go to page `ai_search` |
| Button open_conversation clicked | If conversation empty → Create `Conversation` with property → Go to page `ai_search` |
| Button remove clicked | Delete Current cell's CandidateProperty or change status to removed |

## 4.6 `admin` / 管理者画面

### 目的

管理者がログインユーザー管理と物件データベース更新を行う。

### アクセス制御

| 条件 | 動作 |
|---|---|
| Current User is logged out | `login` へ遷移 |
| Current User's is_admin is no | `index` へ遷移 |
| Current User's is_admin is yes | `admin` を表示 |

### UI構成

| エリア | UI要素 | 内容 |
|---|---|---|
| ヘッダー | Text title | 管理者画面 |
| ヘッダー | Button back_index | ダッシュボードへ戻る |
| ユーザー管理 | RG users | ユーザー一覧表示 |
| ユーザー管理 | Button new_user | 新規ユーザー作成 |
| ユーザー管理 | Popup user_form | ユーザー登録・編集フォーム |
| ユーザー管理 | Button delete_user | ユーザー削除 |
| ユーザー管理 | Toggle is_active | 利用停止 |
| ユーザー管理 | Toggle is_admin | 管理者権限設定 |
| 登記データ更新 | FileUploader registry_file | Claude Codeで登記簿謄本から抽出したExcel/CSVをアップロード |
| 登記データ更新 | RG mapping_rows | Excel/CSVカラムと `PropertyRegistry` Fieldのマッピング |
| 登記データ更新 | Button preview_import | インポート前確認 |
| 登記データ更新 | Button replace_all | 全レコード差し替え実行 |
| 登記データ更新 | Popup confirm_replace | 全差し替え確認ダイアログ |
| DB更新履歴 | RG import_logs | ImportLog一覧 |

### 使用Data Type

| Data Type | 用途 |
|---|---|
| `User` | ログインユーザー管理 |
| `PropertyRegistry` | 全レコード差し替え対象 |
| `ImportLog` | 物件DB更新履歴 |

### 実行Workflow

| Trigger | Workflow |
|---|---|
| Page is loaded | If Current User is logged out → Go to page `login` |
| Page is loaded | If Current User's is_admin is no → Go to page `index` |
| Button new_user clicked | Show Popup `user_form` |
| Button save_user clicked | Create new User or Make changes to selected User |
| Button delete_user clicked | Show confirm delete dialog |
| Confirm delete user clicked | Delete selected User |
| Toggle is_active changed | Make changes to User's `is_active` |
| Toggle is_admin changed | Make changes to User's `is_admin` |
| FileUploader registry_file changed | Store uploaded Excel/CSV file |
| Button preview_import clicked | Show column mapping preview |
| Button replace_all clicked | Show Popup `confirm_replace` |
| Confirm replace clicked | Create `ImportLog` with status = running |
| Confirm replace clicked | Delete all existing `PropertyRegistry` records |
| Confirm replace clicked | Import uploaded file rows as new `PropertyRegistry` records |
| Import completed | Update `ImportLog.imported_count`, `error_count`, `status`, `executed_at` |
| Import failed | Update `ImportLog.status = failed`, `memo` |

## 5. MVP画面別Data Type対応表

| 画面 | User | PropertyRegistry | Conversation | Message | CandidateProperty | SearchCondition | SearchConditionItem | InvestigationNote | ImportLog |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `login` | ○ |  |  |  |  |  |  |  |  |
| `index` | ○ | ○ | ○ |  | ○ | ○ |  |  |  |
| `ai_search` | ○ | ○ | ○ | ○ | ○ | ○ | ○ |  |  |
| `property_detail` | ○ | ○ | ○ | ○ | ○ |  |  | ○ |  |
| `candidate_properties` | ○ | ○ | ○ |  | ○ |  |  |  |  |
| `admin` | ○ | ○ |  |  |  |  |  |  | ○ |

## 6. MVP画面別Workflow対応表

| 画面 | 主なWorkflow |
|---|---|
| `login` | 管理者が作成した社内ユーザーのログイン、利用停止判定、ログイン後ダッシュボード遷移 |
| `index` | 新規検索セッション作成、最近のConversation再開、候補物件遷移、管理者のみadmin遷移 |
| `ai_search` | 自然文検索、検索条件変換、追加絞り込み、PropertyRegistry再検索、検索結果表示、Claude分析、候補保存 |
| `property_detail` | 物件情報表示、候補追加、現在Conversationへの復帰、現在ConversationでのClaude分析 |
| `candidate_properties` | 候補一覧表示、ステータス更新、優先度更新、物件詳細遷移、関連Conversation遷移 |
| `admin` | ユーザー作成・削除・利用停止・管理者権限設定、PropertyRegistry全削除、Excel/CSV全件再登録、ImportLog保存 |

## 7. 実装優先順位

### Phase 1: 最小導線

1. `login`
2. `index`
3. `ai_search`
4. `property_detail`
5. `candidate_properties`
6. `admin`

### Phase 2: 検索セッション品質向上

1. `SearchConditionItem` の条件チップ操作
2. 表示列変更指示への対応
3. 検索結果のClaude分析
4. 候補保存時の理由・要約保存

### Phase 3: 管理者機能強化

1. `User` 管理の操作ログ
2. `ImportLog` 詳細表示
3. `PropertyRegistry` 全差し替え前プレビュー強化

## 8. 画面設計上の注意点

- CRMではないため、顧客詳細画面、商談詳細画面、追客履歴画面、契約管理画面はMVPでは作らない。
- 社内向けシステムのため、一般ユーザー向けサインアップ画面はMVPでは作らない。ユーザーアカウントは管理者が `admin` 画面で作成・削除・管理する。
- `property_search` と `search_conditions` は作らず、`ai_search` に自然言語検索、追加絞り込み、検索結果表示、Claude会話を統合する。
- 検索条件は `Conversation.current_search_condition`、`SearchCondition`、`SearchConditionItem` に保持する。
- 検索結果全件は `Conversation` に保存せず、現在条件で `PropertyRegistry` を都度再検索して取得する。
- 所有者情報・抵当権情報は個人情報やセンシティブ情報を含む可能性があるため、Privacy Rulesとログイン必須制御を前提にする。
- `admin` 画面は `Current User's is_admin = yes` のユーザーのみアクセス可能とし、非管理者は `index` にリダイレクトする。
- `PropertyRegistry` 全差し替え更新は管理者のみ実行可能とし、実行前に確認ダイアログを必ず表示する。
- Claude回答は法的判断ではなく、検索条件解釈・結果分析・調査支援として表示する。
- Bubbleではページ遷移時にData to sendを使い、`property_detail` は `PropertyRegistry`、`ai_search` は `Conversation` をType of contentにする。
