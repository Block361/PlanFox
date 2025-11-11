"use client";

import { useEffect, useState } from "react";

interface Inventory {
  id: number;
  name: string;
  quantity: number;
  serial: number;
}

interface Job {
  id: number;
  title: string;
  description?: string;
  startDate: string;
  endDate: string;
  status: string;
  userName?: string;
  articles?: Inventory[];
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedJobId, setExpandedJobId] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/jobs")
      .then(res => res.json())
      .then(setJobs)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;

  const toggleJob = (id: number) => {
    setExpandedJobId(prev => (prev === id ? null : id));
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Jobs</h1>
      <ul className="space-y-4">
        {jobs.map(job => (
          <li key={job.id} className="border rounded shadow">
            <button
              className="w-full text-left p-4 flex justify-between items-center"
              onClick={() => toggleJob(job.id)}
            >
              <span className="font-semibold">{job.title}</span>
              <span>{expandedJobId === job.id ? "▲" : "▼"}</span>
            </button>

            {expandedJobId === job.id && (
              <div className="p-4 border-t bg-gray-50 dark:bg-gray-800 space-y-2">
                <p><strong>Description:</strong> {job.description || "—"}</p>
                <p><strong>Status:</strong> {job.status}</p>
                <p><strong>Start:</strong> {new Date(job.startDate).toLocaleDateString()}</p>
                <p><strong>End:</strong> {new Date(job.endDate).toLocaleDateString()}</p>
                {job.userName && <p><strong>Assigned to:</strong> {job.userName}</p>}
                {job.articles && job.articles.length > 0 && (
                  <div className="mt-2">
                    <strong>Inventory:</strong>
                    <ul className="ml-4 list-disc">
                      {job.articles.map(item => (
                        <li key={item.id}>
                          {item.name} — Qty: {item.quantity} — Serial: {item.serial}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
