<template>
  <div
    v-if="reportMarkdown"
    class="report-block"
    :class="{ 'block-highlight': reportHighlight }"
  >
    <h3>最终报告</h3>
    <pre class="block-pre">{{ reportMarkdown }}</pre>
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  reportMarkdown: string;
  reportHighlight: boolean;
}>();
</script>
