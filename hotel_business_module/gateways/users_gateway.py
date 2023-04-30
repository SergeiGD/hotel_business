import hashlib
import uuid
from datetime import datetime
from typing import List
import bcrypt
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session
from ..models.black_list_tokens import BlackListJWT
from ..models.groups import group_permission
from ..models.permissions import Permission
from ..models.tokens import Token, TokenType
from ..models.users import User
from ..models.users import user_group
from ..settings import settings


def gen_confirm_token():
    """
    Генерация токенов для регестрации и сброса пароля
    :return:
    """
    clean_token = uuid.uuid4().hex
    hashed_token = hashlib.sha512(
        clean_token.encode('utf-8')
    ).hexdigest()
    return clean_token, hashed_token


class UsersGateway:
    """
    Класс для работы с пользователями (аутентификация, сброс пароля, регистрация и т.п.)
    """

    @staticmethod
    def authenticate_user(login: str, password: str, db: Session):
        """
        Аутнетификация пользоватя
        :param login: логин (почта)
        :param password: пароль (в чистом виде)
        :param db: сессия БД
        :return:
        """
        user = db.query(User).filter_by(email=login).first()
        if user is None \
                or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')) \
                or not user.is_confirmed:
            raise ValueError('Активный пользователь с таким логином и паролем не найден')
        return user

    @staticmethod
    def can_actions(user: User, codes: List[str], db: Session):
        """
        Проверка, если ли у пользователя права на выполение действий
        :param user: пользователь, разрешения которого будут проверятся
        :param codes: список кодов разрешений
        :param db: сессия БД
        :return:
        """
        db.add(user)
        if hasattr(user, 'is_superuser') and user.is_superuser:
            return True

        # получаем id разрешений пользователя
        user_permissions = db.query(group_permission.c.permission_id).filter(
            group_permission.c.group_id.in_(
                db.query(user_group.c.group_id).filter(
                    user_group.c.user_id == user.id,
                )
            )
        )

        # подзапрос, в котором получаем id необходимых разрешений
        required_permissions = db.query(Permission.id.label('permission_id')).filter(
            Permission.code.in_(codes),
        ).subquery('required_permissions')

        if db.query(
                db.query(required_permissions).filter(
                    required_permissions.c.permission_id.not_in(user_permissions)
                ).exists()
        ).scalar():
            # если не хватет каких-то прав, то возращаем False
            return False

        return True

    @staticmethod
    def register_user(user: User, db: Session):
        # проверяем есть ли зарегестрированный (с паролем) пользователь с такой эл. почтой
        if db.query(
                db.query(User).filter(
                    User.email == user.email,
                    User.is_confirmed == True,
                ).exists()
        ).scalar():
            raise ValueError('Пользователь с таким адресом эл. почты уже ререгестрирован')

        unregistered_user = db.query(User).filter(
            User.email == user.email,
            User.is_confirmed == False,
        ).first()
        if unregistered_user is not None:
            # если есть созданный, но не зарегестрированный (без пароля) клиент, то устанавливаем регестрируем его
            user = unregistered_user

        # хэшируем пароль (bcrypt сохраняет соль прямо в хэш)
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf8')
        db.add(user)
        db.flush()

        clean_token, hashed_token = gen_confirm_token()
        confirm_token = Token(user=user, token_type=TokenType.register, token=hashed_token)
        db.add(confirm_token)
        db.commit()

        return user, clean_token

    @staticmethod
    def confirm_account(token: Token, db: Session):
        """
        Подтверждение аккаунта после регистрации
        :param token: токен
        :param db: сессия БД
        :return:
        """
        db.add(token)
        db.add(token.user)
        token.user.is_confirmed = True
        # отмечаем токен как использованный
        token.is_used = True
        db.commit()

    @staticmethod
    # def request_reset(user: User):
    def request_reset(email: str, db: Session):
        """
        Запроса сброса пароля
        :param email: эл почта пользователя, которому нужно сбросить пароль
        :param db: сессия БД
        :return:
        """
        # ищем пользователя
        user = db.query(User).filter(
            User.email == email,
            User.is_confirmed == True,
        ).first()
        if user is None:
            raise ValueError('Не найден активный пользователь с такой эл. почтой')
        # генерируем токены
        clean_token, hashed_token = gen_confirm_token()
        reset_token = Token(user=user, token_type=TokenType.reset, token=hashed_token)
        db.add(reset_token)
        db.commit()

        return user, clean_token

    @staticmethod
    def confirm_reset(token: Token, password: str, db: Session):
        """
        Подтверждение сброса пароля
        :param token: токен сброса пароля
        :param password: пароль (в чистом виде)
        :param db: сессия БД
        :return:
        """
        db.add(token)
        db.add(token.user)
        # отмечаем токен как использованный
        token.is_used = True
        # хэшируем пароль
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        token.user.password = hashed_password.decode('utf8')
        db.commit()

    @staticmethod
    def check_token(token: str, token_type: TokenType, db: Session):
        """
        Проверка валидности токена (токен сброса пароля/регистрации)
        :param token: токен (сброса пароля/регистрации)
        :param token_type: тип токена
        :param db: сессия БД
        :return:
        """
        try:
            hashed_token = hashlib.sha512(
                token.encode('utf-8')
            ).hexdigest()
            return db.query(Token).filter(
                Token.token == hashed_token,
                Token.token_type == token_type,
                Token.expires > datetime.now(tz=settings.TIMEZONE),
                Token.is_used == False,
            ).first()
        except Exception:
            return None

    @staticmethod
    def generate_auth_tokens(user_id: int):
        """
        Генерация jwt токенов после аутентификации
        :param user_id: id пользователя, прошеднего аутентификацию
        :return:
        """
        access_token = jwt.encode({
            'id': user_id,
            'exp': datetime.now(tz=settings.TIMEZONE) + settings.ACCESS_TOKEN_LIVE_TIME,
            'is_refresh_token': False,
        }, settings.SECRET_KEY, algorithm='HS256')

        refresh_token = jwt.encode({
            'id': user_id,
            'exp': datetime.now(tz=settings.TIMEZONE) + settings.REFRESH_TOKEN_LIVE_TIME,
            'is_refresh_token': True,
        }, settings.SECRET_KEY, algorithm='HS256')

        return access_token, refresh_token

    @staticmethod
    def refresh_auth_tokens(refresh_token: str, db: Session):
        """
        Обновление jwt токенов
        :param refresh_token: токен обновления
        :param db: сессия БД
        :return:
        """
        try:
            # пытаемся декодировать токен
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except (DecodeError, ExpiredSignatureError):
            raise ValueError('Недействительный токен обновления')

        # проверяем не забанен ли (уже не использован) токен
        is_banned = db.query(
            db.query(BlackListJWT).filter(
                BlackListJWT.token == refresh_token,
            ).exists()
        ).scalar()

        if not payload['is_refresh_token'] or is_banned:
            raise ValueError('Недействительный токен обновления')

        # помечаем токен как использованный
        db.add(BlackListJWT(token=refresh_token))
        db.commit()

        # генерируем новые токен
        access_token = jwt.encode({
            'id': payload['id'],
            'exp': datetime.now(tz=settings.TIMEZONE) + settings.ACCESS_TOKEN_LIVE_TIME,
            'is_refresh_token': False,
        }, settings.SECRET_KEY, algorithm='HS256')

        refresh_token = jwt.encode({
            'id': payload['id'],
            'exp': datetime.now(tz=settings.TIMEZONE) + settings.REFRESH_TOKEN_LIVE_TIME,
            'is_refresh_token': True,
        }, settings.SECRET_KEY, algorithm='HS256')

        return access_token, refresh_token

    @staticmethod
    def get_all(db: Session):
        return db.query(User).filter(date_deleted=None).all()

    @staticmethod
    def get_by_id(user_id: int, db: Session):
        return db.query(User).filter_by(id=user_id, date_deleted=None).first()
