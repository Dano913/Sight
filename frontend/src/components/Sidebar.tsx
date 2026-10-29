import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ChartColumn,
  Globe,
  Scale,
  Database,
  Settings,
} from "lucide-react";

const NAVIGATION = [
  {
    path: "/",
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    path: "/indicators",
    label: "Indicators",
    icon: ChartColumn,
  },
  {
    path: "/countries",
    label: "Countries",
    icon: Globe,
  },
  {
    path: "/compare",
    label: "Compare",
    icon: Scale,
  },
  {
    path: "/sources",
    label: "Sources",
    icon: Database,
  },
  {
    path: "/settings",
    label: "Settings",
    icon: Settings,
  },
];

function SideSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          color: "#94a3b8",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          padding: "10px 16px 8px",
        }}
      >
        {title}
      </div>

      {children}
    </div>
  );
}

function SideLink({
  to,
  icon: Icon,
  children,
}: {
  to: string;
  icon: React.ElementType;
  children: React.ReactNode;
}) {
  return (
    <NavLink
      to={to}
      style={({ isActive }) => ({
        display: "flex",
        alignItems: "center",
        gap: 12,
        margin: "4px 8px",
        padding: "10px 12px",
        borderRadius: 10,
        textDecoration: "none",
        fontSize: 14,
        fontWeight: isActive ? 600 : 500,
        color: isActive ? "#2563eb" : "#475569",
        background: isActive ? "#eff6ff" : "transparent",
        transition: "0.15s ease",
      })}
    >
      <Icon size={18} />
      <span>{children}</span>
    </NavLink>
  );
}

export default function Sidebar() {
  return (
    <aside
      style={{
        position: "fixed",
        top: 60,
        left: 0,
        bottom: 0,
        width: 240,
        background: "#1b2a39",
        borderRight: "1px solid #1b2a39",
        paddingTop: 20,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <SideSection title="Navigation">
        {NAVIGATION.map((item) => (
          <SideLink
            key={item.path}
            to={item.path}
            icon={item.icon}
          >
            {item.label}
          </SideLink>
        ))}
      </SideSection>

      <div style={{ flex: 1 }} />
    </aside>
  );
}