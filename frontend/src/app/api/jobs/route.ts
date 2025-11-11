// frontend/src/lib/api.ts
export async function fetchJobs() {
  const res = await fetch("http://localhost:3000/jobs"); // dein Backend-Endpoint
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}
