import re
import logging

from .__distance__ import Distance

re_katakana = re.compile(r'[\u30A1-\u30F4ー]+')


def calc_socre_include(score, a, b):
    # 片方を含む場合はスコアダウン
    if a in b:
        # 長音ルールのゆれはスコアアップ
        if (a + "ー") == b and re_katakana.fullmatch(a):
            return score*1.2
        else:
            return score*0.5
    return score



def calc_score(section):
    # 編集距離が近いほどスコア大
    score = section.distance.normalized.midasi
    # 出現数の差が大きいほどスコア大
    la = len(section.a.mrphs)
    lb = len(section.b.mrphs)
    ls = (1.0 - min(la,lb)/(la+lb)*2)
    score *= 1.0 + ls
    # 読みが同じならスコアアップ
    if section.distance.normalized.yomi >= 1.0:
        score *= 1.2
    score = calc_socre_include(score, section.a.midasi, section.b.midasi)
    score = calc_socre_include(score, section.b.midasi, section.a.midasi)
    return score

class SectionPoint:

    def __init__(self, k, mrphs):
        self.midasi = k
        self.mrphs = mrphs


class Section:

    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
        self.distance = Distance(a.mrphs[0].mrph, b.mrphs[0].mrph)
        self.score = calc_score(self)

    def format(self):
        a = "{}({})".format(self.a.midasi, len(self.a.mrphs))
        b = "{}({})".format(self.b.midasi, len(self.b.mrphs))
        levenshtein = "{}, {:.2f}, {:.2f}".format(self.distance.levenshtein.midasi, self.distance.normalized.midasi, self.distance.normalized.yomi)
        return "{}: {} vs {} : {:.2f}".format(levenshtein, a, b, self.score)


class Swing:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def distance(self, words, ids):
        inputs = {}
        for id in ids:
            if id in words.hinsi:
                target = filter(lambda x: self.target_filter(x[0], x[1]), words.hinsi[id].items())
                inputs.update(sorted(target, key=lambda x:len(x[1])))
        self.logger.debug('combinations')
        keys = list(inputs.keys())
        while len(keys) > 0:
            lhs = keys.pop(0)
            d = []
            for rhs in keys:
                a = SectionPoint(lhs, inputs[lhs])
                b = SectionPoint(rhs, inputs[rhs])
                d.append(Section(a, b))
            yield sorted(d, key=lambda x:x.distance.levenshtein.midasi)

    def swing(self, words, ids):
        for d in self.distance(words, ids):
            yield sorted(filter(lambda x:x.score > 0, d), reverse=True, key=lambda x:x.score)

    def target_filter(self, midasi, mrphs):
        # 数字のみは除外
        if midasi.isnumeric():
            return False
        # 数詞は除外
        mrph = mrphs[0].mrph
        if mrph.hinsi_id == 6 and mrph.bunrui_id == 7:
            return False
        return True
