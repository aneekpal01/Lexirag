"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WORKSPACE_ID = "default"; // TODO: replace with authenticated workspace id

type Citation = {
  document_name: string;
  page_number: number;
  section_label: string | null;
  confidence: number;
  excerpt: string;
};

type ChatTurn = {
  question: string;
  answer: string;
  citations: Citation[];
};

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatTurn[]>([]);

  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, workspace_id: WORKSPACE_ID }),
      });
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const data = await res.json();
      setHistory((prev) => [
        ...prev,
        { question, answer: data.answer, citations: data.citations },
      ]);
      setQuestion("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Ask a Legal Question</h1>

      <div className="space-y-4">
        {history.map((turn, i) => (
          <div key={i} className="space-y-2">
            <p className="font-medium">{turn.question}</p>
            <p className="text-sm text-slate-700">{turn.answer}</p>
            <div className="space-y-1">
              {turn.citations.map((c, j) => (
                <div
                  key={j}
                  className="text-xs rounded border border-slate-200 p-2 bg-white"
                >
                  <span className="font-medium">{c.document_name}</span>
                  {" · Page "}
                  {c.page_number}
                  {c.section_label ? ` · ${c.section_label}` : ""}
                  {` · Confidence ${c.confidence}%`}
                  <p className="text-slate-500 mt-1">{c.excerpt}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="e.g. Can an employer terminate an employee without notice?"
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          onClick={handleAsk}
          disabled={loading}
          className="rounded-md bg-slate-900 text-white px-4 py-2 text-sm disabled:opacity-50"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
