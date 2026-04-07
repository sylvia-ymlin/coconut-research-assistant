<template>
  <aside class="tasks-list">
    <h3>任务清单</h3>
    <ul>
      <li
        v-for="task in tasks"
        :key="task.id"
        :class="['task-item', { active: task.id === activeTaskId, completed: task.status === 'completed' }]"
      >
        <button
          type="button"
          class="task-button"
          @click="$emit('selectTask', task.id)"
        >
          <span class="task-title">{{ task.title }}</span>
          <span class="task-status" :class="task.status">
            {{ formatTaskStatus(task.status) }}
          </span>
        </button>
        <p class="task-intent">{{ task.intent }}</p>
      </li>
    </ul>
  </aside>
</template>

<script lang="ts" setup>
import type { TodoTaskView } from "../types/research";

defineProps<{
  tasks: TodoTaskView[];
  activeTaskId: number | null;
  formatTaskStatus: (status: string) => string;
}>();

defineEmits<{
  selectTask: [taskId: number];
}>();
</script>
