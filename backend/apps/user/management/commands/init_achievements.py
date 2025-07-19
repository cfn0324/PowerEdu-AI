from django.core.management.base import BaseCommand
from apps.user.achievement_models import Achievement


class Command(BaseCommand):
    help = '初始化成就数据'

    def handle(self, *args, **options):
        achievements = [
            # 学习时长类成就
            {
                'name': '初窥门径', 
                'description': '累计学习1小时', 
                'icon': 'clock-circle',
                'achievement_type': 1, 
                'condition_value': 1, 
                'points': 20
            },
            {
                'name': '勤学苦练', 
                'description': '累计学习5小时', 
                'icon': 'clock-circle',
                'achievement_type': 1, 
                'condition_value': 5, 
                'points': 50
            },
            {
                'name': '学而时习', 
                'description': '累计学习10小时', 
                'icon': 'clock-circle',
                'achievement_type': 1, 
                'condition_value': 10, 
                'points': 100
            },
            {
                'name': '博学笃行', 
                'description': '累计学习25小时', 
                'icon': 'clock-circle',
                'achievement_type': 1, 
                'condition_value': 25, 
                'points': 200
            },
            {
                'name': '学识渊博', 
                'description': '累计学习50小时', 
                'icon': 'clock-circle',
                'achievement_type': 1, 
                'condition_value': 50, 
                'points': 300
            },
            {
                'name': '学海无涯', 
                'description': '累计学习100小时', 
                'icon': 'clock-circle',
                'achievement_type': 1, 
                'condition_value': 100, 
                'points': 500
            },
            
            # 课程完成类成就
            {
                'name': '初出茅庐', 
                'description': '完成第1门课程', 
                'icon': 'trophy',
                'achievement_type': 2, 
                'condition_value': 1, 
                'points': 50
            },
            {
                'name': '小有所成', 
                'description': '完成3门课程', 
                'icon': 'trophy',
                'achievement_type': 2, 
                'condition_value': 3, 
                'points': 100
            },
            {
                'name': '学有所成', 
                'description': '完成5门课程', 
                'icon': 'trophy',
                'achievement_type': 2, 
                'condition_value': 5, 
                'points': 200
            },
            {
                'name': '才华横溢', 
                'description': '完成10门课程', 
                'icon': 'trophy',
                'achievement_type': 2, 
                'condition_value': 10, 
                'points': 300
            },
            {
                'name': '博学大师', 
                'description': '完成20门课程', 
                'icon': 'trophy',
                'achievement_type': 2, 
                'condition_value': 20, 
                'points': 500
            },
            
            # 连续学习类成就
            {
                'name': '坚持不懈', 
                'description': '连续学习3天', 
                'icon': 'fire',
                'achievement_type': 3, 
                'condition_value': 3, 
                'points': 30
            },
            {
                'name': '持之以恒', 
                'description': '连续学习7天', 
                'icon': 'fire',
                'achievement_type': 3, 
                'condition_value': 7, 
                'points': 80
            },
            {
                'name': '锲而不舍', 
                'description': '连续学习15天', 
                'icon': 'fire',
                'achievement_type': 3, 
                'condition_value': 15, 
                'points': 150
            },
            {
                'name': '永不言弃', 
                'description': '连续学习30天', 
                'icon': 'fire',
                'achievement_type': 3, 
                'condition_value': 30, 
                'points': 300
            },
            {
                'name': '学习达人', 
                'description': '连续学习60天', 
                'icon': 'fire',
                'achievement_type': 3, 
                'condition_value': 60, 
                'points': 500
            },
            {
                'name': '学习传奇', 
                'description': '连续学习100天', 
                'icon': 'fire',
                'achievement_type': 3, 
                'condition_value': 100, 
                'points': 800
            },
            
            # 知识探索类成就
            {
                'name': '好奇宝宝', 
                'description': '发表第1条评论', 
                'icon': 'message',
                'achievement_type': 4, 
                'condition_value': 1, 
                'points': 20
            },
            {
                'name': '积极发言', 
                'description': '发表5条评论', 
                'icon': 'message',
                'achievement_type': 4, 
                'condition_value': 5, 
                'points': 50
            },
            {
                'name': '热心交流', 
                'description': '发表10条评论', 
                'icon': 'message',
                'achievement_type': 4, 
                'condition_value': 10, 
                'points': 100
            },
            
            # 互动参与类成就
            {
                'name': '收藏达人', 
                'description': '收藏5门课程', 
                'icon': 'star',
                'achievement_type': 5, 
                'condition_value': 5, 
                'points': 30
            },
            {
                'name': '收藏专家', 
                'description': '收藏10门课程', 
                'icon': 'star',
                'achievement_type': 5, 
                'condition_value': 10, 
                'points': 80
            },
        ]

        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'创建成就: {achievement.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'成就已存在: {achievement.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('成就数据初始化完成!')
        )
