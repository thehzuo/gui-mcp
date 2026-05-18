import { CircuitBoard, ClipboardCheck, GitBranch, Gauge, ListChecks } from "lucide-react";
import { NavLink, Route, Routes, useParams } from "react-router-dom";
import { ContractPage } from "./pages/ContractPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PlanEditorPage } from "./pages/PlanEditorPage";
import { ReviewQueuePage } from "./pages/ReviewQueuePage";
import { RunListPage } from "./pages/RunListPage";

function RunNav() {
  const { runId } = useParams();
  if (!runId) return null;
  const items = [
    { to: `/runs/${runId}/contract`, label: "Contract", icon: ClipboardCheck },
    { to: `/runs/${runId}/plan`, label: "DAG", icon: GitBranch },
    { to: `/runs/${runId}/reviews`, label: "Reviews", icon: ListChecks },
    { to: `/runs/${runId}/dashboard`, label: "Dashboard", icon: Gauge }
  ];
  return (
    <nav className="flex flex-wrap gap-2">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-chip ${isActive ? "nav-chip-active" : ""}`}>
            <Icon size={15} /> {item.label}
          </NavLink>
        );
      })}
    </nav>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-carbon text-ink">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_20%_10%,rgba(213,255,91,0.08),transparent_30%),linear-gradient(135deg,rgba(255,107,53,0.06),transparent_35%)]" />
      <div className="grain" />
      <header className="sticky top-0 z-20 border-b border-steel/15 bg-carbon/85 px-5 py-4 backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center border border-limewire/50 bg-limewire text-carbon">
              <CircuitBoard size={20} />
            </span>
            <span>
              <span className="block font-display text-lg font-black uppercase leading-none text-ink">Agent Loom</span>
              <span className="block font-mono text-[10px] uppercase text-steel">Control kernel for long-horizon execution</span>
            </span>
          </NavLink>
          <Routes>
            <Route path="/runs/:runId/*" element={<RunNav />} />
          </Routes>
        </div>
      </header>
      <main className="p-5">
        <Routes>
          <Route path="/" element={<RunListPage />} />
          <Route path="/runs/:runId/contract" element={<ContractPage />} />
          <Route path="/runs/:runId/plan" element={<PlanEditorPage />} />
          <Route path="/runs/:runId/reviews" element={<ReviewQueuePage />} />
          <Route path="/runs/:runId/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
    </div>
  );
}

