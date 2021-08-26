import codecs
import os
import logging

from pyknp import Juman

# zen2han = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


class LinkedMrph:

    def __init__(self, mrph, prev, next):
        self.mrph = mrph
        self.prev = prev
        self.next = next


class Words:

    def __init__(self):
        self.jumanpp = Juman()
        self.hinsi = {}
        self.mrphs = []
        self.logger = logging.getLogger(__name__)

    def parse(self, path, recursive=True, encoding="utf-8"):
        if os.path.isdir(path):
            for f in os.listdir(path):
                child = os.path.join(path, f)
                if os.path.isfile(child):
                    self.parse_file(child, encoding)
                elif os.path.isdir(child) and recursive:
                    self.parse(child, recursive, encoding)
        elif os.path.isfile(path):
            self.parse_file(path, encoding)

    def parse_file(self, file, encoding="utf-8"):
        f = codecs.open(file, 'r', encoding)
        self.logger.info(file)
        for line in f:
            line = self.normalize(line)
            if len(line):
                result = self.jumanpp.analysis(line)
                self.mrphs.append(result.mrph_list())
                prev = None
                curr = None
                for next in result.mrph_list():
                    prev = self.append(prev, curr, next)
                    curr = next
                prev = self.append(prev, curr, None)

    def append(self, prev, curr, next):
        if curr is None:
            return None

        mrph = LinkedMrph(curr, prev, None)
        if prev:
            prev.next = mrph
        id = curr.hinsi_id
        if id not in self.hinsi:
            self.hinsi[id] = {}
        midasi = curr.midasi
        if midasi not in self.hinsi[id]:
            self.hinsi[id][midasi] = []
        self.hinsi[id][midasi].append(mrph)
        return mrph

    def normalize(self, s):
        # 半角スペース+アルファベットがあると "\ A" のような出力がされ、
        # 半角スペースで split しているため配列インデックスが想定とずれてエラーとなる
        # e.g. ValueError: invalid literal for int() with base 10: '\\'
        # s = s.translate(zen2han)
        return s.replace(' ', '　').strip()
