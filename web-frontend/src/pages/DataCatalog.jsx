import { useEffect, useState } from "react";
import { Search } from "lucide-react";

export default function DataCatalog() {
  const [files, setFiles] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setFiles([
      { name: "report.pdf", owner: "Alice", type: "PDF" },
      { name: "data.csv", owner: "Bob", type: "CSV" },
    ]);
  }, []);

  const filtered = files.filter((f) =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-8">Data Catalog</h1>

      {/* Search */}
      <div className="flex items-center gap-3 
        bg-white/60 dark:bg-gray-900/60 
        backdrop-blur-xl border 
        border-gray-200 dark:border-gray-800 
        rounded-xl px-4 py-3 mb-8 w-96"
      >
        <Search size={18} />
        <input
          type="text"
          placeholder="Search files..."
          className="bg-transparent outline-none w-full"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Grid */}
      <div className="grid grid-cols-3 gap-6">
        {filtered.map((file, i) => (
          <div
            key={i}
            className="bg-white/60 dark:bg-gray-900/60 
            backdrop-blur-xl rounded-2xl p-5 
            border border-gray-200 dark:border-gray-800 
            hover:shadow-lg hover:-translate-y-1 
            transition-all cursor-pointer"
          >
            <div className="text-3xl mb-2">📄</div>
            <p className="font-semibold">{file.name}</p>
            <p className="text-sm text-gray-500">{file.owner}</p>
          </div>
        ))}
      </div>
    </div>
  );
}