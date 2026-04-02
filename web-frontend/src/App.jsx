import { Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";

import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import DataCatalog from "./pages/DataCatalog";
import AccessControl from "./pages/AccessControl";
import AuditLogs from "./pages/AuditLogs";

export default function App() {
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <div className="flex h-screen transition-all duration-300
      bg-gradient-to-br 
      from-gray-50 via-gray-100 to-gray-200 
      dark:from-gray-950 dark:via-gray-900 dark:to-black
      text-gray-800 dark:text-gray-200"
    >
      <Sidebar />

      <main className="flex-1 p-10">
        {/* Toggle */}
        <div className="flex justify-end mb-6">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-4 py-2 rounded-xl text-sm font-medium 
            bg-white/70 dark:bg-gray-800/70 
            backdrop-blur-xl border border-gray-200 dark:border-gray-700
            hover:scale-105 transition"
          >
            {darkMode ? "☀️ Light" : "🌙 Dark"}
          </button>
        </div>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/catalog" element={<DataCatalog />} />
          <Route path="/access" element={<AccessControl />} />
          <Route path="/logs" element={<AuditLogs />} />
        </Routes>
      </main>
    </div>
  );
}