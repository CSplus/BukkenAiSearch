# Bubble Data Type 設計案

正式版 `requirements.md` に基づき、次工程として **DB設計** を整理します。  
今回の設計では、`PropertyRegistry` を中核Data Typeとし、AIチャット、候補物件保存、調査メモ、検索条件、Claude設定をその周辺に配置します。正式要件でも、`PropertyRegistry` は登記情報・物件情報を検索可能な形で管理する中核Data Typeと定義されています。 docs/requirements.md:345-384

---

## 0. 設計方針

## 0.1 中心に置くData Type

中心は以下です。

```text
PropertyRegistry
```

`PropertyRegistry` は、登記PDF由来のExcel/CSVデータをBubble内で検索可能にするための登記物件DBです。候補物件探索、所有者確認、権利関係確認、Claude相談の入力文脈として利用します。正式要件でも、登記データ本体はKnowledge資料ではなく `PropertyRegistry` として分離して扱う方針です。 docs/requirements.md:291-292

---

## 0.2 MVPでのDB設計方針

MVPでは、まず **1つの `PropertyRegistry` レコードに物件基本情報・所有者情報・甲区情報・乙区情報を持たせる設計** を推奨します。

理由は以下です。

- Bubbleで実装しやすい
- CSV/Excel取り込み時に扱いやすい
- 物件検索画面を早く作れる
- 物件詳細からClaudeへ渡す文脈を作りやすい
- MVP範囲では「複数所有者」「複数抵当権」の完全な正規化より、まず検索・詳細・Claude相談を優先すべき

ただし、正式要件上も「同一物件に複数所有者・複数抵当権がある場合のデータ構造」は未実装・要確認項目です。 docs/requirements.md:778-783

そのため、将来的には以下のように分離する余地を残します。

```text
PropertyRegistry
  ├─ RegistryOwner
  └─ RegistryMortgage
```

ただし、これはMVP後の拡張候補とします。

---

# 1. Data Type一覧

正式要件に記載されている主なData Typeは以下です。 docs/requirements.md:294-306

| 優先度 | Data Type | 目的 | MVP対象 |
|---|---|---|---|
| 高 | `User` | 利用者・権限管理 | 対象 |
| 高 | `PropertyRegistry` | 登記物件DB・物件調査の中核 | 対象 |
| 高 | `Conversation` | Claude相談の会話単位 | 対象 |
| 高 | `Message` | ユーザー発言・Claude回答 | 対象 |
| 高 | `CandidateProperty` | 候補物件保存 | 対象 |
| 中 | `SearchCondition` | 物件探索条件の保存 | MVP簡易対象 |
| 中 | `InvestigationNote` | 物件・会話ごとの調査メモ | MVP後半または次フェーズ |
| 中 | `AiProject` | Claude設定管理 | 既存設定を活用 |
| 中 | `KnowledgeDocument` | Claude参照資料管理 | MVP後半または次フェーズ |

---

# 2. 推奨Data Type構成

## 2.1 `User`

## 目的

Bubble標準のUserを拡張し、営業担当者・管理者を識別します。

正式要件では、`User` に `email`、`name`、`role`、`company_name`、`is_admin` を持たせる方針です。 docs/requirements.md:308-316

## フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `email` | text | no | yes | Bubble標準ログイン用メール |
| `name` | text | no | no | 表示名 |
| `role` | text | no | no | 営業担当者 / 管理者など |
| `company_name` | text | no | no | 所属会社 |
| `is_admin` | yes/no | no | no | 管理者判定 |

## Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N Conversation | `Conversation.owner_user` |
| User 1 : N CandidateProperty | `CandidateProperty.owner_user` |
| User 1 : N SearchCondition | `SearchCondition.owner_user` |
| User 1 : N InvestigationNote | `InvestigationNote.owner_user` |
| User 1 : N AiProject | `AiProject.owner_user` |
| User 1 : N KnowledgeDocument | `KnowledgeDocument.owner_user` |

## Bubble実装メモ

`User` 側に `conversations` などのListを持たせるより、各Data Type側に `owner_user` を持たせて `Search for Conversations where owner_user = Current User` の形で検索する方が扱いやすいです。

---

# 3. `PropertyRegistry`

## 3.1 目的

`PropertyRegistry` は本システムの中核Data Typeです。

主な用途は以下です。

- 登記情報の保存
- 物件情報の保存
- 物件検索
- 所有者確認
- 権利関係確認
- 抵当権確認
- 物件詳細表示
- Claude相談時の文脈生成
- 候補物件保存の参照元

正式要件でも、`PropertyRegistry` は「登記情報・物件情報を検索可能な形で管理する中核Data Type」と定義されています。 docs/requirements.md:342-347

---

## 3.2 フィールド一覧

### A. 識別・取込系

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `area_group` | text | no | no | 地域 |
| `registry_type` | text | no | yes | 種別。建物・土地・地図など |
| `pdf_url` | text | no | no | 登記PDFリンク |
| `property_number` | text | no | no | 不動産番号 |
| `issued_date` | date | no | no | 発行日 |
| `source_file_name` | text | no | no | 取込元ファイル名。MVPでは任意 |
| `imported_at` | date | no | no | 取込日時。MVPでは任意 |
| `import_memo` | text | no | no | 取込時メモ。MVPでは任意 |

正式要件では、`area_group`、`registry_type`、`pdf_url`、`property_number`、`issued_date` が `PropertyRegistry` の項目として定義されています。 docs/requirements.md:349-384

---

### B. 所在・物件特定情報

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `location` | text | no | yes | 所在 |
| `land_number` | text | no | no | 地番 |
| `building_number` | text | no | no | 家屋番号 |
| `building_name` | text | no | no | 建物の名称 |

正式要件でも、`location`、`land_number`、`building_number`、`building_name` が `PropertyRegistry` の主要項目として定義されています。 docs/requirements.md:355-358

---

### C. 土地情報

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `land_category` | text | no | no | 地目 |
| `land_area_sqm` | number | no | no | 地積 |

正式要件では、`land_category` と `land_area_sqm` が土地情報として定義されています。 docs/requirements.md:359-366

---

### D. 建物情報

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `building_type` | text | no | no | 建物の種類 |
| `use_category` | text | no | no | 用途分類 |
| `income_rank` | text | no | no | 収益区分 |
| `is_condo_unit` | yes/no | no | no | 区分建物かどうか |
| `structure` | text | no | no | 建物の構造 |
| `floors` | number | no | no | 階数 |
| `building_area_sqm` | number | no | no | 建築面積 |
| `total_floor_area_sqm` | number | no | no | 延床面積 |
| `exclusive_area_sqm` | number | no | no | 専有面積 |
| `max_area_sqm` | number | no | no | 最大面積 |

正式要件では、用途分類、収益区分、構造、階数、建築面積、延床面積、専有面積などが `PropertyRegistry` に含まれています。 docs/requirements.md:360-370

---

### E. 甲区情報 / 所有者情報

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `ownership_rank` | number | no | no | 甲区_順位 |
| `ownership_purpose` | text | no | no | 甲区_目的 |
| `ownership_date` | text | no | no | 甲区_受付日 |
| `ownership_cause` | text | no | no | 甲区_原因 |
| `owner_name` | text | no | yes | 甲区_所有者 |
| `owner_address` | text | no | no | 甲区_所有者住所 |

正式要件では、所有者名・所有者住所を含む甲区情報が `PropertyRegistry` の項目として定義されています。 docs/requirements.md:371-376

---

### F. 乙区情報 / 抵当権情報

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `mortgage_status` | text | no | no | 乙区_状態 |
| `mortgage_rank` | number | no | no | 乙区_順位 |
| `mortgage_purpose` | text | no | no | 乙区_目的 |
| `mortgage_date` | text | no | no | 乙区_受付日 |
| `mortgage_cause` | text | no | no | 乙区_原因 |
| `mortgage_amount` | text | no | no | 乙区_債権額 |
| `mortgage_holder` | text | no | no | 乙区_抵当権者 |

正式要件では、抵当権状態、順位、目的、受付日、原因、債権額、抵当権者が `PropertyRegistry` に含まれています。 docs/requirements.md:377-384

---

### G. Claude連携用の補助フィールド

要件書には明示されていませんが、Bubble実装上は以下を追加すると便利です。

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `ai_summary` | text | no | no | Claudeによる物件要約 |
| `rights_summary` | text | no | no | 権利関係サマリー |
| `risk_memo` | text | no | no | 注意点メモ |
| `last_ai_checked_at` | date | no | no | 最後にClaude確認した日時 |

ただし、MVPでは必須ではありません。最初は `CandidateProperty.ai_summary` や `InvestigationNote.content` にClaude回答を保存し、必要になった段階で `PropertyRegistry` 側へサマリーを追加する形でも問題ありません。

---

## 3.3 `PropertyRegistry` のRelation

| 関係 | 実装方法 | 用途 |
|---|---|---|
| PropertyRegistry 1 : N CandidateProperty | `CandidateProperty.property` | 候補保存 |
| PropertyRegistry 1 : N InvestigationNote | `InvestigationNote.property` | 調査メモ |
| PropertyRegistry 1 : N Conversation | `Conversation.target_property` | 物件を主題にしたClaude相談 |
| PropertyRegistry N : N Message | `Message.referenced_properties` | Claude回答時に参照した物件 |
| PropertyRegistry N : N Conversation | `Conversation.related_properties` | 複数候補を比較する会話 |

`Conversation` には主対象物件として `target_property`、関連候補として `related_properties` を持つ要件になっています。 docs/requirements.md:318-331

---

# 4. `Conversation`

## 4.1 目的

Claude相談の会話単位です。

1つの調査テーマ、1つの対象物件、または複数候補物件の比較を1つの `Conversation` として扱います。

正式要件では、`Conversation` に `target_property` と `related_properties` を持たせる設計になっています。 docs/requirements.md:318-331

---

## 4.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `owner_user` | User | no | yes | 会話の所有者 |
| `title` | text | no | yes | 会話タイトル |
| `investigation_theme` | text | no | no | 調査テーマ |
| `target_area` | text | no | no | 対象エリア |
| `target_property` | PropertyRegistry | no | no | 主対象物件 |
| `related_properties` | PropertyRegistry | yes | no | 関連候補物件 |
| `last_message_at` | date | no | no | 最終更新日時 |
| `last_message_text` | text | no | no | 会話一覧に表示する抜粋 |
| `project` | AiProject | no | no | 使用するAI設定 |
| `status` | text | no | no | 調査中 / 保留 / 完了など |

---

## 4.3 Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N Conversation | `Conversation.owner_user` |
| Conversation 1 : N Message | `Message.conversation` |
| Conversation N : 1 PropertyRegistry | `Conversation.target_property` |
| Conversation N : N PropertyRegistry | `Conversation.related_properties` |
| Conversation N : 1 AiProject | `Conversation.project` |
| Conversation 1 : N CandidateProperty | `CandidateProperty.conversation` |
| Conversation 1 : N InvestigationNote | `InvestigationNote.conversation` |

---

# 5. `Message`

## 5.1 目的

ユーザー発言とClaude回答を保存します。

正式要件では、`Message` は `content`、`conversation`、`role`、`referenced_properties`、APIレスポンスID、エラー、token数を持つ設計です。 docs/requirements.md:333-343

---

## 5.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `content` | text | no | yes | メッセージ本文 |
| `conversation` | Conversation | no | yes | 所属会話 |
| `role` | text | no | yes | `user` / `assistant` |
| `referenced_properties` | PropertyRegistry | yes | no | 回答時に参照した物件 |
| `api_response_id` | text | no | no | Claude APIレスポンスID |
| `error_message` | text | no | no | APIエラー内容 |
| `token_count` | number | no | no | 使用token数 |
| `is_error` | yes/no | no | no | エラー表示制御用 |
| `prompt_snapshot` | text | no | no | Claudeに送った文脈の控え。必要に応じて |

---

## 5.3 Relation

| 関係 | 実装方法 |
|---|---|
| Conversation 1 : N Message | `Message.conversation` |
| Message N : N PropertyRegistry | `Message.referenced_properties` |

---

# 6. `CandidateProperty`

## 6.1 目的

営業担当者が気になる物件を保存し、後から比較・調査できるようにします。

正式要件では、`CandidateProperty` は検索結果から営業担当者が気になる物件を保存するData Typeとして定義されています。 docs/requirements.md:386-401

---

## 6.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `owner_user` | User | no | yes | 作成者 |
| `conversation` | Conversation | no | no | 関連会話 |
| `property` | PropertyRegistry | no | yes | 候補物件 |
| `search_condition` | SearchCondition | no | no | 元になった検索条件 |
| `priority` | number | no | no | 優先度 |
| `reason` | text | no | no | 候補にした理由 |
| `ai_summary` | text | no | no | Claudeによる要約 |
| `next_research` | text | no | no | 次に調査すべきこと |
| `status` | text | no | no | 未調査 / 調査中 / 有望 / 除外など |
| `memo` | text | no | no | 営業担当者メモ |

---

## 6.3 Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N CandidateProperty | `CandidateProperty.owner_user` |
| PropertyRegistry 1 : N CandidateProperty | `CandidateProperty.property` |
| Conversation 1 : N CandidateProperty | `CandidateProperty.conversation` |
| SearchCondition 1 : N CandidateProperty | `CandidateProperty.search_condition` |

---

# 7. `SearchCondition`

## 7.1 目的

物件探索時の条件を保存・再利用します。

正式要件では、`SearchCondition` は物件探索時の条件保存・再利用のためのData Typeです。 docs/requirements.md:403-420

---

## 7.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `owner_user` | User | no | yes | 作成者 |
| `title` | text | no | yes | 条件名 |
| `area` | text | no | no | 対象エリア |
| `property_type` | text | no | no | 土地 / 建物 / 区分 / 収益物件など |
| `budget_min` | number | no | no | 予算下限。必要な場合のみ |
| `budget_max` | number | no | no | 予算上限。必要な場合のみ |
| `land_area_min` | number | no | no | 土地面積下限 |
| `building_area_min` | number | no | no | 建物面積下限 |
| `use_category` | text | no | no | 用途分類 |
| `income_rank` | text | no | no | 収益区分 |
| `rights_filter` | text | no | no | 権利関係条件 |
| `memo` | text | no | no | 調査メモ |

---

## 7.3 Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N SearchCondition | `SearchCondition.owner_user` |
| SearchCondition 1 : N CandidateProperty | `CandidateProperty.search_condition` |

---

# 8. `InvestigationNote`

## 8.1 目的

物件ごと、または会話ごとの調査メモを保存します。

正式要件では、`InvestigationNote` は物件ごと、または会話ごとに調査メモを保存するData Typeとして定義されています。 docs/requirements.md:422-432

---

## 8.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `owner_user` | User | no | yes | 作成者 |
| `property` | PropertyRegistry | no | no | 対象物件 |
| `conversation` | Conversation | no | no | 関連会話 |
| `note_type` | text | no | no | 所有者確認 / 権利関係 / 現地確認 / 価格調査など |
| `content` | text | no | yes | メモ本文 |
| `ai_generated` | yes/no | no | no | Claude生成かどうか |
| `next_action` | text | no | no | 次アクション |
| `due_date` | date | no | no | 調査期限がある場合 |

---

## 8.3 Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N InvestigationNote | `InvestigationNote.owner_user` |
| PropertyRegistry 1 : N InvestigationNote | `InvestigationNote.property` |
| Conversation 1 : N InvestigationNote | `InvestigationNote.conversation` |

---

# 9. `AiProject`

## 9.1 目的

Claude APIに渡すモデル設定・system promptを管理します。

正式要件では、`AiProject` に `name`、`model`、`system_prompt`、`max_tokens`、`temperature`、`is_active`、`owner_user` を持たせる設計です。 docs/requirements.md:434-444

---

## 9.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `name` | text | no | yes | AIプロジェクト名 |
| `model` | text | no | yes | 利用モデル名 |
| `system_prompt` | text | no | yes | Claudeへ渡すシステムプロンプト |
| `max_tokens` | number | no | no | 最大出力トークン |
| `temperature` | number | no | no | 生成の揺らぎ |
| `is_active` | yes/no | no | no | 利用中かどうか |
| `owner_user` | User | no | no | 所有者 |

---

## 9.3 Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N AiProject | `AiProject.owner_user` |
| AiProject 1 : N Conversation | `Conversation.project` |

---

# 10. `KnowledgeDocument`

## 10.1 目的

Claude回答の補助文脈として使う営業資料・調査手順・社内ルールを保存します。

登記データ本体はKnowledgeではなく `PropertyRegistry` に保存します。正式要件でも、Knowledge資料は補助資料であり、登記データ本体は `PropertyRegistry` として分離するとされています。 docs/requirements.md:276-292

---

## 10.2 フィールド一覧

| Field name | Type | List | 必須 | 用途 |
|---|---|---:|---:|---|
| `title` | text | no | yes | 資料タイトル |
| `summary` | text | no | no | 資料要約 |
| `content` | text | no | no | AIに渡す本文 |
| `document_file` | file | no | no | 元資料ファイル |
| `is_active` | yes/no | no | no | Claude参照対象にするか |
| `owner_user` | User | no | no | 所有者 |

正式要件では、`KnowledgeDocument` は `title`、`summary`、`content`、`document_file`、`is_active`、`owner_user` を持つ設計です。 docs/requirements.md:446-455

---

## 10.3 Relation

| 関係 | 実装方法 |
|---|---|
| User 1 : N KnowledgeDocument | `KnowledgeDocument.owner_user` |
| KnowledgeDocument → Claude API | API送信時に active な資料を検索してプロンプトに含める |

---

# 11. Relation全体図

## 11.1 全体Relation

```text
User
 ├─ Conversation
 │   ├─ Message
 │   ├─ CandidateProperty
 │   └─ InvestigationNote
 │
 ├─ SearchCondition
 │   └─ CandidateProperty
 │
 ├─ CandidateProperty
 │   └─ PropertyRegistry
 │
 ├─ InvestigationNote
 │   └─ PropertyRegistry
 │
 ├─ AiProject
 │   └─ Conversation
 │
 └─ KnowledgeDocument


PropertyRegistry
 ├─ Conversation.target_property
 ├─ Conversation.related_properties
 ├─ Message.referenced_properties
 ├─ CandidateProperty.property
 └─ InvestigationNote.property
```

---

## 11.2 中核Relation

```text
PropertyRegistry
   ↓
物件検索
   ↓
CandidateProperty として保存
   ↓
Conversation でClaude相談
   ↓
Message にClaude回答保存
   ↓
InvestigationNote に調査メモ保存
```

この流れは、正式要件のWorkflowにも沿っています。物件検索では `PropertyRegistry` を検索し、候補物件保存では対象の `PropertyRegistry` を `CandidateProperty` として保存し、物件詳細からClaude相談では対象の `PropertyRegistry` を取得してClaude APIへ送信する流れです。 docs/requirements.md:628-652

---

# 12. Bubbleでの実装順序

AGENTS.mdの指示どおり、現在は **DB設計** の段階です。次の実装順序は以下を推奨します。

## Step 1: MVP必須Data Typeを作成

まず以下を作成します。

1. `PropertyRegistry`
2. `Conversation`
3. `Message`
4. `CandidateProperty`
5. `SearchCondition`
6. `User` の拡張フィールド

---

## Step 2: Claude設定・補助Data Typeを作成

次に以下を作成します。

1. `AiProject`
2. `KnowledgeDocument`
3. `InvestigationNote`

---

## Step 3: `PropertyRegistry` 最小版から作成

MVPでは、正式要件にある以下の最小項目を優先します。 docs/requirements.md:712-731

| 分類 | MVP必須項目 |
|---|---|
| 所在 | `location` |
| 物件特定 | `land_number`, `building_number`, `building_name` |
| 種別 | `registry_type` |
| 用途・収益 | `use_category`, `income_rank` |
| 面積 | `land_area_sqm`, `building_area_sqm` |
| 所有者 | `owner_name`, `owner_address` |
| 抵当権 | `mortgage_status`, `mortgage_amount`, `mortgage_holder` |
| 参照 | `pdf_url`, `issued_date` |

---

# 13. Option Set案

Bubbleでは、固定値に近い項目はData Typeではなく **Option Set** にする方が扱いやすいです。

## 推奨Option Set

| Option Set | 使用フィールド | 候補値 |
|---|---|---|
| `UserRole` | `User.role` | 営業担当者 / 管理者 |
| `ConversationStatus` | `Conversation.status` | 調査中 / 保留 / 完了 |
| `MessageRole` | `Message.role` | user / assistant |
| `RegistryType` | `PropertyRegistry.registry_type` | 土地 / 建物 / 地図 / 区分建物 |
| `CandidateStatus` | `CandidateProperty.status` | 未調査 / 調査中 / 有望 / 除外 |
| `InvestigationNoteType` | `InvestigationNote.note_type` | 所有者確認 / 権利関係 / 現地確認 / 価格調査 / その他 |

MVPではtextでも問題ありませんが、画面のDropdownや検索条件で使う項目はOption Set化すると安定します。

---

# 14. Privacy Rules設計方針

正式要件では、登記データ・所有者情報・顧客に関連し得る情報を扱うため、Privacy Rulesを本番運用前に必ず設計・検証するとされています。 docs/requirements.md:654-662

## 基本方針

| Data Type | 読み取り | 作成 | 編集 | 削除 |
|---|---|---|---|---|
| `User` | 本人またはAdmin | サインアップ時 | 本人またはAdmin | Admin |
| `PropertyRegistry` | ログインユーザー | Admin / 取込担当 | Admin / 取込担当 | Admin |
| `Conversation` | `owner_user = Current User` またはAdmin | ログインユーザー | ownerまたはAdmin | ownerまたはAdmin |
| `Message` | 関連ConversationのownerまたはAdmin | ログインユーザー | 原則編集不可 | ownerまたはAdmin |
| `CandidateProperty` | `owner_user = Current User` またはAdmin | ログインユーザー | ownerまたはAdmin | ownerまたはAdmin |
| `SearchCondition` | `owner_user = Current User` またはAdmin | ログインユーザー | ownerまたはAdmin | ownerまたはAdmin |
| `InvestigationNote` | `owner_user = Current User` またはAdmin | ログインユーザー | ownerまたはAdmin | ownerまたはAdmin |
| `AiProject` | ownerまたはAdmin | ownerまたはAdmin | ownerまたはAdmin | ownerまたはAdmin |
| `KnowledgeDocument` | ownerまたはAdmin | ownerまたはAdmin | ownerまたはAdmin | ownerまたはAdmin |

---

# 15. MVPで作成すべきData Typeの優先順位

## 最優先

| 順位 | Data Type | 理由 |
|---:|---|---|
| 1 | `PropertyRegistry` | 物件検索・所有者確認・権利関係確認の中核 |
| 2 | `Conversation` | Claude相談単位 |
| 3 | `Message` | 会話履歴保存 |
| 4 | `CandidateProperty` | 候補物件保存 |
| 5 | `User` 拡張 | owner管理・Privacy Rulesの前提 |

## 次点

| 順位 | Data Type | 理由 |
|---:|---|---|
| 6 | `SearchCondition` | 検索条件保存 |
| 7 | `InvestigationNote` | 調査結果・次アクション保存 |
| 8 | `AiProject` | system prompt管理 |
| 9 | `KnowledgeDocument` | Claude補助文脈 |

---

# 16. 要確認事項

正式要件でも未実装・要確認として挙がっているため、DB実装前に以下は確認が必要です。 docs/requirements.md:778-789

1. `PropertyRegistry` はMVPでは1物件1レコードで進めてよいか
2. 同一物件に複数所有者がいる場合、MVPでは `owner_name` / `owner_address` にまとめて保存してよいか
3. 同一物件に複数抵当権がある場合、MVPでは `mortgage_*` に代表値または連結テキストで保存してよいか
4. `issued_date` はBubble上で `date` にするか、元データ優先で `text` にするか
5. `pdf_url` は外部URLか、Bubbleのfile型で保持するか
6. CSV/Excel取込はMVPで手動投入から始めるか、自動取込画面まで作るか

---

# 17. 今回の作業について

今回は **設計回答のみ** で、ファイル変更は行っていません。  
そのため、コミットおよびPull Request作成は行っていません。

**参照したファイル**

* `docs/requirements.md`

**使用したコマンド**

* ✅ `git status --short && git branch --show-current && nl -ba docs/requirements.md | sed -n '291,455p' && printf '\n--- core overview ---\n' && nl -ba docs/requirements.md | sed -n '1,85p' && printf '\n--- workflows/mvp ---\n' && nl -ba docs/requirements.md | sed -n '603,789p'`
