import React, { useState, useEffect } from 'react';
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
  Empty,
  Spin,
  Button,
  message,
  Switch,
  Alert
} from 'antd';
import {
  TrophyOutlined,
  FireOutlined,
  ClockCircleOutlined,
  StarOutlined,
  MessageOutlined,
  CrownOutlined,
  GiftOutlined,
  RiseOutlined
} from '@ant-design/icons';
import { getAchievementSummary, getLeaderboard, getUserPoints } from '../../service';
import { useAuth } from '../../hooks/useAuthGuard';
import LoginPrompt from '../../components/common/LoginPrompt';
import { useNavigate } from 'react-router-dom';
import StaticAchievement from './StaticAchievement';
import './index.css';

const { TabPane } = Tabs;

// 图标映射
const iconMap = {
  'trophy': <TrophyOutlined />,
  'fire': <FireOutlined />,
  'clock-circle': <ClockCircleOutlined />,
  'star': <StarOutlined />,
  'message': <MessageOutlined />,
  'crown': <CrownOutlined />,
  'gift': <GiftOutlined />,
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

const Achievement = () => {
  const [loading, setLoading] = useState(true);
  const [summaryData, setSummaryData] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [pointsHistory, setPointsHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [useStaticMode, setUseStaticMode] = useState(false);
  
  // 获取认证状态
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // 检查登录状态
    if (!isAuthenticated) {
      return; // 让组件渲染处理未登录状态
    }
    
    // 只有在非静态模式下才加载数据
    if (!useStaticMode) {
      loadData();
    }
  }, [isAuthenticated, useStaticMode]);

  const loadData = async () => {
    // 再次检查认证状态
    if (!isAuthenticated) {
      return;
    }
    
    try {
      setLoading(true);
      console.log('开始加载成就数据...');
      
      // 分步加载数据，便于调试
      let summaryRes, leaderboardRes, pointsRes;
      
      try {
        console.log('加载成就总览...');
        summaryRes = await getAchievementSummary();
        console.log('成就总览响应:', summaryRes);
      } catch (err) {
        console.error('加载成就总览失败:', err);
        throw new Error('成就总览加载失败: ' + err.message);
      }
      
      try {
        console.log('加载排行榜...');
        leaderboardRes = await getLeaderboard(10);
        console.log('排行榜响应:', leaderboardRes);
      } catch (err) {
        console.error('加载排行榜失败:', err);
        // 排行榜失败不影响主要功能
        leaderboardRes = { data: [] };
      }
      
      try {
        console.log('加载积分记录...');
        pointsRes = await getUserPoints(20);
        console.log('积分记录响应:', pointsRes);
      } catch (err) {
        console.error('加载积分记录失败:', err);
        // 积分记录失败不影响主要功能
        pointsRes = { data: [] };
      }

      // 设置数据
      if (summaryRes?.data) {
        console.log('设置成就总览数据:', summaryRes.data);
        setSummaryData(summaryRes.data);
      } else {
        console.warn('成就总览数据为空');
        throw new Error('成就总览数据为空');
      }
      
      if (leaderboardRes?.data) {
        setLeaderboard(leaderboardRes.data);
      }
      
      if (pointsRes?.data) {
        setPointsHistory(pointsRes.data);
      }
      
      console.log('成就数据加载完成');
      
    } catch (error) {
      console.error('加载数据失败:', error);
      if (error.response?.status === 401) {
        message.error('登录已过期，请重新登录');
        navigate('/');
      } else if (error.response?.status === 404) {
        message.error('成就系统未初始化，请联系管理员');
      } else {
        message.error('加载数据失败: ' + (error.message || '未知错误'));
      }
    } finally {
      setLoading(false);
    }
  };

  // 如果启用静态模式，直接返回静态组件
  if (useStaticMode) {
    return (
      <div style={{ padding: '20px' }}>
        <div style={{ marginBottom: '16px' }}>
          <Alert
            message="静态演示模式"
            description="当前使用静态数据展示成就系统功能，您可以切换到动态模式尝试连接后端API。"
            type="info"
            showIcon
            action={
              <Switch
                checked={useStaticMode}
                onChange={(checked) => {
                  setUseStaticMode(checked);
                  if (!checked) {
                    setLoading(true);
                    loadData();
                  }
                }}
                checkedChildren="静态"
                unCheckedChildren="动态"
              />
            }
          />
        </div>
        <StaticAchievement />
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  // 未登录状态
  if (!isAuthenticated) {
    return (
      <LoginPrompt 
        title="查看学习成就需要登录"
        description="登录后可以查看您的学习统计、成就进度和积分排行"
        buttonText="返回首页"
        extra={
          <Button onClick={() => window.location.reload()}>
            刷新页面
          </Button>
        }
      />
    );
  }

  if (!summaryData) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Empty 
          description={
            <div>
              <p>成就系统暂无数据</p>
              <p style={{ fontSize: '12px', color: '#999' }}>
                如果您是管理员，请确保已运行: python manage.py init_achievements
              </p>
            </div>
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <div style={{ marginTop: '16px' }}>
            <Button type="primary" onClick={() => window.location.reload()} style={{ marginRight: '8px' }}>
              重新加载
            </Button>
            <Button onClick={() => setUseStaticMode(true)}>
              使用静态演示
            </Button>
          </div>
        </Empty>
      </div>
    );
  }

  // 用户等级进度组件
  const LevelProgress = () => {
    if (!summaryData?.level_info) {
      return <Card><Empty description="等级信息加载中..." image={Empty.PRESENTED_IMAGE_SIMPLE} /></Card>;
    }
    
    return (
      <Card className="level-card">
        <div className="level-content">
          <div className="level-info">
            <div className="level-badge">
              <CrownOutlined style={{ fontSize: '24px', color: '#ffa940' }} />
              <span className="level-text">Lv.{summaryData.level_info.current_level}</span>
            </div>
            <div className="level-points">
              <span className="current-points">{summaryData.level_info.current_points}</span>
              <span className="separator"> / </span>
              <span className="next-points">{summaryData.level_info.next_level_points}</span>
            </div>
          </div>
          <Progress
            percent={summaryData.level_info.progress_percentage}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
            showInfo={false}
          />
          <div className="level-desc">
            距离下一级还需 {summaryData.level_info.next_level_points - summaryData.level_info.current_points} 积分
          </div>
        </div>
      </Card>
    );
  };

  // 统计卡片组件
  const StatsCards = () => {
    if (!summaryData?.stats) {
      return <Empty description="统计数据加载中..." image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    }
    
    return (
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="学习时长"
              value={Math.floor((summaryData.stats.total_study_time || 0) / 60)}
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
              value={summaryData.stats.completed_courses || 0}
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
              value={summaryData.stats.continuous_days || 0}
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
              value={summaryData.stats.total_points || 0}
              prefix={<StarOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  // 成就进度组件
  const AchievementProgress = () => {
    if (!summaryData?.achievement_progress) {
      return <Card title="成就进度"><Empty description="成就进度加载中..." image={Empty.PRESENTED_IMAGE_SIMPLE} /></Card>;
    }
    
    return (
      <Card title="成就进度" className="achievement-progress-card">
        <Row gutter={[16, 16]}>
          {summaryData.achievement_progress.map((item, index) => (
            <Col xs={24} sm={12} md={8} lg={6} key={index}>
              <Card 
                size="small" 
                className={`achievement-item ${item.is_completed ? 'completed' : ''}`}
              >
                <div className="achievement-header">
                  <div className="achievement-icon">
                    {iconMap[item.achievement?.icon] || <TrophyOutlined />}
                  </div>
                  <div className="achievement-info">
                    <div className="achievement-name">{item.achievement?.name || '未知成就'}</div>
                    <Tag 
                      color={achievementTypeMap[item.achievement?.achievement_type]?.color || 'default'}
                      size="small"
                    >
                      {achievementTypeMap[item.achievement?.achievement_type]?.name || '未知类型'}
                    </Tag>
                  </div>
                </div>
                <div className="achievement-desc">{item.achievement?.description || '暂无描述'}</div>
                <div className="achievement-progress">
                  <Progress
                    percent={item.progress_percentage || 0}
                    size="small"
                    status={item.is_completed ? 'success' : 'active'}
                    format={() => `${item.progress || 0}/${item.achievement?.condition_value || 0}`}
                  />
                </div>
                <div className="achievement-points">
                  <GiftOutlined /> {item.achievement?.points || 0} 积分
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>
    );
  };

  // 最近成就组件
  const RecentAchievements = () => (
    <Card title="最近获得的成就" className="recent-achievements-card">
      {summaryData.recent_achievements.length > 0 ? (
        <List
          dataSource={summaryData.recent_achievements}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <Badge dot={true}>
                    <Avatar 
                      size="large" 
                      style={{ 
                        backgroundColor: achievementTypeMap[item.achievement.achievement_type]?.color 
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
      ) : (
        <Empty description="暂无成就记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Card>
  );

  // 积分历史组件
  const PointsHistory = () => (
    <Card title="积分历史" className="points-history-card">
      {pointsHistory.length > 0 ? (
        <Timeline>
          {pointsHistory.map((item, index) => (
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
      ) : (
        <Empty description="暂无积分记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Card>
  );

  // 排行榜组件
  const Leaderboard = () => (
    <Card title="积分排行榜" className="leaderboard-card">
      {leaderboard.length > 0 ? (
        <List
          dataSource={leaderboard}
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
      ) : (
        <Empty description="暂无排行榜数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Card>
  );

  return (
    <div className="achievement-page" style={{ padding: '20px' }}>
      <div style={{ marginBottom: '16px' }}>
        <Alert
          message="动态数据模式"
          description="当前连接后端API加载真实数据。如果遇到问题，可以切换到静态演示模式。"
          type="success"
          showIcon
          action={
            <Switch
              checked={useStaticMode}
              onChange={(checked) => setUseStaticMode(checked)}
              checkedChildren="静态"
              unCheckedChildren="动态"
            />
          }
        />
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: '#0a2d5f' }}>
          <TrophyOutlined style={{ marginRight: '8px' }} />
          学习成就
        </h2>
        <Button 
          type="primary" 
          icon={<RiseOutlined />} 
          onClick={loadData}
          loading={loading}
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

export default Achievement;
