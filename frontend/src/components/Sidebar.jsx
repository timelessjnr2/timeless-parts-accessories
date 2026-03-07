import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Package,
  Users,
  FileText,
  BarChart3,
  Settings,
  Plus,
} from "lucide-react";

const LOGO_URL =
  "https://customer-assets.emergentagent.com/job_c8ea836d-f376-4793-85ac-d42fefdf5d7d/artifacts/mxjzjbvw_WhatsApp%20Image%202026-03-05%20at%204.13.42%20PM.jpeg";

const navItems = [
  { path: "/", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/inventory", icon: Package, label: "Inventory" },
  { path: "/customers", icon: Users, label: "Customers" },
  { path: "/invoices", icon: FileText, label: "Invoices" },
  { path: "/reports", icon: BarChart3, label: "Reports" },
  { path: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar fixed left-0 top-0 h-screen w-64 flex flex-col z-50">
      {/* Logo */}
      <div className="logo-container border-b border-red-700 py-4">
        <img
          src={LOGO_URL}
          alt="Timeless Auto Imports"
          className="max-w-[160px] h-auto"
          data-testid="logo"
        />
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1" data-testid="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? "active" : ""}`
            }
            data-testid={`nav-${item.label.toLowerCase()}`}
            end={item.path === "/"}
          >
            <item.icon size={20} strokeWidth={1.5} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Quick Action */}
      <div className="p-4 border-t border-red-700">
        <NavLink
          to="/invoices/create"
          className="flex items-center justify-center gap-2 w-full bg-white text-red-600 py-2.5 px-4 rounded-lg font-semibold text-sm hover:bg-red-50 transition-colors"
          data-testid="create-invoice-btn"
        >
          <Plus size={18} />
          <span>NEW INVOICE</span>
        </NavLink>
      </div>

      {/* Footer */}
      <div className="p-4 text-xs text-slate-400 text-center">
        <p>Timeless Parts & Accessories</p>
        <p className="mt-1">876-403-8436</p>
      </div>
    </aside>
  );
}
