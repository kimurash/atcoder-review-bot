# python3.10のイメージをダウンロード
FROM python:3.10-bookworm
# 入出力のバッファリングを無効にする
ENV PYTHONUNBUFFERED=1

# 以降のコマンドを/srcで実行
WORKDIR /src

# pipを使ってpoetryをインストール
RUN pip install poetry
# 仮想環境をプロジェクトのルートディレクトリに作成
RUN poetry config virtualenvs.in-project true

# poetryの定義ファイルをコピー
COPY pyproject.toml poetry.lock ./
# poetryでライブラリをインストール
# --no-root: プロジェクトのパッケージはインストールしない
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

# uvicornのサーバーを立ち上げる
# --host 0.0.0.0:
# 全てのアドレスからのリクエストを受け付ける
# --reload:
# ソースコードの変更を検知して自動でリロード
ENTRYPOINT ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload"]