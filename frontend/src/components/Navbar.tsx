import { NavLink } from "react-router-dom";
import {
  Search,
  Moon,
  Bell,
} from "lucide-react";

export default function Navbar() {
  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        height: 60,
        background: "#1b2a39",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderBottom: "1px solid #1b2a39",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 24px",
      }}
    >
      {/* Logo */}
      <NavLink
        to="/"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          textDecoration: "none",
        }}
      >
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: 10,
            background: "linear-gradient(135deg,#2563eb,#1d4ed8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: 700,
          }}
        >
          S
        </div>

        <span
          style={{
            fontSize: 18,
            fontWeight: 700,
            color: "#0f172a",
          }}
        >
          Sight
        </span>
      </NavLink>

      {/* Global Search */}
      <div
        style={{
          position: "relative",
          width: 360,
          maxWidth: "40%",
        }}
      >
        <Search
          size={16}
          style={{
            position: "absolute",
            left: 12,
            top: "50%",
            transform: "translateY(-50%)",
            color: "#1b2a39",
          }}
        />

        <input
          placeholder="Search..."
          style={{
            width: "100%",
            padding: "5px 5px 5px 38px",
            borderRadius: 10,
            border: "1px solid #e2e8f0",
            background: "#1b2a39",
            outline: "none",
            fontSize: 14,
          }}
        />
      </div>

      {/* Right */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
        }}
      >
        <span
          style={{
            fontSize: 12,
            color: "#64748b",
          }}
        >
          Updated Jul 31, 2026
        </span>

        <Moon
          size={19}
          style={{
            cursor: "pointer",
            color: "#64748b",
          }}
        />

        <Bell
          size={19}
          style={{
            cursor: "pointer",
            color: "#64748b",
          }}
        />

        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: "50%",
            background: "#2563eb",
            color: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          D
        </div>
      </div>
    </header>
  );
}