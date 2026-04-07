<template>
  <header class="status-bar">
    <div class="status-main">
      <div class="status-chip" :class="{ active: loading }">
        <span class="dot"></span>
        {{ loading ? "研究进行中" : "研究流程完成" }}
      </div>
      <span class="status-meta">
        任务进度：{{ completedTasks }} / {{ effectiveTotalTasks }}
        · 阶段记录 {{ progressLogs.length }} 条
      </span>
    </div>
    <div class="status-controls">
      <button
        v-if="showReportButton"
        class="secondary-btn report-cta"
        @click="$emit('viewReport')"
      >
        查看最终报告
      </button>
      <button class="secondary-btn" @click="$emit('toggleLogs')">
        {{ logsCollapsed ? "展开流程" : "收起流程" }}
      </button>
    </div>
  </header>

  <div class="timeline-wrapper" v-show="!logsCollapsed && progressLogs.length">
    <transition-group name="timeline" tag="ul" class="timeline">
      <li v-for="(log, index) in progressLogs" :key="`${log}-${index}`">
        <span class="timeline-node"></span>
        <p>{{ log }}</p>
      </li>
    </transition-group>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";

const props = defineProps<{
  loading: boolean;
  completedTasks: number;
  totalTasks: number;
  progressLogs: string[];
  logsCollapsed: boolean;
  showReportButton: boolean;
}>();

defineEmits<{
  toggleLogs: [];
  viewReport: [];
}>();

const effectiveTotalTasks = computed(() => props.totalTasks || 1);
</script>
