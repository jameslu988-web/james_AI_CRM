"""认证路由 - 处理用户登录、注册、权限验证"""
from datetime import datetime, timedelta
from typing import Optional
import json
import os
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator
import re

from ...crm.database import get_session, User, Role

router = APIRouter()
logger = logging.getLogger(__name__)

# 安全配置（从环境变量读取）
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 120))  # 2小时
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))  # 7天

# 登录安全配置
MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
LOGIN_ATTEMPT_WINDOW = int(os.getenv('LOGIN_ATTEMPT_WINDOW', 900))  # 15分钟

# 登录失败记录（生产环境应使用Redis）
login_attempts = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic模型
class Token(BaseModel):
    access_token: str
    refresh_token: str  # 新增refresh_token
    token_type: str
    user: dict


class TokenRefresh(BaseModel):
    """Token刷新请求"""
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None
    token_type: Optional[str] = "access"  # access 或 refresh


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    role_ids: list[int] = []
    
    @validator('password')
    def validate_password_strength(cls, v):
        """密码强度验证"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class PasswordChange(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """密码强度验证"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    department: Optional[str]
    position: Optional[str]
    roles: list[dict]
    created_at: datetime


# 密码哈希
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT Token创建
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    to_encode["token_type"] = "access"
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建刷新令牌"""
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 获取当前用户
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type", "access")
        
        # 确保是access token
        if token_type != "access":
            raise credentials_exception
        
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, token_type=token_type)
    except JWTError:
        raise credentials_exception
    
    db = get_session()
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# 登录限流
def record_failed_login(ip: str, username: str):
    """记录登录失败"""
    key = f"{ip}:{username}"
    now = datetime.utcnow().timestamp()
    
    if key not in login_attempts:
        login_attempts[key] = []
    
    # 清除过期记录
    login_attempts[key] = [
        attempt for attempt in login_attempts[key]
        if now - attempt < LOGIN_ATTEMPT_WINDOW
    ]
    
    login_attempts[key].append(now)
    

def is_login_allowed(ip: str, username: str) -> bool:
    """检查是否允许登录"""
    key = f"{ip}:{username}"
    now = datetime.utcnow().timestamp()
    
    if key not in login_attempts:
        return True
    
    # 清除过期记录
    login_attempts[key] = [
        attempt for attempt in login_attempts[key]
        if now - attempt < LOGIN_ATTEMPT_WINDOW
    ]
    
    return len(login_attempts[key]) < MAX_LOGIN_ATTEMPTS


# 权限验证
def check_permission(user: User, resource: str, action: str) -> bool:
    """检查用户是否有某个资源的某个操作权限"""
    if user.is_superuser:
        return True
    
    for role in user.roles:
        if not role.is_active:
            continue
        permissions = json.loads(role.permissions) if role.permissions else {}
        if resource in permissions and action in permissions[resource]:
            return True
    
    return False


# API路由
@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录（带限流和Token刷新）"""
    client_ip = request.client.host if request.client else "unknown"
    
    # 检查登录限流
    if not is_login_allowed(client_ip, form_data.username):
        logger.warning(f"登录限流触发: {form_data.username} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录失败次数过多，请{LOGIN_ATTEMPT_WINDOW // 60}分钟后再试"
        )
    
    db = get_session()
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # 记录失败
        record_failed_login(client_ip, form_data.username)
        logger.warning(f"登录失败: {form_data.username} from {client_ip}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 创建访问令牌和刷新令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    # 构建用户信息
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_superuser": user.is_superuser,
        "department": user.department,
        "position": user.position,
        "avatar": user.avatar,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "permissions": json.loads(role.permissions) if role.permissions else {}
            }
            for role in user.roles
        ]
    }
    
    logger.info(f"用户登录成功: {user.username} from {client_ip}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """刷新访问令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的刷新令牌",
    )
    
    try:
        payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        
        # 确保是refresh token
        if token_type != "refresh":
            raise credentials_exception
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 获取用户
    db = get_session()
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not user.is_active:
        raise credentials_exception
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 构建用户信息
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_superuser": user.is_superuser,
        "department": user.department,
        "position": user.position,
        "avatar": user.avatar,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "permissions": json.loads(role.permissions) if role.permissions else {}
            }
            for role in user.roles
        ]
    }
    
    logger.info(f"Token刷新成功: {user.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": token_data.refresh_token,  # 保持原refresh_token
        "token_type": "bearer",
        "user": user_data
    }


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    db = get_session()
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    logger.info(f"密码修改成功: {current_user.username}")
    
    return {"success": True, "message": "密码修改成功"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "department": current_user.department,
        "position": current_user.position,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "permissions": json.loads(role.permissions) if role.permissions else {}
            }
            for role in current_user.roles
        ],
        "created_at": current_user.created_at
    }


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, current_user: User = Depends(get_current_active_user)):
    """注册新用户（仅管理员可用）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限创建用户")
    
    db = get_session()
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        department=user_data.department,
        position=user_data.position
    )
    
    # 添加角色
    if user_data.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
        new_user.roles = roles
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "is_active": new_user.is_active,
        "is_superuser": new_user.is_superuser,
        "department": new_user.department,
        "position": new_user.position,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name
            }
            for role in new_user.roles
        ],
        "created_at": new_user.created_at
    }


@router.get("/check-permission/{resource}/{action}")
async def check_user_permission(
    resource: str,
    action: str,
    current_user: User = Depends(get_current_active_user)
):
    """检查当前用户权限"""
    has_permission = check_permission(current_user, resource, action)
    return {
        "has_permission": has_permission,
        "resource": resource,
        "action": action
    }
