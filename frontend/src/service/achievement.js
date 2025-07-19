import api from "./req";

// 获取用户学习统计
export function getUserStats() {
  return api({
    method: "GET",
    url: "/achievement/stats",
  });
}

// 获取用户等级信息
export function getUserLevel() {
  return api({
    method: "GET", 
    url: "/achievement/level",
  });
}

// 获取用户成就列表
export function getUserAchievements(completed = null) {
  return api({
    method: "GET",
    url: "/achievement/achievements",
    params: { completed },
  });
}

// 获取成就进度
export function getAchievementProgress() {
  return api({
    method: "GET",
    url: "/achievement/achievements/progress",
  });
}

// 获取积分记录
export function getUserPoints(limit = 20) {
  return api({
    method: "GET",
    url: "/achievement/points",
    params: { limit },
  });
}

// 获取成就总览
export function getAchievementSummary() {
  return api({
    method: "GET",
    url: "/achievement/summary",
  });
}

// 获取积分排行榜
export function getLeaderboard(limit = 10) {
  return api({
    method: "GET",
    url: "/achievement/leaderboard",
    params: { limit },
  });
}

// 记录学习行为
export function recordStudyActivity(courseId, studyMinutes = 0) {
  return api({
    method: "POST",
    url: "/achievement/study",
    params: { course_id: courseId, study_minutes: studyMinutes },
  });
}

// 标记课程完成
export function completeCourse(courseId) {
  return api({
    method: "POST",
    url: "/achievement/course/complete",
    params: { course_id: courseId },
  });
}
