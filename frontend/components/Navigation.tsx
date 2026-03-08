"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Mic2 } from "lucide-react";

export default function Navigation() {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-primary-600">
            <Mic2 size={28} />
            <span>Swara</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/calibrate"
              className={`font-medium transition-colors ${
                isActive("/calibrate")
                  ? "text-primary-600"
                  : "text-gray-600 hover:text-primary-600"
              }`}
            >
              Calibrate
            </Link>
            <Link
              href="/generate"
              className={`font-medium transition-colors ${
                isActive("/generate")
                  ? "text-primary-600"
                  : "text-gray-600 hover:text-primary-600"
              }`}
            >
              Generate
            </Link>
            <Link
              href="/profile"
              className={`font-medium transition-colors ${
                isActive("/profile")
                  ? "text-primary-600"
                  : "text-gray-600 hover:text-primary-600"
              }`}
            >
              Profile
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
