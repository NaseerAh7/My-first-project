import React, { useMemo, useState } from "react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

import { toast } from "@/hooks/use-toast";
import { api } from "@/lib/apiClient";
import { Mail, Copy, Send, ShieldCheck, RefreshCw } from "lucide-react";

const schema = z.object({
  name: z.string().min(2, "Please enter your name."),
  email: z.string().email("Please enter a valid email."),
  message: z.string().min(10, "Message should be at least 10 characters."),
});

export default function ContactForm({ ownerEmail }) {
  const [lastSubmissions, setLastSubmissions] = useState([]);
  const [adminKey, setAdminKey] = useState("");
  const [adminLoading, setAdminLoading] = useState(false);

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", message: "" },
    mode: "onChange",
  });

  const canSubmit = useMemo(
    () => form.formState.isValid && !form.formState.isSubmitting,
    [form.formState.isValid, form.formState.isSubmitting]
  );

  const onSubmit = async (values) => {
    try {
      const res = await api.post("/contact", values);
      const created = res.data;

      setLastSubmissions((prev) => [created, ...prev].slice(0, 3));
      toast({
        title: "Message sent",
        description: "Thanks — I’ll get back to you soon.",
      });
      form.reset();
    } catch (e) {
      const msg = e?.response?.data?.detail
        ? String(e.response.data.detail)
        : "Could not send your message. Please try again.";
      toast({
        title: "Send failed",
        description: msg,
        variant: "destructive",
      });
    }
  };

  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(ownerEmail);
      toast({ title: "Copied", description: ownerEmail });


  const fetchAdminRecent = async () => {
    const key = adminKey.trim();
    if (!key) {
      toast({
        title: "Admin key required",
        description: "Enter your admin key to load recent submissions.",
        variant: "destructive",
      });
      return;
    }

    setAdminLoading(true);
    try {
      const res = await api.get("/contact/recent", {
        params: { limit: 20 },
        headers: { "x-admin-key": key },
      });
      setLastSubmissions(res.data.slice(0, 3));
      toast({
        title: "Loaded",
        description: `Fetched ${res.data.length} recent submissions.`,
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
          title: "Failed to load",
          description: "Could not fetch recent submissions.",
          variant: "destructive",
        });
      }
    } finally {
      setAdminLoading(false);
    }
  };

    } catch {
      toast({
        title: "Copy failed",
        description: "Your browser blocked clipboard access.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-5">
      <Card className="border-zinc-200 shadow-sm md:col-span-2">
        <CardHeader>
          <CardTitle className="text-base">Quick contact</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center gap-2 text-sm font-semibold text-zinc-900">
                  <Mail className="h-4 w-4 text-teal-700" />
                  <span className="truncate">{ownerEmail}</span>
                </div>
                <div className="mt-1 text-xs text-zinc-600">
                  Best for proposals, questions, and collaboration.
                </div>
              </div>
              <Button variant="outline" className="border-zinc-200" onClick={copyEmail}>
                <Copy className="mr-2 h-4 w-4" />
                Copy
              </Button>
            </div>
          </div>

          <div>
            <div className="text-sm font-semibold text-zinc-900">Recent submissions</div>
            <div className="mt-2 space-y-2">
              {lastSubmissions.length === 0 ? (
                <div className="text-sm text-zinc-600">
                  Nothing yet — send a message to see it appear here.
                </div>
              ) : (
                lastSubmissions.map((s) => (
                  <div
                    key={s.id}
                    className="rounded-lg border border-zinc-200 bg-white p-3"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="truncate text-sm font-medium text-zinc-900">{s.name}</div>
                      <Badge className="bg-teal-50 text-teal-800" variant="secondary">
                        saved
                      </Badge>
                    </div>
                    <div className="mt-1 truncate text-xs text-zinc-600">{s.email}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="text-xs text-zinc-500">
            Note: form submission is <span className="font-semibold">MOCKED</span> — it only saves locally.
          </div>
        </CardContent>
      </Card>

      <Card className="border-zinc-200 shadow-sm md:col-span-3">
        <CardHeader>
          <CardTitle className="text-base">Send a message</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Your name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input placeholder="you@example.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="message"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Message</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Tell me what you're building, what you need, and your timeline."
                        className="min-h-[130px] resize-y"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-xs text-zinc-500">
                  Response time: usually within 24–48 hours.
                </div>
                <Button
                  type="submit"
                  disabled={!canSubmit}
                  className="bg-teal-700 text-white hover:bg-teal-800"
                >
                  <Send className="mr-2 h-4 w-4" />
                  Send (save locally)
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
