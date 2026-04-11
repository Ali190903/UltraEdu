"""
Export Qdrant collections as snapshots for production migration.
Run locally: python scripts/export_qdrant_snapshot.py
Then upload the .snapshot files to the production server and run import_qdrant_snapshot.py
"""
import sys
import pathlib
import requests

QDRANT_URL = "http://localhost:6333"
COLLECTIONS = ["textbooks", "dim_tests"]
OUT_DIR = pathlib.Path(__file__).parent.parent / "qdrant_snapshots"
OUT_DIR.mkdir(exist_ok=True)


def create_snapshot(collection: str) -> str:
    resp = requests.post(f"{QDRANT_URL}/collections/{collection}/snapshots")
    resp.raise_for_status()
    name = resp.json()["result"]["name"]
    print(f"[{collection}] Snapshot created: {name}")
    return name


def download_snapshot(collection: str, name: str):
    url = f"{QDRANT_URL}/collections/{collection}/snapshots/{name}"
    dest = OUT_DIR / f"{collection}.snapshot"
    print(f"[{collection}] Downloading to {dest} ...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"[{collection}] Done: {dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    for col in COLLECTIONS:
        try:
            snap_name = create_snapshot(col)
            download_snapshot(col, snap_name)
        except Exception as e:
            print(f"ERROR [{col}]: {e}", file=sys.stderr)

    print(f"\nSnapshots saved to: {OUT_DIR}")
    print("Upload to server and run: python scripts/import_qdrant_snapshot.py")
