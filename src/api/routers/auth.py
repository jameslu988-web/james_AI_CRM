"""认证路由 - 处理用户登录、注册、权限验证"""
from datetime import datetime, timedelta
from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ...crm.database import get_session, User, Role

router = APIRouter()

# 安全配置
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境请修改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8小时

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    role_ids: list[int] = []


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
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
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
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
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
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    db = get_session()
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
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
    
    # 创建访问令牌
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


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
