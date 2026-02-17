import React from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Github, Linkedin, ExternalLink } from "lucide-react";

const iconByType = {
  github: Github,
  linkedin: Linkedin,
  x: ExternalLink,
};

export default function Footer({ name, socials }) {
  return (
    <footer className="border-t border-zinc-200 bg-white">
      <div className="mx-auto w-full max-w-6xl px-6 py-10 md:px-10">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-sm font-semibold text-zinc-900">{name}</div>
            <div className="mt-1 text-sm text-zinc-600">
              Built with React + shadcn/ui. (Contact saving is MOCKED locally.)
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {socials.map((s) => {
              const Icon = iconByType[s.type] || ExternalLink;
              return (
                <Button
                  key={s.label}
                  variant="outline"
                  className="border-zinc-200"
                  onClick={() => window.open(s.href, "_blank", "noopener,noreferrer")}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {s.label}
                </Button>
              );
            })}
          </div>
        </div>

        <Separator className="my-8" />

        <div className="flex flex-col gap-2 text-xs text-zinc-500 md:flex-row md:items-center md:justify-between">
          <span>© {new Date().getFullYear()} {name}. All rights reserved.</span>
          <span className="tracking-wide">Minimal • Teal accent • Fast & accessible</span>
        </div>
      </div>
    </footer>
  );
}
