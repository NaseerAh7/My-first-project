import React from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Mail, ArrowUpRight } from "lucide-react";

function scrollToId(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function Header({ name, email }) {
  return (
    <header className="sticky top-0 z-50 border-b border-zinc-200 bg-white/75 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-3 px-6 py-3 md:px-10">
        <button
          type="button"
          onClick={() => scrollToId("top")}
          className="group flex items-baseline gap-2 rounded-md px-2 py-1 text-left transition-colors hover:bg-zinc-100"
          aria-label="Go to top"
        >
          <span className="text-sm font-semibold tracking-tight text-zinc-900">
            {name}
          </span>
          <span className="hidden text-xs text-zinc-500 md:inline">Portfolio</span>
        </button>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          <Button variant="ghost" onClick={() => scrollToId("about")}>About</Button>
          <Button variant="ghost" onClick={() => scrollToId("skills")}>Skills</Button>
          <Button variant="ghost" onClick={() => scrollToId("projects")}>Projects</Button>
          <Button variant="ghost" onClick={() => scrollToId("contact")}>Contact</Button>
          <Separator orientation="vertical" className="mx-1 h-6" />
          <Button
            className="bg-teal-700 text-white hover:bg-teal-800"
            onClick={() => {
              window.location.href = `mailto:${email}`;
            }}
          >
            <Mail className="mr-2 h-4 w-4" />
            Email
            <ArrowUpRight className="ml-2 h-4 w-4 opacity-90" />
          </Button>
        </nav>

        <div className="flex items-center gap-2 md:hidden">
          <Button variant="outline" onClick={() => scrollToId("projects")}>Projects</Button>
          <Button
            className="bg-teal-700 text-white hover:bg-teal-800"
            onClick={() => scrollToId("contact")}
          >
            Contact
          </Button>
        </div>
      </div>
    </header>
  );
}
