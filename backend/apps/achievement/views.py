from ninja import Router

# 创建成就系统路由器
router = Router()


@router.get("/stats")
def get_user_stats(request):
    """获取用户统计数据"""
    # 直接返回示例数据，不检查用户认证
    return {
        'totalCourses': 12,
        'completedCourses': 8,
        'totalStudyTime': 156,
        'streakDays': 7,
        'totalPoints': 2840,
        'knowledgeUsage': 45,
        'predictionUsage': 12,
    }


@router.get("/list")
def get_user_achievements(request):
    """获取用户成就列表"""
    return [
        {
            'id': 1,
            'title': "初学者",
            'description': "完成第一门课程",
            'icon': "BookOutlined",
            'earned': True,
            'earnedDate': "2024-01-15",
            'progress': None,
            'color': "#52c41a"
        },
        {
            'id': 2,
            'title': "学霸",
            'description': "完成10门课程",
            'icon': "TrophyOutlined",
            'earned': False,
            'earnedDate': None,
            'progress': 80,
            'color': "#faad14"
        },
        {
            'id': 3,
            'title': "坚持者",
            'description': "连续学习7天",
            'icon': "FireOutlined",
            'earned': True,
            'earnedDate': "2024-07-19",
            'progress': None,
            'color': "#f5222d"
        },
        {
            'id': 4,
            'title': "时间管理大师",
            'description': "累计学习200小时",
            'icon': "ClockCircleOutlined",
            'earned': False,
            'earnedDate': None,
            'progress': 78,
            'color': "#1890ff"
        },
        {
            'id': 5,
            'title': "知识探索者",
            'description': "使用知识库问答100次",
            'icon': "StarOutlined",
            'earned': False,
            'earnedDate': None,
            'progress': 45,
            'color': "#722ed1"
        }
    ]


@router.get("/activity")
def get_user_activity(request):
    """获取用户最近活动"""
    return [
        {
            'date': '2024-07-19',
            'activity': '首次访问学习成就页面',
            'type': 'system',
            'points': 10
        },
        {
            'date': '2024-07-18',
            'activity': '开始使用PowerEdu-AI平台',
            'type': 'system',
            'points': 20
        },
        {
            'date': '2024-07-17',
            'activity': '完成课程：电力系统基础',
            'type': 'course_complete',
            'points': 100
        },
        {
            'date': '2024-07-16',
            'activity': '使用AI预测功能',
            'type': 'prediction_usage',
            'points': 20
        }
    ]


@router.post("/progress")
def update_learning_progress(request):
    """更新学习进度"""
    return {'message': '进度更新成功'}
