import { createBrowserRouter } from "react-router-dom";
import Home from "../pages/home";
import Layout from "../pages/layout";
import Detail from "../pages/detail";
import Profile from "../pages/profile";
import Courses from "../pages/courses";
import PredictionDashboard from "../pages/prediction/PredictionDashboard";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: "course/:id",
        element: <Detail />,
      },
      {
        path: "profile/",
        element: <Profile />,
      },
      {
        path:"courses/",
        element: <Courses/>
      },
      {
        path: "prediction/",
        element: <PredictionDashboard/>
      }
    ],
  },
]);
export default router;
