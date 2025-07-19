from django.contrib import admin
from .achievement_models import Achievement, UserAchievement, UserPoints, StudyStats


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_type', 'condition_value', 'points', 'is_active']
    list_filter = ['achievement_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['achievement_type', 'condition_value']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'is_completed', 'progress', 'unlocked_at']
    list_filter = ['is_completed', 'achievement__achievement_type']
    search_fields = ['user__username', 'achievement__name']
    raw_id_fields = ['user', 'achievement']
    ordering = ['-unlocked_at']


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'point_type', 'description', 'created_at']
    list_filter = ['point_type', 'created_at']
    search_fields = ['user__username', 'description']
    raw_id_fields = ['user']
    ordering = ['-created_at']


@admin.register(StudyStats)
class StudyStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'current_level', 'completed_courses', 'total_study_time', 'continuous_days']
    list_filter = ['current_level']
    search_fields = ['user__username']
    raw_id_fields = ['user']
    readonly_fields = ['updated_at']
    ordering = ['-total_points']
