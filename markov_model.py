import math
import string
from collections import Counter, defaultdict


START = "<START>"
END = "<END>"
PRINTABLE_ASCII = tuple(chr(code) for code in range(32, 127))

class MarkovModel:

    def __init__(
        self,
        order,
        normalization="end",
        delta=0.01,
        alphabet=PRINTABLE_ASCII,
        min_length=4,
        max_length=40,
    ):

        self.order = order
        self.normalization = normalization
        self.delta = float(delta)
        self.alphabet = tuple(alphabet)
        self.alphabet_set = set(alphabet)
        self.min_length = min_length
        self.max_length = max_length

        self.transitions = defaultdict(Counter)
        self.length_counts = Counter()
        self.training_total = 0

    def fit(self, corpus):
        self.transitions.clear()
        self.length_counts.clear()
        self.training_total = 0

        for count, password in corpus:

            self.training_total += count
            self.length_counts[len(password)] += count
            history = [START] * self.order

            for character in password:
                context = tuple(history[-self.order:])
                self.transitions[context][character] += count
                history.append(character)

            if self.normalization == "end" and len(password) < self.max_length:
                context = tuple(history[-self.order:])
                self.transitions[context][END] += count

        if self.training_total == 0:
            raise ValueError("训练集为空")
        return self

    def _character_denominator(self, counter):
        character_total = sum(counter[c] for c in self.alphabet)
        return character_total + self.delta * len(self.alphabet)

    def transition_probability(self, context, symbol, current_length):
        context = tuple(context[-self.order:])
        counter = self.transitions.get(context, Counter())

        if self.normalization == "distribution":
            if symbol not in self.alphabet_set or current_length >= self.max_length:
                return 0.0
            denominator = self._character_denominator(counter)
            return (counter[symbol] + self.delta) / denominator

        # 达到最大长度后强制结束，不再为 END 额外乘一个概率
        if current_length >= self.max_length:
            return 1.0 if symbol == END else 0.0

        # 最短长度以前 END 不属于输出空间。分母中也不含 END 的计数和平滑质量。
        if current_length < self.min_length:
            if symbol not in self.alphabet_set:
                return 0.0
            denominator = self._character_denominator(counter)
            return (counter[symbol] + self.delta) / denominator

        total = sum(counter[c] for c in self.alphabet) + counter[END]
        denominator = total + self.delta * (len(self.alphabet) + 1)
        if symbol == END or symbol in self.alphabet_set:
            return (counter[symbol] + self.delta) / denominator
        return 0.0

    def length_probability(self, length):
        if self.normalization != "distribution":
            raise ValueError("只有 distribution 模型单独计算长度概率")
        return self.length_counts[length] / self.training_total

    def surprisal(self, password):
        """返回 -log2 P(password)，数值越小表示概率越高。"""
        if not self.min_length <= len(password) <= self.max_length:
            return math.inf
        if any(character not in self.alphabet_set for character in password):
            return math.inf

        cost = 0.0
        if self.normalization == "distribution":
            length_probability = self.length_probability(len(password))
            if length_probability == 0:
                return math.inf
            cost -= math.log2(length_probability)

        history = [START] * self.order
        for current_length, character in enumerate(password):
            probability = self.transition_probability(history, character, current_length)
            cost -= math.log2(probability)
            history.append(character)

        if self.normalization == "end":
            end_probability = self.transition_probability(history, END, len(password))
            cost -= math.log2(end_probability)
        return cost

    def probability(self, password):
        cost = self.surprisal(password)
        return 0.0 if math.isinf(cost) else 2.0 ** (-cost)

    def next_character_options(self, history, current_length):
        """按概率从高到低返回下一字符，供候选生成使用。"""
        options = []
        for character in self.alphabet:
            probability = self.transition_probability(history, character, current_length)
            if probability > 0:
                options.append((character, -math.log2(probability)))
        options.sort(key=lambda item: (item[1], item[0]))
        return options
