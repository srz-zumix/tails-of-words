import codecs
import os
import logging
import glob

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
        self.lines = []
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
        else:
            for f in glob.glob(path, recursive=recursive):
                self.parse(f, recursive, encoding)

    def parse_file(self, file, encoding="utf-8"):
        f = codecs.open(file, 'r', encoding)
        self.logger.info(file)
        for line in f:
            self.parse_string(line)

    def parse_string(self, str):
        str = self.normalize(str)
        if len(str):
            result = self.jumanpp.analysis(str)
            self.mrphs.append(result.mrph_list())
            first = None
            prev = None
            curr = None
            for next in result.mrph_list():
                prev = self.append(prev, curr, next)
                curr = next
                if first is None:
                    first = prev
            last = self.append(prev, curr, None)
            if first:
                self.lines.append(first)
            elif last:
                self.lines.append(last)


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
