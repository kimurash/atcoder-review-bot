# 全てのアドレスからのリクエストを受け付ける
bind = "0.0.0.0:8000"

workers = 3
worker_class = "uvicorn.workers.UvicornWorker"

loglevel  = "debug"
errorlog  = "/src/log/error.log"
accesslog = "/src/log/access.log"
