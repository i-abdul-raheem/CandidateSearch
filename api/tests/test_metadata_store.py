from pathlib import Path

from src.store.metadata_db import MetadataStore


def test_role_lifecycle(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path / "metadata.sqlite3")
    role = store.create_role({
        "title": "Backend Engineer", "department": "Engineering",
        "location": "Berlin", "work_mode": "Hybrid",
        "description": "Build reliable candidate search services.", "status": "open",
    })
    assert store.list_roles()[0]["title"] == "Backend Engineer"
    updated = store.update_role(role["id"], {**role, "status": "paused"})
    assert updated and updated["status"] == "paused"
    assert store.delete_role(role["id"])
    assert store.list_roles() == []


def test_recent_searches_are_newest_first(tmp_path: Path) -> None:
    store = MetadataStore(tmp_path / "metadata.sqlite3")
    first = store.record_search("Python", 3)
    second = store.record_search("React", 2)
    assert [item["id"] for item in store.list_searches()] == [second["id"], first["id"]]
    assert store.delete_search(first["id"])
    store.clear_searches()
    assert store.list_searches() == []
