import re
import logging

from .__config__ import score_config
from .__distance__ import Distance

re_katakana = re.compile(r'[\u30A1-\u30F4ー]+')
use_jaro_winkler = False


def calc_socre_include(score, a, b):
    # 片方を含む場合はスコアダウン
    if a in b:
        # 長音ルールのゆれはスコアアップ
        if (a + "ー") == b and re_katakana.fullmatch(a):
            return score * score_config.diff_only_long_vowel_scale
        else:
            return score * score_config.inclue_other_one
    return score


def calc_score(section):
    # 編集距離が近いほどスコア大
    score = section.distance.normalized_distance().midasi
    # 出現数の差が大きいほどスコア大
    la = section.a.count
    lb = section.b.count
    ls = (1.0 - min(la,lb)/(la+lb)*2)
    score *= 1.0 + (ls * score_config.occurrences_sacle)
    # 読みが同じならスコアアップ
    if section.distance.normalized_distance().yomi >= 1.0:
        score *= score_config.same_yomi_scale
    score = calc_socre_include(score, section.a.midasi, section.b.midasi)
    score = calc_socre_include(score, section.b.midasi, section.a.midasi)
    # 読みが同じで、読みから長音が消えてる場合、スコアを下げる
    if section.a.get_rep_unit().yomi == section.b.get_rep_unit().yomi:
        if 'ー' not in section.a.get_rep_unit().yomi and ('ー' in section.a.midasi or 'ー' in section.b.midasi):
            score *= score_config.same_yomi_with_remove_long_vowel_scale
    return score

class SectionPoint:

    def __init__(self, k, units):
        self.midasi = k
        self.units = units
        self.count = len(units)

    def get_rep_unit(self):
        return self.units[0]

    def get_rep_unit_dict(self):
        unit = self.get_rep_unit()
        mrphs = unit.mrphs
        if len(mrphs) == 1:
            mrph = mrphs[0]
            return {
                "midasi": mrph.midasi,
                "yomi": mrph.yomi,
                "genkei": mrph.genkei,
                "hinsi": mrph.hinsi,
                "hinsi_id": mrph.hinsi_id,
                "bunrui": mrph.bunrui,
                "bunrui_id": mrph.bunrui_id,
                "katuyou1": mrph.katuyou1,
                "katuyou1_id": mrph.katuyou1_id,
                "katuyou2": mrph.katuyou2,
                "katuyou2_id": mrph.katuyou2_id,
                "imis": mrph.imis,
                "fstring": mrph.fstring
            }
        else:
            return {
                "midasi": unit.midasi,
                "yomi": unit.yomi
            }

class Section:

    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
        self.distance = Distance(a.get_rep_unit(), b.get_rep_unit(), use_jaro_winkler)
        self.score = calc_score(self)

    def format(self):
        a = "{}({})".format(self.a.midasi, self.a.count)
        b = "{}({})".format(self.b.midasi, self.b.count)
        return "{}: {} vs {} : {:.2f}".format(self.distance.format(), a, b, self.score)


class SwingOption:

    def __init__(self, exclude_alphabet, exclude_ascii, jaro_winkler):
        self.exclude_alphabet = exclude_alphabet
        self.exclude_ascii = exclude_ascii
        self.jaro_winkler = jaro_winkler


class Swing:

    def __init__(self, option):
        global use_jaro_winkler
        self.option = option
        use_jaro_winkler = option.jaro_winkler
        self.logger = logging.getLogger(__name__)

    def distance(self, words, ids):
        inputs = {}
        for id in ids:
            if id in words.hinsi:
                target = filter(lambda x: self.target_filter(x[0], x[1]), words.hinsi[id].items())
                inputs.update(sorted(target, key=lambda x: len(x[1])))
        self.logger.debug('combinations')
        keys = list(inputs.keys())
        while len(keys) > 0:
            lhs = keys.pop(0)
            d = []
            for rhs in keys:
                a = SectionPoint(lhs, inputs[lhs])
                b = SectionPoint(rhs, inputs[rhs])
                d.append(Section(a, b))
            yield sorted(d, key=lambda x: x.distance.normalized_distance().midasi)

    def swing(self, words, ids):
        for d in self.distance(words, ids):
            yield sorted(filter(lambda x: x.score > 0, d), reverse=True, key=lambda x: x.score)

    def target_filter(self, midasi, units):
        # 数値は除外
        if midasi.isnumeric():
            return False
        # 一文字だけの場合は常に除外する
        is_one = len(midasi) <= 1
        # 英数字も除外
        if self.option.exclude_alphabet or is_one:
            if midasi.encode('utf-8').isalnum():
                return False
        # ASCII のみは除外
        if self.option.exclude_ascii or is_one:
            if midasi.encode('utf-8').isascii():
                return False
        # 数詞は除外
        unit = units[0]
        if unit.hinsi_id == 6 and unit.bunrui_id == 7:
            return False
        return True
