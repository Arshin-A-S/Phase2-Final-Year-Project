import { useState } from "react";

export default function AccessControl() {
  const [users, setUsers] = useState([
    { name: "Alice", role: "Admin" },
    { name: "Bob", role: "Editor" },
    { name: "Charlie", role: "Viewer" },
  ]);

  const roles = ["Admin", "Editor", "Viewer"];

  const roleStyles = {
    Admin: "bg-red-500/10 text-red-400",
    Editor: "bg-blue-500/10 text-blue-400",
    Viewer: "bg-gray-500/10 text-gray-400",
  };

  const updateRole = (index, newRole) => {
    const updated = [...users];
    updated[index].role = newRole;
    setUsers(updated);
  };

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-8">Access Control</h1>

      <div className="bg-white/60 dark:bg-gray-900/60 
        backdrop-blur-xl rounded-2xl border 
        border-gray-200 dark:border-gray-800 
        shadow-sm overflow-hidden"
      >
        {users.map((user, index) => (
          <div
            key={index}
            className="flex justify-between items-center px-6 py-4 
            border-b last:border-none 
            border-gray-200 dark:border-gray-800
            hover:bg-gray-100 dark:hover:bg-gray-800 
            transition"
          >
            {/* User */}
            <div>
              <p className="font-medium">{user.name}</p>
              <p className="text-xs text-gray-500">User account</p>
            </div>

            {/* Role */}
            <div className="flex items-center gap-3">
              <span
                className={`text-xs px-3 py-1 rounded-lg font-medium ${roleStyles[user.role]}`}
              >
                {user.role}
              </span>

              <select
                value={user.role}
                onChange={(e) => updateRole(index, e.target.value)}
                className="bg-gray-200 dark:bg-gray-800 
                px-3 py-1 rounded-lg text-sm 
                outline-none hover:scale-105 transition"
              >
                {roles.map((role) => (
                  <option key={role}>{role}</option>
                ))}
              </select>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}