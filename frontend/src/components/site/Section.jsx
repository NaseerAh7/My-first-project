import React from "react";
import { cn } from "@/lib/utils";

export default function Section({ id, eyebrow, title, description, className, children }) {
  return (
    <section id={id} className={cn("scroll-mt-24", className)}>
      <div className="mx-auto w-full max-w-6xl px-6 md:px-10">
        <div className="mb-8">
          {eyebrow ? (
            <div className="mb-2 text-xs font-semibold tracking-[0.22em] text-zinc-500">
              {eyebrow}
            </div>
          ) : null}
          {title ? (
            <h2 className="text-pretty text-2xl font-semibold tracking-tight text-zinc-900 md:text-3xl">
              {title}
            </h2>
          ) : null}
          {description ? (
            <p className="mt-2 max-w-2xl text-pretty text-sm leading-6 text-zinc-600 md:text-base">
              {description}
            </p>
          ) : null}
        </div>
        {children}
      </div>
    </section>
  );
}
