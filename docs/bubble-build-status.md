# Bubble Build Status

## Current status

Bubble AI App Generator was used with a shortened prompt.

The generated app currently has the following pages:

- index
- login
- admin
- property_detail
- ai_search
- candidate_properties
- reset_pw
- 404

The MVP pages required by the design are present:

- login
- index
- ai_search
- property_detail
- candidate_properties
- admin

Do not restart the app generation.

## Important design rules

- This is not a CRM.
- Do not create signup.
- Do not create property_search.
- Do not create search_conditions.
- ai_search is the central page.
- ai_search must combine natural-language search, filtering, result display, conversation, and candidate saving.
- PropertyRegistry is the core searchable database.
- Search conditions are stored in Conversation / SearchCondition / SearchConditionItem.
- Full search results must not be stored in Conversation.
- Do not create Conversation.current_search_results.
- Search results must be obtained by searching PropertyRegistry each time.

## Data Types generated

The following Data Types exist:

- User
- PropertyRegistry
- Conversation
- SearchCondition
- SearchConditionItem
- Message
- CandidateProperty
- ImportLog

## Bubble field naming notes

Bubble AI created some field names different from the formal docs.

Use the Bubble-generated names as-is to avoid duplicate fields.

Examples:

- CandidateProperty.user = formal owner_user
- CandidateProperty.property_registry = formal property
- SearchCondition.summary = formal current_condition_summary
- SearchConditionItem.field = formal field_name
- SearchConditionItem.value = formal value_text
- ImportLog.imported_by_user = formal executed_by
- ImportLog.error_detail = formal error memo/details
- Conversation.last_message_preview = formal last_message_text

Do not create duplicate fields only to match docs naming.

## ai_search current state

ai_search now has a Repeating Group for search results.

The intended structure is:

- Page type: Conversation
- RG property_results
  - Type of content: PropertyRegistry
  - Data source: Search for PropertyRegistries
- Cell / row group
  - Type of content: PropertyRegistry
  - Data source: Current cell's PropertyRegistry
- Text cells should use:
  - Parent group's PropertyRegistry's location
  - Parent group's PropertyRegistry's building_name
  - Parent group's PropertyRegistry's owner_name
  - Parent group's PropertyRegistry's registry_type
  - Parent group's PropertyRegistry's use_category
  - Parent group's PropertyRegistry's land_area_sqm:formatted as text
  - Parent group's PropertyRegistry's building_area_sqm:formatted as text
  - Parent group's PropertyRegistry's mortgage_status
  - Parent group's PropertyRegistry's has_mortgage:formatted as text

## Current issues

As of the latest Bubble screenshot, there are about 73 issues.

Main issue categories:

1. ai_search page type / Current page Conversation issues
2. SearchCondition data source expecting one item but receiving list
3. SearchConditionItem search receiving list instead of single SearchCondition
4. RG property_results cell text expressions need text formatting
5. rg-result-row and rg-cell-actions data source needs PropertyRegistry
6. CandidateProperty creation still has empty PropertyRegistry / Conversation values
7. Message creation still has empty Conversation value
8. Some delete condition workflows have empty target values

## Next recommended steps

Do not add new pages or data types.

Fix in this order:

1. Confirm ai_search page type is Conversation.
2. Ensure all navigation to ai_search sends a Conversation.
3. Fix conditions-summary-group:
   - Type: SearchCondition
   - Data source: Current page Conversation's current_search_condition
4. Fix condition chips:
   - RG type: SearchConditionItem
   - Data source: Search for SearchConditionItems where search_condition = Current page Conversation's current_search_condition and is_active = yes
5. Fix RG property_results:
   - Type: PropertyRegistry
   - Data source: Search for PropertyRegistries
6. Fix result row group:
   - Type: PropertyRegistry
   - Data source: Current cell's PropertyRegistry
7. Fix text cells:
   - Use Parent group's PropertyRegistry fields
   - Add formatted as text for number / yes-no fields
8. Fix detail button:
   - Go to property_detail
   - Data to send = Parent group's PropertyRegistry
9. Fix candidate save:
   - Create CandidateProperty
   - property_registry = Parent group's PropertyRegistry
   - user = Current User
   - conversation = Current page Conversation
   - status = 未調査
10. Fix AI analysis message:
   - Create Message
   - conversation = Current page Conversation
   - role = user
   - intent_type = analyze_results
   - content = この物件を分析して

## Do later

- Claude API Connector
- Natural language to SearchConditionItem conversion
- CSV / Excel import workflow
- Privacy Rules
- Admin import confirmation UX

## 2026-06-03 ai_search Issues fix note

Created the detailed Bubble editor fix runbook at `docs/bubble-ai-search-issue-fix.md` and use it as the source of truth for the current Issues修正フェーズ.

Priority for the current pass:

1. Keep `ai_search` as `Type of content = Conversation` and ensure every navigation sends a `Conversation`.
2. Set `RG property_results` to `Type of content = PropertyRegistry` and `Data source = Search for PropertyRegistries`.
3. Set result row/action groups to `Type of content = PropertyRegistry` with data source from the current cell or parent group.
4. Rewrite result cell text expressions to use `Parent group's PropertyRegistry`; format number and yes/no fields as text.
5. In candidate-save Workflow, create `CandidateProperty` with `property_registry = Parent group's PropertyRegistry`, `user = Current User`, `conversation = Current page Conversation`, and `status = 未調査`.
6. In analyze-row Workflow, create `Message` with `conversation = Current page Conversation`, `role = user`, `intent_type = analyze_results`, and `content = この物件を分析して`.

Do not proceed to Claude API Connector fixes until these Bubble type/reference Issues are cleared.

## 2026-06-06 PR creation note

Codex Webの「PRを作成する」では、`.docx` のようなバイナリファイルが差分に含まれるとPR作成がキャンセルされる場合がある。

そのため、クライアント提示用のWord互換ファイルは、GitHub/CodexのPR差分で扱えるテキスト形式のRTFとして管理する。

- Wordで開くファイル: `docs/BukkenAiSearch_client_design_document.rtf`
- 元Markdown: `docs/client-design-document.md`
- RTF再生成コマンド: `python scripts/generate_rtf_from_markdown.py docs/client-design-document.md docs/BukkenAiSearch_client_design_document.rtf`

`main` に反映するには、Codex Web右上の「PRを作成する」をクリックし、GitHubで作成されたPull RequestをMergeする。
