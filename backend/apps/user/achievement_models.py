from django.db import models
from apps.user.models import User
from apps.course.models import Course


class Achievement(models.Model):
    """成就类型定义"""
    ACHIEVEMENT_TYPES = (
        (1, '学习时长'),
        (2, '课程完成'),
        (3, '连续学习'),
        (4, '知识探索'),
        (5, '互动参与'),
    )
    
    name = models.CharField(max_length=50, verbose_name="成就名称")
    description = models.TextField(verbose_name="成就描述")
    icon = models.CharField(max_length=50, verbose_name="图标", default="trophy")
    achievement_type = models.IntegerField(choices=ACHIEVEMENT_TYPES, verbose_name="成就类型")
    condition_value = models.IntegerField(verbose_name="达成条件数值")
    points = models.IntegerField(verbose_name="奖励积分", default=0)
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "成就"
        verbose_name_plural = "成就管理"


class UserAchievement(models.Model):
    """用户成就记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name="成就")
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="获得时间")
    progress = models.IntegerField(default=0, verbose_name="进度")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

    class Meta:
        verbose_name = "用户成就"
        verbose_name_plural = "用户成就管理"
        unique_together = ('user', 'achievement')


class UserPoints(models.Model):
    """用户积分记录"""
    POINT_TYPES = (
        (1, '学习课程'),
        (2, '完成成就'),
        (3, '连续登录'),
        (4, '评论课程'),
        (5, '分享课程'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    points = models.IntegerField(verbose_name="积分变化", help_text="正数为获得，负数为扣减")
    point_type = models.IntegerField(choices=POINT_TYPES, verbose_name="积分类型")
    description = models.CharField(max_length=200, verbose_name="描述")
    related_id = models.IntegerField(null=True, blank=True, verbose_name="关联ID", help_text="课程ID、成就ID等")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="获得时间")

    def __str__(self):
        return f"{self.user.username} {'+' if self.points > 0 else ''}{self.points}分"

    class Meta:
        verbose_name = "积分记录"
        verbose_name_plural = "积分记录管理"


class StudyStats(models.Model):
    """用户学习统计"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    total_study_time = models.IntegerField(default=0, verbose_name="总学习时长(分钟)")
    completed_courses = models.IntegerField(default=0, verbose_name="完成课程数")
    continuous_days = models.IntegerField(default=0, verbose_name="连续学习天数")
    max_continuous_days = models.IntegerField(default=0, verbose_name="最大连续学习天数")
    total_points = models.IntegerField(default=0, verbose_name="总积分")
    current_level = models.IntegerField(default=1, verbose_name="当前等级")
    comments_count = models.IntegerField(default=0, verbose_name="评论数量")
    favorites_count = models.IntegerField(default=0, verbose_name="收藏数量")
    last_study_date = models.DateField(null=True, blank=True, verbose_name="最后学习日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.user.username} - Lv.{self.current_level}"

    class Meta:
        verbose_name = "学习统计"
        verbose_name_plural = "学习统计管理"
