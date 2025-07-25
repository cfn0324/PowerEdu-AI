import "./index.css";
import { StarOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { addActByCourseId } from "../../service";
import { message } from "antd";
import { getLevel, getImageUrl } from "../../tools";
import React,{useState} from "react";

export const CourseItem = ({ item, clickFlav, clickCourse }) => {
  const [isFavorited,setIsFavorited] = useState(false);

  const clickFlavEvent = (e, item) => {
    // 阻止事件冒泡
    e.stopPropagation();
    clickFlav(item).then((success) => {
      if (success) isFavorited ? setIsFavorited(false):setIsFavorited(true);
    });
  };

  const clickCourseEvent = (item) => {
    clickCourse(item);
  };

  return (
    <div className="course-item" onClick={() => clickCourseEvent(item)}>
      <img className="course-img" src={getImageUrl(item.image)} />
      <p className="title">{item.name}</p>
      <div className="course-data">
        <p className="level-study">
          {getLevel(item.level)} · {item.study_number}人报名
        </p>
        <p onClick={(e) => clickFlavEvent(e, item)}>
          <StarOutlined style={{ margin: "0px 3px" ,
            color:isFavorited ? "red" : "gray", //根据状态改变颜色
          }} />
          <span style={{ margin: "0px" }}>收藏</span>
        </p>
      </div>
    </div>
  );
};

export const CourseList = ({ courses }) => {
  // 课程列表
  const navigate = useNavigate();

  //   点击收藏
  const clickFlav = async (item) => {
    try{
      const res = await addActByCourseId(item.id, 2);

      if (res.data.code) {
        message.success(res.data.msg);
        return true;
      }
      return false;
    }catch(error){
      message.error("收藏失败，请稍后重试！");
      return false;
    }
  };

  const clickCourse = (item) => {
    navigate(`/course/${item.id}`);
  };

  return (
    <div className="course-list">
      {courses?.map((item) => (
        <CourseItem
          item={item}
          clickFlav={clickFlav}
          clickCourse={clickCourse}
          key={item.id}
        />
      ))}
    </div>
  );
};
