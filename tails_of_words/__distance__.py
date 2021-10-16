import Levenshtein
from pyxdameraulevenshtein import damerau_levenshtein_distance

zen2han = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


class EditDistance:

    def __init__(self, midasi, yomi):
        self.midasi = midasi
        self.yomi = yomi


class LevenshteinEditDistanceCalculator:

    def distance(self, a, b):
        return Levenshtein.distance(a, b)

    def _normalized(self, a, b, distance):
        return 1.0 - (distance / max(len(a), len(b)))

    def normalized(self, a, b):
        return self._normalized(a, b, self.distance(a, b))

    def pair(self, a, b):
        d = self.distance(a, b)
        return (d, self._normalized(a, b, d))


class DamerauLevenshteinEditDistanceCalculator:

    def distance(self, a, b):
        return damerau_levenshtein_distance(a, b)

    def _normalized(self, a, b, distance):
        return 1.0 - (distance / max(len(a), len(b)))

    def normalized(self, a, b):
        return self._normalized(a, b, self.distance(a, b))

    def pair(self, a, b):
        d = self.distance(a, b)
        return (d, self._normalized(a, b, d))


class JaroWinklerEditDistanceCalculator:

    def distance(self, a, b):
        return self._distance(a, b, self.normalized(a, b))

    def _distance(self, a, b, normalized):
        return None
        # return int((1.0 - normalized) * max(len(a), len(b)))

    def normalized(self, a, b):
        return Levenshtein.jaro_winkler(a, b)

    def pair(self, a, b):
        n = self.normalized(a, b)
        return (self._distance(a, b, n), n)


class Distance:

    calculator = LevenshteinEditDistanceCalculator()

    def __init__(self, a, b):
        self.section = [a, b]
        a_midasi = self.normalize(a.midasi)
        b_midasi = self.normalize(b.midasi)

        (md, mn) = Distance.calculator.pair(a_midasi, b_midasi)
        (yd, yn) = Distance.calculator.pair(a.yomi, b.yomi)
        self.distance = EditDistance(md, yd)
        # 0 : 不一致
        # 1 : 一致
        self.normalized = EditDistance(mn, yn)
        # if len(a_midasi) == len(b_midasi):
        #     self.hamming = Levenshtein.hamming(a_midasi, b_midasi)
        # else:
        #     self.hamming = None

    def normalized_distance(self):
        return self.normalized

    def normalize(self, s):
        # 編集距離を取るときに正規化を行うことで距離が短いのに違う単語を検出しやすくする
        return s.translate(zen2han).lower()

    def format(self):
        s = ""
        if self.distance.midasi is not None:
            s += "{:>2}, ".format(str(self.distance.midasi))
        if self.distance.yomi is not None:
            s += "{:>2}, ".format(str(self.distance.yomi))
        s += "{:.2f}, {:.2f}".format(self.normalized.midasi, self.normalized.yomi)
        # s += ", {:>4}".format(str(self.hamming))
        return s

    @classmethod
    def levenshtein(cls):
        cls.calculator = LevenshteinEditDistanceCalculator()

    @classmethod
    def damerau_levenshtein(cls):
        cls.calculator = DamerauLevenshteinEditDistanceCalculator()

    @classmethod
    def jaro_winkler(cls):
        cls.calculator = JaroWinklerEditDistanceCalculator()
