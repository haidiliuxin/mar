import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


def read_curves(csv_path):
    curves = {}
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            name = row["model"]
            x = float(row["negative_log2_probability"])
            y = float(row["covered_fraction"])
            if math.isfinite(x):
                curves.setdefault(name, [[], []])
                curves[name][0].append(x)
                curves[name][1].append(y)
    return curves


def draw_probability_curves(curves, output_path):
    plt.figure(figsize=(8, 5.2))
    for name, (x, y) in curves.items():
        plt.plot(x, y, label=name, linewidth=1.8)

    plt.xlabel("-log2 P(password)")
    plt.ylabel("Covered fraction")
    plt.title("Probability-threshold curves")
    plt.ylim(0, 1.02)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def draw_anll_chart(metrics, output_path):
    names = list(metrics)
    anll = [metrics[name]["ANLL"] for name in names]
    anll_08 = [metrics[name]["ANLL_theta"] for name in names]
    positions = list(range(len(names)))
    width = 0.36

    plt.figure(figsize=(8, 5.2))
    plt.bar([x - width / 2 for x in positions], anll, width, label="ANLL")
    plt.bar([x + width / 2 for x in positions], anll_08, width, label="ANLL_0.8")
    plt.xticks(positions, names, rotation=20)
    plt.ylabel("Average negative log likelihood")
    plt.title("ANLL comparison")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def make_figures(result_directory):
    result_directory = Path(result_directory)
    curves = read_curves(result_directory / "probability_threshold_curves.csv")
    result = json.loads(
        (result_directory / "probability_metrics.json").read_text(encoding="utf-8")
    )
    draw_probability_curves(
        curves,
        result_directory / "probability_threshold_curves.svg",
    )
    draw_anll_chart(
        result["models"],
        result_directory / "anll_comparison.svg",
    )
