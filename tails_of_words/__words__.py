import codecs
import csv
import io
import os
import logging
import glob
import jaconv
import sys
import html2text
import xml.etree.ElementTree as ET

from .__analyzer__ import JumanAnalyzer
from .__analyzer__ import KnpAnalyzer
from .__analyzer__ import NamedEntry

# zen2han = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})


def attr_join(mrphs, name):
    return "".join(getattr(x, name) for x in mrphs)


def attr_one(mrphs, name, default_value=None):
    r = None
    for x in mrphs:
        if r is None:
            r = getattr(x, name)
        elif r != getattr(x, name):
            return default_value
    return r


class WordUnit:

    def __init__(self, entries):
        if isinstance(entries, NamedEntry):
            self.mrphs = entries.mrph_list()
            self.bunrui = entries.bunrui
            self.bunrui_id = entries.bunrui_id
            self.hinsi = attr_one(self.mrphs, "hinsi", entries.hinsi)
            self.hinsi_id = attr_one(self.mrphs, "hinsi_id", entries.hinsi_id)
            self.unit_type = 'NE'
        else:
            self.mrphs = [entries]
            self.bunrui = entries.bunrui
            self.bunrui_id = entries.bunrui_id
            self.hinsi = entries.hinsi
            self.hinsi_id = entries.hinsi_id
            self.unit_type = 'mrph'
        self.midasi = attr_join(self.mrphs, 'midasi')
        self.yomi = attr_join(self.mrphs, 'yomi')
        self.span = (self.mrphs[0].span[0], self.mrphs[-1].span[1])


class Words:

    def __init__(self, excludes=[], columns=[], is_html2text=False, stdin_type="", knp=False):
        if knp:
            self.analyzer = KnpAnalyzer()
        else:
            self.analyzer = JumanAnalyzer()
        self.hinsi = {}
        self.lines = []
        self.logger = logging.getLogger(__name__)
        self.columns = columns
        self.stdin_type = stdin_type
        self.is_html2text = is_html2text
        self.excludes = []
        for e in excludes:
            self.excludes.extend(glob.glob(e, recursive=True))
        self.logger.debug(self.excludes)

    def parse(self, path, recursive=True, encoding="utf-8"):
        if path == '-':
            self.parse_from_type(io.StringIO(sys.stdin.read()), self.stdin_type)
            return
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
            ext = os.path.splitext(file)[1]
            if ext in [".csv", ".tsv"]:
                self.parse_from_type(f, "csv")
            elif ext in [".xml"]:
                self.parse_from_type(f, "xml")
            elif ext in [".html"]:
                self.parse_from_type(f, "html")
            else:
                self.parse_from_reader(f)

    def parse_from_type(self, f, type):
        if type == "csv":
            self.parse_from_reader(csv.DictReader(f))
        elif type == "xml":
            self.parse_from_reader(self._readxml(f))
        elif type == "html":
            self.parse_string(html2text.html2text(f.read()))
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
            elif isinstance(r, ET.Element):
                if r.text:
                    self.parse_string(r.text)
            else:
                self.parse_string(r)

    def parse_string(self, str):
        if self.is_html2text:
            str = html2text.html2text(str)
        for s in str.split('\n'):
            self._parse_string(s)

    def _parse_string(self, str):
        if len(str):
            result = self._analyze(str)
            if result:
                self.lines.append(result)
                for mrph in result.mrph_list():
                    self.normalize_yomi(mrph)
                    self.append(mrph)
                for ne in result.named_entry_list():
                    self.append(ne)

    def _analyze(self, str):
        return self.analyzer.analysis(str)

    def append(self, mrph):
        unit = WordUnit(mrph)
        midasi = unit.midasi
        hinsi_id = unit.hinsi_id
        if hinsi_id not in self.hinsi:
            self.hinsi[hinsi_id] = {}
        if midasi not in self.hinsi[hinsi_id]:
            self.hinsi[hinsi_id][midasi] = []
        self.hinsi[hinsi_id][midasi].append(unit)
        return unit

    def normalize_yomi(self, mrph):
        # yomi はひらがなとカタカナが入る場合がある
        # 同じ音の場合は編集距離が 0 になってほしいので合わせる
        mrph.yomi = jaconv.kata2hira(mrph.yomi)

    def _readxml(self, file):
        tree = ET.parse(file)
        return tree.iter()
