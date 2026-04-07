import { Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";

import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import DataCatalog from "./pages/DataCatalog";
import AccessControl from "./pages/AccessControl";
import AuditLogs from "./pages/AuditLogs";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);

  // Apply dark mode class to HTML
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-950 text-gray-800 dark:text-gray-200">
      <Sidebar />

      <main className="flex-1 p-8">
        {/* 🔥 Better Toggle Button */}
        <div className="flex justify-end mb-6">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-4 py-2 rounded-lg text-sm font-medium 
              bg-gray-900 text-white 
              hover:bg-gray-700 
              dark:bg-gray-200 dark:text-black 
              dark:hover:bg-gray-300 
              transition"
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