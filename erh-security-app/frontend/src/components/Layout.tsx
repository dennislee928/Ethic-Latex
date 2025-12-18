import React, { ReactNode } from 'react';

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
      </header>
      <main className="px-6 py-6">{children}</main>
    </div>
  );
};


