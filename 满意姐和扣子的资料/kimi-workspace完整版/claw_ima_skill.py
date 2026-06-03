#!/usr/bin/env python3
"""
腾讯 ima Skill 封装 - 改造版
支持真实 API 模式或本地 Stub（演示/储备）模式
"""
from __future__ import annotations
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import os

STUB_DB = Path.home() / ".config" / "ima_skill_stub" / "notes_db.json"

@dataclass
class ImaNote:
    note_id: str
    title: str
    content: str
    notebook: str
    created_at: str
    updated_at: str
    tags: List[str] = None

@dataclass
class ImaNotebook:
    notebook_id: str
    name: str
    note_count: int
    created_at: str

class ImaSkill:
    """
    腾讯 ima Skill 封装
    - 若 api_key 为空或 base_url 为示例地址，则自动进入本地 Stub 模式
    - Stub 模式将笔记持久化到本地 JSON，可用于演示、测试和储备
    """

    def __init__(self, api_key: str = "", base_url: str = "https://ima.tencent.com/api/v1"):
        self.api_key = api_key or os.environ.get("IMA_API_KEY", "")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # 自动判断 stub 模式：无 key 或用默认示例地址即 stub
        self.stub_mode = (not self.api_key) or ("ima.tencent.com/api/v1" in self.base_url)
        if self.stub_mode:
            STUB_DB.parent.mkdir(parents=True, exist_ok=True)
            if not STUB_DB.exists():
                STUB_DB.write_text(json.dumps({"notebooks": {}, "notes": {}}, ensure_ascii=False))

    def _load_stub(self) -> Dict:
        return json.loads(STUB_DB.read_text(encoding='utf-8'))

    def _save_stub(self, data: Dict):
        STUB_DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    async def list_notebooks(self) -> List[ImaNotebook]:
        if self.stub_mode:
            db = self._load_stub()
            return [ImaNotebook(**v) for v in db.get("notebooks", {}).values()]
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/notebooks", headers=self.headers) as resp:
                data = await resp.json()
                return [ImaNotebook(**item) for item in data.get("notebooks", [])]

    async def create_notebook(self, name: str) -> ImaNotebook:
        now = datetime.now().isoformat()
        if self.stub_mode:
            db = self._load_stub()
            nb_id = f"nb_{len(db['notebooks'])+1:03d}"
            nb = ImaNotebook(notebook_id=nb_id, name=name, note_count=0, created_at=now)
            db["notebooks"][nb_id] = asdict(nb)
            self._save_stub(db)
            return nb
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/notebooks", headers=self.headers, json={"name": name}) as resp:
                data = await resp.json()
                return ImaNotebook(**data)

    async def create_note(self, title: str, content: str, notebook: str, tags: List[str] = None) -> ImaNote:
        now = datetime.now().isoformat()
        if self.stub_mode:
            db = self._load_stub()
            note_id = f"note_{len(db['notes'])+1:04d}"
            note = ImaNote(note_id=note_id, title=title, content=content, notebook=notebook,
                           created_at=now, updated_at=now, tags=tags or [])
            db["notes"][note_id] = asdict(note)
            if notebook in db.get("notebooks", {}):
                db["notebooks"][notebook]["note_count"] = db["notebooks"][notebook].get("note_count", 0) + 1
            self._save_stub(db)
            return note
        import aiohttp
        payload = {
            "title": title,
            "content": content,
            "notebook": notebook,
            "tags": tags or [],
            "source": "claw_auto_sync",
            "created_by": "openclaw"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/notes", headers=self.headers, json=payload) as resp:
                data = await resp.json()
                return ImaNote(**data)

    async def update_note(self, note_id: str, content: str = None, title: str = None, append: bool = False) -> ImaNote:
        if self.stub_mode:
            db = self._load_stub()
            note_data = db["notes"].get(note_id)
            if not note_data:
                raise RuntimeError(f"Note {note_id} not found")
            if append and content:
                note_data["content"] = note_data["content"] + "\n\n" + content
            elif content:
                note_data["content"] = content
            if title:
                note_data["title"] = title
            note_data["updated_at"] = datetime.now().isoformat()
            self._save_stub(db)
            return ImaNote(**note_data)
        import aiohttp
        payload = {}
        if content:
            payload["content"] = content
        if title:
            payload["title"] = title
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/notes/{note_id}", headers=self.headers, json=payload) as resp:
                data = await resp.json()
                return ImaNote(**data)

    async def get_note(self, note_id: str) -> Optional[ImaNote]:
        if self.stub_mode:
            db = self._load_stub()
            note_data = db["notes"].get(note_id)
            return ImaNote(**note_data) if note_data else None
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/notes/{note_id}", headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return ImaNote(**data)
                return None

    async def search_notes(self, query: str, notebook: str = None, limit: int = 10) -> List[ImaNote]:
        if self.stub_mode:
            db = self._load_stub()
            results = []
            for note_data in db["notes"].values():
                if notebook and note_data.get("notebook") != notebook:
                    continue
                if query.lower() in note_data.get("title", "").lower() or query.lower() in note_data.get("content", "").lower():
                    results.append(ImaNote(**note_data))
                if len(results) >= limit:
                    break
            return results
        import aiohttp
        payload = {"query": query, "limit": limit, "search_fields": ["title", "content"]}
        if notebook:
            payload["notebook"] = notebook
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/notes/search", headers=self.headers, json=payload) as resp:
                data = await resp.json()
                return [ImaNote(**item) for item in data.get("results", [])]

    async def delete_note(self, note_id: str) -> bool:
        if self.stub_mode:
            db = self._load_stub()
            if note_id in db["notes"]:
                del db["notes"][note_id]
                self._save_stub(db)
                return True
            return False
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/notes/{note_id}", headers=self.headers) as resp:
                return resp.status == 204

    async def batch_sync_notes(self, notes: List[Dict], notebook: str,
                               conflict_resolution: Literal["skip", "overwrite", "append"] = "append") -> Dict:
        results = {"created": 0, "updated": 0, "skipped": 0, "errors": []}
        for note_data in notes:
            try:
                existing = await self._find_note_by_title(note_data["title"], notebook)
                if existing:
                    if conflict_resolution == "skip":
                        results["skipped"] += 1
                    elif conflict_resolution == "overwrite":
                        await self.update_note(existing.note_id, **note_data)
                        results["updated"] += 1
                    elif conflict_resolution == "append":
                        await self.update_note(existing.note_id, content=note_data["content"], append=True)
                        results["updated"] += 1
                else:
                    await self.create_note(title=note_data["title"], content=note_data["content"],
                                           notebook=notebook, tags=note_data.get("tags", []))
                    results["created"] += 1
            except Exception as e:
                results["errors"].append({"title": note_data.get("title"), "error": str(e)})
        return results

    async def _find_note_by_title(self, title: str, notebook: str) -> Optional[ImaNote]:
        notes = await self.search_notes(title, notebook=notebook, limit=5)
        for note in notes:
            if note.title == title:
                return note
        return None


async def _demo():
    ima = ImaSkill()  # 默认进入 stub 模式
    nb = await ima.create_notebook("DemoNotebook")
    note = await ima.create_note("Hello", "This is a stub demo note.", "DemoNotebook", tags=["demo"])
    print(f"Created notebook: {nb.name} ({nb.notebook_id})")
    print(f"Created note: {note.title} ({note.note_id})")
    searched = await ima.search_notes("stub")
    print(f"Search result: {len(searched)} note(s)")
    for n in searched:
        print(f"  - {n.title}: {n.content[:40]}...")

if __name__ == '__main__':
    import asyncio
    asyncio.run(_demo())
