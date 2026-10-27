# Copyright (c) 2024-2026 Aditya001-max <kaushikadityaraj001@gmail.com>
# MIT License

import os
import tempfile
import pytest
from pillow_engine import parse_song_file, generate_all_slides
from slidegen_web import app


@pytest.fixture
def sample_song_file():
    content = """title: Test Anthem
book: Test Hymnal #1
text: Test Lyricist
melody: Test Composer
structure: 1, 2

[1]
Line one of verse one.
Line two of verse one.

[2]
Line one of verse two.
Line two of verse two.
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_parse_song_file(sample_song_file):
    metadata, songtext = parse_song_file(sample_song_file)
    assert metadata["title"] == "Test Anthem"
    assert metadata["book"] == "Test Hymnal #1"
    assert metadata["text"] == "Test Lyricist"
    assert metadata["melody"] == "Test Composer"
    assert metadata["structure"] == "1, 2"
    assert "1" in songtext
    assert "2" in songtext
    assert "Line one of verse one." in songtext["1"]


def test_generate_all_slides(sample_song_file):
    with tempfile.TemporaryDirectory() as temp_out:
        slides = generate_all_slides(sample_song_file, temp_out)
        # 1 start slide + 2 verses = 3 slides
        assert len(slides) == 3
        for slide_path in slides:
            assert os.path.isfile(slide_path)
            assert os.path.getsize(slide_path) > 1000


def test_web_server_health():
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["author"] == "Aditya001-max"


def test_web_server_generate_endpoint():
    client = app.test_client()
    resp = client.post("/api/generate", json={"text": "title: Demo\n[1]\nHi", "structure": "1"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
