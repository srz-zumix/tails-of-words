# 言葉のしっぽ（tails-of-words）

[![PyPI version](https://badge.fury.io/py/tails-of-words.svg)](https://badge.fury.io/py/tails-of-words)
[![Python Versions](https://img.shields.io/pypi/pyversions/tails-of-words.svg)](https://pypi.org/project/tails-of-words/)
[![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/srzzumix/tails-of-words)](https://hub.docker.com/r/srzzumix/tails-of-words)
[![GitHub Actions](https://github.com/srz-zumix/tails-of-words/actions/workflows/main.yml/badge.svg)](https://github.com/srz-zumix/tails-of-words/actions/workflows/main.yml)

表記ゆれ検出の実装実験

## 概要

* 形態素解析（jumanpp）による名詞の検出
* knp による固有表現の検出
* 任意品詞の出現数のレポート
* 任意品詞の編集距離のレポート
  * レーベンシュタイン距離
  * ダメラウ・レーベンシュタイン距離
  * ジャロ・ウィンクラー距離
  * それぞれ読みの距離
* 任意品詞の表記ゆれ検出

## Install

### pip

```sh
pip install tails-of-words
```

別途 jumanpp と knp のインストールが必要です

e.g. brew install jumanpp

### docker

docker pull srzzumix/tails-of-words

## Usage

e.g.

```sh
$ echo コンピュータとコンピューター | tails-of-words swing -
 1, 0.86, 0.86: コンピュータ(1) vs コンピューター(1) : 1.03
```

```sh
curl -fsSL https://srz-zumix.blogspot.com/2021/09/cedec.html | tails-of-words --stdin-type html swing --exclude-alphabet --exclude-ascii -t 1 -
 1, 0.75, 0.75: ブクログ(1) vs ブログ(6) : 1.29
 1, 0.67, 0.67: ホスト(1) vs リスト(3) : 1.00
 1, 0.67, 0.67: ホスト(1) vs テスト(3) : 1.00
```

```sh
$ docker run --rm -w /work -v $(pwd):/work srzzumix/tails-of-words swing /work/testdata -t 1
 1, 0.86, 0.86: コンピューター(1) vs コンピュータ(1) : 1.03
 0, 1.00, 0.67: Max(1) vs max(1) : 1.00
```

use knp

```sh
$ echo 奈良先端科学技術大学院大学 | tails-of-words --knp count -
1 : 奈良
1 : 先端
1 : 科学
1 : 技術
1 : 大学院
1 : 大学
1 : 奈良先端科学技術大学院大学
```

use jaro winkler

```sh
$ echo 時間と歌人 | tails-of-words distance --jw -
0.00, 0.89: 時間(1) vs 歌人(1) : 0.00
```

use damerau levenshtein

```sh
$ echo 時間と歌人 | tails-of-words distance --damerau -
 2,  1, 0.00, 0.67: 時間(1) vs 歌人(1) : 0.00
$ echo 時間と歌人 | tails-of-words distance -
 2,  2, 0.00, 0.33: 時間(1) vs 歌人(1) : 0.00
```

### Help

```sh
usage: tails-of-words [-h] [-v] [--dumpversion] [--log {DEBUG,INFO,WARN,ERROR,CRITICAL,debug,info,warn,error,critical}] [-c CONFIG]
                      [-f {csv,xml,html,plain}] [--h2t] [--knp]
                      {count,distance,show,swing,help} ...

positional arguments:
  {count,distance,show,swing,help}
    count               count words. see `count -h`
    distance            distance counted words. see `distance -h`
    show                show words. see `show -h`
    swing               show notation fluctuations. see `swing -h`
    help                show subcommand help. see `help -h`

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --dumpversion         show program's version number and exit
  --log {DEBUG,INFO,WARN,ERROR,CRITICAL,debug,info,warn,error,critical}
                        set log level
  -c CONFIG, --config CONFIG
                        config.yml file path
  -f {csv,xml,html,plain}, --stdin-type {csv,xml,html,plain}, --stdin-format {csv,xml,html,plain}
                        set stdin format type
  --h2t, --html2text    Convert input text with html2text
  --knp                 use knp.
```

```sh
tails-of-words help swing
usage: tails-of-words swing [-h] [-n NUM] [-t THRESHOLD] [--jw] [--damerau] [--no-alnum] [--no-ascii] [-o OUTPUT] [-c COLUMN] [-i HINSI] [-e EXCLUDE]
                            SOURCE [SOURCE ...]

show notation fluctuations

positional arguments:
  SOURCE                input files

optional arguments:
  -h, --help            show this help message and exit
  -n NUM, --num NUM     Display n items from the highest score. All if n is less than or equal to 0
  -t THRESHOLD, --threshold THRESHOLD
                        Display words whose score exceeds the threshold.
  --jw, --jaro-winkler  use jaro_winkler.
  --damerau, --damerau-levenshtein
                        use damerau_levenshtein.
  --no-alnum, --exclude-alphabet
                        exclude isalpha or isalnum string.
  --no-ascii, --exclude-ascii
                        exclude isascii string.
  -o OUTPUT, --output OUTPUT
                        output json file path.
  -c COLUMN, --column COLUMN
                        specific csv file column name.
  -i HINSI, --hinsi HINSI
                        set collect hinsi_id. default [6, 15]
  -e EXCLUDE, --exclude EXCLUDE
                        exclude files
```

## 参考

* [CEDEC2021: ゲーム制作効率化のためのAIによる画像認識・自然言語処理への取り組み](https://cedec.cesa.or.jp/2021/session/detail/s6049c15401f23)
  * [ゲーム制作効率化のためのAIによる画像認識・自然言語処理への取り組み - Speaker Deck](https://speakerdeck.com/cygames/kemuzhi-zuo-xiao-lu-hua-falsetamefalseainiyoruhua-xiang-ren-shi-zi-ran-yan-yu-chu-li-hefalsequ-rizu-mi) 
* [pyknp: Python Module for JUMAN++/KNP — pyknp documentation](https://pyknp.readthedocs.io/en/latest/index.html)
* [JUMAN品詞体系 | Yuta Hayashibe](https://hayashibe.jp/tr/juman/dictionary/pos)

## 貢献

このリポジトリは表記ゆれ検出の実験的な実装をしています。
アイディアや PR を歓迎します。
