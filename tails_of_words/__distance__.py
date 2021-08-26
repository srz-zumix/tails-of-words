import Levenshtein


class LevenshteinDistance:

    def __init__(self, midasi, yomi):
        self.midasi = midasi
        self.yomi = yomi

class Distance:

    def __init__(self, a, b):
        self.section = [a, b]
        self.levenshtein = LevenshteinDistance(
            Levenshtein.distance(a.midasi, b.midasi),
            Levenshtein.distance(a.yomi, b.yomi)
        )
        self.normalized = LevenshteinDistance(
            1.0 - (self.levenshtein.midasi / max(len(a.midasi), len(b.midasi))),
            1.0 - (self.levenshtein.yomi / max(len(a.yomi), len(b.yomi)))
        )
