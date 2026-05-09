"""Vision multimodal dispatch helpers and CLI flags (ham-022b commit 2)."""

from __future__ import annotations

import base64
import sys
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))

from hammerstein import backends  # noqa: E402
from hammerstein.cli import build_parser, main  # noqa: E402

# Smallest valid 1x1 transparent PNG (hand-verified structure).
_MIN_PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_load_image_as_base64_returns_data_and_media_type(tmp_path: Path) -> None:
    path = tmp_path / "one.png"
    path.write_bytes(_MIN_PNG_1X1)
    b64, mt = backends.load_image_as_base64(str(path))
    assert mt == "image/png"
    assert isinstance(b64, str)
    assert base64.b64decode(b64.encode("ascii")) == _MIN_PNG_1X1


def test_load_image_as_base64_rejects_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "nope.png"
    with pytest.raises(backends.BackendError, match="not found"):
        backends.load_image_as_base64(str(missing))


def test_load_image_as_base64_rejects_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "x.gif"
    path.write_bytes(b"")
    with pytest.raises(backends.BackendError, match="unsupported image extension"):
        backends.load_image_as_base64(str(path))


def test_image_argparse_flag_present() -> None:
    args = build_parser().parse_args(["--image", "foo.png", "query"])
    assert args.image == "foo.png"
    args2 = build_parser().parse_args(["query"])
    assert args2.image is None


def test_backend_tier_argparse_flag_present() -> None:
    args = build_parser().parse_args(["--backend-tier", "free", "query"])
    assert args.backend_tier == "free"
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--backend-tier", "expensive", "query"])


def test_image_only_with_audit_this_visual() -> None:
    code = main(
        ["--image", "any.png", "--template", "audit-this-plan", "hello"]
    )
    assert code == 2


def test_deepseek_vision_probe_silent_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_a, **_kw):
        raise OSError("network down")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert backends.deepseek_supports_vision("fake-key") is False
