<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <button class="back-btn" @click="$emit('goBack')" :disabled="loading">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>
      <h2>🔍 深度研究助手</h2>
    </div>

    <div class="research-info">
      <div class="info-item">
        <label>研究主题</label>
        <p class="topic-display">{{ topic || "选择历史研究或开始新的研究任务" }}</p>
      </div>

      <div class="info-item" v-if="searchApi">
        <label>搜索引擎</label>
        <p>{{ searchApi }}</p>
      </div>

      <div class="info-item" v-if="totalTasks > 0">
        <label>研究进度</label>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${(completedTasks / totalTasks) * 100}%` }"></div>
        </div>
        <p class="progress-text">{{ completedTasks }} / {{ totalTasks }} 任务完成</p>
      </div>

      <div class="info-item history-section">
        <div class="history-header">
          <label>Recent Research</label>
          <span class="history-count">{{ sessions.length }}</span>
        </div>

        <div v-if="sessions.length" class="session-list">
          <button
            v-for="session in sessions"
            :key="session.session_id"
            type="button"
            class="session-card"
            :class="{ active: session.session_id === activeSessionId }"
            :disabled="loading"
            @click="$emit('openSession', session.session_id)"
          >
            <div class="session-card-top">
              <span class="session-status" :data-status="session.status">
                {{ formatStatus(session.status) }}
              </span>
              <span class="session-time">{{ formatTime(session.updated_at) }}</span>
            </div>
            <p class="session-topic">{{ session.topic }}</p>
            <div class="session-meta">
              <span>{{ session.completed_task_count }}/{{ session.task_count }} tasks</span>
              <span v-if="session.search_api">{{ session.search_api }}</span>
            </div>
          </button>
        </div>

        <p v-else class="history-empty">还没有历史研究记录。</p>
      </div>
    </div>

    <div class="sidebar-actions">
      <button class="new-research-btn" @click="$emit('startNewResearch')">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
        </svg>
        开始新研究
      </button>
    </div>
  </aside>
</template>

<script lang="ts" setup>
import type { ResearchSessionSummary } from "../types/research";

defineProps<{
  loading: boolean;
  topic: string;
  searchApi: string;
  totalTasks: number;
  completedTasks: number;
  sessions: ResearchSessionSummary[];
  activeSessionId: number | null;
}>();

defineEmits<{
  goBack: [];
  startNewResearch: [];
  openSession: [sessionId: number];
}>();

function formatStatus(status: string): string {
  const labels: Record<string, string> = {
    running: "进行中",
    completed: "已完成",
    failed: "失败"
  };
  return labels[status] ?? status;
}

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}
</script>
