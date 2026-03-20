import { Outlet } from "react-router-dom";

import { AppShell } from "../components/AppShell";

export function DashboardShell() {
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}