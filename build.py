#!/usr/bin/env python3
"""Build gallery cache: thumb + view WebP. Never publishes the original.

Run this yourself when a new image exists. The 2048 / ~1600 JPG stays
offline (backup or inbox). Only smaller WebPs are written and pushed.

  # one new file
  python3 build.py --collection avalanche_nature_stories --id 388 --src /path/nowy.jpg

  # drop files as inbox/<collection>/<token_id>.jpg then:
  python3 build.py --inbox

  # from jb_nft backup_offline (same machine)
  python3 build.py --from-backup --collection avalanche_nature_stories --id 388

  python3 build.py --inbox --push
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Potrzebny Pillow:  pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "inbox"
BACKUP_DEFAULT = ROOT.parent / "backup_offline" / "by_collection"

THUMB_MAX = 440
VIEW_MAX = 900
THUMB_Q = 72
VIEW_Q = 70
# If the source is already small, still shrink — never ship 100% of original.
SHRINK_IF_SMALLER = 0.72

STEM_ID = re.compile(r"^(\d+)$")


def target_side(orig_long: int, cap: int) -> int:
    if orig_long <= cap:
        return max(64, int(orig_long * SHRINK_IF_SMALLER))
    return cap


def write_pair(src: Path, dest_dir: Path, token_id: int) -> tuple[Path, Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = dest_dir / f"{token_id}.thumb.webp"
    view_path = dest_dir / f"{token_id}.view.webp"
    with Image.open(src) as im:
        im = im.convert("RGB")
        long_side = max(im.size)
        t = target_side(long_side, THUMB_MAX)
        v = target_side(long_side, VIEW_MAX)
        thumb = im.copy()
        thumb.thumbnail((t, t), Image.Resampling.LANCZOS)
        view = im.copy()
        view.thumbnail((v, v), Image.Resampling.LANCZOS)
        thumb.save(thumb_path, "WEBP", quality=THUMB_Q, method=6)
        view.save(view_path, "WEBP", quality=VIEW_Q, method=6)
        if max(thumb.size) >= long_side or max(view.size) >= long_side:
            raise SystemExit(
                f"Odmowa: wynik nie jest mniejszy niż oryginał {src} ({long_side}px)"
            )
    return thumb_path, view_path


def find_backup(collection: str, token_id: int, backup_root: Path) -> Path | None:
    media = backup_root / collection / "media"
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".avif"):
        p = media / f"{token_id}{ext}"
        if p.is_file():
            return p
    return None


def parse_ids(raw: str | None, single: int | None) -> list[int]:
    ids: list[int] = []
    if single is not None:
        ids.append(single)
    if raw:
        for part in raw.split(","):
            part = part.strip()
            if part:
                ids.append(int(part))
    return sorted(set(ids))


def jobs_from_inbox() -> list[tuple[str, int, Path]]:
    jobs = []
    if not INBOX.is_dir():
        return jobs
    for col_dir in sorted(p for p in INBOX.iterdir() if p.is_dir() and p.name != "_done"):
        for src in sorted(col_dir.iterdir()):
            if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
                continue
            m = STEM_ID.match(src.stem)
            if not m:
                print(f"  pomijam (nazwa nie jest token_id): {src}", file=sys.stderr)
                continue
            jobs.append((col_dir.name, int(m.group(1)), src))
    return jobs


def git_push(paths: list[Path]) -> None:
    rel = [str(p.relative_to(ROOT)) for p in paths]
    subprocess.check_call(["git", "add", "--", *rel], cwd=ROOT)
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", *rel],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    if not status.stdout.strip():
        print("git: brak nowych plików do push")
        return
    msg = "Present cache: " + ", ".join(rel[:8])
    if len(rel) > 8:
        msg += f" (+{len(rel) - 8})"
    subprocess.check_call(["git", "commit", "-m", msg], cwd=ROOT)
    subprocess.check_call(["git", "push", "origin", "HEAD"], cwd=ROOT)
    print("pushed → https://jackbeatnic.github.io/jbg-present/")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--collection", help="np. avalanche_nature_stories")
    ap.add_argument("--id", type=int, help="jeden token_id")
    ap.add_argument("--ids", help="lista: 388,389,390")
    ap.add_argument("--src", type=Path, help="ścieżka do oryginału JPG (nie kopiujemy go)")
    ap.add_argument("--inbox", action="store_true", help="weź inbox/<collection>/<id>.jpg")
    ap.add_argument("--from-backup", action="store_true")
    ap.add_argument(
        "--backup-root",
        type=Path,
        default=BACKUP_DEFAULT,
        help="backup_offline/by_collection",
    )
    ap.add_argument("--push", action="store_true", help="git commit + push na Pages")
    args = ap.parse_args()

    jobs: list[tuple[str, int, Path]] = []

    if args.inbox:
        jobs.extend(jobs_from_inbox())
        if not jobs:
            print("inbox pusty — wrzuć pliki jako inbox/<collection>/<token_id>.jpg")
            return 1

    ids = parse_ids(args.ids, args.id)
    if args.src:
        if not args.collection or not ids:
            raise SystemExit("--src wymaga --collection i --id")
        if not args.src.is_file():
            raise SystemExit(f"brak pliku: {args.src}")
        jobs.append((args.collection, ids[0], args.src.resolve()))
        ids = ids[1:]

    if args.from_backup:
        if not args.collection or not ids:
            raise SystemExit("--from-backup wymaga --collection i --id/--ids")
        for tid in ids:
            src = find_backup(args.collection, tid, args.backup_root)
            if not src:
                raise SystemExit(f"brak backupu {args.collection}/{tid} w {args.backup_root}")
            jobs.append((args.collection, tid, src))
        ids = []

    if ids:
        raise SystemExit("zostały --id/--ids bez --src ani --from-backup")

    if not jobs:
        ap.print_help()
        return 1

    written: list[Path] = []
    for collection, tid, src in jobs:
        dest = ROOT / collection
        thumb, view = write_pair(src, dest, tid)
        print(
            f"OK {collection} #{tid}  "
            f"thumb={thumb.name} ({thumb.stat().st_size} B)  "
            f"view={view.name} ({view.stat().st_size} B)  "
            f"src={src.name} [oryginał nie skopiowany]"
        )
        written.extend([thumb, view])
        if args.inbox and INBOX in src.parents:
            done = INBOX / "_done" / collection
            done.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(done / src.name))

    print(f"\n{len(jobs)} prac. Live:")
    for collection, tid, _src in jobs:
        print(
            f"  https://jackbeatnic.github.io/jbg-present/{collection}/{tid}.thumb.webp"
        )

    if args.push:
        git_push(written)
    else:
        print("\nBez --push. Gdy gotowe:  python3 build.py --inbox --push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
