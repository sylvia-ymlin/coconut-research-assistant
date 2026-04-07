export interface SourceItem {
  title: string;
  url: string;
  snippet: string;
  raw: string;
}

export interface ToolCallLog {
  eventId: number;
  agent: string;
  tool: string;
  parameters: Record<string, unknown>;
  result: string;
  noteId: string | null;
  notePath: string | null;
  timestamp: number;
}

export interface TodoTaskView {
  id: number;
  title: string;
  intent: string;
  query: string;
  status: string;
  summary: string;
  sourcesSummary: string;
  sourceItems: SourceItem[];
  notices: string[];
  noteId: string | null;
  notePath: string | null;
  toolCalls: ToolCallLog[];
}

export interface ResearchSessionSummary {
  session_id: number;
  topic: string;
  status: string;
  search_api: string | null;
  created_at: string;
  updated_at: string;
  task_count: number;
  completed_task_count: number;
  report_available: boolean;
}

export interface ResearchSessionDetail extends ResearchSessionSummary {
  report_markdown: string;
  error_detail: string | null;
  report_note_id: string | null;
  report_note_path: string | null;
  todo_items: Array<{
    id: number;
    title: string;
    intent: string;
    query: string;
    status: string;
    summary: string | null;
    sources_summary: string | null;
    notices: string[];
    note_id: string | null;
    note_path: string | null;
  }>;
}
