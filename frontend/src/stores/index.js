import { create } from "zustand";
import { getCourses, userLogin, userLogout, userRegister } from "../service";
import { message } from "antd";
// 持久化缓存
import { createJSONStorage, persist } from "zustand/middleware";

// init state

// 创建一个zustand store用于存储token
export const useTokenStore = create(
  persist(
    (set) => ({
      auth: null,
      courses: [],
      setAuth: (newAuth) => set({ auth: newAuth }),
      loginAct: async (payload) => {
        const res = await userLogin(payload);
        if (res.status !== 200) {
          message.error("登录出现故障");
        }
        if (res.data?.token) {
          // 登录成功
          set({ auth: res.data });
          message.success("欢迎回来！" + res.data.user.username);
          return true;
        } else {
          message.error(res.data?.msg);
        }
      },
      //注册
      registerAct: async (payload) =>{
        const res = await userRegister(payload);
        if (res.status !== 200){
          message.error("注册出现故障");
          return false;
        }
        if (res.data?.msg === "ok"){
          return true;
        }else{
          message.error(res.data?.msg);
          return false;
        }
      },
      // logout
      logoutAct: async () => {
        await userLogout();
        set({ auth: null });
        message.success("欢迎下次回来！");
      },
      //
      getCoursesAct: async (name) => {
        const res = await getCourses(name);
        if (res.data) {
          set({ courses: res.data });
        }
      },
    }),
    {
      name: "auth-storage", // 存储的键名
      sotrage: createJSONStorage(() => localStorage), // 使用localStorage进行存储
    }
  )
);
