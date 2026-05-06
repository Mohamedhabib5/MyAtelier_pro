import { Outlet } from "react-router-dom";

import { AppShell } from "../components/AppShell";
import { PageTransition } from "../components/navigation/PageTransition";

export function DashboardShell() {
  return (
    <AppShell>
      <PageTransition>
        <Outlet />
      </PageTransition>
    </AppShell>
  );
}