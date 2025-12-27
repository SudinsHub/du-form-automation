"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  GraduationCap,
  FileText,
  BarChart3,
  Upload,
  Table,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/useAuthStore";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const user = useAuthStore((s) => s.user);

  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(useAuthStore.persist.hasHydrated());
  }, []);

  useEffect(() => {
    if (hydrated && !isAuthenticated) {
      router.replace("/login");
    } else if (hydrated && isAuthenticated && user?.role === "teacher" && !pathname.startsWith("/teacher")) {
      router.replace("/teacher-dashboard");
    } else if (hydrated && isAuthenticated && user?.is_super_admin && pathname.startsWith("/teacher")) {
      router.replace("/dashboard");
    }
  }, [hydrated, isAuthenticated, router, user, pathname]);

  if (!hydrated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  const links = user?.role === "teacher" ? [
    { href: "/teacher-dashboard", label: "ড্যাশবোর্ড", icon: BarChart3 },
    { href: "/teacher-remuneration-form", label: "পরীক্ষা সম্মানী ফর্ম", icon: FileText },
  ] : [
    { href: "/remuneration-form", label: "শিক্ষক সম্মানী ফর্ম", icon: FileText },
    { href: "/dashboard", label: "ড্যাশবোর্ড", icon: BarChart3 },
    { href: "/import", label: "শিক্ষক ইম্পোর্ট", icon: Upload },
    { href: "/excel-import", label: "এক্সেল ইম্পোর্ট", icon: Table },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r shadow-sm flex flex-col">
        <div className="flex items-center gap-3 p-4 border-b">
          <GraduationCap className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="font-bold text-gray-900 text-lg">
              ঢাকা বিশ্ববিদ্যালয়
            </h1>
            <p className="text-xs text-gray-500">
              স্বয়ংক্রিয় ফর্ম পূরণ ব্যবস্থা
            </p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-md text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition",
                pathname === href &&
                  "bg-blue-100 text-blue-700 font-medium"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {
              useAuthStore.getState().logout();
              router.replace("/login");
            }}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">{children}</main>
    </div>
  );
}
