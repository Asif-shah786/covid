#!/usr/bin/env python3
"""Normalize CovidVaccinations.csv for friendlier DataGrip type detection."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


INTEGER_COLUMNS = {
    "new_tests",
    "total_tests",
    "new_tests_smoothed",
    "total_vaccinations",
    "people_vaccinated",
    "people_fully_vaccinated",
    "new_vaccinations",
    "new_vaccinations_smoothed",
    "population_density",  # kept as float downstream, handled by FLOAT_COLUMNS
}

FLOAT_COLUMNS = {
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

# Ensure population_density only uses float normalization.
INTEGER_COLUMNS.discard("population_density")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize CovidVaccinations CSV so DataGrip infers types better."
    )
    parser.add_argument(
        "--input",
        default="",
        help="Source CSV path. If omitted, prefers CovidVaccinations_un.csv then CovidVaccinations.csv.",
    )
    parser.add_argument(
        "--output",
        default="CovidVaccinations_for_datagrip.csv",
        help="Output CSV path (default: CovidVaccinations_for_datagrip.csv)",
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

    # Accept both US and ISO input, write ISO for better autodetection.
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
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
        number = Decimal(text)
    except InvalidOperation:
        return text

    return str(int(number))


def normalize_float(value: str, null_token: str, fill_zero: bool) -> str:
    text = value.strip()
    if not text:
        return "0" if fill_zero else null_token
    try:
        number = Decimal(text)
    except InvalidOperation:
        return text

    # Avoid scientific notation so import wizards keep numeric type.
    return format(number.normalize(), "f").rstrip("0").rstrip(".") or "0"


def preview_fields(columns: Iterable[str]) -> str:
    names = list(columns)
    if not names:
        return "none"
    return ", ".join(names)


def main() -> None:
    args = parse_args()
    fill_missing_numeric = args.fill_missing_numeric and not args.no_fill_missing_numeric
    if args.input:
        input_path = Path(args.input)
    else:
        candidate_un = Path("CovidVaccinations_un.csv")
        input_path = candidate_un if candidate_un.exists() else Path("CovidVaccinations.csv")
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
                value = raw or ""
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
                    cleaned[col] = value.strip()
            writer.writerow(cleaned)

    print(f"Read rows: {rows_read}")
    print(f"Input file: {input_path}")
    print(f"Wrote file: {output_path}")
    print(f"Integer columns ({len(INTEGER_COLUMNS)}): {preview_fields(INTEGER_COLUMNS)}")
    print(f"Float columns ({len(FLOAT_COLUMNS)}): {preview_fields(FLOAT_COLUMNS)}")
    print(
        "Tip: In DataGrip import wizard set 'Value for NULL' to "
        f"{args.null_token!r} and ensure delimiter is comma."
    )


if __name__ == "__main__":
    main()
