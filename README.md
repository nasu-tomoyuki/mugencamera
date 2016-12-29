# 無限カメラ
----
Raspberry Pi で写真と動画を撮影します。
それを、無限のストレージ容量を持つ Google Photos (Picasa) へアップロードして、オリジナルのデータは削除します。
つまり、Raspberry Pi のストレージ容量を気にせずに無限に撮影します。

 ***現在のバージョンでは動画のアップロードが出来ません。*** 正確には、アップロードは出来ますが、Google Photos で再生待ちから進まず、しばらくすると削除されてしまいます。おそらくメタタグの指定が足りないんだと思います。情報をお持ちの方は教えてください。


# 開発環境
* Raspberry Pi 2 Model B
	* Raspberry Pi Camera Board Rev 1.3
* Raspbian
* Python3

## Python ライブラリ
pip3 で入ります。
* requests_toolbelt
* google-api-python-client


# 事前準備
## Google
* Google アカウントの取得
	* 持っていない場合は取得しましょう。
* Google プロジェクトの作成
	* [Google Developers Console](https://console.developers.google.com/) で、空のプロジェクトを作成します。名前は何でもいいです。
* プロジェクトの認証情報を作成
	* 上記で作成した空のプロジェクトへの認証情報を作成します。
		* 認証情報 > 認証情報を作成 > OAuth クライアント ID > アプリケーションの種類 その他 (名前はなんでもいいです) > 作成
	* JSON 形式でダウンロードします。
		* ファイルは ./secret/oauth2.json として保存します。
	* これは Google への OAuth2 認証で利用します。

## 設定ファイル
* config.sample.py をコピーして config.py に変更してください。
	* GOOGLE_USER_ID に Google の User ID を設定してください。 Google+ の URL やプロフィール画面などで確認できます。
		* https://plus.google.com/u/2/xxxxxxxxxxxxxxxxxxxxx みたいなやつです。xxx の部分です。
* RECORDING_THRESHOLD の値を大きくすることで感度を下げられます。


# 実行

```
$ python3 mugencamera.py --tmpdir /mugencamera
```

このような感じで実行します。

初回は OAuth2 認証のために URL が出力されます。それをブラウザで開いて認証するとコードが出てくるので、それをコマンドラインに貼り付けてエンターで起動します。

OAuth2 のクレデンシャルは ./secret/credentials.json として保存されます。このファイルがあれば次回からはブラウザでの認証は必要ありません。

起動するとカメラで撮影を続け、映像に変化があれば写真と動画を撮ります。そしてそれを Google Photos へアップロードします。

終了は ^C です。


## オプション
* --tmpdir
	* 一時保存先のディレクトリを指定



# 動作原理
1. 起動するとカメラで撮影を始めます。この時点ではファイルへは保存しません。
1. 映像に変化があると写真を保存し、動画を撮影します。
	* 変化の検出には Average Hash という類似画像を検出するアルゴリズムを使用しています。これを選択した理由は、実装が簡単で処理が軽そうだったからです。
	* 参考: [Go言語を使って類似画像を検索する](https://developers.eure.jp/tech/go_image_hash/)
	* 使ってみた感想としては、ボールが転がるといった、小さな範囲の検出には弱いので用途に応じてアルゴリズムを変えた方がいいですね。
1. 撮影中にも定期的に映像の変化を検出し、変化があれば動画撮影を継続します。設定した最大時間まで延長します。
	* 変化の検出のために写真を撮っていますが、そのタイミングで動画のフレームをドロップします。
1. 別スレッドで指定ディレクトリを監視していて、写真や動画が書き込まれたらバックグラウンドで転送を行い、元ファイルを削除します。


# Tips
## RAM ディスク
Raspberry Pi のストレージは Micro SD なので、書き込み耐性が低いです。
写真の書き出し先を RAM ディスクにするとストレージの劣化を防げ、動画の書き込み速度向上も見込めます。
* 参考: [Raspberry PiのログをRAMDISKに置く方法](https://curecode.jp/tech/raspberrypi-ramdisk/)

## レンズアタッチメント
スマホのカメラ向けアタッチメントが販売されています。そういうものを付けることで機能が向上します。
たとえば広角や魚眼レンズを付ければ、撮影範囲が広くなるので監視カメラとしては使いやすいでしょう。
マクロレンズを付ければ、植物か何かの観察に向いているでしょう。


# そのほかの参考
* [Google Photosの無料容量15GBを有効活用！cURLでGoogle Photosへ画像アップロードするには？](http://qiita.com/tamanobi/items/be3eede75c9ede41fce4)
* [Picasa Web Albums Data API](https://developers.google.com/picasa-web/docs/2.0/developers_guide_protocol)
* [Google APIs Picasaへアップロード](https://awaitingstock.wordpress.com/2012/03/07/google-apis-picasa%E3%81%B8%E3%82%A2%E3%83%83%E3%83%97%E3%83%AD%E3%83%BC%E3%83%89/)


