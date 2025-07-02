# validation.py
import json, math, pandas as pd
from pathlib import Path

# load database once
DB_PATH = Path(__file__).with_name("data") / "materials.json"
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
    
    # 非切削工序（rpm=0 且 feed=0）强制判定为 True
    mask = (df["Spindle Speed (RPM)"] == 0) & (df["Feed Rate (mm/min)"] == 0)
    df.loc[mask, ["RPM Valid", "Feed Valid"]] = True 
    
    return df


# --- optional: power / torque check ---------------------------------
def add_power_check(df: pd.DataFrame,
                    material: str,
                    cutter_diam_mm: float = 10.0) -> pd.DataFrame:
    """
    Add 'Power (kW)'  and 'Power Valid' columns.
    Power limit (kW) is read from materials.json -> "power".
    """
    # 1) 取得该材料功率上限，默认为 5 kW
    power_limit_kw = MATERIAL_DATA.get(material.lower(), {}).get("power", 5.0)

    # 2) 计算粗略切削功率
    vc = math.pi * cutter_diam_mm * df["Spindle Speed (RPM)"] / 60_000  # 切削速度 m/s
    kc = 0.75                                                           # 简化切削力系数
    fc = df["Feed Rate (mm/min)"] / 1000 * kc                           # kN
    df["Power (kW)"]  = vc * fc                                         # kW

    # 3) 校验功率是否低于 80% 上限
    df["Power Valid"] = df["Power (kW)"] < power_limit_kw * 0.8
    return df