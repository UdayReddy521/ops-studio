"""Collect NVIDIA GPU inventory and compare it with an agreed node spec."""
import argparse
import csv
import io
import json
import subprocess

QUERY = "index,name,driver_version"
SAMPLE = "0, NVIDIA H100 80GB HBM3, 570.133.20\n"


def inspect_inventory(raw, expected_count, expected_model, expected_driver):
    rows = [[cell.strip() for cell in row] for row in csv.reader(io.StringIO(raw)) if row]
    if any(len(row) != 3 or not row[0].isdigit() or any(not cell for cell in row) for row in rows):
        raise ValueError("Unexpected NVIDIA inventory format")
    indices = {int(row[0]) for row in rows}
    return {
        "count_matches": len(rows) == len(indices) == expected_count,
        "model_matches": bool(rows) and all(row[1] == expected_model for row in rows),
        "driver_matches": bool(rows) and all(row[2] == expected_driver for row in rows),
        "devices": [dict(zip(QUERY.split(","), row)) for row in rows],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--expected-model", required=True)
    parser.add_argument("--expected-driver", required=True)
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()
    if args.expected_count < 1:
        parser.error("--expected-count must be positive")
    report = {"source": "synthetic" if args.sample else "live",
              "scope": "inventory only"}
    try:
        raw = SAMPLE if args.sample else subprocess.run(
            ["nvidia-smi", f"--query-gpu={QUERY}", "--format=csv,noheader"],
            check=True, capture_output=True, text=True, timeout=20,
        ).stdout
        checks = inspect_inventory(raw, args.expected_count, args.expected_model, args.expected_driver)
        report.update(checks)
        report["verdict"] = "PASS" if all(checks[key] for key in
                                          ("count_matches", "model_matches", "driver_matches")) else "FAIL"
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        report.update(verdict="INCONCLUSIVE", error=str(exc))
    print(json.dumps(report, indent=2))
    return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}[report["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
