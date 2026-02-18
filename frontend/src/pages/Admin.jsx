import React, { useEffect, useMemo, useState } from "react";

import Header from "@/components/site/Header";
import Footer from "@/components/site/Footer";
import Section from "@/components/site/Section";

import { profile } from "@/mock";

import { api, AdminAuthStorage } from "@/lib/apiClient";
import { toast } from "@/hooks/use-toast";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

import { ShieldCheck, RefreshCw, LogOut, ArrowLeft, Copy } from "lucide-react";

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function Admin() {
  const [email, setEmail] = useState(profile.email);
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(() => AdminAuthStorage.getToken());

  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);
  const [nextCursor, setNextCursor] = useState(null);

  const authed = useMemo(() => token.trim().length > 0, [token]);

  const loadPage = async ({ reset = false } = {}) => {
    const t = token.trim();
    if (!t) {
      toast({
        title: "Login required",
        description: "Sign in to load submissions.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const res = await api.get("/contact/recent", {
        params: {
          limit: 10,
          cursor: reset ? undefined : nextCursor || undefined,
        },
        headers: { Authorization: `Bearer ${t}` },
      });

      const payload = res.data;
      const pageItems = payload?.items || [];
      const cursor = payload?.next_cursor ?? null;

      setItems((prev) => (reset ? pageItems : [...prev, ...pageItems]));
      setNextCursor(cursor);

      toast({
        title: reset ? "Loaded" : "Loaded more",
        description: `${pageItems.length} submissions fetched.`,
      });
    } catch (e) {
      const status = e?.response?.status;
      if (status === 401) {
        toast({
          title: "Unauthorized",
          description: "Invalid admin key.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Failed",
          description: "Could not fetch submissions.",
          variant: "destructive",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) AdminAuthStorage.setToken(token);
  }, [token]);

  const login = async () => {
    if (!email.trim() || !password) {
      toast({
        title: "Missing credentials",
        description: "Enter email + password.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/auth/login", { email, password });
      const t = res.data?.access_token;
      if (!t) throw new Error("No token");
      setToken(t);
      AdminAuthStorage.setToken(t);
      toast({ title: "Signed in", description: "Admin access granted." });
      await loadPage({ reset: true });
    } catch (e) {
      toast({
        title: "Login failed",
        description: "Invalid credentials.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-zinc-900">
      <Header name={profile.name} email={profile.email} />

      <main className="py-10 md:py-14">
        <Section
          id="admin"
          eyebrow="ADMIN"
          title="Recent contact submissions"
          description="Protected endpoint using x-admin-key. This page is intentionally not linked in the main navigation."
        >
          <div className="grid gap-6 md:grid-cols-12">
            <Card className="border-zinc-200 shadow-sm md:col-span-4">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Access</CardTitle>
                  <Badge className="border border-zinc-200 bg-white text-zinc-700" variant="secondary">
                    /admin
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
                  <div className="flex items-center gap-2 text-xs font-semibold tracking-[0.18em] text-zinc-500">
                    <ShieldCheck className="h-4 w-4 text-teal-700" />
                    X-ADMIN-KEY
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <Input
                      value={adminKey}
                      onChange={(e) => setAdminKey(e.target.value)}
                      placeholder="Enter admin key"
                      className="h-9 border-zinc-200"
                      type="password"
                    />
                    <Button
                      variant="outline"
                      className="h-9 border-zinc-200"
                      onClick={() => {
                        navigator.clipboard
                          ?.writeText(adminKey)
                          .then(() => toast({ title: "Copied", description: "Admin key copied." }))
                          .catch(() =>
                            toast({
                              title: "Copy failed",
                              description: "Clipboard access blocked.",
                              variant: "destructive",
                            })
                          );
                      }}
                      disabled={!adminKey}
                    >
                      <Copy className="mr-2 h-4 w-4" />
                      Copy
                    </Button>
                  </div>
                  <div className="mt-2 text-xs text-zinc-500">
                    Stored in <span className="font-semibold">sessionStorage</span> for this browser session.
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Button
                    className="bg-teal-700 text-white hover:bg-teal-800"
                    onClick={() => loadPage({ reset: true })}
                    disabled={!authed || loading}
                  >
                    <RefreshCw className={"mr-2 h-4 w-4 " + (loading ? "animate-spin" : "")} />
                    Refresh
                  </Button>
                  <Button
                    variant="outline"
                    className="border-zinc-200"
                    onClick={() => {
                      AdminKeyStorage.clear();
                      setAdminKey("");
                      setItems([]);
                      setNextCursor(null);
                      toast({ title: "Cleared", description: "Admin key removed for this session." });
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Clear key
                  </Button>
                  <Button
                    variant="ghost"
                    className="justify-start text-zinc-700 hover:bg-zinc-100"
                    onClick={() => {
                      window.location.href = "/";
                    }}
                  >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to portfolio
                  </Button>
                </div>

                <Separator />

                <div className="text-xs text-zinc-500">
                  Endpoint: <span className="font-semibold">GET /api/contact/recent</span> (cursor pagination)
                </div>
              </CardContent>
            </Card>

            <Card className="border-zinc-200 shadow-sm md:col-span-8">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between gap-3">
                  <CardTitle className="text-base">Submissions</CardTitle>
                  <Badge className="bg-teal-50 text-teal-800" variant="secondary">
                    {items.length} loaded
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {items.length === 0 ? (
                  <div className="rounded-xl border border-zinc-200 bg-white p-6 text-sm text-zinc-600">
                    No data loaded yet. Enter your admin key and click Refresh.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {items.map((s) => (
                      <div key={s.id} className="rounded-xl border border-zinc-200 bg-white p-4">
                        <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between">
                          <div className="min-w-0">
                            <div className="truncate text-sm font-semibold text-zinc-900">{s.name}</div>
                            <div className="truncate text-xs text-zinc-600">{s.email}</div>
                          </div>
                          <div className="text-xs text-zinc-500">{formatDate(s.created_at)}</div>
                        </div>
                        <div className="mt-3 whitespace-pre-wrap rounded-lg border border-zinc-200 bg-zinc-50 p-3 text-sm text-zinc-700">
                          {s.message}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="pt-2">
                  <Button
                    variant="outline"
                    className="border-zinc-200"
                    onClick={() => loadPage({ reset: false })}
                    disabled={!authed || loading || !nextCursor}
                  >
                    <RefreshCw className={"mr-2 h-4 w-4 " + (loading ? "animate-spin" : "")} />
                    Load more
                  </Button>
                  {!nextCursor ? (
                    <div className="mt-2 text-xs text-zinc-500">No more pages.</div>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          </div>
        </Section>
      </main>

      <Footer name={profile.name} socials={profile.socials} />
    </div>
  );
}
