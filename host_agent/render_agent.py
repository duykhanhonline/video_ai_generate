"""
Host-side render agent.

Runs OUTSIDE Docker, directly on the host machine (this is deliberate -- see
CLAUDE.md's "FFmpeg is NOT part of Docker" / application-boundary rules).

What it does:
    1. Polls data/manifest/{project_id}_{clip_id}_manifest.json files for changes.
       Each file is a manifest for ONE clip's video (a project can have many
       clips, so many manifests/videos -- these are NOT combined into one).
    2. When a manifest changes, acquires an exclusive OS-level file lock
       (data/renders/.render.lock) so only one render runs at a time, even
       across multiple copies of this agent or a manual loop_video.py run.
       If the lock is already held, the manifest is left unmarked and simply
       retried on the next poll -- no blocking, no stale-lock bookkeeping
       (the OS releases the lock automatically if a process dies).
    3. Registers a render job with the web app (POST /api/clips/{clip_id}/render-jobs).
       Exporting a manifest already creates a PENDING job so the UI can show
       "waiting for the agent" -- this call transitions that same job to
       RUNNING rather than creating a second one.
    4. Runs loop_video.py (in this same folder) with that clip's video and
       the project's currently-included music tracks, writing the final
       rendered file to data/renders/{project_id}_{clip_id}_rendered.mp4.
    5. Reports COMPLETED/FAILED back to the app (PATCH /api/jobs/{job_id}).

Setup:
    pip install -r requirements.txt
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
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from filelock import FileLock, Timeout

DATA_ROOT = Path(os.environ.get("DATA_ROOT", Path(__file__).resolve().parent.parent / "data"))
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "5"))

LOOP_VIDEO_SCRIPT = Path(__file__).resolve().parent / "loop_video.py"
RENDERS_DIR = DATA_ROOT / "renders"
RENDER_LOCK = FileLock(str(RENDERS_DIR / ".render.lock"))


def run_render(manifest: dict[str, Any], data_root: Path) -> None:
    """
    Calls loop_video.py with this manifest's video + approved music tracks.

    `manifest` looks like:
        {
            "project_id": 3,
            "clip_id": 6,
            "project_name": "a lonely Samurai 3",
            "target_duration": 3600,
            "videos": ["projects/3/videos/clip_06.mp4"],
            "music": ["projects/3/music/track_01.mp3", ...],
        }

    `videos` has exactly one entry (this clip's video); `music` is the
    project's shared, currently-included music tracks (loop_video.py
    concatenates multiple tracks into one combined track before looping it).

    Raises on failure (non-zero exit from loop_video.py); the agent catches
    that, reports the job as FAILED with the error, and keeps watching for
    the next manifest change.
    """
    video_path = data_root / manifest["videos"][0]
    music_paths = [data_root / p for p in manifest["music"]]

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RENDERS_DIR / f"{manifest['project_id']}_{manifest['clip_id']}_rendered.mp4"

    cmd = [
        sys.executable, str(LOOP_VIDEO_SCRIPT),
        "--clip", str(video_path),
        "--duration", str(manifest["target_duration"]),
        "--output", str(output_path),
    ]
    if music_paths:
        cmd += ["--music", *(str(p) for p in music_paths)]

    print(f"[render_agent] Running: {' '.join(cmd)}")
    # Explicitly capture stdout/stderr rather than letting the child inherit
    # this process's handles: when this agent itself was started headless
    # (e.g. via pythonw.exe, as start_render_agent.ps1 does), there's no
    # real console to inherit and loop_video.py's progress output crashes
    # it outright. Capturing gives the child real pipes regardless.
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"loop_video.py exited with code {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    print(f"[render_agent] Rendered: {output_path}")


def _register_render_job(clip_id: int) -> int:
    response = requests.post(f"{API_BASE_URL}/api/clips/{clip_id}/render-jobs", timeout=10)
    response.raise_for_status()
    return response.json()["id"]


def _update_job(job_id: int, **fields: Any) -> None:
    response = requests.patch(f"{API_BASE_URL}/api/jobs/{job_id}", json=fields, timeout=10)
    response.raise_for_status()


def _process_manifest(manifest_path: Path) -> bool:
    """Handle one changed manifest. Returns True if it was handled (rendered,
    or failed trying) -- the caller should mark it seen in that case. Returns
    False if it was skipped because another render is in progress -- the
    caller should leave it unmarked so it's retried on the next poll."""
    manifest = json.loads(manifest_path.read_text())
    clip_id = manifest["clip_id"]

    try:
        RENDER_LOCK.acquire(timeout=0)
    except Timeout:
        print(f"[render_agent] Another render is in progress; will retry clip {clip_id} later")
        return False

    try:
        print(f"[render_agent] New manifest for clip {clip_id}: {manifest_path}")
        job_id = _register_render_job(clip_id)
        print(f"[render_agent] Registered job {job_id}, status=RUNNING")

        try:
            run_render(manifest, DATA_ROOT)
        except Exception as exc:
            print(f"[render_agent] Job {job_id} FAILED: {exc}")
            _update_job(job_id, status="FAILED", error_message=str(exc)[:1000])
            return True

        print(f"[render_agent] Job {job_id} COMPLETED")
        _update_job(job_id, status="COMPLETED", progress=100)
        return True
    finally:
        RENDER_LOCK.release()


def main() -> None:
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[render_agent] Watching {DATA_ROOT}/manifest/*_manifest.json")
    print(f"[render_agent] API base URL: {API_BASE_URL}")

    seen_mtimes: dict[Path, float] = {}

    while True:
        for manifest_path in DATA_ROOT.glob("manifest/*_manifest.json"):
            mtime = manifest_path.stat().st_mtime
            if seen_mtimes.get(manifest_path) != mtime:
                try:
                    handled = _process_manifest(manifest_path)
                except Exception as exc:
                    print(f"[render_agent] Error processing {manifest_path}: {exc}")
                    handled = True  # don't tight-loop retrying a broken manifest
                if handled:
                    seen_mtimes[manifest_path] = mtime

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
