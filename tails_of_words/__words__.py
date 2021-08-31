import codecs
import csv
import os
import logging
import glob
import jaconv

from pyknp import Juman

# zen2han = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


class LinkedMrph:

    def __init__(self, mrph, prev, next):
        self.mrph = mrph
        self.prev = prev
        self.next = next

class Words:

    def __init__(self, excludes=[], columns=[]):
        self.jumanpp = Juman()
        self.hinsi = {}
        self.mrphs = []
        self.lines = []
        self.logger = logging.getLogger(__name__)
        self.columns = columns
        self.excludes = []
        for e in excludes:
            self.excludes.extend(glob.glob(e, recursive=True))
        self.logger.debug(self.excludes)

    def parse(self, path, recursive=True, encoding="utf-8"):
        if os.path.normpath(path) in self.excludes:
            return
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
        if os.path.normpath(file) in self.excludes:
            return
        self.logger.info(file)
        with codecs.open(file, 'r', encoding) as f:
            if os.path.splitext(file)[1] in [".csv", ".tsv"]:
                self.parse_from_reader(csv.DictReader(f))
            else:
                self.parse_from_reader(f)

    def parse_from_reader(self, reader):
        for r in reader:
            if isinstance(r, list):
                for s in r:
                    self.parse_string(s)
            elif isinstance(r, dict):
                if len(self.columns) > 0:
                    for column in self.columns:
                        self.parse_string(r[column])
                else:
                    for s in r.values():
                        self.parse_string(s)
            else:
                self.parse_string(r)

    def parse_string(self, str):
        for s in str.split('\n'):
            self._parse_string(s)

    def _parse_string(self, str):
        str = self.normalize(str)
        if len(str):
            result = self.jumanpp.analysis(str)
            for mrph in result.mrph_list():
                self.normalize_yomi(mrph)
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
        # えー！？が１つの名詞になってしまうので「！・？」は半角にする
        s = s.replace('！','!').replace('？','?')
        # 半角スペース+アルファベットがあると "\ A" のような出力がされ、
        # 半角スペースで split しているため配列インデックスが想定とずれてエラーとなる
        # e.g. ValueError: invalid literal for int() with base 10: '\\'
        return s.replace(' ', '　').strip()

    def normalize_yomi(self, mrph):
        # yomi はひらがなとカタカナが入る場合がある
        # 同じ音の場合は編集距離が 0 になってほしいので合わせる
        mrph.yomi = jaconv.kata2hira(mrph.yomi)
