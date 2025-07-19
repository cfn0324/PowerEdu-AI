import { Input, Avatar, message } from "antd";
import { useTokenStore } from "../../stores";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import LoginModal from "../../components/login";
import { getImageUrl } from "../../tools";

const { Search } = Input;

const Header = () => {
  const { auth, loginAct, logoutAct, getCoursesAct,registerAct} = useTokenStore();

  const location = useLocation();

  const [showLogin, setShowLogin] = useState(false);

  const onSearch = (value) => {
    if (!value) {
      return;
    }
    if (location.pathname != "/" && location.pathname != "/courses") {
      message.warning("当前页面无法搜索");
      return;
    }

    getCoursesAct(value);
  };
  const navigate = useNavigate();

  const handleLogin = async (values) => {
    const result = await loginAct(values);
    if (result) {
      setShowLogin(false);
    }
  };

  const handleRegister = async (values) =>{
    if (values.password !== values.confirmPassword){
      message.error("两次输入的密码不一致！");
      return ;
    }
    const result = await registerAct({
      username:values.username,
      password:values.password,
    });
    console.log(result);
    if(result){
      message.success("注册成功！请登录");
      setShowLogin(false);
    }else{
      message.error("注册失败，请重试！");
    }
  };
  return (
    <div className="layout-header">
      <div className="header-left">
        <Link to="/"style={{ color: 'white' ,paddingLeft: "30px" }}>VOLTX
        <ul style={{ display: 'inline-flex', gap: '100px',marginLeft: "100px" ,listStyleType: 'none'}}>
          <li>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>首页</Link>
          </li>
          <li>
            <Link to="/knowledge" style={{ textDecoration: 'none', color: 'inherit' }}>知识库</Link>
          </li>
          <li>
            <Link to="/courses" style={{ textDecoration: 'none', color: 'inherit' }}>在线课程</Link>
          </li>
          <li>
            <Link to="/prediction" style={{ textDecoration: 'none', color: 'inherit' }}>AI预测</Link>
          </li>
          <li>学习成就</li>
          <li>
            <Link to="/profile" style={{ textDecoration: 'none', color: 'inherit' }}>用户中心</Link>
          </li>
        </ul>
        </Link>
      </div>
      <Search placeholder="搜索" onSearch={onSearch} style={{ width: 200 }} />
      <div className="header-right">
        {auth ? (
          <div>
            <Avatar
              size={30}
              src={getImageUrl(auth.user.avatar)}
              onClick={() => navigate("/profile")}
            />
            <span onClick={async () => await logoutAct()}>退出</span>
          </div>
        ) : (
          <span onClick={() => setShowLogin(true)}>登录</span>
        )}
      </div>
      <LoginModal
        open={showLogin}
        close={() => setShowLogin(false)}
        login={handleLogin}
        register={handleRegister}
      />
    </div>
  );
};

export default Header;
