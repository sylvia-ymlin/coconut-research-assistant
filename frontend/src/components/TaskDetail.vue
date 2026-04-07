<template>
  <article class="task-detail" v-if="task">
    <header class="task-header">
      <div>
        <h3>{{ task.title || "当前任务" }}</h3>
        <p class="muted" v-if="task.intent">
          {{ task.intent }}
        </p>
      </div>
      <div class="task-chip-group">
        <span class="task-label">查询：{{ task.query || "" }}</span>
        <span
          v-if="task.noteId"
          class="task-label note-chip"
          :title="task.noteId"
        >
          笔记：{{ task.noteId }}
        </span>
        <span
          v-if="task.notePath"
          class="task-label note-chip path-chip"
          :title="task.notePath"
        >
          <span class="path-label">路径：</span>
          <span class="path-text">{{ task.notePath }}</span>
          <button
            class="chip-action"
            type="button"
            @click="copyNotePath(task.notePath)"
          >
            复制
          </button>
        </span>
      </div>
    </header>

    <section v-if="task.notices.length" class="task-notices">
      <h4>系统提示</h4>
      <ul>
        <li v-for="(notice, idx) in task.notices" :key="`${notice}-${idx}`">
          {{ notice }}
        </li>
      </ul>
    </section>

    <section
      class="sources-block"
      :class="{ 'block-highlight': sourcesHighlight }"
    >
      <h3>最新来源</h3>
      <template v-if="task.sourceItems.length">
        <ul class="sources-list">
          <li
            v-for="(item, index) in task.sourceItems"
            :key="`${item.title}-${index}`"
            class="source-item"
          >
            <a
              class="source-link"
              :href="item.url || '#'"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ item.title || item.url || `来源 ${index + 1}` }}
            </a>
            <div v-if="item.snippet || item.raw" class="source-tooltip">
              <p v-if="item.snippet">{{ item.snippet }}</p>
              <p v-if="item.raw" class="muted-text">{{ item.raw }}</p>
            </div>
          </li>
        </ul>
      </template>
      <p v-else class="muted">暂无可用来源</p>
    </section>

    <section
      class="summary-block"
      :class="{ 'block-highlight': summaryHighlight }"
    >
      <h3>任务总结</h3>
      <pre class="block-pre">{{ task.summary || "暂无可用信息" }}</pre>
    </section>

    <section
      class="tools-block"
      :class="{ 'block-highlight': toolHighlight }"
      v-if="task.toolCalls.length"
    >
      <h3>工具调用记录</h3>
      <ul class="tool-list">
        <li
          v-for="entry in task.toolCalls"
          :key="`${entry.eventId}-${entry.timestamp}`"
          class="tool-entry"
        >
          <div class="tool-entry-header">
            <span class="tool-entry-title">
              #{{ entry.eventId }} {{ entry.agent }} → {{ entry.tool }}
            </span>
            <span
              v-if="entry.noteId"
              class="tool-entry-note"
            >
              笔记：{{ entry.noteId }}
            </span>
          </div>
          <p v-if="entry.notePath" class="tool-entry-path">
            笔记路径：
            <button
              class="link-btn"
              type="button"
              @click="copyNotePath(entry.notePath)"
            >
              复制
            </button>
            <span class="path-text">{{ entry.notePath }}</span>
          </p>
          <p class="tool-subtitle">参数</p>
          <pre class="tool-pre">{{ formatToolParameters(entry.parameters) }}</pre>
          <template v-if="entry.result">
            <p class="tool-subtitle">执行结果</p>
            <pre class="tool-pre">{{ formatToolResult(entry.result) }}</pre>
          </template>
        </li>
      </ul>
    </section>
  </article>

  <article class="task-detail" v-else>
    <p class="muted">等待任务规划或执行结果。</p>
  </article>
</template>

<script lang="ts" setup>
import type { TodoTaskView } from "../types/research";

defineProps<{
  task: TodoTaskView | null;
  summaryHighlight: boolean;
  sourcesHighlight: boolean;
  toolHighlight: boolean;
  copyNotePath: (path: string | null | undefined) => void | Promise<void>;
  formatToolParameters: (parameters: Record<string, unknown>) => string;
  formatToolResult: (result: string) => string;
}>();
</script>
