import { Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/pages/DashboardPage";
import { DocumentExplorer } from "@/pages/DocumentExplorer";
import { DriftPage } from "@/pages/DriftPage";
import { EventStudyPage } from "@/pages/EventStudyPage";
import { CopilotPage } from "@/pages/CopilotPage";
import { ReviewPage } from "@/pages/ReviewPage";
import { SettingsPage } from "@/pages/SettingsPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/documents" element={<DocumentExplorer />} />
        <Route path="/drift" element={<DriftPage />} />
        <Route path="/event-study" element={<EventStudyPage />} />
        <Route path="/copilot" element={<CopilotPage />} />
        <Route path="/reviews" element={<ReviewPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
