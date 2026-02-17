import React, { useMemo, useState } from "react";

import Header from "@/components/site/Header";
import Footer from "@/components/site/Footer";
import Section from "@/components/site/Section";

import { profile, about, skills, projects } from "@/mock";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";

import ProjectCard from "@/components/site/ProjectCard";
import ContactForm from "@/components/site/ContactForm";

import { toast } from "@/hooks/use-toast";
import {
  ArrowDown,
  ArrowUpRight,
  Briefcase,
  Code2,
  GraduationCap,
  Sparkles,
} from "lucide-react";

function scrollToId(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function downloadTextFile(filename, content) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function Portfolio() {
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState("All");

  const allTags = useMemo(() => {
    const set = new Set();
    projects.forEach((p) => p.tags.forEach((t) => set.add(t)));
    return ["All", ...Array.from(set)];
  }, []);

  const filteredProjects = useMemo(() => {
    const q = query.trim().toLowerCase();
    return projects.filter((p) => {
      const matchesTag = tag === "All" ? true : p.tags.includes(tag);
      const matchesQuery =
        !q ||
        p.title.toLowerCase().includes(q) ||
        p.subtitle.toLowerCase().includes(q) ||
        p.tags.some((t) => t.toLowerCase().includes(q));
      return matchesTag && matchesQuery;
    });
  }, [query, tag]);

  return (
    <div id="top" className="min-h-screen bg-white text-zinc-900">
      <Header name={profile.name} email={profile.email} />

      {/* HERO */}
      <main>
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-0">
            <div className="absolute -left-24 -top-24 h-80 w-80 rounded-full bg-teal-100 blur-3xl" />
            <div className="absolute -bottom-24 -right-24 h-80 w-80 rounded-full bg-zinc-100 blur-3xl" />
          </div>

          <div className="mx-auto w-full max-w-6xl px-6 pb-16 pt-14 md:px-10 md:pb-20 md:pt-20">
            <div className="grid items-start gap-10 md:grid-cols-12">
              <div className="md:col-span-7">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className="border border-teal-200 bg-teal-50 text-teal-800" variant="secondary">
                    Available for internships & freelance
                  </Badge>
                  <Badge className="border border-zinc-200 bg-white text-zinc-700" variant="secondary">
                    Minimal + performance-focused
                  </Badge>
                </div>

                <h1 className="mt-5 text-pretty text-4xl font-semibold tracking-tight text-zinc-900 md:text-5xl">
                  {profile.name}
                </h1>
                <p className="mt-3 text-pretty text-lg leading-7 text-zinc-700 md:text-xl">
                  {profile.tagline}
                </p>
                <p className="mt-5 max-w-2xl text-pretty text-sm leading-6 text-zinc-600 md:text-base">
                  {profile.bioShort}
                </p>

                <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center">
                  <Button
                    className="bg-teal-700 text-white hover:bg-teal-800"
                    onClick={() => scrollToId("projects")}
                  >
                    <Briefcase className="mr-2 h-4 w-4" />
                    View projects
                    <ArrowUpRight className="ml-2 h-4 w-4 opacity-90" />
                  </Button>
                  <Button variant="outline" className="border-zinc-200" onClick={() => scrollToId("contact")}>
                    <Sparkles className="mr-2 h-4 w-4 text-teal-700" />
                    Let’s build something
                  </Button>
                  <Button
                    variant="ghost"
                    className="justify-start text-zinc-700 hover:bg-zinc-100"
                    onClick={() => scrollToId("about")}
                  >
                    <ArrowDown className="mr-2 h-4 w-4" />
                    About me
                  </Button>
                </div>
              </div>

              <div className="md:col-span-5">
                <Card className="border-zinc-200 bg-white/70 shadow-sm backdrop-blur">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Snapshot</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-3">
                      <div className="flex items-start gap-3 rounded-lg border border-zinc-200 bg-white p-3">
                        <GraduationCap className="mt-0.5 h-5 w-5 text-teal-700" />
                        <div>
                          <div className="text-sm font-semibold text-zinc-900">Computer Science student</div>
                          <div className="mt-0.5 text-sm text-zinc-600">Learning by building real projects.</div>
                        </div>
                      </div>
                      <div className="flex items-start gap-3 rounded-lg border border-zinc-200 bg-white p-3">
                        <Code2 className="mt-0.5 h-5 w-5 text-teal-700" />
                        <div>
                          <div className="text-sm font-semibold text-zinc-900">Frontend + APIs</div>
                          <div className="mt-0.5 text-sm text-zinc-600">React, FastAPI, MongoDB.</div>
                        </div>
                      </div>
                    </div>

                    <Separator />

                    <div className="flex flex-col gap-3 sm:flex-row">
                      <Button
                        className="bg-teal-700 text-white hover:bg-teal-800"
                        onClick={() => {
                          const content = [
                            `${profile.name}`,
                            `${profile.tagline}`,
                            "",
                            profile.bioLong,
                            "",
                            "Skills: React, FastAPI, MongoDB, Tailwind",
                            "",
                            "Email: " + profile.email,
                          ].join("\n");
                          downloadTextFile("Naseer_Ahmad_Zarmati_CV.txt", content);
                          toast({
                            title: "Downloaded",
                            description: "A simple CV text file was generated (MOCKED).",
                          });
                        }}
                      >
                        Download CV
                      </Button>
                      <Button
                        variant="outline"
                        className="border-zinc-200"
                        onClick={() => {
                          toast({
                            title: "Tip",
                            description: "We can replace the CV with a real PDF later.",
                          });
                        }}
                      >
                        How this works
                      </Button>
                    </div>

                    <div className="text-xs text-zinc-500">
                      CV download is <span className="font-semibold">MOCKED</span> (generates a text file).
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* ABOUT */}
        <div className="py-16 md:py-20">
          <Section
            id="about"
            eyebrow="ABOUT"
            title="A developer who values clarity and craft"
            description={profile.bioLong}
          >
            <div className="grid gap-6 md:grid-cols-12">
              <Card className="border-zinc-200 shadow-sm md:col-span-7">
                <CardHeader>
                  <CardTitle className="text-base">What I focus on</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 text-sm leading-6 text-zinc-700">
                    {about.bullets.map((b) => (
                      <li key={b} className="flex gap-3">
                        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-700" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="border-zinc-200 shadow-sm md:col-span-5">
                <CardHeader>
                  <CardTitle className="text-base">Now</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {about.now.map((n) => (
                    <div key={n.label} className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
                      <div className="text-xs font-semibold tracking-[0.18em] text-zinc-500">
                        {n.label.toUpperCase()}
                      </div>
                      <div className="mt-2 text-sm font-semibold text-zinc-900">{n.value}</div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </Section>
        </div>

        {/* SKILLS */}
        <div className="border-y border-zinc-200 bg-zinc-50 py-16 md:py-20">
          <Section
            id="skills"
            eyebrow="SKILLS"
            title="Tools I use to ship reliably"
            description="A quick overview of what I’m comfortable with — and what I’m actively improving."
          >
            <Tabs defaultValue="Frontend" className="w-full">
              <TabsList className="flex w-full flex-wrap justify-start gap-2 bg-transparent p-0">
                {skills.featured.map((s) => (
                  <TabsTrigger
                    key={s.title}
                    value={s.title}
                    className="rounded-full border border-zinc-200 bg-white px-4 py-2 text-sm data-[state=active]:border-teal-200 data-[state=active]:bg-teal-50 data-[state=active]:text-teal-900"
                  >
                    {s.title}
                  </TabsTrigger>
                ))}
              </TabsList>

              {skills.featured.map((s) => (
                <TabsContent key={s.title} value={s.title} className="mt-6">
                  <div className="grid gap-3 md:grid-cols-2">
                    {s.items.map((it) => (
                      <div
                        key={it}
                        className="rounded-xl border border-zinc-200 bg-white p-4 text-sm font-medium text-zinc-800 shadow-sm"
                      >
                        {it}
                      </div>
                    ))}
                  </div>
                </TabsContent>
              ))}
            </Tabs>

            <div className="mt-10">
              <div className="text-sm font-semibold text-zinc-900">Also comfortable with</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {skills.chips.map((c) => (
                  <Badge
                    key={c}
                    variant="secondary"
                    className="border border-zinc-200 bg-white text-zinc-700"
                  >
                    {c}
                  </Badge>
                ))}
              </div>
            </div>
          </Section>
        </div>

        {/* PROJECTS */}
        <div className="py-16 md:py-20">
          <Section
            id="projects"
            eyebrow="PROJECTS"
            title="Selected work"
            description="Three placeholder projects for now. Later we can connect real links, screenshots, and case studies."
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="flex flex-wrap gap-2">
                {allTags.map((t) => {
                  const active = t === tag;
                  return (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setTag(t)}
                      className={
                        "rounded-full border px-4 py-2 text-sm font-medium transition-colors " +
                        (active
                          ? "border-teal-200 bg-teal-50 text-teal-900"
                          : "border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50")
                      }
                    >
                      {t}
                    </button>
                  );
                })}
              </div>

              <div className="w-full md:w-[360px]">
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search projects (title, tags…)"
                  className="border-zinc-200 bg-white"
                />
              </div>
            </div>

            <div className="mt-8 grid gap-6 md:grid-cols-2">
              {filteredProjects.map((p) => (
                <ProjectCard key={p.id} project={p} />
              ))}
            </div>

            {filteredProjects.length === 0 ? (
              <div className="mt-8 rounded-xl border border-zinc-200 bg-white p-6 text-sm text-zinc-600">
                No matches. Try clearing the search or selecting “All”.
              </div>
            ) : null}
          </Section>
        </div>

        {/* CONTACT */}
        <div className="border-t border-zinc-200 bg-zinc-50 py-16 md:py-20">
          <Section
            id="contact"
            eyebrow="CONTACT"
            title="Let’s talk"
            description="Tell me about your project or opportunity. For now, submissions save locally (MOCKED) — we’ll wire up email later."
          >
            <ContactForm ownerEmail={profile.email} />
          </Section>
        </div>
      </main>

      <Footer name={profile.name} socials={profile.socials} />
    </div>
  );
}
