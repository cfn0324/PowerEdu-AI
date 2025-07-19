from ninja import Schema
from typing import List, Optional
from datetime import datetime


class AchievementSchema(Schema):
    id: int
    name: str
    description: str
    icon: str
    achievement_type: int
    condition_value: int
    points: int
    is_active: bool


class UserAchievementSchema(Schema):
    id: int
    achievement: AchievementSchema
    unlocked_at: datetime
    progress: int
    is_completed: bool


class UserPointSchema(Schema):
    id: int
    points: int
    point_type: int
    description: str
    related_id: Optional[int]
    created_at: datetime


class StudyStatsSchema(Schema):
    id: int
    total_study_time: int
    completed_courses: int
    continuous_days: int
    max_continuous_days: int
    total_points: int
    current_level: int
    comments_count: int
    favorites_count: int
    last_study_date: Optional[str]


class AchievementProgressSchema(Schema):
    achievement: AchievementSchema
    progress: int
    is_completed: bool
    progress_percentage: float


class UserLevelSchema(Schema):
    current_level: int
    current_points: int
    next_level_points: int
    progress_percentage: float


class AchievementSummarySchema(Schema):
    stats: StudyStatsSchema
    recent_achievements: List[UserAchievementSchema]
    recent_points: List[UserPointSchema]
    achievement_progress: List[AchievementProgressSchema]
    level_info: UserLevelSchema
