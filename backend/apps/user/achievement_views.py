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
    """获取用户成就总览（增强版错误处理）"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"开始获取成就总览 - 用户ID: {request.auth}")
        
        # 获取统计数据
        try:
            stats = AchievementService.get_or_create_stats(request.auth)
            logger.info(f"统计数据获取成功 - 用户ID: {request.auth}")
        except Exception as e:
            logger.error(f"获取统计数据失败: {str(e)}")
            stats = None
        
        # 获取最近获得的成就
        try:
            recent_achievements_queryset = UserAchievement.objects.filter(
                user_id=request.auth,
                is_completed=True
            ).select_related('achievement').order_by('-unlocked_at')[:5]
            
            # 转换为字典格式
            recent_achievements = []
            for ua in recent_achievements_queryset:
                recent_achievements.append({
                    'id': ua.id,
                    'achievement': {
                        'id': ua.achievement.id,
                        'name': ua.achievement.name,
                        'description': ua.achievement.description,
                        'icon': ua.achievement.icon,
                        'achievement_type': ua.achievement.achievement_type,
                        'condition_value': ua.achievement.condition_value,
                        'points': ua.achievement.points,
                        'is_active': ua.achievement.is_active
                    },
                    'unlocked_at': ua.unlocked_at,
                    'progress': ua.progress,
                    'is_completed': ua.is_completed
                })
            
            logger.info(f"最近成就获取成功 - 数量: {len(recent_achievements)}")
        except Exception as e:
            logger.error(f"获取最近成就失败: {str(e)}")
            recent_achievements = []
        
        # 获取最近的积分记录
        try:
            recent_points_queryset = UserPoints.objects.filter(
                user_id=request.auth
            ).order_by('-created_at')[:10]
            
            # 转换为字典格式
            recent_points = []
            for up in recent_points_queryset:
                recent_points.append({
                    'id': up.id,
                    'points': up.points,
                    'point_type': up.point_type,
                    'description': up.description,
                    'related_id': up.related_id,
                    'created_at': up.created_at
                })
            
            logger.info(f"积分记录获取成功 - 数量: {len(recent_points)}")
        except Exception as e:
            logger.error(f"获取积分记录失败: {str(e)}")
            recent_points = []
        
        # 获取成就进度
        try:
            achievement_progress = AchievementService.get_achievement_progress(request.auth)
            logger.info(f"成就进度获取成功 - 数量: {len(achievement_progress)}")
        except Exception as e:
            logger.error(f"获取成就进度失败: {str(e)}")
            achievement_progress = []
        
        # 获取等级信息
        try:
            level_info = AchievementService.get_user_level_info(request.auth)
            logger.info(f"等级信息获取成功 - 用户ID: {request.auth}")
        except Exception as e:
            logger.error(f"获取等级信息失败: {str(e)}")
            level_info = {
                'current_level': 1,
                'current_points': 0,
                'next_level_points': 100,
                'progress_percentage': 0
            }
        
        # 如果关键数据（stats）为空，返回默认数据
        if not stats:
            logger.warning(f"统计数据为空，返回默认数据 - 用户ID: {request.auth}")
            # 创建一个默认的StudyStats对象而不是字典
            from apps.user.achievement_models import StudyStats
            stats, _ = StudyStats.objects.get_or_create(
                user_id=request.auth,
                defaults={
                    'total_study_time': 0,
                    'completed_courses': 0,
                    'continuous_days': 0,
                    'max_continuous_days': 0,
                    'total_points': 0,
                    'current_level': 1,
                    'comments_count': 0,
                    'favorites_count': 0
                }
            )
        
        # 将模型实例转换为字典格式以确保正确序列化
        stats_dict = {
            'id': stats.id,
            'total_study_time': stats.total_study_time,
            'completed_courses': stats.completed_courses,
            'continuous_days': stats.continuous_days,
            'max_continuous_days': stats.max_continuous_days,
            'total_points': stats.total_points,
            'current_level': stats.current_level,
            'comments_count': stats.comments_count,
            'favorites_count': stats.favorites_count,
            'last_study_date': str(stats.last_study_date) if stats.last_study_date else None,
            'updated_at': stats.updated_at
        }
        
        # 将模型实例转换为字典格式以确保正确序列化
        stats_dict = {
            'id': stats.id,
            'total_study_time': stats.total_study_time,
            'completed_courses': stats.completed_courses,
            'continuous_days': stats.continuous_days,
            'max_continuous_days': stats.max_continuous_days,
            'total_points': stats.total_points,
            'current_level': stats.current_level,
            'comments_count': stats.comments_count,
            'favorites_count': stats.favorites_count,
            'last_study_date': str(stats.last_study_date) if stats.last_study_date else None,
            'updated_at': stats.updated_at
        }
        
        result = {
            'stats': stats_dict,
            'recent_achievements': recent_achievements,
            'recent_points': recent_points,
            'achievement_progress': achievement_progress,
            'level_info': level_info
        }
        
        logger.info(f"成就总览获取完成 - 用户ID: {request.auth}")
        return result
        
    except Exception as e:
        logger.error(f"获取成就总览失败 - 用户ID: {request.auth}, 错误: {str(e)}")
        
        # 返回空的但结构正确的数据，而不是错误
        default_stats, _ = StudyStats.objects.get_or_create(
            user_id=request.auth,
            defaults={
                'total_study_time': 0,
                'completed_courses': 0,
                'continuous_days': 0,
                'max_continuous_days': 0,
                'total_points': 0,
                'current_level': 1,
                'comments_count': 0,
                'favorites_count': 0
            }
        )
        
        # 转换为字典格式
        default_stats_dict = {
            'id': default_stats.id,
            'total_study_time': default_stats.total_study_time,
            'completed_courses': default_stats.completed_courses,
            'continuous_days': default_stats.continuous_days,
            'max_continuous_days': default_stats.max_continuous_days,
            'total_points': default_stats.total_points,
            'current_level': default_stats.current_level,
            'comments_count': default_stats.comments_count,
            'favorites_count': default_stats.favorites_count,
            'last_study_date': str(default_stats.last_study_date) if default_stats.last_study_date else None,
            'updated_at': default_stats.updated_at
        }
        
        return {
            'stats': default_stats_dict,
            'recent_achievements': [],
            'recent_points': [],
            'achievement_progress': [],
            'level_info': {
                'current_level': 1,
                'current_points': 0,
                'next_level_points': 100,
                'progress_percentage': 0
            }
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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"记录学习行为 - 用户ID: {request.auth}, 课程ID: {course_id}, 学习时间: {study_minutes}分钟")
        
        AchievementService.update_study_progress(
            request.auth, course_id, study_minutes
        )
        return R.ok(msg="学习记录更新成功")
    except Exception as e:
        logger.error(f"记录学习行为失败 - 用户ID: {request.auth}, 课程ID: {course_id}, 错误: {str(e)}")
        return R.fail(f"更新失败: {str(e)}")


@router.post('/course/complete', summary="标记课程完成", **auth)
def complete_course(request, course_id: int):
    """标记课程为已完成"""
    try:
        AchievementService.update_course_completion(request.auth, course_id)
        return R.ok(msg="课程完成状态更新成功")
    except Exception as e:
        return R.fail(f"更新失败: {str(e)}")
