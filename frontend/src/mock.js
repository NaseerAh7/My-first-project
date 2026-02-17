// MOCK DATA for Naseer Ahmad Zarmati portfolio
// This file is intentionally frontend-only so we can later swap to backend APIs cleanly.

export const profile = {
  name: "Naseer Ahmad Zarmati",
  tagline: "Web Developer & Computer Science Student",
  location: "",
  bioShort:
    "I build clean, fast web apps with thoughtful UI, strong fundamentals, and a focus on shipping.",
  bioLong:
    "I'm a web developer and computer science student who enjoys building modern interfaces and reliable backend services. I care about performance, accessibility, and clear user flows — and I love turning rough ideas into polished products.",
  email: "naseer@example.com",
  socials: [
    { label: "GitHub", href: "https://github.com/", type: "github" },
    { label: "LinkedIn", href: "https://www.linkedin.com/", type: "linkedin" },
    { label: "X", href: "https://x.com/", type: "x" },
  ],
};

export const skills = {
  featured: [
    {
      title: "Frontend",
      items: [
        "React",
        "React Router",
        "Tailwind CSS",
        "shadcn/ui",
        "Forms & Validation",
      ],
    },
    {
      title: "Backend",
      items: ["FastAPI", "REST APIs", "MongoDB", "Authentication Basics"],
    },
    {
      title: "Quality",
      items: ["Component Design", "State Management", "Error Handling", "DX"],
    },
  ],
  chips: [
    "React",
    "FastAPI",
    "MongoDB",
    "Tailwind",
    "TypeScript",
    "Node.js",
    "Git",
    "Testing",
  ],
};

export const projects = [
  {
    id: "proj-1",
    title: "Campus Companion",
    subtitle: "A student-friendly dashboard for schedules, reminders, and tasks.",
    year: "2025",
    tags: ["React", "UX", "Product"],
    links: {
      live: "#",
      repo: "#",
    },
    highlights: [
      "Quick-add tasks with keyboard-first UX",
      "Responsive layouts with accessible components",
      "Local-first persistence (offline-friendly)",
    ],
  },
  {
    id: "proj-2",
    title: "API Starter Kit",
    subtitle: "A FastAPI boilerplate with clean structure and error handling.",
    year: "2025",
    tags: ["FastAPI", "MongoDB", "REST"],
    links: {
      live: "#",
      repo: "#",
    },
    highlights: [
      "Opinionated folder structure",
      "Input validation with Pydantic",
      "CRUD examples + pagination patterns",
    ],
  },
  {
    id: "proj-3",
    title: "Portfolio vNext",
    subtitle: "A modern portfolio with smooth sections and interactive project cards.",
    year: "2025",
    tags: ["UI", "Animation", "Brand"],
    links: {
      live: "#",
      repo: "#",
    },
    highlights: [
      "Teal accent system and minimalist layout",
      "Micro-interactions for buttons & cards",
      "Contact form with validation",
    ],
  },
];

export const about = {
  bullets: [
    "Enjoys building modern React UIs with clean component patterns",
    "Interested in backend APIs, data modeling, and scalable architecture",
    "Always learning — currently improving data structures & system design",
  ],
  now: [
    { label: "Currently learning", value: "Advanced React patterns + FastAPI" },
    { label: "Open to", value: "Internships, freelance, collaboration" },
  ],
};
