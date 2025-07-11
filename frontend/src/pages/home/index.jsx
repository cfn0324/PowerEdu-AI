// src/pages/home/index.jsx
import { useEffect, useState } from "react";
import { getBanners } from "../../service";
import { Carousel } from "antd";
import { CourseList } from "../../components/course";
import "./index.css";
import { useNavigate } from "react-router-dom";
import { useTokenStore } from "../../stores";
import { getImageUrl } from "../../tools";


const Home = () => {
  const [banners, setBanners] = useState([]);
  const [randomCourses, setRandomCourses] = useState([]);
  const navigate = useNavigate();
  const { courses, getCoursesAct } = useTokenStore();

  useEffect(() => {
    async function getData() {
      const res = await getBanners();
      console.log(res.data);
      setBanners(res.data);
      getCoursesAct(null);
    }
    getData();
  }, []);

   // 随机选择5个课程
   useEffect(() => {
    if (courses.length > 0) {
      // 将课程数组随机打乱并取前五个课程
      const shuffledCourses = [...courses].sort(() => Math.random() - 0.5);
      setRandomCourses(shuffledCourses.slice(0, 5));
    }
  }, [courses]);  // 当课程列表变化时更新

  const handleClickBanner = (item) => {
    console.log(" banner click", item);
    if (item.to_id) {
      navigate("/course/" + item.to_id);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'left', width: '100%' }}>
      {/* 轮播图和文字内容 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', maxWidth: '1200px', margin: '0 auto', padding: '20px 10px' }}>
        {/* 调整轮播图宽度和左侧间距 */}
        <div style={{ width: "55%", marginLeft: '0' }}>
          <Carousel autoplay>
            {banners.map((item) => (
              <img
                className="banner"
                src={getImageUrl(item.image)}
                key={item.id}
                onClick={() => handleClickBanner(item)}
                style={{ width: '100%', height: 'auto', cursor: 'pointer' }}
              />
            ))}
          </Carousel>
        </div>
        {/* 文字内容 */}
        <div style={{ width: "40%", textAlign: 'left', color: '#0a2d5f', fontSize: '20px', lineHeight: '2', fontFamily: 'Arial, sans-serif', fontWeight: 'bold' }}>
          <p>欢迎来到电力探客平台！</p>
          <p>与全球超过 2100 万名电力行业学习者一同交流分享、实战考验，并时刻掌握最新的电力知识与技术！
          探索由社区发布的海量知识库、在线课程和互动学习资源，为您的下一个电力技术项目助力！</p>
        </div>
      </div>

      {/* 推荐课程标题 */}
      <h2 style={{ textAlign: "left", color: "#0a2d5f", margin: "20px 0", paddingLeft: "100px" }}>推荐课程</h2>

      {/* 课程列表推荐 */}
      <div style={{ display: 'flex', justifyContent: 'center', marginLeft: '100px', marginRight: '20px' }}>
        <CourseList courses={randomCourses} />
      </div>
     
    </div>
  );
};

export default Home;