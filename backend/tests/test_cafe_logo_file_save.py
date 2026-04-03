from pathlib import Path

import pytest
from fastapi import HTTPException

import app.commands.cafe_commands as cafe_commands


class DummyUpload:
    def __init__(self, filename: str, data: bytes):
        self.filename = filename
        self._data = data

    async def read(self) -> bytes:
        return self._data


@pytest.mark.asyncio
async def test_save_logo_writes_file_to_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(cafe_commands, "LOGO_DIR", str(tmp_path))

    upload = DummyUpload("sample.jpeg", b"image-bytes")
    stored_name = await cafe_commands._save_logo(upload)

    assert stored_name.endswith(".jpeg")
    saved_path = Path(tmp_path) / stored_name
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"image-bytes"


@pytest.mark.asyncio
async def test_save_logo_rejects_large_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cafe_commands, "LOGO_DIR", str(tmp_path))
    monkeypatch.setattr(cafe_commands, "MAX_LOGO_BYTES", 3)

    upload = DummyUpload("large.png", b"1234")

    with pytest.raises(HTTPException) as exc_info:
        await cafe_commands._save_logo(upload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Logo file must be 2 MB or smaller"
