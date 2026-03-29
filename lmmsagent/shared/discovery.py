from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .tool_client import ToolClient

AUDIO_EXTS = {".wav", ".aiff", ".aif", ".flac", ".ogg", ".mp3"}


@dataclass
class Asset:
    id: str
    type: str
    display_name: str
    canonical_name: str
    aliases: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    path: Optional[str] = None
    source: str = "unknown"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "display_name": self.display_name,
            "canonical_name": self.canonical_name,
            "aliases": self.aliases,
            "tags": self.tags,
            "path": self.path,
            "source": self.source,
        }


class DiscoveryIndex:
    def __init__(self, tool_client: ToolClient, sample_roots: Optional[List[str]] = None) -> None:
        self.tool_client = tool_client
        self.sample_roots = sample_roots or []
        self._assets: List[Asset] = []

    @staticmethod
    def _norm(value: str) -> str:
        return "".join(ch for ch in value.lower() if ch.isalnum())

    @staticmethod
    def _tokens(value: str) -> List[str]:
        return [part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in value).split() if part]

    def _score(self, query: str, asset: Asset, preferred_type: Optional[str] = None) -> float:
        q_norm = self._norm(query)
        if not q_norm:
            return 0.0

        names = [asset.canonical_name, asset.display_name, *asset.aliases]
        normalized_names = [self._norm(name) for name in names if name]

        if q_norm in normalized_names:
            base = 1.0
        elif any(name.startswith(q_norm) for name in normalized_names):
            base = 0.9
        elif any(q_norm in name for name in normalized_names):
            base = 0.75
        else:
            q_tokens = set(self._tokens(query))
            a_tokens = set(self._tokens(" ".join(names + asset.tags)))
            overlap = len(q_tokens & a_tokens)
            union = max(1, len(q_tokens | a_tokens))
            base = overlap / union

        if preferred_type and asset.type == preferred_type:
            base += 0.1
        if any(token in asset.tags for token in self._tokens(query)):
            base += 0.05
        return min(base, 1.0)

    def _add_asset(self, asset: Asset) -> None:
        self._assets.append(asset)

    def index_plugins(self) -> Dict[str, int]:
        self._assets = [a for a in self._assets if a.type == "sample"]
        instruments = self.tool_client.call_tool("list_instruments")["result"].get("installed", [])
        effects = self.tool_client.call_tool("list_effects")["result"].get("installed", [])
        tools = self.tool_client.call_tool("list_tool_windows")["result"].get("tools", [])

        for item in instruments:
            name = item.get("name", "")
            display_name = item.get("display_name", name)
            self._add_asset(
                Asset(
                    id=f"plugin:instrument:{name}",
                    type="instrument_plugin",
                    display_name=display_name,
                    canonical_name=name,
                    aliases=[display_name],
                    tags=["instrument", "plugin"],
                    source="plugin",
                )
            )

        for item in effects:
            name = item.get("name", "")
            display_name = item.get("display_name", name)
            self._add_asset(
                Asset(
                    id=f"plugin:effect:{name}",
                    type="effect_plugin",
                    display_name=display_name,
                    canonical_name=name,
                    aliases=[display_name],
                    tags=["effect", "plugin"],
                    source="plugin",
                )
            )

        for item in tools:
            name = item.get("name", "")
            display_name = item.get("display_name", name)
            self._add_asset(
                Asset(
                    id=f"tool:{name}",
                    type="tool_window",
                    display_name=display_name,
                    canonical_name=name,
                    aliases=[display_name],
                    tags=["tool", "window"],
                    source="plugin",
                )
            )

        windows = self.tool_client.call_tool("list_tool_windows")["result"].get("windows", [])
        for window_name in windows:
            self._add_asset(
                Asset(
                    id=f"window:{self._norm(window_name)}",
                    type="tool_window",
                    display_name=window_name,
                    canonical_name=window_name,
                    aliases=[],
                    tags=["window"],
                    source="factory",
                )
            )

        return {
            "instruments": len(instruments),
            "effects": len(effects),
            "tool_windows": len(windows),
        }

    def index_samples(self, project_path: Optional[str] = None) -> Dict[str, int]:
        self._assets = [a for a in self._assets if a.type != "sample"]

        added = 0
        project_audio = self.tool_client.call_tool("search_project_audio", {"query": ""})["result"].get("matches", [])
        for idx, item in enumerate(project_audio):
            sample_path = item.get("sample_path")
            if not sample_path:
                continue
            sample_name = Path(sample_path).name
            self._add_asset(
                Asset(
                    id=f"sample:project:{idx}",
                    type="sample",
                    display_name=sample_name,
                    canonical_name=sample_name,
                    aliases=[item.get("track_name", "")],
                    tags=["project", "audio"],
                    path=sample_path,
                    source="project",
                )
            )
            added += 1

        roots = list(self.sample_roots)
        if project_path:
            roots.append(str(Path(project_path).parent))
        roots.append(str(Path.home() / "Downloads"))

        seen_paths = {asset.path for asset in self._assets if asset.path}
        for root in roots:
            if not root:
                continue
            root_path = Path(root).expanduser()
            if not root_path.exists() or not root_path.is_dir():
                continue
            for path in root_path.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in AUDIO_EXTS:
                    continue
                path_str = str(path)
                if path_str in seen_paths:
                    continue
                seen_paths.add(path_str)
                self._add_asset(
                    Asset(
                        id=f"sample:file:{len(seen_paths)}",
                        type="sample",
                        display_name=path.name,
                        canonical_name=path.name,
                        aliases=[path.stem],
                        tags=["audio", path.suffix.lower().lstrip(".")],
                        path=path_str,
                        source="downloads" if "Downloads" in path_str else "user_library",
                    )
                )
                added += 1

        return {"samples": added}

    def search_assets(
        self,
        query: str,
        *,
        asset_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        scored = []
        for asset in self._assets:
            if asset_type and asset.type != asset_type:
                continue
            score = self._score(query, asset, preferred_type=asset_type)
            if score <= 0:
                continue
            scored.append((score, asset))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {
                **asset.as_dict(),
                "score": round(score, 3),
            }
            for score, asset in scored[:limit]
        ]

    def resolve_plugin(self, query: str, plugin_type: str) -> Optional[Dict[str, Any]]:
        expected_type = "instrument_plugin" if plugin_type == "instrument" else "effect_plugin"
        matches = self.search_assets(query, asset_type=expected_type, limit=3)
        return matches[0] if matches else None

    def resolve_sample(self, query: str) -> Optional[Dict[str, Any]]:
        matches = self.search_assets(query, asset_type="sample", limit=3)
        return matches[0] if matches else None

    def resolve_track_reference(self, query: str) -> Optional[Dict[str, Any]]:
        tracks = self.tool_client.call_tool("list_tracks")["result"].get("tracks", [])
        if not tracks:
            return None
        wanted = self._norm(query)
        exact = next((t for t in tracks if self._norm(t.get("name", "")) == wanted), None)
        if exact:
            return exact
        return next((t for t in tracks if wanted in self._norm(t.get("name", ""))), None)

    def refresh(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        return {
            "plugins": self.index_plugins(),
            "samples": self.index_samples(project_path=project_path),
            "asset_count": len(self._assets),
        }
