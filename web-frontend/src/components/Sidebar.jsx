import { LayoutDashboard, FileText, Shield, List } from "lucide-react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 h-full 
      bg-white/70 dark:bg-gray-900/70 
      backdrop-blur-xl 
      border-r border-gray-200 dark:border-gray-800 
      p-5 shadow-sm"
    >
      <h1 className="text-2xl font-semibold mb-8 tracking-tight">
        Governance Hub
      </h1>

      <nav className="space-y-2">
        <SidebarItem icon={<LayoutDashboard size={18} />} label="Dashboard" to="/" />
        <SidebarItem icon={<FileText size={18} />} label="Data Catalog" to="/catalog" />
        <SidebarItem icon={<Shield size={18} />} label="Access Control" to="/access" />
        <SidebarItem icon={<List size={18} />} label="Audit Logs" to="/logs" />
      </nav>
    </div>
  );
}

function SidebarItem({ icon, label, to }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200 ${
          isActive
            ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow"
            : "hover:bg-gray-200 dark:hover:bg-gray-800"
        }`
      }
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </NavLink>
  );
}