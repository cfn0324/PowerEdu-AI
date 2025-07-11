import { Card, Avatar, Form, Input, Button, message } from "antd";
import { useTokenStore } from "../../stores";
import { addComment, getConmentsByCourseId } from "../../service"; // 确保有 getComments 函数
import { getImageUrl } from "../../tools";
import { useState, useEffect } from "react";

const { TextArea } = Input;
const { Meta } = Card;

const CommentList = ({ course }) => {
  const { auth } = useTokenStore();
  const [comments, setComments] = useState([]);
  
  // 获取评论列表数据
  const fetchComments = async () => {
    const res = await getConmentsByCourseId(course.id); // 假设你有一个 API 方法来获取评论列表
    if (res.data) {
      setComments(res.data); // 更新评论数据
    }
  };
  const [form] = Form.useForm();
  // 初始化加载评论
  useEffect(() => {
    fetchComments();
  }, [course.id]); // 依赖项为 course.id，当课程变化时重新加载评论

  
  // 提交评论
  const onFinish = async (values) => {
    values["course_id"] = course.id;
    const res = await addComment(values);
    if (res.data.msg) {
      message.success("评论成功");
      fetchComments(); // 评论成功后重新加载评论
      form.resetFields();
    }
  };

  return (
    <>
      {/* 新增评论表单 */}
      <Form form={form} onFinish={onFinish}>
        <Form.Item
          name="content"
          rules={[{ required: true, message: "好像忘记留下些什么了" }]}
        >
          <TextArea rows={4} placeholder="留言..." />
        </Form.Item>
        <Form.Item>
          <Button
            htmlType="submit"
            style={{ float: "right" }}
            type="primary"
            disabled={!auth?.user}
          >
            {auth?.user ? "评论" : "请登录"}
          </Button>
        </Form.Item>
      </Form>

      {/* 评论列表 */}
      {comments.map((item) => (
        <Card className="wrap" style={{ width: "100%", marginTop: 16 }} key={item.id}>
          <Meta
            avatar={<Avatar src={getImageUrl(item.user.avatar)} />}
            title={item.user.username}
            description={item.content}
          />
        </Card>
      ))}
    </>
  );
};

export default CommentList;
