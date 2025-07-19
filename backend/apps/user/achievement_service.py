from datetime import datetime, date, timedelta
from django.db.models import Sum, F
from apps.user.achievement_models import Achievement, UserAchievement, UserPoints, StudyStats
from apps.user.models import User
from apps.course.models import UserHub, Comment
import logging

logger = logging.getLogger(__name__)


class AchievementService:
    """成就系统服务类"""
    
    # 等级所需积分配置
    LEVEL_POINTS = {
        1: 0, 2: 100, 3: 250, 4: 500, 5: 1000,
        6: 1800, 7: 3000, 8: 5000, 9: 8000, 10: 12000
    }
    
    @classmethod
    def get_or_create_stats(cls, user_id):
        """获取或创建用户统计数据"""
        stats, created = StudyStats.objects.get_or_create(
            user_id=user_id,
            defaults={
                'total_study_time': 0,
                'completed_courses': 0,
                'continuous_days': 0,
                'max_continuous_days': 0,
                'total_points': 0,
                'current_level': 1,
                'comments_count': 0,
                'favorites_count': 0,
            }
        )
        return stats
    
    @classmethod
    def add_points(cls, user_id, points, point_type, description, related_id=None):
        """添加用户积分"""
        try:
            # 创建积分记录
            UserPoints.objects.create(
                user_id=user_id,
                points=points,
                point_type=point_type,
                description=description,
                related_id=related_id
            )
            
            # 更新用户总积分
            stats = cls.get_or_create_stats(user_id)
            stats.total_points = F('total_points') + points
            stats.save()
            stats.refresh_from_db()
            
            # 检查等级提升
            cls.check_level_up(user_id, stats.total_points)
            
            logger.info(f"用户 {user_id} 获得 {points} 积分: {description}")
            
        except Exception as e:
            logger.error(f"添加积分失败: {e}")
    
    @classmethod
    def check_level_up(cls, user_id, total_points):
        """检查用户等级提升"""
        stats = cls.get_or_create_stats(user_id)
        current_level = stats.current_level
        
        # 计算新等级
        new_level = current_level
        for level, required_points in cls.LEVEL_POINTS.items():
            if total_points >= required_points:
                new_level = level
            else:
                break
        
        # 如果等级提升
        if new_level > current_level:
            stats.current_level = new_level
            stats.save()
            
            # 等级提升奖励积分
            bonus_points = (new_level - current_level) * 50
            cls.add_points(
                user_id, bonus_points, 2,
                f"等级提升至 Lv.{new_level} 奖励",
                new_level
            )
            
            logger.info(f"用户 {user_id} 等级提升至 Lv.{new_level}")
    
    @classmethod
    def update_study_progress(cls, user_id, course_id=None, study_minutes=0):
        """更新学习进度"""
        stats = cls.get_or_create_stats(user_id)
        today = date.today()
        
        # 更新学习时长
        if study_minutes > 0:
            stats.total_study_time = F('total_study_time') + study_minutes
            
            # 奖励学习积分
            points = min(study_minutes // 10, 20)  # 每10分钟1积分，最多20积分
            if points > 0:
                cls.add_points(
                    user_id, points, 1,
                    f"学习 {study_minutes} 分钟",
                    course_id
                )
        
        # 更新连续学习天数
        if stats.last_study_date:
            if stats.last_study_date == today:
                # 今天已经学习过了
                pass
            elif stats.last_study_date == today - timedelta(days=1):
                # 连续学习
                stats.continuous_days = F('continuous_days') + 1
                stats.last_study_date = today
            else:
                # 中断学习
                stats.continuous_days = 1
                stats.last_study_date = today
        else:
            # 第一次学习
            stats.continuous_days = 1
            stats.last_study_date = today
        
        stats.save()
        stats.refresh_from_db()
        
        # 更新最大连续天数
        if stats.continuous_days > stats.max_continuous_days:
            stats.max_continuous_days = stats.continuous_days
            stats.save()
        
        # 检查连续学习成就
        cls.check_continuous_study_achievements(user_id, stats.continuous_days)
        
        # 检查学习时长成就
        cls.check_study_time_achievements(user_id, stats.total_study_time)
    
    @classmethod
    def update_course_completion(cls, user_id, course_id):
        """更新课程完成状态"""
        stats = cls.get_or_create_stats(user_id)
        stats.completed_courses = F('completed_courses') + 1
        stats.save()
        stats.refresh_from_db()
        
        # 奖励课程完成积分
        cls.add_points(
            user_id, 100, 1,
            "完成课程学习",
            course_id
        )
        
        # 检查课程完成成就
        cls.check_course_completion_achievements(user_id, stats.completed_courses)
    
    @classmethod
    def update_comment_stats(cls, user_id, course_id):
        """更新评论统计"""
        stats = cls.get_or_create_stats(user_id)
        stats.comments_count = F('comments_count') + 1
        stats.save()
        
        # 奖励评论积分
        cls.add_points(
            user_id, 10, 4,
            "发表课程评论",
            course_id
        )
    
    @classmethod
    def update_favorite_stats(cls, user_id, course_id):
        """更新收藏统计"""
        stats = cls.get_or_create_stats(user_id)
        stats.favorites_count = F('favorites_count') + 1
        stats.save()
        
        # 奖励收藏积分
        cls.add_points(
            user_id, 5, 1,
            "收藏课程",
            course_id
        )
    
    @classmethod
    def check_continuous_study_achievements(cls, user_id, continuous_days):
        """检查连续学习成就"""
        milestones = [3, 7, 15, 30, 60, 100]
        for milestone in milestones:
            if continuous_days >= milestone:
                cls.unlock_achievement_by_condition(
                    user_id, 3, milestone
                )
    
    @classmethod
    def check_study_time_achievements(cls, user_id, total_minutes):
        """检查学习时长成就"""
        # 转换为小时
        total_hours = total_minutes // 60
        milestones = [1, 5, 10, 25, 50, 100, 200]
        for milestone in milestones:
            if total_hours >= milestone:
                cls.unlock_achievement_by_condition(
                    user_id, 1, milestone
                )
    
    @classmethod
    def check_course_completion_achievements(cls, user_id, completed_count):
        """检查课程完成成就"""
        milestones = [1, 3, 5, 10, 20, 50]
        for milestone in milestones:
            if completed_count >= milestone:
                cls.unlock_achievement_by_condition(
                    user_id, 2, milestone
                )
    
    @classmethod
    def unlock_achievement_by_condition(cls, user_id, achievement_type, condition_value):
        """根据条件解锁成就"""
        try:
            achievement = Achievement.objects.filter(
                achievement_type=achievement_type,
                condition_value=condition_value,
                is_active=True
            ).first()
            
            if achievement:
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user_id=user_id,
                    achievement=achievement,
                    defaults={
                        'is_completed': True,
                        'progress': condition_value
                    }
                )
                
                if created:
                    # 新解锁的成就，奖励积分
                    cls.add_points(
                        user_id, achievement.points, 2,
                        f"解锁成就: {achievement.name}",
                        achievement.id
                    )
                    logger.info(f"用户 {user_id} 解锁成就: {achievement.name}")
                
        except Exception as e:
            logger.error(f"解锁成就失败: {e}")
    
    @classmethod
    def get_user_level_info(cls, user_id):
        """获取用户等级信息"""
        stats = cls.get_or_create_stats(user_id)
        current_level = stats.current_level
        current_points = stats.total_points
        
        # 获取下一级所需积分
        next_level = current_level + 1
        next_level_points = cls.LEVEL_POINTS.get(next_level, current_points)
        
        # 计算进度百分比
        if next_level <= max(cls.LEVEL_POINTS.keys()):
            current_level_points = cls.LEVEL_POINTS.get(current_level, 0)
            progress_points = current_points - current_level_points
            level_points_gap = next_level_points - current_level_points
            progress_percentage = (progress_points / level_points_gap * 100) if level_points_gap > 0 else 100
        else:
            # 已达到最高等级
            progress_percentage = 100
            next_level_points = current_points
        
        return {
            'current_level': current_level,
            'current_points': current_points,
            'next_level_points': next_level_points,
            'progress_percentage': min(progress_percentage, 100)
        }
    
    @classmethod
    def get_achievement_progress(cls, user_id):
        """获取用户成就进度"""
        stats = cls.get_or_create_stats(user_id)
        achievements = Achievement.objects.filter(is_active=True)
        progress_list = []
        
        for achievement in achievements:
            user_achievement = UserAchievement.objects.filter(
                user_id=user_id,
                achievement=achievement
            ).first()
            
            if user_achievement:
                progress = user_achievement.progress
                is_completed = user_achievement.is_completed
            else:
                # 计算当前进度
                if achievement.achievement_type == 1:  # 学习时长(小时)
                    progress = stats.total_study_time // 60
                elif achievement.achievement_type == 2:  # 课程完成
                    progress = stats.completed_courses
                elif achievement.achievement_type == 3:  # 连续学习
                    progress = stats.max_continuous_days
                elif achievement.achievement_type == 4:  # 知识探索
                    progress = stats.comments_count
                elif achievement.achievement_type == 5:  # 互动参与
                    progress = stats.favorites_count
                else:
                    progress = 0
                
                is_completed = progress >= achievement.condition_value
            
            progress_percentage = min((progress / achievement.condition_value * 100), 100)
            
            progress_list.append({
                'achievement': achievement,
                'progress': progress,
                'is_completed': is_completed,
                'progress_percentage': progress_percentage
            })
        
        return progress_list
