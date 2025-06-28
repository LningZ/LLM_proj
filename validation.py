# validation.py
import json, math, pandas as pd
from pathlib import Path

# load database once
DB_PATH = Path(__file__).with_name("materials.json")
MATERIAL_DATA = json.loads(DB_PATH.read_text(encoding="utf-8"))

def validate_plan(df: pd.DataFrame, material: str) -> pd.DataFrame:
    """Add 'RPM Valid' & 'Feed Valid' columns based on material database."""
    limits = MATERIAL_DATA.get(material.lower())
    if limits is None:
        # unknown material -> mark invalid
        df["RPM Valid"] = False
        df["Feed Valid"] = False
        return df

    r_min, r_max = limits["rpm"]
    f_min, f_max = limits["feed"]

    df["RPM Valid"]  = df["Spindle Speed (RPM)"].between(r_min, r_max)
    df["Feed Valid"] = df["Feed Rate (mm/min)"].between(f_min, f_max)
    return df


# --- optional: power / torque check ---------------------------------
def add_power_check(df: pd.DataFrame,
                    cutter_diam_mm: float = 10.0,
                    power_limit_kw: float = 5.0) -> pd.DataFrame:
    """Rough power = cutting force × cutting speed."""
    vc = math.pi * cutter_diam_mm * df["Spindle Speed (RPM)"] / 60_000  # m/s
    kc = 0.75  # cutting-force coefficient (simplified)
    fc = df["Feed Rate (mm/min)"] / 1000 * kc  # kN
    df["Power (kW)"]   = vc * fc               # kW
    df["Power Valid"]  = df["Power (kW)"] < power_limit_kw * 0.8
    return df
