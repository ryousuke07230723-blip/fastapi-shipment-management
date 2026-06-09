# Redisへの接続・JWTブラックリスト管理
from redis.asyncio import Redis

from app.config import db_settings

# Redisへの接続クライアントを作成
_token_blacklist = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=0,  # RedisのDBの0番目を指定(Redisの仕様が関係)
)


# JTIをブラックリストに登録（ログアウト済みトークンを無効化）
async def add_jwt_to_blacklist(jti: str):
    await _token_blacklist.set(jti, "blacklisted")


# JTIがブラックリストに存在するか確認
async def is_jti_blacklisted(jti: str):
    return await _token_blacklist.exists(jti)
