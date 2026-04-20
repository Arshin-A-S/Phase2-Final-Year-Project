import { useEffect, useState } from "react";
import { Search, Upload, Trash2, Download } from "lucide-react";

export default function DataCatalog() {
  const [files, setFiles] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [policy, setPolicy] = useState("");

  // 🔥 Upload Context
  const [location, setLocation] = useState("");
  const [device, setDevice] = useState("");
  const [department, setDepartment] = useState("");

  const [username] = useState("alice");

  // 🔽 Download Modal State
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [selectedFileForDownload, setSelectedFileForDownload] = useState(null);
  const [downloadLocation, setDownloadLocation] = useState("");
  const [downloadDevice, setDownloadDevice] = useState("");
  const [downloadDepartment, setDownloadDepartment] = useState("");

  // ---------------- FETCH FILES ----------------
  const fetchFiles = async () => {
    try {
      const res = await fetch("http://localhost:5001/files");
      const data = await res.json();

      if (Array.isArray(data)) {
        setFiles(data);
      } else {
        console.warn("Invalid files response:", data);
        setFiles([]);
      }
    } catch (err) {
      console.error("Fetch error:", err);
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

    if (location) formData.append("allowed_locations", location);
    if (device) formData.append("required_device", device);
    if (department) formData.append("required_department", department);

    try {
      const res = await fetch("http://localhost:5001/upload", {
        method: "POST",
        body: formData,
      });

      const text = await res.text();

      let data;
      try {
        data = JSON.parse(text);
      } catch {
        console.error("Invalid JSON:", text);
        alert("Server error");
        return;
      }

      if (res.ok && data.success) {
        alert("Uploaded 🚀");
        setSelectedFile(null);
        setPolicy("");
        fetchFiles();
      } else {
        alert(data.error || "Upload failed");
      }

    } catch (err) {
      console.error("Upload error:", err);
      alert("Network error");
    }
  };

  // ---------------- DELETE ----------------
  const handleDelete = async (fileId) => {
    if (!fileId) {
      alert("Invalid file_id");
      return;
    }

    if (!window.confirm("Delete this file?")) return;

    try {
      const res = await fetch("http://localhost:5001/delete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ file_id: fileId }),
      });

      const text = await res.text();

      let data;
      try {
        data = JSON.parse(text);
      } catch {
        console.error("Invalid JSON:", text);
        alert("Server error");
        return;
      }

      if (data.success) {
        fetchFiles();
      } else {
        alert(data.error || "Delete failed");
      }

    } catch (err) {
      console.error(err);
      alert("Delete failed");
    }
  };

  // ---------------- DOWNLOAD (FIXED) ----------------
  const handleDownload = async (fileId, fileName, loc, dev, dept) => {
    if (!loc || !dev || !dept) {
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
          username,
          file_id: fileId,
          context: {
            location: loc.toLowerCase(),
            device: dev.toLowerCase(),
            department: dept.toLowerCase(),
          }
        }),
      });

      if (!res.ok) {
        const text = await res.text();
        try {
          const err = JSON.parse(text);
          alert(err.error);
        } catch {
          alert("Download failed");
        }
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = fileName || "downloaded_file";
      a.click();

      window.URL.revokeObjectURL(url);

      // ✅ reset modal fields
      setDownloadLocation("");
      setDownloadDevice("");
      setDownloadDepartment("");

    } catch (err) {
      console.error("Download error:", err);
      alert("Download failed");
    }
  };

  // ---------------- FILTER ----------------
  const filtered = Array.isArray(files)
    ? files.filter((f) =>
        (f.name || "").toLowerCase().includes(search.toLowerCase())
      )
    : [];

  return (
    <div>
      <h1 className="text-3xl font-semibold mb-6">Data Catalog</h1>

      {/* 🔥 Upload + Context */}
      <div className="bg-white dark:bg-gray-900 p-4 rounded-xl border mb-6 flex flex-wrap gap-4 items-center">

        <input type="file" onChange={(e) => setSelectedFile(e.target.files[0])} />

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
          disabled={!selectedFile || !policy}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
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
          <div key={file.file_id || i} className="p-4 rounded-xl bg-white dark:bg-gray-900 border">
            <div className="text-3xl mb-2">📄</div>

            <p className="font-medium">{file.name || "Unknown"}</p>
            <p className="text-sm text-gray-500">{file.owner || "Unknown"}</p>

            <div className="flex justify-between mt-3">
              <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                {file.type || "file"}
              </span>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setSelectedFileForDownload(file);
                    setShowDownloadModal(true);
                  }}
                  className="text-blue-500"
                >
                  <Download size={16} />
                </button>

                <button
                  onClick={() => handleDelete(file.file_id)}
                  className="text-red-500"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 🔽 DOWNLOAD MODAL (FIXED) */}
      {showDownloadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-xl w-80 space-y-4">

            <h2 className="text-lg font-semibold">Enter Access Context</h2>

            <input
              placeholder="Location"
              className="w-full px-3 py-2 border rounded dark:bg-gray-800"
              value={downloadLocation}
              onChange={(e) => setDownloadLocation(e.target.value)}
            />

            <input
              placeholder="Device"
              className="w-full px-3 py-2 border rounded dark:bg-gray-800"
              value={downloadDevice}
              onChange={(e) => setDownloadDevice(e.target.value)}
            />

            <input
              placeholder="Department"
              className="w-full px-3 py-2 border rounded dark:bg-gray-800"
              value={downloadDepartment}
              onChange={(e) => setDownloadDepartment(e.target.value)}
            />

            <div className="flex justify-between">
              <button
                onClick={() => {
                  handleDownload(
                    selectedFileForDownload.file_id,
                    selectedFileForDownload.name,
                    downloadLocation,
                    downloadDevice,
                    downloadDepartment
                  );
                  setShowDownloadModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded"
              >
                Download
              </button>

              <button
                onClick={() => setShowDownloadModal(false)}
                className="px-4 py-2 bg-gray-400 text-white rounded"
              >
                Cancel
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}