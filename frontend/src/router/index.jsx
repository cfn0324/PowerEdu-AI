import { createBrowserRouter } from "react-router-dom";
import Home from "../pages/home";
import Layout from "../pages/layout";
import Detail from "../pages/detail";
import Profile from "../pages/profile";
import Courses from "../pages/courses";
import PredictionDashboard from "../pages/prediction/PredictionDashboard";
import KnowledgeHome from "../pages/knowledge";
import KnowledgeChat from "../pages/knowledge/Chat";
import DocumentManage from "../pages/knowledge/DocumentManage";
import DocumentDetail from "../pages/knowledge/DocumentDetail";
import KnowledgeDetail from "../pages/knowledge/KnowledgeDetail";
import ModelSettings from "../pages/knowledge/ModelSettings";
import ConnectionTest from "../pages/knowledge/ConnectionTest";
import Login from "../pages/login";

const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
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
      },
      {
        path: "knowledge/",
        element: <KnowledgeHome/>
      },
      {
        path: "knowledge/settings",
        element: <ModelSettings/>
      },
      {
        path: "knowledge/test",
        element: <ConnectionTest/>
      },
      {
        path: "knowledge/detail/:kbId",
        element: <KnowledgeDetail/>
      },
      {
        path: "knowledge/documents/:kbId",
        element: <DocumentManage/>
      },
      {
        path: "knowledge/document/:docId",
        element: <DocumentDetail/>
      },
      {
        path: "knowledge/chat/:kbId",
        element: <KnowledgeChat/>
      }
    ],
  },
]);
export default router;
