# GraphRAG AI — PDF Assistant (Frontend Only)

A premium, ChatGPT/Claude/Perplexity-style dashboard UI for a GraphRAG-powered
PDF assistant. This is **frontend only** — every value (chat messages,
documents, graph stats) is dummy data. There is no backend, no API calls, and
no authentication.

## Tech stack

- React 18 + Vite + TypeScript
- Tailwind CSS
- Framer Motion (animations)
- lucide-react (icons)
- react-router-dom (page navigation)

## Getting started

```bash
npm install
npm run dev
```

Then open the URL Vite prints (usually `http://localhost:5173`).

To type-check and build for production:

```bash
npm run build
npm run preview
```

## Pages

- `/` and `/chat` — Dashboard: chat interface + PDF viewer panel
- `/documents` — Documents table with search
- `/knowledge-graph` — Knowledge graph stats + graph canvas placeholder
- `/settings` — Theme, model, chunking, and temperature settings

Clicking **Upload PDFs** in the sidebar opens the upload modal (drag & drop,
simulated progress bar, and success state) from anywhere in the app.

## Project structure

```
src/
  components/
    layout/      Sidebar, Navbar, MobileNav
    chat/        ChatWindow, ChatBubble, MessageInput, SourceCard, TypingIndicator, SuggestedPrompts
    pdf/         PDFViewer, DocumentInfo, RecentDocuments
    upload/      UploadModal
    graph/       KnowledgeGraphCard
    documents/   DocumentTable
    settings/    SettingsCard
    common/      LoadingSkeleton
  pages/         Dashboard, Documents, KnowledgeGraph, Settings
  data/          dummyData.ts (all mock data lives here)
  types/         Shared TypeScript interfaces
  utils/         cn.ts (class merge helper), AppContext.tsx
```

## Notes

- All data in `src/data/dummyData.ts` — swap in real API calls later without
  touching component markup.
- Colors are defined as custom Tailwind tokens (`app.bg`, `app.sidebar`,
  `app.accent`, etc.) in `tailwind.config.ts`.
