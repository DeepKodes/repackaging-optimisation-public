"""
Generate synthetic SKU and box data for the repackaging-optimisation project.

The original coursework used confidential client data supplied by the university.
This script produces fake data with the SAME structure and the SAME kind of
patterns (a small number of large standard boxes used for a population of much
smaller, dimensionally-varied SKUs) so that anyone cloning the repo can run the
full pipeline and the Streamlit dashboard end-to-end without the client data.

"""

import os
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)         
N_SKUS = 900
OUT_DIR = "data_files"

ARCHETYPES = [
    ((160, 120,  80),  16, 0.30),   # small parcels
    ((320, 240, 150),  22, 0.27),   # medium boxes
    ((470, 300,  60),  20, 0.20),   # flat / wide items
    ((600, 130, 100),  22, 0.16),   # long / narrow items
    ((540, 400, 300),  28, 0.07),   # large items
]

OVERSIZED = [
    (1450, 980, 760),
    (1380, 1050, 700),
    (1500, 900, 820),
    (1420, 1010, 690),
]


def _make_sku(mean, spread):
    dims = RNG.normal(loc=mean, scale=spread)
    dims = np.clip(dims, 30, None)              # no sub-30mm dimensions
    return np.round(dims).astype(int)


def build_returns():
    means = [a[0] for a in ARCHETYPES]
    spreads = [a[1] for a in ARCHETYPES]
    weights = np.array([a[2] for a in ARCHETYPES])
    weights = weights / weights.sum()

    rows = []
    n_normal = N_SKUS - len(OVERSIZED)
    cluster_ids = RNG.choice(len(ARCHETYPES), size=n_normal, p=weights)

    for i, c in enumerate(cluster_ids):
        l, w, h = _make_sku(means[c], spreads[c])
        qty = int(RNG.integers(1, 40))          # units per SKU line
        rows.append((f"SKU{i + 1:04d}", l, w, h, qty))

    # append the oversized outlier SKUs with small quantities
    for j, (l, w, h) in enumerate(OVERSIZED):
        rows.append((f"SKU{n_normal + j + 1:04d}", l, w, h, int(RNG.integers(1, 6))))

    df = pd.DataFrame(rows, columns=["sku_id", "l", "w", "h", "quantity"])
    return df.sample(frac=1, random_state=1).reset_index(drop=True)   # shuffle


def build_current_boxes():
    # Five large standard boxes (mirrors the real "few sizes, lots of void" setup).
    boxes = [
        ("AS", 450, 350, 250),
        ("BS", 700, 500, 350),
        ("CS", 950, 650, 450),
        ("DS", 1100, 800, 550),
        ("ES", 1300, 950, 720),
    ]
    return pd.DataFrame(boxes, columns=["box_id", "l", "w", "h"])


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    returns = build_returns()
    boxes = build_current_boxes()
    returns.to_csv(os.path.join(OUT_DIR, "returns_data.csv"), index=False)
    boxes.to_csv(os.path.join(OUT_DIR, "current_boxes.csv"), index=False)
    print(f"Wrote {len(returns)} SKU lines ({returns['quantity'].sum()} units) "
          f"and {len(boxes)} boxes to ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
