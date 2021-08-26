import itertools

from .__distance__ import Distance


class SectionPoint:

    def __init__(self, k, mrphs):
        self.midasi = k
        self.mrphs = mrphs


class Section:

    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
        self.distance = Distance(a.mrphs[0].mrph, b.mrphs[0].mrph)
        la = len(a.mrphs)
        lb = len(b.mrphs)
        ls = min(la,lb)/(la+lb)
        self.score = (self.distance.normalized.midasi + self.distance.normalized.yomi) / 2 + ls

    def format(self):
        a = "{}({})".format(self.a.midasi, len(self.a.mrphs))
        b = "{}({})".format(self.b.midasi, len(self.b.mrphs))
        levenshtein = "{}, {}, {}".format(self.distance.levenshtein.midasi, self.distance.normalized.midasi, self.distance.normalized.yomi)
        return "{}: {} vs {} : {}".format(levenshtein, a, b, self.score)


class Swing:

    def __init__(self):
        pass

    def distance(self, words, ids):
        inputs = {}
        d = []
        for id in ids:
            if id in words.hinsi:
                target = filter(lambda x: not x[0].isnumeric(), words.hinsi[id].items())
                inputs.update(sorted(target, key=lambda x:len(x[1])))
        for pair in itertools.combinations(inputs, 2):
            a = SectionPoint(pair[0], inputs[pair[0]])
            b = SectionPoint(pair[1], inputs[pair[1]])
            d.append(Section(a, b))
        return sorted(d, key=lambda x:x.distance.levenshtein.midasi)

    def swing(self, words, ids):
        d = filter(lambda x:x.score > 1, self.distance(words, ids))
        return sorted(d, key=lambda x:x.score)
