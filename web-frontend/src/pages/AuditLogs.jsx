import { FileUp, Eye, AlertTriangle } from "lucide-react";

export default function AuditLogs() {
  const logs = [
    { user: "Alice", action: "Uploaded file", time: "2 min ago", type: "upload" },
    { user: "Bob", action: "Accessed report.pdf", time: "10 min ago", type: "access" },
    { user: "Charlie", action: "Permission denied", time: "1 hour ago", type: "error" },
  ];

  const getIcon = (type) => {
    if (type === "upload")
      return <FileUp size={18} className="text-blue-400" />;
    if (type === "access")
      return <Eye size={18} className="text-green-400" />;
    if (type === "error")
      return <AlertTriangle size={18} className="text-red-400" />;
  };

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-8">Audit Logs</h1>

      <div className="bg-white/60 dark:bg-gray-900/60 
        backdrop-blur-xl rounded-2xl border 
        border-gray-200 dark:border-gray-800 
        shadow-sm overflow-hidden"
      >
        {logs.map((log, index) => (
          <div
            key={index}
            className="flex items-center justify-between px-6 py-4 
            border-b last:border-none 
            border-gray-200 dark:border-gray-800
            hover:bg-gray-100 dark:hover:bg-gray-800 
            transition"
          >
            {/* Left */}
            <div className="flex items-center gap-4">
              {/* Icon */}
              <div className="w-10 h-10 flex items-center justify-center 
                rounded-xl bg-gray-200 dark:bg-gray-800"
              >
                {getIcon(log.type)}
              </div>

              {/* Text */}
              <div>
                <p className="font-medium">{log.user}</p>
                <p className="text-sm text-gray-500">{log.action}</p>
              </div>
            </div>

            {/* Time */}
            <span className="text-sm text-gray-400">{log.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}