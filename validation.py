import json
import math
from pathlib import Path
from typing import Dict

import pandas as pd

# === Load material property database once at import ===
# Expected format: {"aluminum": {"rpm": [min, max], "feed": [...], "power": ...}, ...}
DB_PATH = Path(__file__).with_name("data") / "materials.json"
MATERIAL_DATA = json.loads(DB_PATH.read_text(encoding="utf-8"))


def validate_plan(df: pd.DataFrame, material: str) -> pd.DataFrame:
    """
    Add 'RPM Valid' and 'Feed Valid' columns to the machining plan based on material limits.

    For operations with both RPM=0 and Feed=0 (non-cutting steps), mark as valid.

    Args:
        df (pd.DataFrame): The machining plan (must include 'Spindle Speed (RPM)' and 'Feed Rate (mm/min)').
        material (str): Material name (e.g., "aluminum").

    Returns:
        pd.DataFrame: Plan with added validation columns.
    """
    limits = MATERIAL_DATA.get(material.lower())
    if limits is None:
        # Unknown material: mark all as invalid
        df["RPM Valid"] = False
        df["Feed Valid"] = False
        return df

    r_min, r_max = limits["rpm"]
    f_min, f_max = limits["feed"]

    # Validate RPM and Feed individually
    df["RPM Valid"]  = df["Spindle Speed (RPM)"].between(r_min, r_max)
    df["Feed Valid"] = df["Feed Rate (mm/min)"].between(f_min, f_max)

    # Non-cutting operation (RPM=0 and Feed=0) → always valid
    mask = (df["Spindle Speed (RPM)"] == 0) & (df["Feed Rate (mm/min)"] == 0)
    df.loc[mask, ["RPM Valid", "Feed Valid"]] = True

    return df


def add_power_check(df: pd.DataFrame,
                    material: str,
                    cutter_diam_mm: float = 10.0) -> pd.DataFrame:
    """
    Add 'Power (kW)' and 'Power Valid' columns based on estimated cutting power.

    Args:
        df (pd.DataFrame): Plan with RPM and Feed columns.
        material (str): Material name.
        cutter_diam_mm (float): Cutter diameter in mm (default: 10.0).

    Returns:
        pd.DataFrame: Plan with estimated power and pass/fail indicator.
    """
    # 1. Get power limit from database (default = 5.0 kW)
    power_limit_kw = MATERIAL_DATA.get(material.lower(), {}).get("power", 5.0)

    # 2. Estimate cutting power using simplified formula:
    # Power = vc * fc, where:
    #   vc: cutting speed (m/s)
    #   fc: cutting force (kN)
    vc = math.pi * cutter_diam_mm * df["Spindle Speed (RPM)"] / 60000  # m/s
    kc = 0.75  # simplified force coefficient
    fc = df["Feed Rate (mm/min)"] / 1000 * kc                          # kN
    df["Power (kW)"] = vc * fc

    # 3. Check if power < 80% of the material's limit
    df["Power Valid"] = df["Power (kW)"] < power_limit_kw * 0.8

    return df


def repair_power_overload(row: Dict,
                          material: str,
                          rpm_min: int, rpm_max: int,
                          feed_min: int, feed_max: int,
                          power_limit: float = 5.0) -> Dict:
    """
    Repair one machining step that exceeds power limit.
    Prefer reducing feed first, then reduce RPM.

    Args:
        row (Dict): Single machining step with keys "Spindle Speed (RPM)", "Feed Rate (mm/min)".
        material (str): Material name (not used directly here, but for consistency).
        rpm_min, rpm_max (int): RPM bounds.
        feed_min, feed_max (int): Feed bounds.
        power_limit (float): Power cap in kW (default: 5.0).

    Returns:
        Dict: A new dictionary with adjusted {"rpm": int, "feed": int}.
    """
    rpm = row["Spindle Speed (RPM)"]
    feed = row["Feed Rate (mm/min)"]

    kc = 0.75
    vc = math.pi * rpm * 10 / 60000  # default cutter diameter: 10 mm
    fc = feed / 1000 * kc
    power = vc * fc

    # Iteratively reduce feed or rpm until power is below threshold
    while power >= power_limit * 0.8:
        if feed > feed_min:
            feed = max(feed_min, feed * 0.9)  # reduce feed by 10%
        elif rpm > rpm_min:
            rpm = max(rpm_min, rpm * 0.9)     # reduce rpm if feed can't go lower
        else:
            break  # both at lower bound, cannot reduce further

        vc = math.pi * rpm * 10 / 60000
        fc = feed / 1000 * kc
        power = vc * fc

    return {"rpm": int(rpm), "feed": int(feed)}
