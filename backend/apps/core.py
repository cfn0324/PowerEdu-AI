from ninja.errors import AuthenticationError

from datetime import datetime, timezone, timedelta

import secrets
from typing import Any

import jwt
from ninja.security import HttpBearer

from apps.user.models import User

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class R(BaseModel, Generic[T]):
    code: int = 1
    data: Optional[T] = None
    msg: str = "ok"

    @classmethod
    def ok(cls, data: T = None, msg="ok") -> "R":
        return cls(code=1, data=data, msg=msg)

    @classmethod
    def fail(cls, msg: str = "fail") -> "R":
        return cls(code=0, msg=msg)


class TokenUtil:

    def __init__(self, effective_time: int = 3600 * 24 * 7, secret_key: str = None, algorithms: str = "HS256"):
        """
        token 🔧
        :param effective_time: 有效时间-当前时间 + 指定秒数
        :param secret_key: 密钥
        :param algorithms: 加密算法
        """
        if secret_key is None:
            # 使用Django的SECRET_KEY作为JWT的密钥，确保一致性
            from django.conf import settings
            self.secret_key = settings.SECRET_KEY
        else:
            self.secret_key = secret_key
        self.effective_time = effective_time
        self.algorithms = algorithms
        print(f"🔐 TokenUtil初始化，secret_key前10位: {self.secret_key[:10]}...")

    def build(self, payload: Any) -> str:
        """
        生成token
        :param payload: 加密数据
        :return: token
        """
        data = {"exp": datetime.now(tz=timezone.utc) + timedelta(seconds=self.effective_time)}
        data.update({"payload": payload})
        token = jwt.encode(data, self.secret_key, self.algorithms)
        print(f"🔐 生成token，payload: {payload}, token前20位: {token[:20]}...")
        return token

    def parse(self, token: str) -> Any:
        """
        解析token
        :param token: token
        :return: 加密的数据
        """
        try:
            print(f"🔐 解析token，token前20位: {token[:20]}...")
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithms])
            result = payload.get("payload")
            print(f"🔐 token解析成功，payload: {result}")
            return result
        except Exception as e:
            print(f"🔐 token解析失败: {str(e)}")
            raise


token_util = TokenUtil()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            print(f"🔐 AuthBearer收到token: {token[:30]}...")
            user_id = token_util.parse(token)
            from apps.user.models import User  # 使用自定义User模型
            request.user = User.objects.get(id=user_id)
            print(f"🔐 AuthBearer认证成功: {request.user.username}")
            # 返回用户id
            return user_id
        except Exception as e:
            print(f"🔐 AuthBearer认证失败: {str(e)}")
            raise AuthenticationError()


auth = dict(auth=AuthBearer())
