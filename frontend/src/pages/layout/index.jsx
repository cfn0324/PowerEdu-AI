import Header from "./header";
import Message from "../../components/message";
import { Outlet } from "react-router-dom";

import "./index.css";

const Layout = () => {
  return (
    <div>
      <Header />
      <Outlet />
      <Message />
    </div>
  );
};

export default Layout;
