import argparse
import csv
import gc
import json
from collections import Counter
from pathlib import Path

from markov_model import MarkovModel
from plot_results import make_figures
from probability_metrics import score_test_set
from data_processing import cleaned_iterator

def load_testing_counts(path):
    counts = Counter()
    for count, password in cleaned_iterator(path):
        counts[password] += count
    return counts


def model_name(order, normalization):
    suffix = "end" if normalization == "end" else "dis"
    return f"ws-mc{order}-{suffix}"


def run(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    testing = load_testing_counts(args.test)
    args.min_length = 4
    args.max_length = 40
    args.theta = 0.8
    args.thresholds = [20,30,40,50,60,70,80]
    result = {
        "configuration": {
            "orders": args.orders,
            "normalizations": args.normalizations,
            "delta": args.delta,
            "min_length": args.min_length,
            "max_length": args.max_length,
            "theta": args.theta,
            "thresholds": args.thresholds,
            "training_file": str(Path(args.train).resolve()),
            "testing_file": str(Path(args.test).resolve()),
        },
        "testing": {
            "types": len(testing),
            "occurrences": sum(testing.values()),
        },
        "models": {},
    }

    curve_path = output / "probability_threshold_curves.csv"
    with curve_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["model", "negative_log2_probability", "covered_fraction"])

        for normalization in args.normalizations:
            for order in args.orders:
                name = model_name(order, normalization)
                print(f"训练 {name}", flush=True)
                model = MarkovModel(
                    order=order,
                    normalization=normalization,
                    delta=args.delta,
                    min_length=args.min_length,
                    max_length=args.max_length,
                )
                model.fit(cleaned_iterator(args.train))
                metrics = score_test_set(
                    model,
                    testing,
                    theta=args.theta,
                    thresholds=args.thresholds,
                )
                curve = metrics.pop("curve")
                writer.writerows((name, x, y) for x, y in curve)
                result["models"][name] = metrics
                print(
                    f"{name}: ANLL={metrics['ANLL']}, "
                    f"ANLL_{args.theta}={metrics['ANLL_theta']}",
                    flush=True,
                )
                del model
                gc.collect()

    (output / "probability_metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    make_figures(output)
    print(f"结果保存在 {output.resolve()}")


def parse_args():
    parser = argparse.ArgumentParser(description="运行 whole-string Markov 概率评价实验")
    parser.add_argument("--train", default="data/rockyou-withcount.txt.bz2")
    parser.add_argument("--test", default="data/phpbb-withcount.txt.bz2")
    parser.add_argument("--orders", type=int, nargs="+", default=[3, 4, 5])
    parser.add_argument(
        "--normalizations",
        nargs="+",
        choices=["end", "distribution"],
        default=["end", "distribution"],
    )
    parser.add_argument("--delta", type=float, default=0.01)
    parser.add_argument("--output", default="probability_results")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
