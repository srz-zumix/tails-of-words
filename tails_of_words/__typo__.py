class Typo:

    def __init__(self, prev, typo, post, line, column, message, fix=None) -> None:
        self.prev = prev
        self.typo = typo
        self.post = post
        self.line = line
        self.column = column
        self.message = message
        self.fix = fix

    def format(self):
        return "{}:{}: {}\033[33m\033[4m{}\033[0m{}: {}".format(self.line, self.column, self.prev, self.typo, self.post, self.message)


class TypoCheck:

    def __init__(self, words):
        self.words = words

    def _find_hinsi_pattern(self, mrph_list, pattern):
        index = 0
        length = len(pattern)
        find = []
        for mrph in mrph_list:
            if index > 0:
                if mrph.hinsi_id != pattern[index]:
                    index = 0
                    find.clear()
            if mrph.hinsi_id == pattern[index]:
                index += 1
                find.append(mrph)
                if index == length:
                    index = 0
                    yield find

    def kanji_in_auxiliary_verb(self):
        typos = []
        for index, line in enumerate(self.words.lines):
            # 助詞、動詞、動詞（付属動詞候補）
            for mrphs in self._find_hinsi_pattern(line.mrph_list(), [9, 2, 2]):
                if mrphs[2].midasi != mrphs[2].yomi:
                    if "付属動詞候補" in mrphs[2].imis:
                        typos.append(Typo(mrphs[0].midasi + mrphs[1].midasi, mrphs[2].midasi, "", index + 1, mrphs[0].span[0], "補助動詞の漢字"))
            # 動詞、設備辞
            for mrphs in self._find_hinsi_pattern(line.mrph_list(), [2, 14]):
                if mrphs[1].midasi != mrphs[1].yomi:
                    typos.append(Typo(mrphs[0].midasi, mrphs[1].midasi, "", index + 1, mrphs[0].span[0], "補助動詞の漢字"))
        return typos

    def ranuki(self):
        # 代表表記が「れる/れる」
        # 1つ前のトークンの活用形が
        #  * 未然形(3)
        #  * カ変動詞来(15)
        #  * 母音動詞(1)
        pre_katuyou_ids = [1, 3, 15]
        typos = []
        prev = None
        target_prev = None
        for index, line in enumerate(self.words.lines):
            for mrph in line.mrph_list():
                if target_prev is not None:
                    # 〜れ？、〜れ！ は除外
                    if mrph.hinsi_id != 1:
                        typos.append(Typo(target_prev.midasi, prev.midasi, mrph.midasi, index + 1, target_prev.span[0], "ら抜き言葉"))
                    target_prev = None

                if ("れる/れる" == mrph.repname) and (prev is not None):
                    # katuyou2_id を含めると誤検知する
                    # if (prev.katuyou1_id in pre_katuyou_ids) or (prev.katuyou2_id in pre_katuyou_ids):
                    if prev.katuyou1_id in pre_katuyou_ids:
                        target_prev = prev
                prev = mrph
        return typos
