# AI Workflow (InsightGYM)

This document defines the AI workflow for the fitness platform and aligns it with the current backend endpoints and services.

## 1. Purpose
- Goal: Provide AI-assisted coaching, workout planning, and safe exercise guidance.
- Channels: Member chat, workout-plan generation, trial onboarding automation.

## 2. Actors and Roles
- Member: request workouts, ask questions, receive guidance.
- Assistant/Trainer: monitor members, respond to messages, manage progress checks.
- Admin: manage exercises, users, and AI settings.

## 3. Admin Configuration
- AI provider selection: `auto | openai | anthropic | gemini | vertex`.
- API keys stored in `SiteSettings.ai_settings_json` (managed via Admin API).
- Provider resolution: `auto` selects the first available provider with a valid key and SDK installed.

## 4. Entry Points
- `POST /api/ai-coach/chat` for AI coach conversation.
- `POST /api/ai-coach/workout-plan` for AI-generated workout plans.
- `GET /api/training-programs` for trial program auto-generation (AI-assisted) when needed.
- `POST /api/vector-search/search` for vector-based exercise lookup (requires vector DB setup).
- `GET /api/vector-search/recommendations` for profile-based exercise recommendations (requires vector DB setup).
- `POST /api/ai/plan` for AI action planning with structured JSON actions.
- `GET /api/admin/website-kb/status` for KB index status (admin only).
- `GET|PUT /api/admin/website-kb/source` for editing KB source content (admin only).
- `POST /api/admin/website-kb/reindex` to rebuild KB embeddings (admin only).
- `POST /api/website-kb/query` for KB semantic search (auth required).
- `GET|PUT /api/admin/ai-settings` and `POST /api/admin/ai-settings/test` for AI provider configuration.

## 5. Request Handling Flow
1. Member sends a message or workout request.
2. Backend resolves user context (JWT identity, role, language, profile).
3. If vector search is available, exercise candidates are fetched; otherwise, a database fallback is used.
4. Safety checks are applied (injury contraindications, medical conditions).
5. AI provider generates a response or workout plan.
6. Response is returned with metadata (injuries detected, safety checks, suggested exercises).

## 6. AI Response Structure
- For chat: text response plus metadata (`injuries_detected`, `safety_checked`, `exercises_suggested`, `month`).
- For workout plan: text response plus `month`, `safety_checked`, and exercise list.
- For action planner: `assistant_response`, `actions` (validated JSON), `results` (structured execution results), `errors`.

## 6.1 Action Planner (JSON)
The LLM returns only JSON with an `actions` array:
```json
{
  "assistant_response": "Summary for the user",
  "actions": [
    { "action": "search_exercises", "params": { "query": "تمرینات سینه", "max_results": 10 } }
  ]
}
```
Allowed actions:
- `search_exercises`
- `create_workout_plan`
- `update_user_profile`
- `progress_check`
- `trainer_message`
- `site_settings` (admin only)

## 7. Vector Search
- Exercise content can be embedded into vectors (OpenAI embeddings).
- Query is embedded and searched via nearest-neighbor similarity.
- Filtering is applied using user profile (equipment access, injuries, level).
- If vector search is not configured, the system falls back to database queries.

## 8. Knowledge Sources
- Exercise library (DB + optional vector index).
- Training level rules and periodization (monthly rules).
- User profile (equipment, injuries, goals, training level).
- Website KB content (editable and reindexed by admin).

## 9. Conversation Memory
- Chat history is stored per user (`ChatHistory`) and optionally grouped by `session_id`.
- The system may use recent context for continuity when generating responses.

## 10. Security and Permissions
- All AI endpoints require JWT authentication.
- Role checks are enforced server-side (member vs assistant vs admin).
- AI cannot perform actions beyond the user’s permissions.

## 11. Observability and Failures
- Provider selection and errors are logged server-side.
- On AI provider failure, the service returns a safe fallback or error.
- No unsafe exercises are returned when injury contraindications match.

## 12. Testing Checklist
- Chat endpoint returns a valid response with metadata.
- Workout-plan endpoint respects month and safety rules.
- Vector search returns consistent results when configured.
- Permission checks block unauthorized access to admin endpoints.
- Trial program auto-generation works for members on active trial.

## 13. Required Assets (Update as Needed)
- Exercise library in DB (with injury contraindications populated).
- Vector index tables (if using vector search).
- AI workflow docs: `AI_WORKFLOW.md`.
