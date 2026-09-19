import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_verifier():
    path = ROOT / "_scripts" / "verify_release_metadata.py"
    spec = importlib.util.spec_from_file_location("rpx_release_metadata", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseMetadataTests(unittest.TestCase):
    def test_release_metadata_is_aligned(self):
        result = _load_verifier().verify(ROOT)
        self.assertEqual(result["release_status"], "Unreleased")
        self.assertEqual(result["application_version"], "1.0.0")
        self.assertEqual(result["store_version"], "1.0.0.0")


if __name__ == "__main__":
    unittest.main()
