export const API_URL = "http://localhost:3001"; // dein NestJS Backend

export async function fetchJobs() {
  const res = await fetch(`${API_URL}/jobs`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function createJob(data: { title: string; startDate: string; endDate: string }) {
  const res = await fetch(`${API_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create job");
  return res.json();
}
