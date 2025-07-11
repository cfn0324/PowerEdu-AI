import { useEffect, useState } from "react";
import { CourseList } from "../../components/course";  // 假设您已有 CourseList 组件
import { useTokenStore } from "../../stores";
import "./index.css";

const Courses = () => {
  const { courses, getCoursesAct } = useTokenStore(); // 从状态管理获取课程数据
  const [loading, setLoading] = useState(true);  // 用于显示加载状态

  useEffect(() => {
    async function fetchCourses() {
      setLoading(true);
      // 你可以通过 getCoursesAct 获取课程数据，如果是从 API 获取数据，类似上面 Home 页面的方式
      await getCoursesAct(null);  // 传递 null 以获取所有课程
      setLoading(false);  // 数据获取完毕，停止加载状态
    }
    fetchCourses();
  }, [getCoursesAct]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'left', width: '100%' }}>
      {/* 页面标题 */}
      <h2 style={{ textAlign: "left", color: "#0a2d5f", margin: "20px 0", paddingLeft: "100px" }}>
        所有课程
      </h2>

      {/* 课程列表 */}
      <div style={{ display: 'flex', justifyContent: 'center', marginLeft: '100px', marginRight: '20px' }}>
        {loading ? (
          <p>加载中...</p>  // 显示加载状态
        ) : (
          <CourseList courses={courses} />  // 渲染课程列表
        )}
      </div>
    </div>
  );
};

export default Courses;
