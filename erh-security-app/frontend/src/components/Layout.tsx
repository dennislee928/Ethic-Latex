import React, { ReactNode } from 'react';
import Link from 'next/link';

type LayoutProps = {
  children: ReactNode;
};

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-4">
        <h1 className="text-xl font-semibold">ERH-on-Security Dashboard</h1>
        <p className="text-sm text-slate-400">
          Monitoring error growth structure of DevSecOps judges through the ERH lens.
        </p>
        <nav className="mt-3 flex gap-4 text-sm">
          <Link className="text-sky-400 hover:text-sky-300" href="/">
            Security overview
          </Link>
          <Link className="text-sky-400 hover:text-sky-300" href="/ueba">
            UEBA insider-threat
          </Link>
        </nav>
      </header>
      <main className="px-6 py-6">{children}</main>
    </div>
  );
};


