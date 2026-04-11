"""
Import Qdrant snapshots on production server.
Run AFTER docker compose is up and qdrant is healthy:
  python scripts/import_qdrant_snapshot.py

Snapshots must be in ./qdrant_snapshots/ directory.
"""
import sys
import pathlib
import requests

QDRANT_URL = "http://localhost:6333"
COLLECTIONS = ["textbooks", "dim_tests"]
SNAP_DIR = pathlib.Path(__file__).parent.parent / "qdrant_snapshots"
VECTOR_DIM = 3072


def collection_exists(collection: str) -> bool:
    resp = requests.get(f"{QDRANT_URL}/collections/{collection}")
    return resp.status_code == 200


def create_collection(collection: str):
    resp = requests.put(
        f"{QDRANT_URL}/collections/{collection}",
        json={"vectors": {"size": VECTOR_DIM, "distance": "Cosine"}},
    )
    resp.raise_for_status()
    print(f"[{collection}] Collection created")


def upload_and_restore(collection: str):
    snap_file = SNAP_DIR / f"{collection}.snapshot"
    if not snap_file.exists():
        print(f"[{collection}] ERROR: snapshot file not found: {snap_file}")
        return

    print(f"[{collection}] Uploading snapshot ({snap_file.stat().st_size // 1024} KB)...")
    with open(snap_file, "rb") as f:
        resp = requests.post(
            f"{QDRANT_URL}/collections/{collection}/snapshots/upload?priority=snapshot",
            files={"snapshot": (snap_file.name, f, "application/octet-stream")},
        )
    resp.raise_for_status()
    print(f"[{collection}] Restored successfully")

    count_resp = requests.get(f"{QDRANT_URL}/collections/{collection}")
    count = count_resp.json()["result"]["points_count"]
    print(f"[{collection}] Points: {count}")


if __name__ == "__main__":
    for col in COLLECTIONS:
        try:
            if not collection_exists(col):
                create_collection(col)
            upload_and_restore(col)
        except Exception as e:
            print(f"ERROR [{col}]: {e}", file=sys.stderr)
