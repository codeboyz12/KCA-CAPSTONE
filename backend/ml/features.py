"""Inference-time feature engineering, mirroring notebook/train.py."""

import numpy as np
import pandas as pd
from ml.encoders import BinaryEncoder  # noqa: F401 — ensures pickle can resolve the class


def _percentile_in_array(value: float, arr: np.ndarray) -> float:
    """Percentile rank of value within a sorted-or-unsorted array (0-1)."""
    if len(arr) == 0:
        return 0.5
    return float(np.searchsorted(np.sort(arr), value)) / len(arr)


def build_features(data: dict, artifacts: dict) -> pd.DataFrame:
    """
    Convert a raw campaign dict into a DataFrame with TOP15 features ready
    for the classifier.  `data` must contain all fields from CampaignInputV2.
    """
    name         = str(data.get("name", ""))
    category     = str(data.get("category", ""))
    main_category = str(data.get("main_category", ""))
    country      = str(data.get("country", "US"))
    goal_usd     = float(data["goal_usd"])
    duration_days = int(data["duration_days"])
    launch_year   = int(data.get("launch_year", 2020))
    launch_month  = int(data.get("launch_month", 6))
    launch_day    = int(data.get("launch_day", 15))
    launch_hour   = int(data.get("launch_hour", 12))
    launch_minute = int(data.get("launch_minute", 0))
    deadline_year  = int(data.get("deadline_year", launch_year))
    deadline_month = int(data.get("deadline_month", launch_month))
    deadline_day   = int(data.get("deadline_day", launch_day))
    deadline_hour  = int(data.get("deadline_hour", launch_hour))
    deadline_minute = int(data.get("deadline_minute", launch_minute))

    row: dict = {
        "country": country,
        "goal_usd": goal_usd,
        "duration_days": duration_days,
        "launch_year": launch_year,
        "launch_month": launch_month,
        "launch_day": launch_day,
        "launch_hour": launch_hour,
        "launch_minute": launch_minute,
        "deadline_year": deadline_year,
        "deadline_month": deadline_month,
        "deadline_day": deadline_day,
        "deadline_hour": deadline_hour,
        "deadline_minute": deadline_minute,
        "category": category,
        "main_category": main_category,
    }

    # ------------------------------------------------------------------ A: Goal
    row["goal_usd_log"]     = np.log1p(goal_usd)
    row["goal_on_duration"] = goal_usd / (duration_days + 1)
    row["goal_per_week"]    = goal_usd / ((duration_days / 7) + 1)

    # ------------------------------------------------------------------ B: Text
    row["name_len"]        = len(name)
    words = name.split()
    row["name_word_count"] = len(words)
    row["avg_word_len"]    = len(name) / (len(words) + 1)
    row["has_exclamation"] = int("!" in name)
    row["has_number"]      = int(any(c.isdigit() for c in name))
    row["is_upper"]        = int(name.isupper())
    row["name_has_colon"]  = int(":" in name)
    row["name_title_case"] = int(name.istitle())
    row["name_len_sq"]     = len(name) ** 2

    # ------------------------------------------------------------------ C: Time
    launch_year_min = artifacts["launch_year_min"]
    row["launch_year_norm"]           = launch_year - launch_year_min
    row["launch_quarter"]             = (launch_month - 1) // 3
    row["deadline_quarter"]           = (deadline_month - 1) // 3
    row["launch_deadline_month_diff"] = deadline_month - launch_month
    row["launch_deadline_hour_diff"]  = deadline_hour - launch_hour
    row["is_weekend_launch"]          = int(launch_day in (6, 7))
    row["is_night_launch"]            = int(launch_hour >= 22 or launch_hour <= 5)
    row["launch_is_monday"]           = int(launch_day == 1)
    row["launch_is_tuesday"]          = int(launch_day == 2)
    hour_bucket = 0 if launch_hour <= 6 else (1 if launch_hour <= 12 else (2 if launch_hour <= 18 else 3))
    row["launch_hour_bucket"]         = hour_bucket

    dur_bins = artifacts["dur_bins"]
    row["duration_bucket_q"] = int(np.searchsorted(dur_bins[1:-1], duration_days))

    # Competition density lookup
    comp_lookup = artifacts["comp_lookup"]
    n_comp = comp_lookup.get((main_category, launch_month), 1)
    row["n_competitors"]    = n_comp
    row["competition_score"] = np.log1p(n_comp)

    mc_vals = artifacts.get("mc_competitor_values", {}).get(main_category)
    if mc_vals is not None and len(mc_vals) > 0:
        row["competition_pct"] = _percentile_in_array(n_comp, mc_vals)
    else:
        row["competition_pct"] = 0.5

    # ------------------------------------------------------------------ D: Country binary encoding
    df_row = pd.DataFrame([row])
    df_row = artifacts["binary_enc"].transform(df_row)
    row = df_row.iloc[0].to_dict()

    # ------------------------------------------------------------------ E: Category aggregations
    agg_map = artifacts["agg_map"]
    for feat, mapping in agg_map.items():
        row[feat] = float(mapping.get(category, mapping.median()))

    # ------------------------------------------------------------------ F: Ratio / Rank
    cat_goals = artifacts["cat_goal_arrays"].get(category)
    if cat_goals is not None and len(cat_goals) > 0:
        row["goal_rank_in_cat"] = _percentile_in_array(goal_usd, cat_goals)
    else:
        row["goal_rank_in_cat"] = _percentile_in_array(
            goal_usd, artifacts["global_goal_array"]
        )

    row["goal_vs_cat_mean"]   = goal_usd / (row["mean_goal_in_cat"]   + 1)
    row["goal_vs_cat_median"] = goal_usd / (row["median_goal_in_cat"] + 1)
    row["log_goal_ratio"]     = np.log1p(row["goal_vs_cat_median"])
    row["goal_x_duration"]    = row["goal_usd_log"] * duration_days

    log_bins  = artifacts["train_goal_log_bins"]
    row["goal_bucket"] = float(
        np.clip(np.searchsorted(log_bins[1:-1], row["goal_usd_log"]), 0, 4)
    )
    quant_bins = artifacts["train_goal_quant_bins"]
    row["goal_bucket_quantile"] = float(
        np.clip(np.searchsorted(quant_bins[1:-1], goal_usd), 0, 4)
    )

    # ------------------------------------------------------------------ G: Flags
    thresh = artifacts["thresholds"]
    row["low_success_cat"] = int(row["cat_success_rate"]   <= thresh["SUCCESS_THRESH"])
    row["low_goal_vs_cat"] = int(row["goal_vs_cat_median"] <= thresh["GOAL_VS_MED_LOW"])
    row["small_project"]   = int(row["goal_rank_in_cat"]   <= thresh["GOAL_RANK_LOW"])
    row["hard_project"]    = int(
        row["goal_vs_cat_mean"] >= thresh["GOAL_VS_MEAN_HIGH"] and duration_days < 30
    )
    row["easy_win"]          = int(row["small_project"] == 1 and row["low_goal_vs_cat"] == 1)
    row["competition_level"] = np.log1p(row["cat_project_count"])

    # ------------------------------------------------------------------ H: Interactions
    row["success_rate_x_rank"] = row["cat_success_rate"] * row["goal_rank_in_cat"]
    row["success_rate_x_goal"] = row["cat_success_rate"] * row["goal_usd_log"]

    # ------------------------------------------------------------------ I: Target encoding
    df_row = pd.DataFrame([row])
    df_row[["category", "main_category"]] = artifacts["target_enc"].transform(
        df_row[["category", "main_category"]]
    )
    row = df_row.iloc[0].to_dict()

    # ------------------------------------------------------------------ J: Lag feature
    lag1_map = artifacts["lag1_map"]
    prev_month = launch_month - 1 if launch_month > 1 else 12
    row["lag1_sr"] = lag1_map.get((main_category, prev_month), row["cat_success_rate"])

    # ------------------------------------------------------------------ Final
    top15 = artifacts["top15_features"]
    result = pd.DataFrame([row])
    for col in top15:
        if col not in result.columns:
            result[col] = 0.0
    return result[top15].fillna(0).astype(float)
