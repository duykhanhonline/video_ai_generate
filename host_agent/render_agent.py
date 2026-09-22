"""
Host-side render agent.

Runs OUTSIDE Docker, directly on the host machine (this is deliberate -- see
CLAUDE.md's "FFmpeg is NOT part of Docker" / application-boundary rules).

What it does:
    1. Polls the data/projects/*/manifests/manifest.json files for changes.
    2. When a manifest changes, registers a render job with the web app
       (POST /api/projects/{id}/render-jobs) so its status is visible there.
    3. Calls YOUR existing Python + FFmpeg render logic via run_render() below
       -- this script does NOT implement that logic, it only watches for work
       and reports status back to the app.
    4. Reports COMPLETED/FAILED back to the app (PATCH /api/jobs/{job_id}).

Setup:
    pip install requests
    python render_agent.py

Configuration (environment variables, all optional):
    DATA_ROOT       Path to the app's data/ folder on the host.
                     Default: ../data (relative to this script)
    API_BASE_URL     Base URL of the backend API.
                     Default: http://localhost:8000
    POLL_INTERVAL    Seconds between manifest checks. Default: 5
"""

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

DATA_ROOT = Path(os.environ.get("DATA_ROOT", Path(__file__).resolve().parent.parent / "data"))
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "5"))


def run_render(manifest: dict[str, Any], data_root: Path) -> None:
    """
    Plug your existing Python + FFmpeg rendering logic in here.

    `manifest` looks like:
        {
            "project_id": 3,
            "project_name": "a lonely Samurai 3",
            "target_duration": 3600,
            "videos": ["projects/3/videos/clip_04.mp4", ...],
            "music": ["projects/3/music/track_01.mp3", ...],
        }

    All paths in `videos`/`music` are relative to `data_root` -- e.g.
    `data_root / manifest["videos"][0]` is the full path to that clip.

    Raise an exception on failure; the agent will catch it, report the job
    as FAILED with the exception message, and keep watching for the next
    manifest change.
    """
    video_paths = [data_root / p for p in manifest["videos"]]
    music_paths = [data_root / p for p in manifest["music"]]

    raise NotImplementedError(
        "Call your existing render script/function here, e.g.:\n"
        "    import subprocess\n"
        "    subprocess.run(\n"
        "        ['python', 'your_render_script.py',\n"
        "         '--duration', str(manifest['target_duration']),\n"
        "         '--videos', *[str(p) for p in video_paths],\n"
        "         '--music', *[str(p) for p in music_paths]],\n"
        "        check=True,\n"
        "    )"
    )


def _register_render_job(project_id: int) -> int:
    response = requests.post(f"{API_BASE_URL}/api/projects/{project_id}/render-jobs", timeout=10)
    response.raise_for_status()
    return response.json()["id"]


def _update_job(job_id: int, **fields: Any) -> None:
    response = requests.patch(f"{API_BASE_URL}/api/jobs/{job_id}", json=fields, timeout=10)
    response.raise_for_status()


def _process_manifest(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text())
    project_id = manifest["project_id"]

    print(f"[render_agent] New manifest for project {project_id}: {manifest_path}")
    job_id = _register_render_job(project_id)
    print(f"[render_agent] Registered job {job_id}, status=RUNNING")

    try:
        run_render(manifest, DATA_ROOT)
    except Exception as exc:
        print(f"[render_agent] Job {job_id} FAILED: {exc}")
        _update_job(job_id, status="FAILED", error_message=str(exc)[:1000])
        return

    print(f"[render_agent] Job {job_id} COMPLETED")
    _update_job(job_id, status="COMPLETED", progress=100)


def main() -> None:
    print(f"[render_agent] Watching {DATA_ROOT}/projects/*/manifests/manifest.json")
    print(f"[render_agent] API base URL: {API_BASE_URL}")

    seen_mtimes: dict[Path, float] = {}

    while True:
        for manifest_path in DATA_ROOT.glob("projects/*/manifests/manifest.json"):
            mtime = manifest_path.stat().st_mtime
            if seen_mtimes.get(manifest_path) != mtime:
                seen_mtimes[manifest_path] = mtime
                try:
                    _process_manifest(manifest_path)
                except Exception as exc:
                    print(f"[render_agent] Error processing {manifest_path}: {exc}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
