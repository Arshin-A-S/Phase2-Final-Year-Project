import { useEffect, useState } from "react";
import { Search, Upload, Trash2 } from "lucide-react";

export default function DataCatalog() {
  const [files, setFiles] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [policy, setPolicy] = useState("");
  const [username] = useState("Alice");

  const fetchFiles = () => {
    fetch("http://localhost:5001/files")
      .then((res) => res.json())
      .then((data) => setFiles(data))
      .catch(() => setFiles([]));
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  // 🔥 Upload
  const handleUpload = async () => {
    if (!selectedFile || !policy) {
      alert("Select file + policy");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("username", username);
    formData.append("policy", policy);

    try {
      const res = await fetch("http://localhost:5001/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.success) {
        alert("Uploaded 🚀");
        fetchFiles();
      } else {
        alert(data.error);
      }
    } catch {
      alert("Upload failed");
    }
  };

  // 🔥 Delete
  const handleDelete = async (fileId) => {
    if (!confirm("Delete this file?")) return;

    try {
      const res = await fetch("http://localhost:5001/delete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ file_id: fileId }),
      });

      const data = await res.json();

      if (data.success) {
        fetchFiles();
      } else {
        alert(data.error);
      }
    } catch {
      alert("Delete failed");
    }
  };

  const filtered = files.filter((f) =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-6">Data Catalog</h1>

      {/* 🔥 Upload Section */}
      <div className="bg-white dark:bg-gray-900 p-4 rounded-xl border mb-6 flex gap-4 items-center">
        <input type="file" onChange={(e) => setSelectedFile(e.target.files[0])} />

        <input
          type="text"
          placeholder="Policy (Admin, etc)"
          className="px-3 py-2 border rounded dark:bg-gray-800"
          value={policy}
          onChange={(e) => setPolicy(e.target.value)}
        />

        <button
          onClick={handleUpload}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <Upload size={16} />
          Upload
        </button>
      </div>

      {/* 🔍 Search */}
      <div className="flex items-center gap-3 bg-white dark:bg-gray-900 px-4 py-2 rounded-lg mb-6 border w-80">
        <Search size={16} />
        <input
          type="text"
          placeholder="Search..."
          className="bg-transparent outline-none w-full"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* 📁 Files */}
      <div className="grid grid-cols-4 gap-6">
        {filtered.map((file, i) => (
          <div
            key={i}
            className="p-4 rounded-xl bg-white dark:bg-gray-900 border hover:shadow-lg transition"
          >
            <div className="text-3xl mb-2">📄</div>

            <p className="font-medium">{file.name}</p>
            <p className="text-sm text-gray-500">{file.owner}</p>

            <div className="flex justify-between mt-3">
              <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                {file.type}
              </span>

              <button
                onClick={() => handleDelete(file.file_id)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}