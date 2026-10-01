# jbg-present

Presentation images for the **Jack Beatnic Gallery** (`jackbeatnic.github.io`).

This is **not** mint media and **not** the shop.

| Repo | Role |
|------|------|
| `jackbeatnic.github.io` | WWW — gallery app |
| `jb-nft-assets` | on-chain / mint originals + meta |
| `jbg-shop` | studio shop (separate) |
| `jbg-present` | this repo — thumbs + View only |
| `jbg-og` | 1200×630 share cards (not this repo) |

## Rules

- Files here are **WebP derivatives**, always smaller than the offline backup original.
- Grid: `{collection_id}/{token_id}.thumb.webp` (max 440 px)
- Lightbox: `{collection_id}/{token_id}.view.webp` (max 900 px, below 1600–2048 originals)
- Never publish backup JPGs here.
- The original (2048 / ~1600) never goes to the site. The script only writes
  smaller WebPs: thumb 440 and view 900 (never 100% of the backup).

## Live

https://jackbeatnic.github.io/jbg-present/

## Usage (run it yourself)

Install once:

```bash
cd ~/jb_nft/jbg-present
pip install -r requirements.txt
```

### One new image

```bash
python3 build.py \
  --collection avalanche_nature_stories \
  --id 388 \
  --src /path/to/original.jpg \
  --push
```

### Or drop files into the inbox

1. Copy the JPG as `inbox/avalanche_nature_stories/388.jpg`
   (file name = token_id, the same as on OpenSea).
2. Run `python3 build.py --inbox --push`

The original is moved to `inbox/_done/` (it is not published to Pages).

### From the local backup

```bash
python3 build.py --from-backup \
  --collection avalanche_nature_stories \
  --ids 388,389 \
  --push
```

### Shop thumbnails (without adding entries to AI Art)

The shop reads the same URLs as AI Art (`collection_id` + `token_id`) and does
not add entries to `gallery.json`. Shop thumbnails are generated in bulk by the
local pipeline (shop mode, offline mint sources, skipping existing files); then
from `jbg-present`: `git add -A && git commit && git push` and wait ~1 min for
GitHub Pages.

## Output

```text
avalanche_nature_stories/388.thumb.webp   ← grid
avalanche_nature_stories/388.view.webp    ← View button
```

The gallery looks these URLs up on its own (`collection_id` + `token_id`).
After `--push`, wait ~1 min for GitHub Pages, then hard-refresh the page.

## Don't

- ✗ put 2048 JPGs into a collection folder
- ✗ confuse this with `jb-nft-assets` (mint / on-chain)
- ✗ confuse this with `jbg-shop`
