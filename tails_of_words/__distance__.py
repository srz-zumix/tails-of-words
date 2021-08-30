import Levenshtein


zen2han = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})

class LevenshteinDistance:

    def __init__(self, midasi, yomi):
        self.midasi = midasi
        self.yomi = yomi

class Distance:

    def __init__(self, a, b):
        self.section = [a, b]
        a_midasi = self.normalize(a.midasi)
        b_midasi = self.normalize(b.midasi)
        self.levenshtein = LevenshteinDistance(
            Levenshtein.distance(a_midasi, b_midasi),
            Levenshtein.distance(a.yomi, b.yomi)
        )
        self.normalized = LevenshteinDistance(
            1.0 - (self.levenshtein.midasi / max(len(a_midasi), len(b_midasi))),
            1.0 - (self.levenshtein.yomi / max(len(a.yomi), len(b.yomi)))
        )

    def normalize(self, s):
        # 編集距離を取るときに正規化を行うことで距離が短いのに違う単語を検出しやすくする
        return s.translate(zen2han).lower()
