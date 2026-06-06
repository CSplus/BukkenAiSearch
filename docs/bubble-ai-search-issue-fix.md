# Bubble Issues 修正手順（73件対応）

## 1. 要件確認

現在の目的は、Bubble AIで生成された `BukkenAiSearch` のIssue Checkerエラー73件を、アプリ再生成ではなく既存ページ・既存Data Typeの設定修正で解消することである。

修正対象はスクリーンショット上で確認できる次のページである。

| 優先 | Page | 主なエラー種別 | ゴール |
|---|---|---|---|
| 1 | `ai_search` | `Conversation` / `SearchCondition` / `PropertyRegistry` の単体・リスト型不一致、Current page thing未設定、Textに非text式、削除対象empty | 自然言語検索セッション画面として、Conversationを受け取り、PropertyRegistry一覧を表示し、候補保存・分析Message作成ができる状態にする |
| 2 | `candidate_properties` | `CandidateProperty` と `PropertyRegistry` の型不一致、numberとtextの比較、`:sorted` 不正 | 候補一覧からPropertyRegistry詳細へ遷移できる状態にする |
| 3 | `property_detail` | `Header` / `ContentArea` / `Row_*` / `OwnerSection` / `MortgageSection` / `DocumentSection` など「is not a possible option」 | 削除・改名された要素参照をなくし、Current page PropertyRegistryだけで詳細表示できる状態にする |

今回の修正では、次の対応は行わない。

- アプリ全体の再生成
- 新規ページ追加
- 重複Data Type / 重複Field追加
- `Conversation.current_search_results` の追加
- `property_search` / `search_conditions` の復活
- Claude API Connectorの本実装

## 2. DB設計

Issue解消ではDBを増やさず、既存Data Typeの型にBubble式を合わせる。正式設計名とBubble AI生成名がずれている場合は、Bubbleに実在するFieldを優先する。

| Data Type | Field | Type | Issue修正時の使い方 |
|---|---|---|---|
| `Conversation` | `current_search_condition` | `SearchCondition` | `ai_search` の条件チップ・条件要約の親。Listではなく単体として扱う |
| `SearchCondition` | `summary` または `current_condition_summary` | text | 条件要約Textに表示する。実在する方だけ使う |
| `SearchConditionItem` | `search_condition` | `SearchCondition` | 条件チップ一覧の絞り込み条件に使う |
| `SearchConditionItem` | `field` または `field_name` | text | 条件チップの項目名。実在する方だけ使う |
| `SearchConditionItem` | `value` または `value_text` | text | 条件チップの値。実在する方だけ使う |
| `PropertyRegistry` | `location` / `building_name` / `owner_name` など | text | 検索結果・詳細画面の表示元 |
| `PropertyRegistry` | `land_area_sqm` / `building_area_sqm` など | number | Text表示時は必ず `:formatted as text` を付ける |
| `PropertyRegistry` | `has_mortgage` | yes/no | Text表示時は必ず `:formatted as text` を付ける |
| `Message` | `conversation` | `Conversation` | `Create a new Message` で必ず `Current page Conversation` を入れる |
| `Message` | `content` | text | Text式だけを入れる。PropertyRegistry本体などObjectを直接入れない |
| `CandidateProperty` | `property_registry` | `PropertyRegistry` | 候補保存時は結果セルの `Parent group's PropertyRegistry` を入れる |
| `CandidateProperty` | `user` | `User` | 候補保存時は `Current User` を入れる |
| `CandidateProperty` | `conversation` | `Conversation` | 候補保存時は `Current page Conversation` を入れる |
| `CandidateProperty` | `status` | text | 初期値は `未調査` |

### 型不一致の基本ルール

| エラー文 | 原因 | 修正方針 |
|---|---|---|
| `value should be X but right now it is a List of X` | 単体が必要な場所に検索結果リストを入れている | `Current page ...`、`Current cell's ...`、`Parent group's ...`、または `:first item` にする |
| `value should be List of X but right now it is X` | Repeating Groupなどリストが必要な場所に単体を入れている | `Search for Xs` や `Parent group's X's list field` にする |
| `right now it is a empty` | Page type / Group type / Data source / Data to send が未設定 | 参照元のType of contentとData sourceを先に設定する |
| `Dynamic data in text boxes must be printable as text` | TextにThing、List、yes/no、numberなどを直接入れている | text Fieldを選ぶ。number / yes-no / dateは `:formatted as text` を付ける |
| `is not a possible option` | 削除・改名されたElementや、存在しない演算子を参照している | 式を開いて赤字の参照を削除し、現存Element / 正しいOperatorへ差し替える |

## 3. API設計

このIssue解消フェーズではClaude API Connectorは触らない。`ai_search` の `Button analyze_row` は、API呼び出し前の最小Workflowとしてユーザーの分析依頼を `Message` に保存できればよい。

将来Claude APIへ渡すpayloadは、Bubble上で次の値が安定して参照できるようになってから組む。

| Payload項目 | Bubble参照元 |
|---|---|
| `conversation_id` | `Current page Conversation's unique id` |
| `intent_type` | 固定値 `analyze_results` |
| `property_id` | `Parent group's PropertyRegistry's unique id` |
| `property_summary` | `Parent group's PropertyRegistry` の所在地・建物名・所有者・用途・抵当権状態をtext結合 |
| `condition_summary` | `Current page Conversation's current_search_condition's summary` または実在する要約Field |

## 4. 画面設計

### 4.1 `ai_search` Page設定

`Current page's thing - ... this page does not accept data...` を消すため、ページ自体を次の設定にする。

| 設定 | 値 |
|---|---|
| Type of content | `Conversation` |
| Data source | 空でよい。遷移元WorkflowからData to sendで渡す |

`ai_search` へ遷移するすべてのWorkflowは、必ず `Data to send = 対象の Conversation` を設定する。

| 遷移元 | Action例 | Data to send |
|---|---|---|
| `index` 新規検索 | Step 1: Create a new Conversation → Step 2: Go to page `ai_search` | `Result of step 1` |
| `index` 最近の会話 | Go to page `ai_search` | `Current cell's Conversation` |
| `property_detail` 検索へ戻る | Go to page `ai_search` | 保持している `Conversation`。なければボタンを非表示またはWorkflow削除 |

### 4.2 `ai_search` 検索条件エリア

スクリーンショットの次のエラーは、`SearchCondition` の単体・リスト混在が原因である。

- `Group conditions-summary-group: Data source should be SearchCondition but right now it is a List of SearchConditions`
- `Search for SearchConditions: value should be Conversation but right now it is a empty`
- `Search for SearchConditionItems: value should be SearchCondition but right now it is a List of SearchConditions`

修正設定は次のとおり。

| Element | Type of content | Data source / Expression |
|---|---|---|
| `conditions-summary-group` | `SearchCondition` | `Current page Conversation's current_search_condition` |
| 条件要約Text | なし | `Parent group's SearchCondition's summary` または実在する要約Field |
| 条件チップRepeating Group | `SearchConditionItem` | `Search for SearchConditionItems where search_condition = Current page Conversation's current_search_condition` |
| `chip-item` Group | `SearchConditionItem` | `Current cell's SearchConditionItem` |
| `chip-delete-btn` | なし | Parentが `SearchConditionItem` 型のGroup配下にあること |

`Delete thing... To delete should be anything saveable but right now it is a empty` は、削除ボタンの親Groupに型がないことが原因である。`chip-delete-btn` を `chip-item` Group配下に置き、Delete対象を `Parent group's SearchConditionItem` にする。

### 4.3 `ai_search` 検索結果エリア

スクリーンショットの次のエラーは、検索結果を表示するGroupとRepeating Groupの役割が混ざっていることが原因である。

- `Group hit-count-group: Data source should be PropertyRegistry but right now it is a number`
- `Group results-grid: Data source should be PropertyRegistry but right now it is a List of PropertyRegistrys`
- `Group rg-result-row: Data source should be PropertyRegistry but right now it is a empty`
- `Group rg-cell-actions: Data source should be PropertyRegistry but right now it is a empty`

修正設定は次のとおり。

| Element | Type of content | Data source / Expression |
|---|---|---|
| `hit-count-group` | 空 | 空。数値を表示するTextだけを中に置く |
| ヒット件数Text | なし | `Search for PropertyRegistries:count:formatted as text` |
| `results-grid` | 空 | 空。中にRepeating Groupを置くための見た目用Groupにする |
| `RG property_results` | `PropertyRegistry` | `Search for PropertyRegistries` |
| `rg-result-row` | `PropertyRegistry` | `Current cell's PropertyRegistry` |
| `rg-cell-actions` | `PropertyRegistry` | `Parent group's PropertyRegistry` |

条件検索が未完成の間は、`RG property_results` のData sourceを無条件の `Search for PropertyRegistries` にして、まず型エラーを消す。条件絞り込みはIssueが0になってから追加する。

### 4.4 `ai_search` 結果セル内Text

`Dynamic data in text boxes must be printable as text...` は、Textに `PropertyRegistry` 本体やnumber / yes-noを直接入れていることが原因である。結果セル内Textはすべて `rg-result-row` Group配下に置き、次の式へ差し替える。

| 表示 | Bubble expression |
|---|---|
| 所在 | `Parent group's PropertyRegistry's location` |
| 建物名 | `Parent group's PropertyRegistry's building_name` |
| 所有者 | `Parent group's PropertyRegistry's owner_name` |
| 種別 | `Parent group's PropertyRegistry's registry_type` |
| 用途分類 | `Parent group's PropertyRegistry's use_category` |
| 所有者住所 | `Parent group's PropertyRegistry's owner_address` |
| 所有者区分 | `Parent group's PropertyRegistry's owner_type` |
| 土地面積 | `Parent group's PropertyRegistry's land_area_sqm:formatted as text` |
| 建物面積 | `Parent group's PropertyRegistry's building_area_sqm:formatted as text` |
| 延床面積 | `Parent group's PropertyRegistry's total_floor_area_sqm:formatted as text` |
| 抵当権状態 | `Parent group's PropertyRegistry's mortgage_status` |
| 抵当権有無 | `Parent group's PropertyRegistry's has_mortgage:formatted as text` |
| 債権額 | `Parent group's PropertyRegistry's mortgage_amount` |
| 抵当権者 | `Parent group's PropertyRegistry's mortgage_holder` |

### 4.5 `candidate_properties` Page設定

スクリーンショットの次のエラーを解消する。

- `Display data: Data to display should be PropertyRegistry but right now it is a CandidateProperty`
- `Search for CandidatePropertys: value should be number but right now it is a text`
- `:sorted - is not a possible option`

候補一覧のRepeating Groupは `CandidateProperty` を表示し、詳細画面へ送るときだけ `property_registry` を送る。

| Element / Workflow | 設定 |
|---|---|
| `RG candidate_properties` Type of content | `CandidateProperty` |
| `RG candidate_properties` Data source | `Search for CandidateProperties where user = Current User` |
| 候補セルGroup Type of content | `CandidateProperty` |
| 候補セルGroup Data source | `Current cell's CandidateProperty` |
| 候補セル内の物件表示 | `Parent group's CandidateProperty's property_registry's location` など、`property_registry` のFieldまで降りる |
| 詳細表示Workflow | Go to page `property_detail` / Data to send = `Parent group's CandidateProperty's property_registry` |

numberエラーは、検索条件でnumber Fieldにtext Inputをそのまま比較している箇所を直す。

| NG | OK |
|---|---|
| `land_area_sqm >= Input min_area's value` ただしInputがtext | InputのContent formatをInteger/Decimalにする |
| text Inputを維持したままnumber比較 | `Input min_area's value:converted to number` を使う |
| 空文字のままnumber比較 | `Only when Input min_area's value is not empty` を付ける、または条件を一旦削除する |

`:sorted - is not a possible option` は、式の末尾に壊れた `:sorted` が残っている状態である。Data sourceを開き、次のどちらかへ直す。

| 用途 | 修正 |
|---|---|
| 作成日順に並べたい | `Search for CandidateProperties:sorted by Created Date descending yes` |
| まずIssueを消したい | 壊れた `:sorted` 部分を削除する |

### 4.6 `property_detail` Page設定

スクリーンショットの次のエラーは、削除・改名されたElement参照が式やWorkflowに残っている状態である。

- `Header - is not a possible option`
- `ContentArea - is not a possible option`
- `LocationSection - is not a possible option`
- `Row_location - is not a possible option`
- `Row_buildingName - is not a possible option`
- `Row_registryType - is not a possible option`
- `Row_useCategory - is not a possible option`
- `Row_incomeRank - is not a possible option`
- `OwnerSection - is not a possible option`
- `Row_ownerName - is not a possible option`
- `Row_ownerAddress - is not a possible option`
- `Row_ownerType - is not a possible option`
- `MortgageSection - is not a possible option`
- `Row_mortgageStatus - is not a possible option`
- `Row_hasMortgage - is not a possible option`
- `Row_mortgageAmount - is not a possible option`
- `Row_mortgageHolder - is not a possible option`
- `DocumentSection - is not a possible option`
- `Row_issuedDate - is not a possible option`

まずPage設定を次にする。

| 設定 | 値 |
|---|---|
| Type of content | `PropertyRegistry` |
| Data source | 空でよい。遷移元WorkflowからData to sendで渡す |

次に、Issue Checkerで各エラーをクリックし、右パネルで赤字になっている存在しないElement参照を削除する。復旧方法は2択である。

| 状況 | 修正方法 |
|---|---|
| そのElementが画面上に不要 | 参照しているConditional / Workflow / Animation / Data sourceを削除する |
| そのElementが必要 | 同名でGroupを作り直すのではなく、現存するGroupを選び直して式を再構築する |

詳細表示Textは、削除済みElement名に依存させず、すべて `Current page PropertyRegistry` から直接表示する。

| 表示 | Bubble expression |
|---|---|
| 所在 | `Current page PropertyRegistry's location` |
| 建物名 | `Current page PropertyRegistry's building_name` |
| 種別 | `Current page PropertyRegistry's registry_type` |
| 用途分類 | `Current page PropertyRegistry's use_category` |
| 収益区分 | `Current page PropertyRegistry's income_rank` |
| 所有者 | `Current page PropertyRegistry's owner_name` |
| 所有者住所 | `Current page PropertyRegistry's owner_address` |
| 所有者区分 | `Current page PropertyRegistry's owner_type` |
| 抵当権状態 | `Current page PropertyRegistry's mortgage_status` |
| 抵当権有無 | `Current page PropertyRegistry's has_mortgage:formatted as text` |
| 債権額 | `Current page PropertyRegistry's mortgage_amount` |
| 抵当権者 | `Current page PropertyRegistry's mortgage_holder` |
| 発行日 | `Current page PropertyRegistry's issued_date` または `:formatted as text` |

## 5. Workflow設計

### 5.1 `ai_search` への遷移Workflow

`ai_search` は `Conversation` を受け取るページなので、すべての遷移でData to sendを入れる。

| Workflow | Actions |
|---|---|
| 新規検索開始 | Step 1: Create a new Conversation（`owner_user = Current User`, `title = Input search's value` など）→ Step 2: Go to page `ai_search`, Data to send = `Result of step 1` |
| 既存会話再開 | Go to page `ai_search`, Data to send = `Current cell's Conversation` |

### 5.2 `ai_search` 詳細ボタン

| Action | 設定 |
|---|---|
| Go to page | `property_detail` |
| Data to send | `Parent group's PropertyRegistry` |

### 5.3 `ai_search` 候補保存ボタン

`Button add_candidate` は `RG property_results` セル内の `rg-result-row` または `rg-cell-actions` 配下に置く。

| Action | 設定 |
|---|---|
| Create a new thing | Type = `CandidateProperty` |
| `property_registry` | `Parent group's PropertyRegistry` |
| `user` | `Current User` |
| `conversation` | `Current page Conversation` |
| `status` | `未調査` |

重複保存防止Conditionを付ける場合は次の条件にする。

```text
Only when Search for CandidateProperties
  where user = Current User
  and property_registry = Parent group's PropertyRegistry
  and conversation = Current page Conversation
  :count is 0
```

### 5.4 `ai_search` 物件分析Message作成ボタン

Claude API未接続の現段階では、まず `Message.conversation` が空にならないWorkflowにする。

| Action | 設定 |
|---|---|
| Create a new thing | Type = `Message` |
| `conversation` | `Current page Conversation` |
| `role` | `user` |
| `intent_type` | `analyze_results` |
| `content` | `この物件を分析して: ` + `Parent group's PropertyRegistry's location` |

### 5.5 `candidate_properties` 詳細表示Workflow

| Action | 設定 |
|---|---|
| Go to page | `property_detail` |
| Data to send | `Parent group's CandidateProperty's property_registry` |

`CandidateProperty` 自体を送ると、`property_detail` 側で `Data to display should be PropertyRegistry but right now it is a CandidateProperty` が発生する。

### 5.6 `property_detail` 削除済みElement参照の直し方

Issue Checkerで `Header - is not a possible option` などをクリックし、該当Workflow / Conditional / Data sourceの赤字部分を次の方針で直す。

1. 存在しないElement名を式から削除する。
2. 必要な条件は `Current page PropertyRegistry` 起点で作り直す。
3. 見た目だけのGroupにType of contentを設定しない。
4. Text表示はObjectではなくFieldまで選ぶ。
5. number / yes-no / dateは必要に応じて `:formatted as text` を付ける。

## 6. Issue Checkerでの推奨修正順

73件を上から順に直すより、型の根元から直す方が早い。次の順で確認する。

1. `ai_search` PageのType of contentを `Conversation` にする。
2. `ai_search` への全遷移でData to sendにConversationを入れる。
3. `conditions-summary-group` を `Current page Conversation's current_search_condition` にする。
4. 条件チップRepeating Groupを `SearchConditionItem` のリストにする。
5. `chip-delete-btn` の削除対象を `Parent group's SearchConditionItem` にする。
6. `results-grid` / `hit-count-group` など見た目用GroupのType of contentとData sourceを空にする。
7. `RG property_results` だけを `PropertyRegistry` リストにする。
8. 結果セルGroupを `Current cell's PropertyRegistry` にする。
9. 結果セル内TextをPropertyRegistryのField参照へ直す。
10. `add_candidate` Workflowで `property_registry`、`user`、`conversation` を埋める。
11. `analyze_row` Workflowで `Message.conversation` を埋める。
12. `candidate_properties` の詳細遷移で `CandidateProperty.property_registry` を送る。
13. `candidate_properties` のnumber比較Inputをnumber形式または `:converted to number` にする。
14. 壊れた `:sorted` を `:sorted by ...` へ直すか削除する。
15. `property_detail` PageのType of contentを `PropertyRegistry` にする。
16. `property_detail` の削除済みElement参照をすべて削除または現存Elementへ差し替える。
17. Issue Checkerの `Run checks on backend workflows` を実行して残件を確認する。

## 7. 修正後チェックリスト

| チェック | OK条件 |
|---|---|
| `ai_search` Page | Type of contentが `Conversation` |
| `ai_search` 遷移 | Data to sendがConversation |
| 条件要約 | 単体 `SearchCondition` を参照している |
| 条件チップ | `SearchConditionItem` のリストを表示している |
| 条件削除 | Delete対象が `Parent group's SearchConditionItem` |
| 検索結果RG | Type of contentが `PropertyRegistry`、Data sourceがList of PropertyRegistry |
| 結果セル | `Current cell's PropertyRegistry` または `Parent group's PropertyRegistry` 起点 |
| Text | Object直出しなし。number / yes-noはformatted |
| 候補保存 | `CandidateProperty.property_registry` / `user` / `conversation` が空でない |
| 分析Message | `Message.conversation` が `Current page Conversation` |
| 候補詳細遷移 | `property_detail` に `PropertyRegistry` を送っている |
| 詳細画面 | Type of contentが `PropertyRegistry` |
| 壊れたElement参照 | `Header` / `Row_*` などの赤字参照が残っていない |
| 並び替え | `:sorted` 単独ではなく `:sorted by Field`、または削除済み |
