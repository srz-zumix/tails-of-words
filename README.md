# 言葉のしっぽ（tails-of-words）

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
