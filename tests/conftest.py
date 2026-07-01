import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def music_dir():
    # audio fixtures are local-only (not committed); skip integration tests without them
    if not any(FIXTURES_DIR.glob("*.mp3")):
        pytest.skip("no audio fixtures present")
    return FIXTURES_DIR
