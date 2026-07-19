export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">LexiRAG AI</h1>
      <p className="text-slate-600">
        Upload legal documents, then ask questions and get answers with page
        and section citations.
      </p>
      <div className="flex gap-3">
        <a
          href="/upload"
          className="rounded-md bg-slate-900 text-white px-4 py-2 text-sm"
        >
          Upload Documents
        </a>
        <a
          href="/chat"
          className="rounded-md border border-slate-300 px-4 py-2 text-sm"
        >
          Ask a Question
        </a>
      </div>
    </div>
  );
}
