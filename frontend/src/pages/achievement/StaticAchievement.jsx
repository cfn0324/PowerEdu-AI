import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Progress, 
  List, 
  Avatar, 
  Tag, 
  Tabs, 
  Badge,
  Timeline,
  Tooltip,
  Button,
  message
} from 'antd';
import {
  TrophyOutlined,
  FireOutlined,
  ClockCircleOutlined,
  StarOutlined,
  MessageOutlined,
  CrownOutlined,
  GiftOutlined,
  RiseOutlined,
  BookOutlined,
  TeamOutlined
} from '@ant-design/icons';
import './index.css';

const { TabPane } = Tabs;

// 静态模拟数据
const mockData = {
  stats: {
    total_study_time: 720, // 分钟
    completed_courses: 5,
    continuous_days: 7,
    total_points: 850,
    comments_count: 12,
    favorites_count: 8
  },
  level_info: {
    current_level: 3,
    current_points: 850,
    next_level_points: 1000,
    progress_percentage: 75
  },
  achievement_progress: [
    {
      achievement: {
        id: 1,
        name: '初窥门径',
        description: '累计学习1小时',
        icon: 'clock-circle',
        achievement_type: 1,
        condition_value: 1,
        points: 20
      },
      progress: 12,
      is_completed: true,
      progress_percentage: 100
    },
    {
      achievement: {
        id: 2,
        name: '勤学苦练',
        description: '累计学习5小时',
        icon: 'clock-circle',
        achievement_type: 1,
        condition_value: 5,
        points: 50
      },
      progress: 12,
      is_completed: true,
      progress_percentage: 100
    },
    {
      achievement: {
        id: 3,
        name: '学而时习',
        description: '累计学习10小时',
        icon: 'clock-circle',
        achievement_type: 1,
        condition_value: 10,
        points: 100
      },
      progress: 12,
      is_completed: true,
      progress_percentage: 100
    },
    {
      achievement: {
        id: 4,
        name: '博学笃行',
        description: '累计学习25小时',
        icon: 'clock-circle',
        achievement_type: 1,
        condition_value: 25,
        points: 200
      },
      progress: 12,
      is_completed: false,
      progress_percentage: 48
    },
    {
      achievement: {
        id: 5,
        name: '初级完成者',
        description: '完成1门课程',
        icon: 'trophy',
        achievement_type: 2,
        condition_value: 1,
        points: 100
      },
      progress: 5,
      is_completed: true,
      progress_percentage: 100
    },
    {
      achievement: {
        id: 6,
        name: '学习达人',
        description: '完成3门课程',
        icon: 'trophy',
        achievement_type: 2,
        condition_value: 3,
        points: 200
      },
      progress: 5,
      is_completed: true,
      progress_percentage: 100
    },
    {
      achievement: {
        id: 7,
        name: '连续学习3天',
        description: '保持连续学习3天',
        icon: 'fire',
        achievement_type: 3,
        condition_value: 3,
        points: 50
      },
      progress: 7,
      is_completed: true,
      progress_percentage: 100
    },
    {
      achievement: {
        id: 8,
        name: '连续学习7天',
        description: '保持连续学习7天',
        icon: 'fire',
        achievement_type: 3,
        condition_value: 7,
        points: 100
      },
      progress: 7,
      is_completed: true,
      progress_percentage: 100
    }
  ],
  recent_achievements: [
    {
      achievement: {
        name: '连续学习7天',
        description: '保持连续学习7天',
        icon: 'fire',
        points: 100
      },
      unlocked_at: '2025-07-19T10:30:00Z'
    },
    {
      achievement: {
        name: '学习达人',
        description: '完成3门课程',
        icon: 'trophy',
        points: 200
      },
      unlocked_at: '2025-07-18T15:20:00Z'
    },
    {
      achievement: {
        name: '学而时习',
        description: '累计学习10小时',
        icon: 'clock-circle',
        points: 100
      },
      unlocked_at: '2025-07-17T09:15:00Z'
    }
  ],
  points_history: [
    {
      points: 100,
      description: '连续学习7天奖励',
      point_type: 3,
      created_at: '2025-07-19T10:30:00Z'
    },
    {
      points: 20,
      description: '学习 30 分钟',
      point_type: 1,
      created_at: '2025-07-19T09:00:00Z'
    },
    {
      points: 200,
      description: '解锁成就: 学习达人',
      point_type: 2,
      created_at: '2025-07-18T15:20:00Z'
    },
    {
      points: 15,
      description: '学习 25 分钟',
      point_type: 1,
      created_at: '2025-07-18T14:30:00Z'
    },
    {
      points: 10,
      description: '发表课程评论',
      point_type: 4,
      created_at: '2025-07-18T11:45:00Z'
    }
  ],
  leaderboard: [
    {
      rank: 1,
      username: 'admin',
      nickname: 'PowerEdu管理员',
      total_points: 850,
      current_level: 3,
      completed_courses: 5,
      study_time_hours: 12
    },
    {
      rank: 2,
      username: 'student1',
      nickname: '电力学习者',
      total_points: 720,
      current_level: 2,
      completed_courses: 3,
      study_time_hours: 8
    },
    {
      rank: 3,
      username: 'student2',
      nickname: '知识探索者',
      total_points: 650,
      current_level: 2,
      completed_courses: 4,
      study_time_hours: 10
    }
  ]
};

// 图标映射
const iconMap = {
  'trophy': <TrophyOutlined />,
  'fire': <FireOutlined />,
  'clock-circle': <ClockCircleOutlined />,
  'star': <StarOutlined />,
  'message': <MessageOutlined />,
  'crown': <CrownOutlined />,
  'gift': <GiftOutlined />,
  'book': <BookOutlined />,
  'team': <TeamOutlined />
};

// 成就类型映射
const achievementTypeMap = {
  1: { name: '学习时长', color: '#1890ff' },
  2: { name: '课程完成', color: '#52c41a' },
  3: { name: '连续学习', color: '#fa541c' },
  4: { name: '知识探索', color: '#722ed1' },
  5: { name: '互动参与', color: '#eb2f96' },
};

// 积分类型映射
const pointTypeMap = {
  1: { name: '学习课程', color: '#1890ff' },
  2: { name: '完成成就', color: '#52c41a' },
  3: { name: '连续登录', color: '#fa541c' },
  4: { name: '评论课程', color: '#722ed1' },
  5: { name: '分享课程', color: '#eb2f96' },
};

const StaticAchievement = () => {
  const [activeTab, setActiveTab] = useState('overview');

  // 用户等级进度组件
  const LevelProgress = () => (
    <Card className="level-card">
      <div className="level-content">
        <div className="level-info">
          <div className="level-badge">
            <CrownOutlined style={{ fontSize: '24px', color: '#ffa940' }} />
            <span className="level-text">Lv.{mockData.level_info.current_level}</span>
          </div>
          <div className="level-points">
            <span className="current-points">{mockData.level_info.current_points}</span>
            <span className="separator"> / </span>
            <span className="next-points">{mockData.level_info.next_level_points}</span>
          </div>
        </div>
        <Progress
          percent={mockData.level_info.progress_percentage}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          showInfo={false}
        />
        <div className="level-desc">
          距离下一级还需 {mockData.level_info.next_level_points - mockData.level_info.current_points} 积分
        </div>
      </div>
    </Card>
  );

  // 统计卡片组件
  const StatsCards = () => (
    <Row gutter={[16, 16]}>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic
            title="学习时长"
            value={Math.floor(mockData.stats.total_study_time / 60)}
            suffix="小时"
            prefix={<ClockCircleOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic
            title="完成课程"
            value={mockData.stats.completed_courses}
            suffix="门"
            prefix={<TrophyOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic
            title="连续学习"
            value={mockData.stats.continuous_days}
            suffix="天"
            prefix={<FireOutlined />}
            valueStyle={{ color: '#fa541c' }}
          />
        </Card>
      </Col>
      <Col xs={12} sm={6}>
        <Card>
          <Statistic
            title="总积分"
            value={mockData.stats.total_points}
            prefix={<StarOutlined />}
            valueStyle={{ color: '#722ed1' }}
          />
        </Card>
      </Col>
    </Row>
  );

  // 成就进度组件
  const AchievementProgress = () => (
    <Card title="成就进度" className="achievement-progress-card">
      <Row gutter={[16, 16]}>
        {mockData.achievement_progress.map((item, index) => (
          <Col xs={24} sm={12} md={8} lg={6} key={index}>
            <Card 
              size="small" 
              className={`achievement-item ${item.is_completed ? 'completed' : ''}`}
            >
              <div className="achievement-header">
                <div className="achievement-icon">
                  {iconMap[item.achievement.icon] || <TrophyOutlined />}
                </div>
                <div className="achievement-info">
                  <div className="achievement-name">{item.achievement.name}</div>
                  <Tag 
                    color={achievementTypeMap[item.achievement.achievement_type]?.color}
                    size="small"
                  >
                    {achievementTypeMap[item.achievement.achievement_type]?.name}
                  </Tag>
                </div>
              </div>
              <div className="achievement-desc">{item.achievement.description}</div>
              <div className="achievement-progress">
                <Progress
                  percent={item.progress_percentage}
                  size="small"
                  status={item.is_completed ? 'success' : 'active'}
                  format={() => `${item.progress}/${item.achievement.condition_value}`}
                />
              </div>
              <div className="achievement-points">
                <GiftOutlined /> {item.achievement.points} 积分
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  );

  // 最近成就组件
  const RecentAchievements = () => (
    <Card title="最近获得的成就" className="recent-achievements-card">
      <List
        dataSource={mockData.recent_achievements}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <Badge dot={true}>
                  <Avatar 
                    size="large" 
                    style={{ 
                      backgroundColor: '#52c41a'
                    }}
                    icon={iconMap[item.achievement.icon] || <TrophyOutlined />}
                  />
                </Badge>
              }
              title={item.achievement.name}
              description={
                <div>
                  <div>{item.achievement.description}</div>
                  <div style={{ marginTop: '4px', fontSize: '12px', color: '#999' }}>
                    {new Date(item.unlocked_at).toLocaleString()} · +{item.achievement.points} 积分
                  </div>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );

  // 积分历史组件
  const PointsHistory = () => (
    <Card title="积分历史" className="points-history-card">
      <Timeline>
        {mockData.points_history.map((item, index) => (
          <Timeline.Item
            key={index}
            dot={
              <div 
                className="points-dot"
                style={{ 
                  backgroundColor: item.points > 0 ? '#52c41a' : '#ff4d4f',
                  color: 'white'
                }}
              >
                {item.points > 0 ? '+' : ''}{item.points}
              </div>
            }
          >
            <div className="points-item">
              <div className="points-desc">{item.description}</div>
              <div className="points-meta">
                <Tag color={pointTypeMap[item.point_type]?.color} size="small">
                  {pointTypeMap[item.point_type]?.name}
                </Tag>
                <span className="points-time">
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    </Card>
  );

  // 排行榜组件
  const Leaderboard = () => (
    <Card title="积分排行榜" className="leaderboard-card">
      <List
        dataSource={mockData.leaderboard}
        renderItem={(item, index) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <div className={`rank-badge rank-${item.rank <= 3 ? item.rank : 'other'}`}>
                  {item.rank <= 3 ? (
                    <CrownOutlined />
                  ) : (
                    item.rank
                  )}
                </div>
              }
              title={
                <div className="leaderboard-title">
                  <span className="username">{item.nickname}</span>
                  <Tag color="gold">Lv.{item.current_level}</Tag>
                </div>
              }
              description={
                <div className="leaderboard-desc">
                  <div>总积分: {item.total_points}</div>
                  <div>完成课程: {item.completed_courses}门 · 学习时长: {item.study_time_hours}小时</div>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );

  const handleDataRefresh = () => {
    message.success('静态演示数据已刷新');
  };

  return (
    <div className="achievement-page" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#0a2d5f' }}>
          <TrophyOutlined style={{ marginRight: '8px' }} />
          学习成就 (静态演示)
        </h2>
        <Button 
          type="primary" 
          icon={<RiseOutlined />} 
          onClick={handleDataRefresh}
        >
          刷新数据
        </Button>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} type="card">
        <TabPane tab="成就总览" key="overview">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={8}>
              <LevelProgress />
            </Col>
            <Col xs={24} lg={16}>
              <StatsCards />
            </Col>
          </Row>

          <div style={{ marginTop: '20px' }}>
            <AchievementProgress />
          </div>
        </TabPane>

        <TabPane tab="成就记录" key="achievements">
          <RecentAchievements />
        </TabPane>

        <TabPane tab="积分历史" key="points">
          <PointsHistory />
        </TabPane>

        <TabPane tab="排行榜" key="leaderboard">
          <Leaderboard />
        </TabPane>
      </Tabs>
    </div>
  );
};

export default StaticAchievement;
