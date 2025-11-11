import Link from "next/link";

export default function HomePage() {
  return (
    <div className="p-6">
      <h1 className="text-4xl font-bold mb-6">PlanFox 🦊 Dashboard</h1>
      <nav className="space-x-4">
        <Link href="/jobs" className="text-blue-600 underline">Jobs</Link>
        <Link href="/jobs/create" className="text-blue-600 underline">Create Job</Link>
      </nav>
    </div>
  );
}
