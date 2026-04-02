export default function Dashboard() {
  const stats = [
    { title: "Total Files", value: 120, color: "text-blue-500" },
    { title: "Users", value: 15, color: "text-green-500" },
    { title: "Violations", value: 3, color: "text-red-500" },
  ];

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-8">Dashboard</h1>

      <div className="grid grid-cols-3 gap-6">
        {stats.map((item, i) => (
          <div
            key={i}
            className="bg-white/60 dark:bg-gray-900/60 
            backdrop-blur-xl rounded-2xl p-6 
            border border-gray-200 dark:border-gray-800 
            shadow-sm hover:shadow-lg hover:-translate-y-1 
            transition-all duration-200"
          >
            <p className="text-sm text-gray-500">{item.title}</p>

            <div className="flex justify-between items-center mt-3">
              <h2 className={`text-3xl font-bold ${item.color}`}>
                {item.value}
              </h2>

              <div className="w-10 h-10 rounded-xl bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
                <div className={`w-3 h-3 rounded-full ${item.color} bg-current`} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}