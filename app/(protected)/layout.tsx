// app/(protected)/layout.tsx
import ProtectedLayout from "./ProtectedLayout";

export default function ProtectedRouteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <ProtectedLayout>{children}</ProtectedLayout>;
}
