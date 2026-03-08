import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-container">
      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-red-600 text-white px-4 py-3 flex items-center justify-between">
        <Button
          variant="ghost"
          size="icon"
          className="text-white hover:bg-red-700"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          data-testid="mobile-menu-btn"
        >
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </Button>
        <span className="font-bold text-lg font-['Barlow_Condensed'] uppercase">Timeless Parts</span>
        <div className="w-10" /> {/* Spacer for centering */}
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content */}
      <main className="main-content p-4 pt-20 md:pt-6 md:p-8 bg-background min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}
