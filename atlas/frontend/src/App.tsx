import { Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/pages/DashboardPage";
import { SeriesExplorer } from "@/pages/SeriesExplorer";
import { FeatureExplorer } from "@/pages/FeatureExplorer";
import { CopilotPage } from "@/pages/CopilotPage";
import { SettingsPage } from "@/pages/SettingsPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/series" element={<SeriesExplorer />} />
        <Route path="/features" element={<FeatureExplorer />} />
        <Route path="/copilot" element={<CopilotPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
