"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WORKSPACE_ID = "default"; // TODO: replace with authenticated workspace id

type UploadResult = {
  document_id: string;
  document_name: string;
  pages_indexed: number;
  chunks_indexed: number;
};

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);

  async function handleUpload() {
    if (!file) return;
    setStatus("uploading");
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("workspace_id", WORKSPACE_ID);

    try {
      const res = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Upload failed (${res.status})`);
      }
      const data: UploadResult = await res.json();
      setResult(data);
      setStatus("idle");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
      setStatus("error");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Upload a Document</h1>
      <p className="text-sm text-slate-600">
        PDF, DOCX, TXT, or image (OCR). Processed into searchable, cited
        chunks.
      </p>

      <input
        type="file"
        accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.webp"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="block text-sm"
      />

      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading"}
        className="rounded-md bg-slate-900 text-white px-4 py-2 text-sm disabled:opacity-50"
      >
        {status === "uploading" ? "Uploading..." : "Upload & Index"}
      </button>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div className="rounded-md border border-slate-200 p-4 text-sm space-y-1">
          <p className="font-medium">{result.document_name} indexed.</p>
          <p className="text-slate-600">
            {result.pages_indexed} pages, {result.chunks_indexed} chunks
          </p>
        </div>
      )}
    </div>
  );
}
