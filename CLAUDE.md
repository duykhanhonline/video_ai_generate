# CLAUDE.md

## 1. Project Overview

This project is an AI-assisted ambient / repeating video production platform.

The application generates reusable short video clips and music assets around a single **Master Theme**.

Example Master Themes:

* Lone Samurai
* Cozy Rabbit Cottage
* Mountain Wizard
* Cyberpunk Girl at Night
* Medieval Tavern
* Old Fisherman by the Sea

This application is NOT a story generator.

Clips within a project are independent. They do not form a narrative sequence and do not need continuity between activities.

Example:

```text
Master Theme: Lone Samurai

Clip 01 → Drinking tea
Clip 02 → Watching rain
Clip 03 → Meditating
Clip 04 → Reading a scroll
Clip 05 → Watching koi
Clip 06 → Sitting beside a campfire
```

Clip 02 does NOT need to continue from Clip 01.

The only consistency requirements are:

* same Master Theme
* same character identity where applicable
* same general world
* same visual style
* same mood
* compatible animation style

The resulting video clips and music tracks form reusable asset pools.

Final long-form video rendering is handled separately by the user's existing Python + FFmpeg implementation.

---

# 2. CRITICAL WORKING STYLE

## ALWAYS ASK BEFORE IMPLEMENTING THE NEXT STEP

This is the most important development rule for this repository.

Claude must work incrementally with the user.

Do NOT implement multiple development phases automatically.

The expected workflow is:

```text
Discuss Step
    ↓
Propose Solution
    ↓
Ask User for Approval
    ↓
User Approves
    ↓
Implement Step
    ↓
Explain What Changed
    ↓
STOP
    ↓
Ask Before Next Step
```

After completing any meaningful implementation step, STOP.

Do not automatically continue to the next step.

For example:

```text
Step 1:
Create Docker environment

→ explain proposed Docker architecture
→ ask for approval
→ implement only after approval
→ show what was created
→ stop

Step 2:
Database models

→ do NOT start automatically
→ ask user first
```

Never assume:

> "The previous step worked, so I will continue."

Instead ask:

> "Docker setup is complete. Would you like me to proceed with the database setup?"

The user may want to:

* inspect the code
* test it
* modify it
* debug it
* ask questions
* change architecture

before continuing.

---

# 3. Do Not Overbuild

Build the minimum required for the current approved step.

Do not implement future features merely because they might eventually be useful.

Avoid:

* speculative abstractions
* unnecessary dependencies
* premature optimization
* unnecessary microservices
* unnecessary infrastructure

Prefer:

```text
simple
readable
testable
replaceable
```

over:

```text
clever
complex
over-engineered
```

---

# 4. Technology Stack

## Frontend

Use:

* React
* TypeScript
* Vite
* React Router

Frontend communicates with the backend through HTTP APIs.

Never expose provider API credentials to the frontend.

---

# 5. Backend

Use:

* Python 3.12+
* FastAPI
* SQLAlchemy 2.x
* Alembic
* Pydantic
* MySQL
* Redis
* Celery

Use modern Python.

Prefer:

* type hints
* async/await for appropriate I/O
* clear service boundaries
* dependency injection where useful
* small focused functions

Avoid unnecessary design patterns.

---

# 6. Docker Architecture

The main application runs with Docker Compose.

Expected services:

```text
frontend
backend
worker
redis
mysql
```

Architecture:

```text
Browser
   │
   ▼
React
   │
   ▼
FastAPI
   │
   ├──────────► MySQL
   │
   └──────────► Redis
                    │
                    ▼
                 Celery
                    │
                    ▼
               AI Worker
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        LLM       Image     Video
        APIs      APIs      APIs
```

Docker handles the application and AI-generation infrastructure.

---

# 7. Docker Development

The application should eventually start using:

```bash
docker compose up -d
```

Development should not require manually installing:

* MySQL
* Redis
* Node.js
* backend Python dependencies

on the host.

Use Docker volumes for persistent data.

Example:

```text
mysql_data
```

Source code may be mounted for development hot reload.

---

# 8. FFmpeg Is NOT Part of Docker

IMPORTANT:

Do NOT install or configure FFmpeg inside Docker.

Do NOT implement the user's FFmpeg pipeline.

The user already has Python + FFmpeg code and will maintain the rendering system separately.

The application ends after preparing the required assets.

Architecture:

```text
AI APPLICATION
─────────────────────

Master Theme
     ↓
Activities
     ↓
Images
     ↓
Kling Videos
     ↓
Music
     ↓
Asset Pool
     ↓
Render Manifest

=====================
APPLICATION BOUNDARY
=====================

USER'S EXISTING CODE
─────────────────────

Python
     ↓
FFmpeg
     ↓
Final long video
```

Claude must not modify this boundary unless explicitly requested.

---

# 9. External Renderer

The user's external Python + FFmpeg renderer runs directly on the host machine.

It is responsible for:

* video looping
* video concatenation
* audio concatenation
* music looping
* transitions
* normalization
* final duration
* encoding
* NVENC/GPU configuration
* CPU configuration
* progress reporting
* final MP4 generation

Do NOT implement these features inside this application unless explicitly requested.

---

# 10. Render Manifest

The application should eventually be capable of exporting a simple render manifest.

Example:

```json
{
  "project_id": 12,
  "project_name": "Lone Samurai",
  "target_duration": 3600,

  "videos": [
    "projects/12/videos/clip_01.mp4",
    "projects/12/videos/clip_02.mp4",
    "projects/12/videos/clip_03.mp4"
  ],

  "music": [
    "projects/12/music/song_01.mp3",
    "projects/12/music/song_02.mp3"
  ]
}
```

The external renderer decides how these assets are assembled.

---

# 11. File Paths

Store relative asset paths in MySQL.

Good:

```text
projects/12/videos/clip_01.mp4
```

Bad:

```text
D:\ai-video\projects\12\videos\clip_01.mp4
```

Bad:

```text
/app/data/projects/12/videos/clip_01.mp4
```

Environment-specific roots should come from configuration.

Example:

```text
MEDIA_ROOT=/data
```

This keeps assets portable.

---

# 12. Master Theme

The Master Theme is the central creative object.

A Master Theme defines the identity of the content.

Example:

```json
{
  "name": "Lone Samurai",

  "concept": "A solitary samurai living peacefully in rural feudal Japan.",

  "character": {
    "description": "A calm Japanese samurai",
    "clothing": "traditional indigo kimono and hakama"
  },

  "environment": {
    "location": "rural feudal Japan",
    "elements": [
      "mountains",
      "bamboo",
      "traditional houses",
      "streams",
      "cherry trees"
    ]
  },

  "visual_style": {
    "style": "cinematic realistic",
    "mood": "peaceful and contemplative",
    "lighting": "soft natural light"
  },

  "animation_rules": {
    "movement": "slow and subtle",
    "camera": "mostly static",
    "loop_friendly": true
  },

  "music_style": {
    "mood": "peaceful and meditative",
    "instruments": [
      "shakuhachi",
      "koto",
      "soft strings"
    ],
    "vocals": false,
    "tempo": "55-70 BPM"
  }
}
```

Master Themes must be reusable.

---

# 13. Theme Creation

The user should eventually be able to provide a simple idea:

```text
A lonely wizard living in a mountain tower.
```

The AI Director can transform it into a structured Master Theme.

Example:

```text
Simple Idea
     ↓
AI Director
     ↓
Character
Environment
Visual Style
Mood
Animation Rules
Music Style
     ↓
Master Theme
```

Always return programmatically consumed AI results as structured data where practical.

Validate structured AI output using Pydantic.

---

# 14. Reference Images

A Master Theme may have one or more reference images.

Reference images help maintain:

* character appearance
* clothing
* visual identity
* art style
* environment

Reference images must be stored as files.

Do NOT store large image binaries directly inside MySQL.

MySQL stores metadata and relative paths.

---

# 15. Project

A Project represents one production using a Master Theme.

Example:

```text
Master Theme:
Lone Samurai

Project:
Peaceful Samurai Ambience

Clips:
10

Music:
10 tracks

Target final duration:
3600 seconds

Image Provider:
OpenAI

Video Provider:
Kling

Music Provider:
Configured provider / manual
```

A Master Theme may have multiple projects.

Example:

```text
Lone Samurai
     │
     ├── Rainy Samurai
     │
     ├── Winter Samurai
     │
     └── Autumn Samurai
```

---

# 16. Clips Are Independent

This rule is critical.

Do NOT treat clips as sequential scenes.

Incorrect:

```text
Scene 1
   ↓
Scene 2
   ↓
Scene 3
```

Correct:

```text
Master Theme
   │
   ├── Drinking Tea
   ├── Watching Rain
   ├── Meditating
   ├── Reading
   ├── Watching Koi
   └── Sitting by Fire
```

Each clip should work independently.

---

# 17. Activity Generation

The AI Director should eventually generate independent activities from the Master Theme.

Example input:

```text
Theme:
Lone Samurai

Generate:
20 activity ideas
```

Possible output:

```text
Drinking tea
Meditating
Watching rain
Reading a scroll
Writing calligraphy
Watching koi
Sitting beside a fire
Looking at mountains
Lighting a lantern
Resting beneath a tree
```

The user should be able to select activities before expensive AI generation begins.

---

# 18. Cost-Aware Workflow

AI image/video generation costs money.

Never automatically spend provider credits when user approval can reasonably happen first.

Preferred workflow:

```text
Generate ideas
     ↓
USER APPROVAL
     ↓
Generate image prompts
     ↓
Generate images
     ↓
USER REVIEW
     ↓
Generate Kling prompts
     ↓
Generate Kling videos
     ↓
USER REVIEW
```

Do not automatically regenerate paid assets.

Regeneration must be an explicit operation.

---

# 19. Loop-Friendly Video Generation

Kling clips should generally favor repeatable ambient movement.

Good movements:

* breathing
* blinking
* steam rising
* fire flickering
* leaves moving
* rain falling
* snow falling
* water rippling
* clothing moving gently
* hair moving gently

Prefer:

```text
static camera
slow motion
subtle motion
environmental motion
small character movement
```

Avoid by default:

```text
camera cuts
dramatic camera movement
character leaving frame
character entering frame
large body movement
sudden lighting changes
scene transitions
```

Prompts should encourage the end state to visually resemble the beginning where practical.

---

# 20. AI Director

Create an AI Director service responsible for creative reasoning.

Responsibilities:

1. Expand simple ideas into Master Themes.
2. Generate independent activity ideas.
3. Generate image prompts.
4. Generate Kling animation prompts.
5. Generate music prompts.
6. Preserve Master Theme consistency.

The AI Director should depend on provider interfaces rather than a specific vendor SDK.

---

# 21. Provider Architecture

External AI services MUST use provider abstractions.

Required conceptual interfaces:

```text
LLMProvider
ImageProvider
VideoProvider
MusicProvider
```

Example:

```python
from abc import ABC, abstractmethod


class ImageProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        reference_images: list[str] | None = None,
    ) -> str:
        raise NotImplementedError
```

Possible implementations:

```text
OpenAIImageProvider
GrokImageProvider
LocalImageProvider
```

---

# 22. Provider Switching

Provider selection should be configurable.

Example:

```text
LLM Provider:
OpenAI

Image Provider:
OpenAI

Video Provider:
Kling

Music Provider:
Manual / configured API
```

Future example:

```text
Image Provider:
Grok
```

The rest of the application should not need major changes.

---

# 23. Provider Registry

Avoid provider-specific logic scattered throughout the application.

Avoid:

```python
if provider == "openai":
    ...
elif provider == "grok":
    ...
```

in many services.

Prefer:

```python
provider = image_provider_registry.get(
    project.image_provider
)
```

Provider-specific behavior belongs inside provider implementations.

---

# 24. Initial LLM Provider

Initial LLM integration:

```text
OpenAI
```

The architecture must allow future providers such as:

```text
Anthropic
Gemini
Grok
Local models
```

Do not implement these future providers until requested.

---

# 25. Image Generation

Initial image generation may use OpenAI.

Architecture must allow:

```text
OpenAI
Grok
Local image models
Other APIs
```

A generated image belongs to a clip.

Store:

* provider
* model
* prompt
* resulting asset
* creation time
* relevant provider metadata

---

# 26. Kling Video Generation

Initial video provider:

```text
Kling
```

Video generation is asynchronous.

Expected lifecycle:

```text
Submit Kling Request
       ↓
Receive External Job ID
       ↓
Store Job
       ↓
Check Status
       ↓
Completed
       ↓
Download Video
       ↓
Store Asset
```

Do not keep a FastAPI HTTP request open while waiting for Kling.

Use background workers.

---

# 27. Music

Music is independent from individual video clips.

A Master Theme defines the musical identity.

Example:

```text
Peaceful Japanese samurai ambience.

Shakuhachi, koto and subtle strings.

Slow and meditative.

Slightly melancholic.

Instrumental only.

55-70 BPM.
```

The AI Director may generate multiple variations.

Example:

```text
Track 01 → Shakuhachi focused
Track 02 → Koto focused
Track 03 → Rainy atmosphere
Track 04 → Mountain solitude
Track 05 → Sunset mood
Track 06 → Quiet temple
Track 07 → Forest atmosphere
Track 08 → Night ambience
Track 09 → Autumn melancholy
Track 10 → Deep meditation
```

These tracks do NOT correspond directly to specific clips.

---

# 28. Manual Music Must Be Supported

Do not assume every music provider has an API.

The application should allow manual music upload.

This enables:

```text
AI generates music prompts
        ↓
User generates music externally
        ↓
User uploads MP3
        ↓
Music asset pool
```

Automated music APIs can be added later.

---

# 29. Asset Pool Philosophy

The application produces reusable asset pools.

Video:

```text
clip_001.mp4
clip_002.mp4
clip_003.mp4
...
```

Music:

```text
track_001.mp3
track_002.mp3
track_003.mp3
...
```

These assets should remain reusable.

Changing final video duration must NOT require regenerating AI assets.

---

# 30. Database

Use MySQL.

Initial conceptual tables:

```text
master_themes
projects
clips
music_tracks
assets
jobs
prompt_versions
```

Do not create every possible future table prematurely.

Implement tables only when the approved development step requires them.

---

# 31. master_themes

Suggested fields:

```text
id
name
concept
character_json
environment_json
visual_style_json
animation_rules_json
music_style_json
reference_image
created_at
updated_at
```

Use MySQL JSON fields where appropriate.

---

# 32. projects

Suggested fields:

```text
id
master_theme_id
name
status
clip_count
music_count
target_duration
image_provider
video_provider
music_provider
created_at
updated_at
```

---

# 33. clips

Suggested fields:

```text
id
project_id
activity
setting
image_prompt
video_prompt
image_asset_id
video_asset_id
status
approved
created_at
updated_at
```

---

# 34. music_tracks

Suggested fields:

```text
id
project_id
title
prompt
asset_id
duration
status
approved
created_at
updated_at
```

---

# 35. assets

Suggested fields:

```text
id
project_id
asset_type
provider
provider_model
file_path
mime_type
metadata_json
created_at
```

Possible asset types:

```text
reference_image
generated_image
generated_video
music
thumbnail
```

Do not add media-analysis fields unless actually required.

The external renderer owns final media processing.

---

# 36. jobs

Suggested fields:

```text
id
project_id
job_type
provider
external_job_id
status
progress
error_message
retry_count
metadata_json
created_at
started_at
completed_at
```

Suggested statuses:

```text
PENDING
RUNNING
WAITING_PROVIDER
COMPLETED
FAILED
CANCELLED
```

---

# 37. Prompt History

Generated prompts are valuable production assets.

Do not silently overwrite them.

Suggested table:

```text
prompt_versions
───────────────

id
project_id
clip_id
prompt_type
provider
model
prompt
version
created_at
```

This allows the user to determine which prompt produced a successful image/video.

---

# 38. File Storage

For initial development use filesystem storage.

Suggested layout:

```text
/data/
    themes/
        1/
            references/

    projects/
        10/
            images/
            videos/
            music/
            manifests/
            temp/
```

Use a centralized StorageService.

Do not construct file paths throughout unrelated business logic.

---

# 39. Future Storage

Storage architecture should make future migration possible to:

```text
AWS S3
Cloudflare R2
Google Cloud Storage
```

Do NOT implement cloud storage until requested.

Local filesystem storage is sufficient initially.

---

# 40. Background Jobs

Use Celery for slow external API operations.

Examples:

```text
generate_image
submit_kling_video
check_kling_status
download_kling_video
generate_music
```

FastAPI should not wait minutes for these operations.

---

# 41. Retry Strategy

External providers may temporarily fail.

Retries may be appropriate for:

* timeout
* HTTP 429
* temporary server errors
* connection failure

Do not endlessly retry permanent errors.

Store meaningful error information.

---

# 42. Secrets

Use environment variables.

Example:

```text
.env
.env.example
```

Never commit `.env`.

Example `.env.example`:

```text
APP_ENV=development

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=ambient_video
MYSQL_USER=ambient
MYSQL_PASSWORD=

REDIS_URL=redis://redis:6379/0

MEDIA_ROOT=/data

OPENAI_API_KEY=

KLING_API_KEY=
KLING_API_SECRET=

GROK_API_KEY=

MUSIC_API_KEY=
```

Never:

* hardcode API keys
* commit credentials
* log credentials
* return credentials to React

---

# 43. Suggested Backend Structure

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── themes.py
│   │   ├── projects.py
│   │   ├── clips.py
│   │   ├── music.py
│   │   ├── assets.py
│   │   └── jobs.py
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── repositories/
│   │
│   ├── services/
│   │   ├── director_service.py
│   │   ├── theme_service.py
│   │   ├── clip_service.py
│   │   ├── music_service.py
│   │   └── storage_service.py
│   │
│   ├── providers/
│   │   ├── base/
│   │   │   ├── llm.py
│   │   │   ├── image.py
│   │   │   ├── video.py
│   │   │   └── music.py
│   │   │
│   │   ├── llm/
│   │   │   └── openai.py
│   │   │
│   │   ├── image/
│   │   │   ├── openai.py
│   │   │   └── grok.py
│   │   │
│   │   ├── video/
│   │   │   └── kling.py
│   │   │
│   │   └── music/
│   │       └── manual.py
│   │
│   ├── workers/
│   │   ├── celery.py
│   │   ├── image_tasks.py
│   │   ├── video_tasks.py
│   │   └── music_tasks.py
│   │
│   └── core/
│       ├── config.py
│       ├── database.py
│       └── logging.py
│
├── alembic/
├── tests/
├── Dockerfile
└── requirements.txt
```

Do not create every empty file immediately unless required.

This structure represents the intended direction.

---

# 44. Suggested Frontend Structure

```text
frontend/
│
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   │   ├── ThemesPage.tsx
│   │   ├── ThemeEditorPage.tsx
│   │   ├── ProjectsPage.tsx
│   │   └── ProjectPage.tsx
│   │
│   ├── features/
│   │   ├── themes/
│   │   ├── clips/
│   │   └── music/
│   │
│   ├── types/
│   └── App.tsx
│
├── Dockerfile
└── package.json
```

Again, create files only when needed.

---

# 45. API Style

Prefer REST initially.

Potential endpoints:

```text
POST   /api/themes
GET    /api/themes
GET    /api/themes/{id}
PATCH  /api/themes/{id}
DELETE /api/themes/{id}

POST   /api/themes/{id}/generate
POST   /api/themes/{id}/duplicate

POST   /api/projects
GET    /api/projects/{id}

POST   /api/projects/{id}/activities/generate

POST   /api/clips/{id}/image/generate
POST   /api/clips/{id}/video/generate

POST   /api/projects/{id}/images/generate
POST   /api/projects/{id}/videos/generate

POST   /api/projects/{id}/music/prompts

GET    /api/jobs/{id}

GET    /api/projects/{id}/render-manifest
```

These are architectural guidelines, not requirements to implement all endpoints immediately.

---

# 46. Coding Style

Prefer explicit Python.

Good:

```python
async def generate_clip_image(
    clip_id: int,
    provider_name: str,
) -> Asset:
    ...
```

Avoid vague names:

```python
process()
handle()
do_stuff()
run_task()
```

Prefer:

```python
generate_activity_ideas()
generate_image_prompt()
generate_clip_image()
submit_kling_generation()
check_kling_generation_status()
download_generated_video()
generate_music_prompts()
export_render_manifest()
```

---

# 47. Async Guidelines

Use async for appropriate I/O operations.

Good candidates:

* LLM API calls
* image API calls
* Kling API calls
* HTTP downloads
* provider status requests

Do not make a function async merely because it takes a long time.

Long provider workflows should use Celery.

---

# 48. Idempotency

Avoid accidentally repeating paid operations.

If a clip already has:

```text
video_asset_id
```

do not automatically submit another Kling generation.

Distinguish:

```text
Generate Video
```

from:

```text
Regenerate Video
```

Regeneration must be explicit.

---

# 49. Logging

Use Python logging.

Useful context:

```text
project_id
clip_id
job_id
provider
operation
status
```

Never log:

```text
API keys
authorization tokens
provider secrets
```

---

# 50. Testing

Prioritize tests for meaningful application logic.

Examples:

* Master Theme validation
* AI structured-response parsing
* provider registry
* activity generation parsing
* job state transitions
* storage path generation
* render manifest generation

External provider APIs should be mocked in automated tests.

Tests must not spend real AI credits.

---

# 51. Development Phases

Follow these phases incrementally.

Do NOT implement all phases automatically.

## Phase 1

Docker foundation:

```text
React
FastAPI
MySQL
Redis
basic Celery worker
```

STOP and ask user before Phase 2.

## Phase 2

Master Theme database + CRUD.

STOP and ask user before Phase 3.

## Phase 3

Basic React Master Theme interface.

STOP and ask user before Phase 4.

## Phase 4

AI Director + Master Theme generation.

STOP and ask user before Phase 5.

## Phase 5

Project creation + activity generation.

STOP and ask user before Phase 6.

## Phase 6

Activity selection UI.

STOP and ask user before Phase 7.

## Phase 7

Image prompt generation.

STOP and ask user before Phase 8.

## Phase 8

First image provider integration.

STOP and ask user before Phase 9.

## Phase 9

Image review / approval UI.

STOP and ask user before Phase 10.

## Phase 10

Kling prompt generation.

STOP and ask user before Phase 11.

## Phase 11

Kling API integration.

STOP and ask user before Phase 12.

## Phase 12

Video review / approval.

STOP and ask user before Phase 13.

## Phase 13

Music prompt generation.

STOP and ask user before Phase 14.

## Phase 14

Manual music upload.

STOP and ask user before Phase 15.

## Phase 15

Render manifest export.

At this point the application can hand assets to the user's external FFmpeg system.

Additional features require explicit discussion and approval.

---

# 52. Claude Must Explain Changes

After implementing a step, provide a concise summary:

```text
Implemented:

- FastAPI container
- MySQL container
- Redis container
- React container
- basic health endpoint

Files created/changed:

- docker-compose.yml
- backend/Dockerfile
- frontend/Dockerfile
- backend/app/main.py

How to test:

docker compose up -d

Then visit:

http://localhost:8000/health
```

Then STOP.

Ask whether the user wants to proceed.

Do not begin the next phase.

---

# 53. Debugging Style

When an error occurs:

1. Understand the error.
2. Explain the likely cause.
3. Propose the smallest fix.
4. Ask before making significant architectural changes.
5. Fix only the relevant problem.
6. Do not rewrite unrelated working code.

Do not respond to a small bug by redesigning the application.

---

# 54. Existing Code

Respect existing user code.

Before replacing an existing implementation:

1. inspect it
2. understand it
3. explain why a change is necessary
4. ask before performing a major rewrite

Especially:

DO NOT replace or redesign the user's existing Python + FFmpeg renderer unless explicitly requested.

---

# 55. Database Changes

Use Alembic migrations.

Do not manually destroy/recreate the database as the normal solution to schema changes.

Before destructive database operations, explicitly warn the user and ask for approval.

Never delete production/user data automatically.

---

# 56. Provider Cost Safety

Before operations that may trigger many paid API calls, clearly indicate what will happen.

Example:

```text
This action will request:

10 image generations
10 Kling video generations
```

Bulk paid generation should require explicit user action.

Do not silently generate additional assets because a previous result was imperfect.

---

# 57. No Automatic Next-Step Assumptions

Statements such as:

```text
"Now I'll implement Kling."
```

are inappropriate unless the user already approved that step.

Instead:

```text
"The image generation stage is working.

The next planned stage is Kling prompt generation.

Would you like me to proceed?"
```

User approval controls development progression.

---

# 58. Final Product Goal

The eventual workflow is:

```text
User enters:

"A lone samurai living peacefully
in rural Japan."

             ↓

       AI Director

             ↓

       Master Theme

             ↓

User reviews / edits theme

             ↓

User uploads/selects
reference character image

             ↓

AI generates activity ideas

             ↓

User selects activities

             ↓

AI generates image prompts

             ↓

Image Provider

             ↓

Generated Images

             ↓

User reviews images

             ↓

AI generates Kling prompts

             ↓

Kling API

             ↓

Generated short clips

             ↓

User reviews clips

             ↓

AI generates music prompts

             ↓

Music generated externally
or through provider

             ↓

Music uploaded/stored

             ↓

VIDEO ASSET POOL
+
MUSIC ASSET POOL

             ↓

Render Manifest

============= APPLICATION ENDS =============

             ↓

User's Python + FFmpeg renderer

             ↓

1 hour / 2 hours / 3 hours / custom

             ↓

FINAL VIDEO
```

---

# 59. Core Principles Summary

Always preserve these principles:

1. One Master Theme defines the creative identity.
2. Clips are independent, not story scenes.
3. Activities are simple and repeat-friendly.
4. AI providers are replaceable.
5. Paid generations require deliberate user actions.
6. Generated assets are reusable.
7. Prompts should be preserved.
8. MySQL stores metadata, not large media binaries.
9. Docker runs the main application infrastructure.
10. FFmpeg remains outside Docker.
11. The user's existing FFmpeg code is not part of this implementation.
12. The application exports assets / a manifest for the renderer.
13. Build incrementally.
14. Do not over-engineer.
15. Ask before implementing each meaningful next step.
16. After completing a step, STOP and wait for user approval.
17. Never automatically proceed through development phases.
