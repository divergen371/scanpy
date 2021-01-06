# Scanpy


Pythonで書かれたハッカーっぽいツール集。  
学習のために色々参考にしてまとめたものなので何も保証しません。  
(使う人いないと思うけど。)

* scan.py
  * scapyを使ったポートスキャナ。

* pingsweep.py
  * scapyを使ったホストディスカバリーツール。


* dir_burn.py
  * ファイル・ディレクトリスキャナ。

* link_extractor.py
  * webサイト内に存在するリンクをクローリングするツール。

* ssh_brute_force.py
  * SSHサーバーにブルートフォースアタック

* subdomain_scanner.py
  * サブドメインを探す。

Pipenvが必要。

```
git clone https://github.com/divergen371/scanpy
cd scanpy
pipenv install
pipenv shell
```

scan.pyとpingsweep.pyは管理者権限が必要。