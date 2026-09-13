import { Construction } from "lucide-react";

import { EmptyState } from "../components/EmptyState";

export function PlaceholderPage({ title }: { title: string }) {
  return (
    <EmptyState
      icon={Construction}
      title={`${title} arrives in a later phase`}
      message="Phase 1 creates the platform foundation. This module is represented in navigation so role access can be shaped before domain screens are implemented."
    />
  );
}
