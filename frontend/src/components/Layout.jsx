import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function Layout() {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content p-6 md:p-8 bg-background">
        <Outlet />
      </main>
    </div>
  );
}
