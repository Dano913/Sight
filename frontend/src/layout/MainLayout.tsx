import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

const SIDEBAR_WIDTH = 240;

export default function MainLayout() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#1b2a39",
        fontFamily: "var(--font-sans)",
      }}
    >
      <Navbar />
      <Sidebar />

      <main
        style={{
          marginTop: 60,
          marginLeft: SIDEBAR_WIDTH,
          minHeight: "calc(100vh - 60px)",
          padding: "32px",
          boxSizing: "border-box",
        }}
      >
        <Outlet />
      </main>

      <style>{`
        @media (max-width: 1024px) {
          main {
            margin-left: 0 !important;
            padding: 24px 16px 48px !important;
          }
        }
      `}</style>
    </div>
  );
}