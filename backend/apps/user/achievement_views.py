from typing import List
from ninja import Router
from django.db.models import Q
from apps.core import auth, R
from apps.user.achievement_models import Achievement, UserAchievement, UserPoints, StudyStats
from apps.user.achievement_schemas import (
    AchievementSchema, UserAchievementSchema, UserPointSchema, StudyStatsSchema,
    AchievementProgressSchema, UserLevelSchema, AchievementSummarySchema
)
from apps.user.achievement_service import AchievementService

router = Router()


@router.get('/stats', summary="用户学习统计", response=StudyStatsSchema, **auth)
def get_user_stats(request):
    """获取用户学习统计数据"""
    stats = AchievementService.get_or_create_stats(request.auth)
    return stats


@router.get('/level', summary="用户等级信息", response=UserLevelSchema, **auth)
def get_user_level(request):
    """获取用户等级信息"""
    level_info = AchievementService.get_user_level_info(request.auth)
    return level_info


@router.get('/achievements', summary="用户成就列表", response=List[UserAchievementSchema], **auth)
def get_user_achievements(request, completed: bool = None):
    """获取用户成就列表"""
    queryset = UserAchievement.objects.filter(user_id=request.auth).select_related('achievement')
    
    if completed is not None:
        queryset = queryset.filter(is_completed=completed)
    
    achievements = queryset.order_by('-unlocked_at')
    return list(achievements)


@router.get('/achievements/progress', summary="成就进度", response=List[AchievementProgressSchema], **auth)
def get_achievement_progress(request):
    """获取所有成就的进度"""
    progress_list = AchievementService.get_achievement_progress(request.auth)
    return progress_list


@router.get('/points', summary="积分记录", response=List[UserPointSchema], **auth)
def get_user_points(request, limit: int = 20):
    """获取用户积分记录"""
    points = UserPoints.objects.filter(
        user_id=request.auth
    ).order_by('-created_at')[:limit]
    return list(points)


@router.get('/summary', summary="成就总览", response=AchievementSummarySchema, **auth)
def get_achievement_summary(request):
    """获取用户成就总览"""
    # 获取统计数据
    stats = AchievementService.get_or_create_stats(request.auth)
    
    # 获取最近获得的成就
    recent_achievements = UserAchievement.objects.filter(
        user_id=request.auth,
        is_completed=True
    ).select_related('achievement').order_by('-unlocked_at')[:5]
    
    # 获取最近的积分记录
    recent_points = UserPoints.objects.filter(
        user_id=request.auth
    ).order_by('-created_at')[:10]
    
    # 获取成就进度
    achievement_progress = AchievementService.get_achievement_progress(request.auth)
    
    # 获取等级信息
    level_info = AchievementService.get_user_level_info(request.auth)
    
    return {
        'stats': stats,
        'recent_achievements': list(recent_achievements),
        'recent_points': list(recent_points),
        'achievement_progress': achievement_progress,
        'level_info': level_info
    }


@router.get('/leaderboard', summary="积分排行榜", response=List[dict])
def get_leaderboard(request, limit: int = 10):
    """获取积分排行榜"""
    top_users = StudyStats.objects.select_related('user').order_by('-total_points')[:limit]
    
    leaderboard = []
    for i, stats in enumerate(top_users, 1):
        leaderboard.append({
            'rank': i,
            'username': stats.user.username,
            'nickname': stats.user.nickname or stats.user.username,
            'avatar': stats.user.avatar.url if stats.user.avatar else None,
            'total_points': stats.total_points,
            'current_level': stats.current_level,
            'completed_courses': stats.completed_courses,
            'study_time_hours': stats.total_study_time // 60
        })
    
    return leaderboard


@router.post('/study', summary="记录学习行为", **auth)
def record_study_activity(request, course_id: int, study_minutes: int = 0):
    """记录学习活动"""
    try:
        AchievementService.update_study_progress(
            request.auth, course_id, study_minutes
        )
        return R.ok(msg="学习记录更新成功")
    except Exception as e:
        return R.fail(f"更新失败: {str(e)}")


@router.post('/course/complete', summary="标记课程完成", **auth)
def complete_course(request, course_id: int):
    """标记课程为已完成"""
    try:
        AchievementService.update_course_completion(request.auth, course_id)
        return R.ok(msg="课程完成状态更新成功")
    except Exception as e:
        return R.fail(f"更新失败: {str(e)}")
