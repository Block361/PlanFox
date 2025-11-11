"use client";

import { useState } from "react";
import { createJob } from "@/app/lib/api";

export default function CreateJobPage() {
  const [title, setTitle] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createJob({ title, startDate, endDate });
      setMessage("Job created successfully!");
      setTitle(""); setStartDate(""); setEndDate("");
    } catch (err) {
      setMessage("Failed to create job.");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4">Create Job</h1>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <div>
          <label className="block">Title</label>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} className="border p-2 w-full"/>
        </div>
        <div>
          <label>Start Date</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="border p-2 w-full"/>
        </div>
        <div>
          <label>End Date</label>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="border p-2 w-full"/>
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Create</button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}
