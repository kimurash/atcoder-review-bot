from fastapi import FastAPI
from api.routers import webhook_handler

app = FastAPI()

# 別ファイルで定義したルートをアプリケーションに適用
app.include_router(webhook_handler.router)

# パスオペレーション関数
@app.get("/hello")
async def hello():
    return {"message": "hello world!"}