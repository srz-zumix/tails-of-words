import logging
import traceback
import re

from pyknp import Juman
from pyknp import KNP
from pyknp import Features


def _juman_msrs(str):
    msrs = [
        # NOTE: 文字数が変わるような置換は revert の仕様上不可
        # ",@,#,! は全角にする
        (re.finditer(r'"', str), r'"', r'”'),
        (re.finditer(r'@', str), r'@', r'＠'),
        (re.finditer(r'#', str), r'#', r'＃'),
        # 半角スペース+アルファベットがあると "\ A" のような出力がされ、
        # 半角スペースで split しているため配列インデックスが想定とずれてエラーとなる
        # e.g. ValueError: invalid literal for int() with base 10: '\\'
        (re.finditer(r' ', str), r' ', r'　'),
    ]
    return msrs


def _knp_msrs(str):
    msrs = [
        (re.finditer(r'!', str), r'!', r'！'),
        (re.finditer('\t', str), '\t', r'　'),
        (re.finditer(r'/', str), r'/', r'／'),
        (re.finditer(r'\+', str), r'+', r'＋'),
        (re.finditer(r'\*', str), r'*', r'＊'),
    ]
    msrs.extend(_juman_msrs(str))
    return msrs


def _normalize(str, msrs):
    # https://qiita.com/NLPingu/items/3cd77eb2421283b851b4
    for _, s, r in msrs:
        str = str.replace(s, r)
    return str


def _span_mrphs(mrphs):
    start = 0
    for mrph in mrphs:
        length = len(mrph.midasi)
        if mrph.span[0] == mrph.span[1]:
            mrph.span = (start, start + length)
        start += length


def _revert_normalize_mrphs(msrs, mrphs):
    _span_mrphs(mrphs)
    for msr in msrs:
        for m in msr[0]:
            (mstart, mend) = m.span()
            for mrph in mrphs:
                (start, end) = mrph.span
                if (start <= mstart) and (mend <= end):
                    dstart = mstart - start
                    dend = dstart + (mend - mstart)
                    prev = mrph.midasi[0:dstart]
                    post = mrph.midasi[dend:]
                    mrph.midasi = prev + msr[1] + post


def get_named_entry_bunrui(name):
    bunrui_kv = {
        "ORGANIZATION": {'hinsi': "名詞", 'hinsi_id': 6, 'bunrui': "組織名", 'bunrui_id': 6},
        "DATE"        : {'hinsi': "名詞", 'hinsi_id': 6, 'bunrui': "時相名詞", 'bunrui_id': 10},
        "PERSON"      : {'hinsi': "名詞", 'hinsi_id': 6, 'bunrui': "人名", 'bunrui_id': 5},
    }
    if name in bunrui_kv:
        return bunrui_kv[name]
    return {'hinsi': "未定義語", 'hinsi_id': 15, 'bunrui': "*", 'bunrui_id': 0}


class NamedEntry:

    def __init__(self, bunrui_name):
        self.mrphs = []
        bunrui = get_named_entry_bunrui(bunrui_name)
        self.hinsi = bunrui['hinsi']
        self.hinsi_id = bunrui['hinsi_id']
        self.bunrui = bunrui['bunrui']
        self.bunrui_id = bunrui['bunrui_id']

    def push_mrph(self, mrph):
        self.mrphs.append(mrph)

    def mrph_list(self):
        return self.mrphs


class JumanAnalyzer:

    class Result:

        def __init__(self, result) -> None:
            self.result = result

        def mrph_list(self):
            return self.result.mrph_list()

        def bnst_list(self):
            return None

        def tag_list(self):
            return None

        def named_entry_list(self):
            return []

        @property
        def midasi(self):
            return "".join([mrph.midasi for mrph in self.mrph_list()])

    def __init__(self) -> None:
        self.jumanpp = Juman()
        self.logger = logging.getLogger(__name__)

    def analysis(self, str):
        (str, msrs) = self.normalize(str)
        if len(str) > 0:
            try:
                r = JumanAnalyzer.Result(self.jumanpp.analysis(str))
                _revert_normalize_mrphs(msrs, r.mrph_list())
                return r
            except Exception:
                self.logger.debug(str)
                self.logger.error(traceback.format_exc())
        return None

    def normalize(self, str):
        str = str.strip()
        msrs = _juman_msrs(str)
        return (_normalize(str, msrs), msrs)


class KnpAnalyzer:

    class Result:

        def __init__(self, result) -> None:
            self.result = result

        def mrph_list(self):
            return self.result.mrph_list()

        def bnst_list(self):
            return self.result.bnst_list()

        def tag_list(self):
            return None

        def named_entry_list(self):
            nelist = []
            curr = None
            for mrph in self.mrph_list():
                f = Features(mrph.fstring)
                if 'NE' in f:
                    ne = f['NE']
                    v = ne.split(':')
                    ne_type = v[0]
                    ne_pos = v[1]
                    if curr is None:
                        if ne_pos == 'B':
                            curr = NamedEntry(ne_type)
                    if curr:
                        curr.push_mrph(mrph)
                        if ne_pos == 'E':
                            nelist.append(curr)
                            curr = None
            return nelist

        @property
        def midasi(self):
            return "".join([mrph.midasi for mrph in self.mrph_list()])

    def __init__(self) -> None:
        self.knp = KNP()
        self.logger = logging.getLogger(__name__)

    def analysis(self, str):
        (str, msrs) = self.normalize(str)
        if len(str) > 0:
            try:
                r = KnpAnalyzer.Result(self.knp.parse(str))
                _revert_normalize_mrphs(msrs, r.mrph_list())
                return r
            except Exception:
                self.logger.debug(str)
                self.logger.error(traceback.format_exc())
        return None

    def normalize(self, str):
        str = str.strip()
        msrs = _knp_msrs(str)
        return (_normalize(str, msrs), msrs)
