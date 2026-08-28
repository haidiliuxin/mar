"""按口令类型做可复现的随机 50/50 切分。

每个不同口令（type）根据其自身字符串的哈希值，以约 50% 概率分到
train 或 test，同一口令在同一次运行中始终分到同一侧。输出格式与
原始 *-withcount.txt 一致（"计数 口令"每行一条），再用 bz2 压缩，
可以直接作为 run_probability_experiment.py 的 --train / --test 参数。
"""

import argparse
import bz2
import hashlib

from 数据处理 import cleaned_iterator


def assign(password, ratio=0.5, seed="mar-split"):
    digest = hashlib.md5((seed + "\0" + password).encode("utf-8")).hexdigest()
    # 取哈希前 8 位转成 [0, 1) 的浮点数，比例上更均匀
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return "train" if value < ratio else "test"


def run(args):
    train_types = train_occurrences = 0
    test_types = test_occurrences = 0

    with bz2.open(args.train_out, "wt", encoding="latin-1", newline="") as train_file, \
         bz2.open(args.test_out, "wt", encoding="latin-1", newline="") as test_file:
        for count, password in cleaned_iterator(args.input):
            side = assign(password, ratio=args.ratio, seed=args.seed)
            line = f"{count} {password}\n"
            if side == "train":
                train_file.write(line)
                train_types += 1
                train_occurrences += count
            else:
                test_file.write(line)
                test_types += 1
                test_occurrences += count

    total_occurrences = train_occurrences + test_occurrences
    print(f"train: {train_types} 类型, {train_occurrences} 次出现 "
          f"({train_occurrences / total_occurrences:.2%})")
    print(f"test:  {test_types} 类型, {test_occurrences} 次出现 "
          f"({test_occurrences / total_occurrences:.2%})")


def parse_args():
    parser = argparse.ArgumentParser(description="按口令类型随机切分训练/测试集")
    parser.add_argument("--input", default="data/rockyou-withcount.txt.bz2")
    parser.add_argument("--train-out", default="data/rockyou-train50.txt.bz2")
    parser.add_argument("--test-out", default="data/rockyou-test50.txt.bz2")
    parser.add_argument("--ratio", type=float, default=0.5, help="分到 train 的概率")
    parser.add_argument("--seed", default="mar-split", help="哈希种子，改变即可得到不同切分")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())