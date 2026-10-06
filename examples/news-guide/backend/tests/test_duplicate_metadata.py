"""Offline identity and reload checks for the News Guide data stores."""

import json
from pathlib import Path

import pytest
from app.data.article_store import ArticleStore
from app.data.event_store import EventStore


def write_records(root: Path, kind: str, identities: list[str]) -> None:
    rows = []
    if kind == "article":
        (root / "articles").mkdir(exist_ok=True)
    for index, identity in enumerate(identities):
        if kind == "article":
            filename = f"synthetic-{index}.md"
            (root / "articles" / filename).write_text(
                f"Synthetic content {index}", encoding="utf-8"
            )
            rows.append(
                {
                    "id": identity,
                    "title": f"Synthetic article {index}",
                    "heroImage": "fixture.png",
                    "heroImageUrl": "/fixture.png",
                    "url": f"/articles/{identity}",
                    "filename": filename,
                    "date": "2026-01-01T12:00:00Z",
                    "author": "Example Author",
                    "tags": [],
                    "keywords": [],
                }
            )
        else:
            rows.append(
                {
                    "id": identity,
                    "title": f"Synthetic event {index}",
                    "date": "2026-01-01",
                    "dayOfWeek": "Thursday",
                    "time": "12:00",
                    "location": "Example Hall",
                    "details": f"Synthetic details {index}",
                    "category": "Fixture",
                    "keywords": [],
                }
            )
    filename = "articles.json" if kind == "article" else "events.json"
    (root / filename).write_text(json.dumps(rows), encoding="utf-8")


def create_store(root: Path, kind: str):
    return ArticleStore(root) if kind == "article" else EventStore(root)


def records(store, kind: str):
    values = store.list_metadata() if kind == "article" else store.list_events()
    return [value.model_dump() for value in values]


@pytest.mark.parametrize("kind", ["article", "event"])
@pytest.mark.parametrize("identities", [["same", "same"], ["same", "other", "same"]])
def test_duplicate_ids_are_rejected_instead_of_overwriting_records(tmp_path, kind, identities):
    write_records(tmp_path, kind, identities)
    with pytest.raises(ValueError, match="same"):
        create_store(tmp_path, kind)


@pytest.mark.parametrize("kind", ["article", "event"])
def test_failed_duplicate_reload_retains_the_previous_snapshot(tmp_path, kind):
    write_records(tmp_path, kind, ["old-a", "old-b"])
    store = create_store(tmp_path, kind)
    before = records(store, kind)
    write_records(tmp_path, kind, ["new", "duplicate", "duplicate"])
    with pytest.raises(ValueError, match="duplicate"):
        store.reload()
    assert records(store, kind) == before
    lookup = store.get_article if kind == "article" else store.get_event
    assert lookup("old-a") is not None
    assert lookup("new") is None


@pytest.mark.parametrize("kind", ["article", "event"])
def test_unique_ids_preserve_source_order_and_distinct_payloads(tmp_path, kind):
    write_records(tmp_path, kind, ["second", "first"])
    store = create_store(tmp_path, kind)
    result = records(store, kind)
    assert [entry["id"] for entry in result] == ["second", "first"]
    assert result[0]["title"] != result[1]["title"]
    assert records(store, kind) == result


@pytest.mark.parametrize("kind", ["article", "event"])
def test_case_distinct_ids_remain_distinct(tmp_path, kind):
    write_records(tmp_path, kind, ["Example", "example"])
    assert len(records(create_store(tmp_path, kind), kind)) == 2


@pytest.mark.parametrize("kind", ["article", "event"])
def test_successful_reload_can_replace_records_and_then_clear_them(tmp_path, kind):
    write_records(tmp_path, kind, ["original"])
    store = create_store(tmp_path, kind)
    write_records(tmp_path, kind, ["replacement"])
    store.reload()
    assert [entry["id"] for entry in records(store, kind)] == ["replacement"]
    write_records(tmp_path, kind, [])
    store.reload()
    assert records(store, kind) == []
