
# Calendar

```bash
pip install -r requirements.txt
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

最初の実行時は、google 認証画面が出ます。

prompt for ChatGCP-4
```plain
Google Calendar API を使って指定した長さの時間の予定を新たに登録できるかを判定する python プログラムを示してください。
登録が可能な場合は、その候補の時間帯を全て示してください。登録はしないでください。
```

```plain
スケジュールに重なりがあると、free_slots が正しく出力されません。修正してください。
```

```plain
次のコードをリファクタリングしてください。
```

```plain
google calendr api を使って予定を検索する ChatGPT 4 のプラグインのソースコードを示してください。
openapi.yaml, ai-plugin.json の内容も示してください、
ユーザーがプラグインをインストールするときに、google 認証を行うようにしてください。

python , quartを使ってください。
main.py には, 次のメソッドも含めてください。
async def plugin_logo():
async def openapi_spec():
async def plugin_manifest():


検索方法は、期間指定、タイトルに含まれる文字列とします。

chartgpt のプラグインの作成方法については、https://platform.openai.com/docs/plugins/getting-started　を参照してください。
これに倣ってコードを作ってください。
google 認証 (OAuth2 の利用) をする部分を省略せずに示してください。

timenavi という ghatgpt の plugin では、
plugin のインストール時にgoogle の認証画面が現れます。
これと同様の動作にしてください。
```

```plain
このコードを実行する前の手順 (credentials.json のダウンロードまで) を step by step で説明してください。
```

## example

実行例を示します。

```zsh
$ python quickstart.py
Getting the upcoming 5 events
2023-07-04T13:30:00+09:00 - 2023-07-04T15:30:00+09:00 ''
2023-07-04T14:30:00+09:00 - 2023-07-04T15:30:00+09:00 'xxx'
2023-07-04T14:30:00+09:00 - 2023-07-04T15:00:00+09:00 'yyy'

$ python list.py
Free slot: 2023-07-04 00:00:00+00:00 - 2023-07-04 13:30:00+09:00 4:30:00
Free slot: 2023-07-04 15:30:00+09:00 - 2023-07-05 00:00:00+00:00 17:30:00

```

## plugin の作成

### google pauth の設定

TODO

### Google ぁレンダーアクセス

TODO

## movies


- プラグインのインストール時
https://github.com/katoy/plugins-calendar/assets/11354/ba148648-d916-4b1e-aa43-727de5d75b38

<div align="center">
  <video src="./movies/install.mp4" width="600" />
</div>

- giigle calendar アクセス時
https://github.com/katoy/plugins-calendar/assets/11354/7a4b278d-5556-4cc7-a7c2-e4d45dd7476b

<div align="center">
  <video src="./movies/auth-google.mp4" width="600" />
</div>

## See

- https://developers.google.com/calendar/api/quickstart/python?hl=ja
  Google Calendar Python クイックスタート

- https://weekly.ascii.jp/elem/000/004/140/4140826/
  ChatGPTでプログラミングのフラット化がはじまっている

- https://www.youtube.com/watch?v=-tQ-F9loc3g
  How to setup OAuth for ChatGPT Plugin (sign in with Google)