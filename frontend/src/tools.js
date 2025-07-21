// 请求host更换 - 自动检测环境
export const host = process.env.NODE_ENV === 'production' 
  ? (window.location.protocol + '//' + window.location.host)  // 生产环境使用当前域名
  : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
    ? "http://localhost:8000"  // 本地开发环境
    : (window.location.protocol + '//' + window.location.hostname + ':8000');  // 服务器开发环境

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
