# jbg-present

Presentation images for the **Jack Beatnic Gallery** (`jackbeatnic.github.io`).

This is **not** mint media and **not** the shop.

| Repo | Role |
|------|------|
| `jackbeatnic.github.io` | WWW — gallery app |
| `jb-nft-assets` | on-chain / mint originals + meta |
| `jbg-shop` | studio shop (separate) |
| `jbg-present` | this repo — thumbs + View only |

## Rules

- Files here are **WebP derivatives**, always smaller than the offline backup original.
- Grid: `{collection_id}/{token_id}.thumb.webp` (max 440 px)
- Lightbox: `{collection_id}/{token_id}.view.webp` (max 900 px, below 1600–2048 originals)
- Never publish backup JPGs here.

## Live

https://jackbeatnic.github.io/jbg-present/

## New image (run yourself)

See **CZYTAJ_MNIE.txt**. Short version:

```bash
cd ~/jb_nft/jbg-present
python3 build.py --collection avalanche_nature_stories --id 388 --src /path/oryginał.jpg --push
```

Or drop `inbox/<collection>/<token_id>.jpg` and run `python3 build.py --inbox --push`.
