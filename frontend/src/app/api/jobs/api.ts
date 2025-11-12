export const API_URL = "http://localhost:3001";

export async function createJob(data: {
  title: string;
  startDate: string;
  endDate: string;
  userId: string | number; // <- userId muss mitgesendet werden
}) {
  const res = await fetch(`${API_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Failed to create job");
  return res.json();
}
