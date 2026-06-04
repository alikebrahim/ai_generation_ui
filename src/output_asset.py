"""Output asset — normalizes video, 3D model, and preview file types."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OutputAsset:
    """Represents a single output file from generation (video, 3D model, etc.)."""

    asset_type: str  # 'video', 'mesh', 'glb', 'preview_video', 'thumbnail'
    local_path: Path | None = None  # Absolute path if downloaded locally
    provider_url: str | None = None  # Temporary provider delivery URL
    file_size_bytes: int | None = None
    mime_type: str | None = None

    @property
    def has_local_file(self) -> bool:
        """True if file has been downloaded locally and exists."""
        return self.local_path is not None and self.local_path.exists()

    @property
    def display_url(self) -> str | None:
        """Return best-available URL: local file or provider URL."""
        if self.has_local_file:
            return str(self.local_path)
        return self.provider_url

    def __repr__(self) -> str:
        status = "local" if self.has_local_file else "remote"
        return f"OutputAsset({self.asset_type}/{status})"


@dataclass
class GenerationOutput:
    """Complete generation output: primary asset + optional previews/derivatives."""

    primary: OutputAsset  # Main output (video or 3D model)
    previews: list[OutputAsset] | None = None  # Optional preview assets
    metadata: dict | None = None  # Arbitrary generation metadata

    def all_assets(self) -> list[OutputAsset]:
        """Return all assets (primary + previews)."""
        assets = [self.primary]
        if self.previews:
            assets.extend(self.previews)
        return assets

    def all_local_paths(self) -> list[Path]:
        """Return all local file paths that exist."""
        return [
            a.local_path for a in self.all_assets() if a.has_local_file
        ]  # type: ignore[return-value]

    def cleanup_failed_downloads(self) -> None:
        """Remove any partially downloaded files (called on failure)."""
        for asset in self.all_assets():
            if asset.local_path and asset.local_path.exists():
                asset.local_path.unlink()
