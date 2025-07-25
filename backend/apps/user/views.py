import logging
import os.path
from typing import List, Optional, Union

from ninja import Router

from apps.core import R, token_util, auth
from apps.course.models import UserHub, Course
from apps.course.schemas import CourseSchema
from apps.user.models import Banner, User, Feedback
from apps.user.schemas import LoginSchema, BannerSchema, UserSchema, FeedbackSchema, LoginResult
from ninja import File, UploadedFile
from django.contrib.auth.hashers import make_password, check_password

from edu import settings

# Create your views here.

router = Router()


@router.post("/login", summary="登录", response=Union[LoginResult, R])
def auth_login(request, auth: LoginSchema):
    """
    登录接口
    """
    try:
        # 查询用户
        obj = User.objects.get(username=auth.username)
        # 验证密码
        if not check_password(auth.password, obj.password):
            return R.fail("用户名或密码错误")
    except User.DoesNotExist:
        return R.fail("用户不存在，请先注册")

    # 生成token
    token = token_util.build(obj.id)
    return {"token": token, "user": obj}


@router.post("/register", summary="注册", response=R)
def auth_register(request, auth: LoginSchema):
    """
    注册接口
    """
    try:
        # 检查用户名是否已存在
        if User.objects.filter(username=auth.username).exists():
            return R.fail("用户名已被注册")
        
        # 创建用户
        password = make_password(auth.password)  # 对密码进行哈希处理
        User.objects.create(username=auth.username, password=password)
        return R.ok("注册成功")
    except Exception as e:
        return R.fail(f"注册失败: {str(e)}")

@router.post("/logout", summary="退出")
def auth_logout(request):
    request.session.clear()
    return R.ok()


@router.post("/avatar", summary="上传头像", **auth)
def auth_avatar(request, avatar: UploadedFile = File(...)):
    root = settings.MEDIA_ROOT / "avatars"
    if not os.path.isdir(root):
        os.mkdir(root)
    with open(root / avatar.name, "wb") as w:
        w.write(avatar.read())
    user = User.objects.get(id=request.auth)
    user.avatar = f"avatars/{avatar.name}"
    user.save()
    return R.ok(data={"url": user.avatar.url})


@router.patch('/profile', summary="修改信息", **auth)
def auth_profile(request, data: UserSchema):
    if obj := data.dict(exclude_unset=True):
        print(obj)
        if "password" in obj:
            obj["password"] = make_password(obj["password"])
        User.objects.filter(pk=request.auth).update(**obj)
        return R.ok()
    return R.fail("无效修改")


###

@router.get('/banner', summary="轮播图", response=List[BannerSchema])
def get_banners(request):
    return Banner.objects.all().order_by("-sort_number")


@router.get("/course", summary="根据操作类型获取课程", response=List[CourseSchema], **auth)
def get_courses_by_act_type(request, act_type: int = 1):
    """act_type 1 or 2, 1学习 2收藏"""
    objs = UserHub.objects.filter(user_id=request.auth, act_type=act_type)
    return [obj.course for obj in objs]


@router.post("/course", summary="收藏/学习", **auth)
def add_user_hub(request, course_id: int, act_type: int):
    kwargs = dict(user_id=request.auth, act_type=act_type, course_id=course_id)
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return R.fail("课程不存在")
    try:
        obj = UserHub.objects.get(**kwargs)
        if obj.act_type != 1:
            obj.delete()
            logging.info(f"{obj.user_id} 取消 {act_type} {course_id}")
            return R.ok(msg="已取消收藏")
    except UserHub.DoesNotExist:
        UserHub.objects.create(**kwargs)
        if act_type == 1:
            course.study_number += 1
            course.save()
            
            # 更新成就系统 - 学习行为（增强错误处理）
            try:
                from apps.user.achievement_service import AchievementService
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"开始更新学习进度 - 用户ID: {request.auth}, 课程ID: {course_id}")
                
                # 分步骤执行，便于排查问题
                AchievementService.update_study_progress(request.auth, course_id, 0)  # 先不记录学习时长，避免复杂计算
                logger.info(f"学习进度更新成功 - 用户ID: {request.auth}, 课程ID: {course_id}")
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"成就系统更新失败 - 用户ID: {request.auth}, 课程ID: {course_id}, 错误: {str(e)}")
                # 成就系统错误不影响主要功能，但记录详细错误信息
        elif act_type == 2:
            # 更新成就系统 - 收藏行为（增强错误处理）
            try:
                from apps.user.achievement_service import AchievementService
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"开始更新收藏统计 - 用户ID: {request.auth}, 课程ID: {course_id}")
                
                AchievementService.update_favorite_stats(request.auth, course_id)
                logger.info(f"收藏统计更新成功 - 用户ID: {request.auth}, 课程ID: {course_id}")
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"收藏统计更新失败 - 用户ID: {request.auth}, 课程ID: {course_id}, 错误: {str(e)}")
                # 成就系统错误不影响主要功能

    return R.ok(msg="收藏成功")


@router.post("/feedback", summary="反馈留言", **auth)
def add_feedback(request, data: FeedbackSchema):
    Feedback.objects.create(user_id=request.auth, **data.dict())
    return R.ok()
