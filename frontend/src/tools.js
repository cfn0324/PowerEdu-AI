// 请求host更换 - 自动检测环境
export const host = process.env.NODE_ENV === 'production' 
  ? (window.location.protocol + '//' + window.location.host)  // 生产环境使用当前域名
  : "http://localhost:8000";  // 开发环境使用localhost

const levelMap = {
  1: "高级",
  2: "中级",
  3: "初级",
};

export function getLevel(key) {
  return levelMap[key];
}

export function getImageUrl(image) {
  return `${host}${image}`;
}
