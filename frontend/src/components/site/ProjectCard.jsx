import React, { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ChevronDown, ChevronUp, ExternalLink, Github } from "lucide-react";

export default function ProjectCard({ project }) {
  const [open, setOpen] = useState(false);

  const tagLine = useMemo(() => project.tags.join(" • "), [project.tags]);

  return (
    <Card className="group border-zinc-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <CardTitle className="truncate text-base font-semibold text-zinc-900 md:text-lg">
              {project.title}
            </CardTitle>
            <div className="mt-1 text-sm text-zinc-600">
              <span className="font-medium text-zinc-700">{project.year}</span>
              <span className="mx-2 text-zinc-300">•</span>
              <span className="truncate">{tagLine}</span>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <Button
              variant="outline"
              className="border-zinc-200"
              onClick={() => window.open(project.links.repo, "_blank", "noopener,noreferrer")}
              aria-label={`Open repo for ${project.title}`}
            >
              <Github className="mr-2 h-4 w-4" />
              Repo
            </Button>
            <Button
              className="bg-teal-700 text-white hover:bg-teal-800"
              onClick={() => window.open(project.links.live, "_blank", "noopener,noreferrer")}
              aria-label={`Open live demo for ${project.title}`}
            >
              <ExternalLink className="mr-2 h-4 w-4" />
              Live
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <p className="text-pretty text-sm leading-6 text-zinc-600 md:text-base">
          {project.subtitle}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {project.tags.map((t) => (
            <Badge
              key={t}
              variant="secondary"
              className="border border-zinc-200 bg-zinc-50 text-zinc-700"
            >
              {t}
            </Badge>
          ))}
        </div>

        <Separator className="my-5" />

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="flex w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-left text-sm font-medium text-zinc-900 transition-colors hover:bg-zinc-50"
          aria-expanded={open}
        >
          <span>Highlights</span>
          {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>

        {open ? (
          <ul className="mt-3 list-disc space-y-2 pl-6 text-sm text-zinc-600">
            {project.highlights.map((h) => (
              <li key={h} className="leading-6">
                {h}
              </li>
            ))}
          </ul>
        ) : (
          <div className="mt-3 text-sm text-zinc-500">
            Expand to see what I built and why it matters.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
