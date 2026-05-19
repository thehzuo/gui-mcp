from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from web_gui_mcp.schema.artifact import ArtifactSpec
from web_gui_mcp.store.ids import artifact_id_for_spec


class StoredArtifact(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    artifact_id: str
    spec: ArtifactSpec
    html: str
    created_at: datetime
    updated_at: datetime
    revision: int = 1


class MemoryArtifactStore:
    def __init__(self) -> None:
        self._artifacts: dict[str, StoredArtifact] = {}

    def save(self, spec: ArtifactSpec, html: str, artifact_id: str | None = None) -> StoredArtifact:
        now = datetime.now(UTC)
        resolved_id = artifact_id or artifact_id_for_spec(spec)
        existing = self._artifacts.get(resolved_id)
        stored = StoredArtifact(
            artifact_id=resolved_id,
            spec=spec,
            html=html,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            revision=existing.revision + 1 if existing else 1,
        )
        self._artifacts[resolved_id] = stored
        return stored

    def replace(self, artifact_id: str, spec: ArtifactSpec, html: str) -> StoredArtifact:
        if artifact_id not in self._artifacts:
            raise KeyError(f"Unknown artifact_id: {artifact_id}")
        return self.save(spec, html, artifact_id=artifact_id)

    def get(self, artifact_id: str) -> StoredArtifact | None:
        return self._artifacts.get(artifact_id)

    def list(self, limit: int = 20) -> list[StoredArtifact]:
        return sorted(
            self._artifacts.values(),
            key=lambda item: item.updated_at,
            reverse=True,
        )[:limit]

    def clear(self) -> None:
        self._artifacts.clear()
