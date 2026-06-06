# ai_search Issues 修正手順

## 1. 要件確認

現在の作業対象は、Bubble AIで生成された `ai_search` ページのIssues修正である。アプリを再生成せず、既存ページ・既存Data Typeを使って、以下4点を優先して直す。

1. `ai_search` の検索結果Repeating Groupを `PropertyRegistry` 一覧として成立させる。
2. 検索結果セル内の参照を、すべて `Current cell's PropertyRegistry` または `Parent group's PropertyRegistry` に統一する。
3. 候補保存Workflowで `CandidateProperty.property_registry`、`CandidateProperty.user`、`CandidateProperty.conversation` を空にしない。
4. 物件分析Workflowで作成する `Message.conversation` を空にしない。

今回の修正では、新規ページ、新規Data Type、`Conversation.current_search_results`、`property_search`、`search_conditions` は作らない。

## 2. DB設計

Bubble AI生成済みField名を正とする。正式設計名に合わせるためだけの重複Fieldは作らない。

| Data Type | Bubbleで使うField | Type | 設定値 |
|---|---|---|---|
| `Conversation` | `current_search_condition` | `SearchCondition` | 現在の検索条件 |
| `SearchCondition` | `summary` | text | 条件要約。正式設計の `current_condition_summary` 相当 |
| `SearchConditionItem` | `search_condition` | `SearchCondition` | 親条件 |
| `SearchConditionItem` | `field` | text | 正式設計の `field_name` 相当 |
| `SearchConditionItem` | `value` | text | 正式設計の `value_text` 相当 |
| `Message` | `conversation` | `Conversation` | 必須。`Current page Conversation` を入れる |
| `Message` | `role` | text | `user` / `assistant` |
| `Message` | `intent_type` | text | `analyze_results` など |
| `Message` | `content` | text | 表示する本文 |
| `CandidateProperty` | `property_registry` | `PropertyRegistry` | 必須。結果セルの物件を入れる |
| `CandidateProperty` | `user` | `User` | 必須。`Current User` を入れる |
| `CandidateProperty` | `conversation` | `Conversation` | 必須。`Current page Conversation` を入れる |
| `CandidateProperty` | `status` | text | 初期値 `未調査` |

## 3. API設計

この修正フェーズではClaude API Connectorはまだ触らない。`Button analyze_row` は、API実行前の最小Workflowとしてユーザー意図を `Message` に保存するところまでを正しく成立させる。

将来APIへ渡す最小payloadは、Bubble上で次の値を参照できる状態にしてから組む。

| Payload項目 | Bubble参照元 |
|---|---|
| `conversation_id` | `Current page Conversation's unique id` |
| `intent_type` | 固定値 `analyze_results` |
| `property_id` | `Parent group's PropertyRegistry's unique id` |
| `property_summary` | `Parent group's PropertyRegistry` の所在地・建物名・所有者・用途・抵当権状態 |
| `condition_summary` | `Current page Conversation's current_search_condition's summary` |

## 4. 画面設計

### 4.1 Page設定

`ai_search` ページは必ず次の設定にする。

| 設定 | 値 |
|---|---|
| Type of content | `Conversation` |
| Data source | 空でよい。遷移元WorkflowからData to sendで渡す |

`Current page Conversation` が空のままでは `CandidateProperty.conversation` と `Message.conversation` が空になる。したがって、`index`、会話一覧、新規検索ボタンなど、すべての `ai_search` 遷移で `Data to send = 対象の Conversation` を設定する。

### 4.2 検索結果Repeating Group

`RG property_results` は次の設定にする。

| 設定 | 値 |
|---|---|
| Type of content | `PropertyRegistry` |
| Data source | `Search for PropertyRegistries` |

条件変換が未完成の間は、まず無条件の `Search for PropertyRegistries` で型エラーを解消する。条件絞り込みは `SearchConditionItem` から検索式を組めるようになってから追加する。

### 4.3 結果セル構造

`RG property_results` のセル直下に行グループを置き、必ず次の設定にする。

| Element | Type of content | Data source |
|---|---|---|
| `rg-result-row` | `PropertyRegistry` | `Current cell's PropertyRegistry` |
| `rg-cell-actions` | `PropertyRegistry` | `Parent group's PropertyRegistry` または `Current cell's PropertyRegistry` |

結果セル内のTextは、行グループ配下に置き、`Parent group's PropertyRegistry` から参照する。

| Text | Bubble expression |
|---|---|
| 所在 | `Parent group's PropertyRegistry's location` |
| 建物名 | `Parent group's PropertyRegistry's building_name` |
| 所有者 | `Parent group's PropertyRegistry's owner_name` |
| 種別 | `Parent group's PropertyRegistry's registry_type` |
| 用途分類 | `Parent group's PropertyRegistry's use_category` |
| 土地面積 | `Parent group's PropertyRegistry's land_area_sqm:formatted as text` |
| 建物面積 | `Parent group's PropertyRegistry's building_area_sqm:formatted as text` |
| 抵当権状態 | `Parent group's PropertyRegistry's mortgage_status` |
| 抵当権有無 | `Parent group's PropertyRegistry's has_mortgage:formatted as text` |

number型とyes/no型はTextへ直接入れず、必ず `:formatted as text` を付ける。

## 5. Workflow設計

### 5.1 詳細ボタン

`Button detail` のWorkflowは次の設定にする。

| Action | 設定 |
|---|---|
| Go to page | `property_detail` |
| Data to send | `Parent group's PropertyRegistry` |

### 5.2 候補保存ボタン

`Button add_candidate` は `RG property_results` セル内の行グループ配下に置く。Workflowは次の設定にする。

| Action | 設定 |
|---|---|
| Create a new thing | Type = `CandidateProperty` |
| `property_registry` | `Parent group's PropertyRegistry` |
| `user` | `Current User` |
| `conversation` | `Current page Conversation` |
| `status` | `未調査` |

任意で重複保存防止Conditionを追加する場合は、次の条件にする。

```text
Only when Search for CandidateProperties
  where user = Current User
  and property_registry = Parent group's PropertyRegistry
  and conversation = Current page Conversation
  :count is 0
```

### 5.3 物件分析Message作成ボタン

`Button analyze_row` は `RG property_results` セル内の行グループ配下に置く。Claude API未接続の現段階では、まず次の `Message` 作成WorkflowでIssueを消す。

| Action | 設定 |
|---|---|
| Create a new thing | Type = `Message` |
| `conversation` | `Current page Conversation` |
| `role` | `user` |
| `intent_type` | `analyze_results` |
| `content` | `この物件を分析して` |

将来、選択物件をMessageに紐づけるFieldを使う場合だけ、`referenced_properties` に `Parent group's PropertyRegistry` をリストとして追加する。ただし、今回のIssue修正では空の `conversation` を埋めることを最優先にする。

### 5.4 修正後のIssue確認順

1. `ai_search` ページの `Current page Conversation` 参照エラーが消えていること。
2. `RG property_results` が `PropertyRegistry` 型になっていること。
3. 結果セル内の全Textが `Parent group's PropertyRegistry` 参照になっていること。
4. number型・yes/no型Textに `:formatted as text` が付いていること。
5. `CandidateProperty` 作成Actionの `property_registry`、`user`、`conversation` が空でないこと。
6. `Message` 作成Actionの `conversation` が `Current page Conversation` になっていること。
