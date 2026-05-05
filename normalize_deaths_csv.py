#!/usr/bin/env python3
"""Normalize CovidDeaths.csv for friendlier DataGrip type detection."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


INTEGER_COLUMNS = {
    "total_cases",
    "new_cases",
    "total_deaths",
    "new_deaths",
    "icu_patients",
    "hosp_patients",
    "weekly_icu_admissions",
    "weekly_hosp_admissions",
    "new_tests",
    "total_tests",
    "new_tests_smoothed",
    "total_vaccinations",
    "people_vaccinated",
    "people_fully_vaccinated",
    "new_vaccinations",
    "new_vaccinations_smoothed",
    "population",
}

FLOAT_COLUMNS = {
    "new_cases_smoothed",
    "new_deaths_smoothed",
    "total_cases_per_million",
    "new_cases_per_million",
    "new_cases_smoothed_per_million",
    "total_deaths_per_million",
    "new_deaths_per_million",
    "new_deaths_smoothed_per_million",
    "reproduction_rate",
    "icu_patients_per_million",
    "hosp_patients_per_million",
    "weekly_icu_admissions_per_million",
    "weekly_hosp_admissions_per_million",
    "total_tests_per_thousand",
    "new_tests_per_thousand",
    "new_tests_smoothed_per_thousand",
    "positive_rate",
    "tests_per_case",
    "total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "new_vaccinations_smoothed_per_million",
    "stringency_index",
    "population_density",
    "median_age",
    "aged_65_older",
    "aged_70_older",
    "gdp_per_capita",
    "extreme_poverty",
    "cardiovasc_death_rate",
    "diabetes_prevalence",
    "female_smokers",
    "male_smokers",
    "handwashing_facilities",
    "hospital_beds_per_thousand",
    "life_expectancy",
    "human_development_index",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize CovidDeaths CSV so DataGrip infers types better."
    )
    parser.add_argument(
        "--input",
        default="CovidDeaths.csv",
        help="Source CSV path (default: CovidDeaths.csv)",
    )
    parser.add_argument(
        "--output",
        default="CovidDeaths_for_datagrip.csv",
        help="Output CSV path (default: CovidDeaths_for_datagrip.csv)",
    )
    parser.add_argument(
        "--null-token",
        default="",
        help="Token to write for missing numeric/date values (default: empty)",
    )
    parser.add_argument(
        "--fill-missing-numeric",
        action="store_true",
        default=True,
        help="Fill missing numeric values with 0 instead of null token (default: enabled).",
    )
    parser.add_argument(
        "--no-fill-missing-numeric",
        action="store_true",
        help="Disable filling missing numeric values with 0.",
    )
    return parser.parse_args()


def normalize_date(value: str, null_token: str) -> str:
    text = value.strip()
    if not text:
        return null_token

    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


def normalize_integer(value: str, null_token: str, fill_zero: bool) -> str:
    text = value.strip()
    if not text:
        return "0" if fill_zero else null_token
    try:
        return str(int(Decimal(text)))
    except InvalidOperation:
        return text


def normalize_float(value: str, null_token: str, fill_zero: bool) -> str:
    text = value.strip()
    if not text:
        return "0" if fill_zero else null_token
    try:
        number = Decimal(text)
    except InvalidOperation:
        return text
    return format(number.normalize(), "f").rstrip("0").rstrip(".") or "0"


def main() -> None:
    args = parse_args()
    fill_missing_numeric = args.fill_missing_numeric and not args.no_fill_missing_numeric
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    rows_read = 0
    with input_path.open("r", encoding="utf-8", newline="") as src, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.DictReader(src)
        if not reader.fieldnames:
            raise SystemExit("Input file has no header row.")

        writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            rows_read += 1
            cleaned = {}
            for col, raw in row.items():
                value = (raw or "").strip()
                if col == "date":
                    cleaned[col] = normalize_date(value, args.null_token)
                elif col in INTEGER_COLUMNS:
                    cleaned[col] = normalize_integer(
                        value, args.null_token, fill_missing_numeric
                    )
                elif col in FLOAT_COLUMNS:
                    cleaned[col] = normalize_float(
                        value, args.null_token, fill_missing_numeric
                    )
                else:
                    cleaned[col] = value
            writer.writerow(cleaned)

    print(f"Read rows: {rows_read}")
    print(f"Input file: {input_path}")
    print(f"Wrote file: {output_path}")
    print("Tip: In DataGrip import wizard ensure delimiter is comma.")


if __name__ == "__main__":
    main()
