# 言葉のしっぽ（tails-of-words）

[![PyPI version](https://badge.fury.io/py/tails-of-words.svg)](https://badge.fury.io/py/tails-of-words)
[![Python Versions](https://img.shields.io/pypi/pyversions/tails-of-words.svg)](https://pypi.org/project/tails-of-words/)
[![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/srzzumix/tails-of-words)](https://hub.docker.com/r/srzzumix/tails-of-words)
[![GitHub Actions](https://github.com/srz-zumix/tails-of-words/actions/workflows/main.yml/badge.svg)](https://github.com/srz-zumix/tails-of-words/actions/workflows/main.yml)

表記ゆれ検出の実装実験

## 概要

* 形態素解析（jumanpp）による名詞の検出
* 名詞の出現数のレポート
* 名詞の編集距離のレポート
  * レーベンシュタイン距離
  * 読みのレーベンシュタイン距離

## Usage

docker ならビルドするだけで実行環境が整います。

python setup.py install する場合は、別途 jumanpp のインストールが必要です。

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

### Help

```sh
usage: tails-of-words [-h] [-v] [--dumpversion] [--log {DEBUG,INFO,WARN,ERROR,CRITICAL,debug,info,warn,error,critical}] {count,distance,show,swing,help} ...

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
                        set log level.
```

## 参考

* [CEDEC2021: ゲーム制作効率化のためのAIによる画像認識・自然言語処理への取り組み](https://cedec.cesa.or.jp/2021/session/detail/s6049c15401f23)
  * [ゲーム制作効率化のためのAIによる画像認識・自然言語処理への取り組み - Speaker Deck](https://speakerdeck.com/cygames/kemuzhi-zuo-xiao-lu-hua-falsetamefalseainiyoruhua-xiang-ren-shi-zi-ran-yan-yu-chu-li-hefalsequ-rizu-mi) 
* [JUMAN品詞体系 | Yuta Hayashibe](https://hayashibe.jp/tr/juman/dictionary/pos)

## 貢献

このリポジトリは表記ゆれ検出の実験的な実装をしています。
アイディアや PR を歓迎します。
