"""Storage service — downloads generation outputs to local directories."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

import requests

from src.config import (
    OUTPUTS_AUDIO_DIR,
    OUTPUTS_MODELS_3D_DIR,
    OUTPUTS_THUMBNAILS_DIR,
    OUTPUTS_VIDEOS_DIR,
)
from src.output_asset import GenerationOutput, OutputAsset
from src.utils import download_output as _download_output

logger = logging.getLogger(__name__)


class StorageService:
    """Manages local output file downloads and directory organization."""

    def __init__(
        self,
        video_dir: Path = OUTPUTS_VIDEOS_DIR,
        models_3d_dir: Path = OUTPUTS_MODELS_3D_DIR,
        thumbnails_dir: Path = OUTPUTS_THUMBNAILS_DIR,
        audio_dir: Path = OUTPUTS_AUDIO_DIR,
    ):
        """Initialize storage service with output directories."""
        self.video_dir = Path(video_dir)
        self.models_3d_dir = Path(models_3d_dir)
        self.thumbnails_dir = Path(thumbnails_dir)
        self.audio_dir = Path(audio_dir)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.models_3d_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def download_file(
        self,
        url: str,
        destination: Path,
        timeout: int = 30,
    ) -> bool:
        """Download a file from URL to destination path.

        Returns True on success, False on failure.
        """
        try:
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("wb") as file_handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_handle.write(chunk)
            logger.info("Downloaded: %s", destination)
            return True
        except requests.RequestException as exc:
            logger.warning("Download failed for %s: %s", url, exc)
            return False
        except OSError as exc:
            logger.error("File write failed for %s: %s", destination, exc)
            return False

    def ensure_video_thumbnail(self, video_path: Path | str) -> Path | None:
        """Create or return a first-frame thumbnail when ffmpeg is available."""
        video_path = Path(video_path)
        if not video_path.exists():
            return None
        if not shutil.which("ffmpeg"):
            return None

        thumbnail_path = self.thumbnails_dir / f"{video_path.stem}.jpg"
        if thumbnail_path.exists() and thumbnail_path.stat().st_size > 0:
            return thumbnail_path

        last_error: Exception | None = None
        # Some short provider outputs fail if the seek target is past the first
        # frame, so try a visually useful 0.5s frame first and then frame zero.
        for seek_time in ("00:00:00.5", "00:00:00"):
            command = [
                "ffmpeg",
                "-y",
                "-ss",
                seek_time,
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(thumbnail_path),
            ]
            try:
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
                if thumbnail_path.exists() and thumbnail_path.stat().st_size > 0:
                    return thumbnail_path
            except (
                OSError,
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
            ) as exc:
                last_error = exc

        logger.info("Thumbnail generation skipped for %s: %s", video_path, last_error)
        return None

    def download_output(
        self,
        url: str,
        media_type: str,
        prefix: str = "output",
        timeout: int = 120,
    ) -> dict:
        """Download a provider output URL into the configured media directory."""
        if media_type == "video":
            dest_dir = self.video_dir
        elif media_type == "audio":
            dest_dir = self.audio_dir
        else:
            dest_dir = self.models_3d_dir
        result = _download_output(url, dest_dir, prefix=prefix, timeout=timeout)
        local_path = result.get("local_path")
        if local_path and media_type == "audio":
            path = Path(local_path)
            suffix = path.suffix.lower()
            mime = {
                ".mp3": "audio/mpeg",
                ".wav": "audio/wav",
                ".m4a": "audio/mp4",
                ".aac": "audio/aac",
                ".flac": "audio/flac",
            }.get(suffix, "audio/mpeg")
            result["mime_type"] = mime
        if local_path and media_type == "video":
            thumbnail_path = self.ensure_video_thumbnail(local_path)
            if thumbnail_path:
                result["thumbnail_path"] = str(thumbnail_path)
        return result

    def normalize_video_output(
        self,
        prediction: Any,
        generation_id: str,
        download: bool = True,
    ) -> GenerationOutput:
        """Convert Replicate video prediction to GenerationOutput."""
        output_url = prediction.output if prediction.output else None
        local_path = None
        file_size = None

        if output_url and download:
            ext = ".mp4"
            if "." in output_url.split("/")[-1]:
                ext = "." + output_url.split(".")[-1]
            local_filename = f"{generation_id}{ext}"
            local_path = self.video_dir / local_filename

            if self.download_file(output_url, local_path):
                file_size = local_path.stat().st_size
            else:
                local_path = None

        primary = OutputAsset(
            asset_type="video",
            local_path=local_path,
            provider_url=output_url,
            file_size_bytes=file_size,
            mime_type="video/mp4",
        )

        return GenerationOutput(primary=primary)

    def normalize_3d_output(
        self,
        prediction: Any,
        generation_id: str,
        download: bool = True,
    ) -> GenerationOutput:
        """Convert Replicate 3D prediction to GenerationOutput."""
        output = prediction.output
        mesh_url = None
        preview_url = None

        if isinstance(output, str):
            mesh_url = output
        elif isinstance(output, dict):
            mesh_url = output.get("mesh")
            preview_url = output.get("preview_video") or output.get("preview")

        local_mesh_path = None
        local_preview_path = None

        if mesh_url and download:
            ext = ".glb"
            if ".usdz" in mesh_url:
                ext = ".usdz"
            elif ".obj" in mesh_url:
                ext = ".obj"
            local_filename = f"{generation_id}{ext}"
            local_mesh_path = self.models_3d_dir / local_filename

            if not self.download_file(mesh_url, local_mesh_path):
                local_mesh_path = None

        if preview_url and download:
            local_filename = f"{generation_id}_preview.mp4"
            local_preview_path = self.video_dir / local_filename
            if not self.download_file(preview_url, local_preview_path):
                local_preview_path = None

        primary = OutputAsset(
            asset_type="mesh",
            local_path=local_mesh_path,
            provider_url=mesh_url,
            mime_type="model/gltf-binary",
        )

        previews = None
        if preview_url or local_preview_path:
            previews = [
                OutputAsset(
                    asset_type="preview_video",
                    local_path=local_preview_path,
                    provider_url=preview_url,
                    mime_type="video/mp4",
                )
            ]

        return GenerationOutput(primary=primary, previews=previews)


_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Return the lazily-created global storage service."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
