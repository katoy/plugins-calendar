
# Calendar

```bash
pip install -r requirements.txt
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

最初の実行時は、google 認証画面が出ます。

prompt for ChatGCP-4
```plain
Google Calendar API を使って指定した長さの時間の予定を新たに登録できるかを判定する  python  プログラムを示してください。
登録が可能な場合は、その候補の時間帯を全て示してください。登録はしないでください。
```

```plain
スケジュールに重なりがあると、free_slots が正しく出力されません。修正してください。
```

```plain
次のコードをリファクタリングしてください。
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

## See

- https://developers.google.com/calendar/api/quickstart/python?hl=ja
  Google Calendar Python クイックスタート

- https://weekly.ascii.jp/elem/000/004/140/4140826/
  ChatGPTでプログラミングのフラット化がはじまっている
