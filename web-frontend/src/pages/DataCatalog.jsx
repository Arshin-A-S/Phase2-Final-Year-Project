import { useEffect, useState } from "react";
import { Search, Upload, Trash2, Download } from "lucide-react";

export default function DataCatalog() {
  const [files, setFiles] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [policy, setPolicy] = useState("");

  // 🔥 Context (merged into upload box)
  const [location, setLocation] = useState("");
  const [device, setDevice] = useState("");
  const [department, setDepartment] = useState("");

  const [username] = useState("alice");

  // ---------------- FETCH FILES ----------------
  const fetchFiles = async () => {
    try {
      const res = await fetch("http://localhost:5001/files");

      if (!res.ok) {
        console.error("Fetch failed");
        return;
      }

      const data = await res.json();
      setFiles(data || []);
    } catch {
      setFiles([]);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  // ---------------- UPLOAD ----------------
  const handleUpload = async () => {
    if (!selectedFile || !policy) {
      alert("Select file + policy");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("username", username);
    formData.append("policy", policy);

    // 🔥 SEND CONTEXT TO BACKEND
    if (location) formData.append("allowed_locations", location);
    if (device) formData.append("required_device", device);
    if (department) formData.append("required_department", department);

    try {
      const res = await fetch("http://localhost:5001/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        alert(err.error || "Upload failed");
        return;
      }

      const data = await res.json();

      if (data.success) {
        alert("Uploaded 🚀");

        // Reset
        setSelectedFile(null);
        setPolicy("");

        fetchFiles();
      } else {
        alert(data.error);
      }
    } catch {
      alert("Upload failed");
    }
  };

  // ---------------- DELETE ----------------
  const handleDelete = async (fileId) => {
    if (!window.confirm("Delete this file?")) return;

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

  // ---------------- DOWNLOAD ----------------
  const handleDownload = async (fileId, fileName) => {
    if (!location || !device || !department) {
      alert("Enter location, device, and department");
      return;
    }

    try {
      const res = await fetch("http://localhost:5001/download", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          file_id: fileId,
          context: {
            location,
            device,
            department,
          },
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        alert(err.error || "Download blocked");
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      a.click();
    } catch {
      alert("Download failed");
    }
  };

  // ---------------- FILTER ----------------
  const filtered = files.filter((f) =>
    (f.name || "").toLowerCase().includes(search.toLowerCase())
  );

  // ---------------- UI ----------------
  return (
    <div>
      <h1 className="text-3xl font-semibold mb-6">Data Catalog</h1>

      {/* 🔥 COMBINED UPLOAD + CONTEXT BOX */}
      <div className="bg-white dark:bg-gray-900 p-4 rounded-xl border mb-6 flex flex-wrap gap-4 items-center">

        <input
          type="file"
          onChange={(e) => setSelectedFile(e.target.files[0])}
        />

        <input
          type="text"
          placeholder="Policy (e.g., role:admin)"
          className="px-3 py-2 border rounded dark:bg-gray-800"
          value={policy}
          onChange={(e) => setPolicy(e.target.value)}
        />

        <input
          placeholder="Location"
          className="px-3 py-2 border rounded dark:bg-gray-800"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />

        <input
          placeholder="Device"
          className="px-3 py-2 border rounded dark:bg-gray-800"
          value={device}
          onChange={(e) => setDevice(e.target.value)}
        />

        <input
          placeholder="Department"
          className="px-3 py-2 border rounded dark:bg-gray-800"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
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
        {filtered.map((file) => (
          <div
            key={file.file_id}   // ✅ FIXED
            className="p-4 rounded-xl bg-white dark:bg-gray-900 border hover:shadow-lg transition"
          >
            <div className="text-3xl mb-2">📄</div>

            <p className="font-medium">{file.name || "Unknown"}</p>
            <p className="text-sm text-gray-500">{file.owner || "N/A"}</p>

            <div className="flex justify-between mt-3">
              <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                {file.type || "file"}
              </span>

              <div className="flex gap-3">
                <button
                  onClick={() => handleDownload(file.file_id, file.name)}
                  className="text-blue-500 hover:text-blue-700"
                >
                  <Download size={16} />
                </button>

                <button
                  onClick={() => handleDelete(file.file_id)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}