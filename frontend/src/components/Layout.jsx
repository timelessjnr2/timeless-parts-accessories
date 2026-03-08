import { useState, useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  // Close sidebar when clicking outside on mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="app-container min-h-screen bg-background">
      {/* Mobile Header - Always visible on mobile */}
      <header className="md:hidden fixed top-0 left-0 right-0 z-40 bg-red-600 text-white px-4 py-3 flex items-center justify-between shadow-lg">
        <Button
          variant="ghost"
          size="icon"
          className="text-white hover:bg-red-700 h-10 w-10"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          data-testid="mobile-menu-btn"
        >
          <Menu size={24} />
        </Button>
        <span className="font-bold text-lg font-['Barlow_Condensed'] uppercase tracking-wide">
          Timeless Parts
        </span>
        <div className="w-10" /> {/* Spacer for centering */}
      </header>

      {/* Mobile Overlay - only shows when sidebar is open */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
          data-testid="sidebar-overlay"
        />
      )}

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content */}
      <main className="main-content p-4 pt-20 md:pt-6 md:p-8 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}
