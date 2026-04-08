from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

# ---------- FILE PATHS ----------
REDLINING_PATH = Path("redlining.geojson")
TRACT_GEOMETRY_PATH = Path("US_tract_2020.shp")
TRACT_CSV_PATH = Path("nhgis0001_ds258_2020_tract.csv")
OUTPUT_PATH = Path("districtStats.json")

# ---------- NHGIS COLUMN MAP ----------
# These labels are inferred from the arithmetic pattern in your CSV and should be
# spot-checked against the NHGIS codebook for your extract.
NHGIS_COLS = {
    "total": "U7L001",
    "non_hispanic_total": "U7L002",
    "non_hispanic_white": "U7L003",
    "non_hispanic_black": "U7L004",
    "non_hispanic_native": "U7L005",
    "non_hispanic_asian": "U7L006",
    "non_hispanic_pacific": "U7L007",
    "non_hispanic_other": "U7L008",
    "non_hispanic_multiracial": "U7L009",
    "hispanic_total": "U7L010",
    "hispanic_white": "U7L011",
    "hispanic_black": "U7L012",
    "hispanic_native": "U7L013",
    "hispanic_asian": "U7L014",
    "hispanic_pacific": "U7L015",
    "hispanic_other": "U7L016",
    "hispanic_multiracial": "U7L017",
}


def load_redlining(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if "area_id" not in gdf.columns:
        raise ValueError("redlining file must contain an 'area_id' column")
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf[[c for c in ["area_id", "label", "grade", "category", "city", "state", "geometry"] if c in gdf.columns]].copy()



def load_tracts(geometry_path: Path, csv_path: Path) -> gpd.GeoDataFrame:
    tracts_geom = gpd.read_file(geometry_path)
    if tracts_geom.crs is None:
        tracts_geom = tracts_geom.set_crs("EPSG:4326")

    # Normalize tract GEOID so it matches the NHGIS CSV.
    possible_geoid_cols = [c for c in ["GEOID", "geoid", "TRACTCE", "GEOIDFQ"] if c in tracts_geom.columns]
    if not possible_geoid_cols:
        raise ValueError("tract geometry file needs a GEOID-like column (e.g. GEOID or GEOIDFQ)")

    geoid_col = possible_geoid_cols[0]
    tracts_geom = tracts_geom.copy()
    tracts_geom["TRACT_GEOID"] = tracts_geom[geoid_col].astype(str)

    # Some TIGER/NHGIS files use fully qualified GEOIDs like 1400000US25001010100.
    tracts_geom["TRACT_GEOID"] = tracts_geom["TRACT_GEOID"].str.replace("1400000US", "", regex=False)

    csv_df = pd.read_csv(csv_path, dtype={"GEOCODE": str, "GEOID": str})
    csv_df = csv_df.rename(columns={"GEOCODE": "TRACT_GEOID", "GEOID": "TRACT_GEOID_FULL"})
    csv_df["TRACT_GEOID"] = csv_df["TRACT_GEOID"].str.replace(r"\.0$", "", regex=True)

    needed = ["TRACT_GEOID"] + list(NHGIS_COLS.values())
    missing = [c for c in needed if c not in csv_df.columns]
    if missing:
        raise ValueError(f"CSV is missing expected columns: {missing}")

    csv_df = csv_df[needed].copy()
    for col in NHGIS_COLS.values():
        csv_df[col] = pd.to_numeric(csv_df[col], errors="coerce").fillna(0)

    merged = tracts_geom.merge(csv_df, on="TRACT_GEOID", how="inner")
    if merged.empty:
        raise ValueError("No tract geometries matched the CSV. Check your GEOID formatting.")

    keep_cols = ["TRACT_GEOID", "geometry"] + list(NHGIS_COLS.values())
    return merged[keep_cols].copy()



def build_weighted_overlay(tracts: gpd.GeoDataFrame, redlining: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Use a projected CRS so areas are meaningful.
    projected_crs = "EPSG:26986"  # Massachusetts Mainland / meters
    red_proj = redlining.to_crs(projected_crs)
    tracts_proj = tracts.to_crs(projected_crs)

    tracts_proj["tract_area_m2"] = tracts_proj.geometry.area

    overlay = gpd.overlay(
        tracts_proj,
        red_proj,
        how="intersection",
        keep_geom_type=False,
    )
    if overlay.empty:
        raise ValueError("Overlay returned no intersections. Check that both files cover the same geography.")

    overlay["intersection_area_m2"] = overlay.geometry.area
    overlay["area_weight"] = overlay["intersection_area_m2"] / overlay["tract_area_m2"]
    overlay["area_weight"] = overlay["area_weight"].clip(lower=0, upper=1)

    for friendly_name, col in NHGIS_COLS.items():
        overlay[f"weighted_{friendly_name}"] = overlay[col] * overlay["area_weight"]

    return overlay



def summarize_by_district(overlay: gpd.GeoDataFrame) -> list[dict]:
    weighted_cols = [f"weighted_{k}" for k in NHGIS_COLS.keys()]
    meta_cols = [c for c in ["area_id", "label", "grade", "category", "city", "state"] if c in overlay.columns]

    summary = overlay.groupby("area_id", as_index=False)[weighted_cols].sum()
    meta = overlay[meta_cols].drop_duplicates(subset=["area_id"])
    summary = summary.merge(meta, on="area_id", how="left")

    output = []
    for _, row in summary.iterrows():
        total = float(row["weighted_total"])
        if total <= 0:
            continue

        # Build a frontend-friendly structure.
        stats = {
            "total_population_2020": round(total),
            "pct_non_hispanic_white": row["weighted_non_hispanic_white"] / total,
            "pct_non_hispanic_black": row["weighted_non_hispanic_black"] / total,
            "pct_non_hispanic_asian": row["weighted_non_hispanic_asian"] / total,
            "pct_hispanic": row["weighted_hispanic_total"] / total,
            "pct_non_hispanic_native": row["weighted_non_hispanic_native"] / total,
            "pct_non_hispanic_pacific": row["weighted_non_hispanic_pacific"] / total,
            "pct_non_hispanic_other": row["weighted_non_hispanic_other"] / total,
            "pct_non_hispanic_multiracial": row["weighted_non_hispanic_multiracial"] / total,
            "pct_other_combined": (
                row["weighted_non_hispanic_native"]
                + row["weighted_non_hispanic_pacific"]
                + row["weighted_non_hispanic_other"]
                + row["weighted_non_hispanic_multiracial"]
            ) / total,
        }

        output.append(
            {
                "area_id": int(row["area_id"]),
                "label": row.get("label"),
                "grade": row.get("grade"),
                "category": row.get("category"),
                "city": row.get("city"),
                "state": row.get("state"),
                "stats": {k: round(v, 4) if isinstance(v, float) else v for k, v in stats.items()},
            }
        )

    output.sort(key=lambda x: x["area_id"])
    return output



def main() -> None:
    redlining = load_redlining(REDLINING_PATH)
    tracts = load_tracts(TRACT_GEOMETRY_PATH, TRACT_CSV_PATH)
    overlay = build_weighted_overlay(tracts, redlining)
    district_stats = summarize_by_district(overlay)

    OUTPUT_PATH.write_text(json.dumps(district_stats, indent=2))
    print(f"Wrote {len(district_stats)} districts to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
