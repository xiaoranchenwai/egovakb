<template>
  <div class="mcp-panel-container">
    <div class="panel-header">
      <h2>{{ title }}</h2>
      <slot name="extra"></slot>
    </div>
    <div class="panel-body">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string;
}>()

</script>

<style lang="scss">
.mcp-panel-container {
  .panel-header {
    width: 100%;
    height: 56px;
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    box-sizing: border-box;
    // border-bottom: 1px solid #E9ECF2;

    h2 {
      font-size: 14px;
      font-weight: 600;
      color: #081126;
    }
  }

  .panel-body {
    width: 100%;
    height: calc(100% - 56px);
    position: relative;
  }
}
</style>