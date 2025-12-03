<template>
    <div class="mcp-card-container">
        <div class="card-header">
            <h2>{{ title }}</h2>
            <slot name="extra"></slot>
        </div>
        <div class="card-body">
            <slot></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps<{
    title: string;
}>();

</script>

<style lang="scss">
.mcp-card-container {
    width: 100%;
    height: 100%;
    position: relative;
    border: 1px solid #E9ECF2;
    border-radius: 4px;

    .card-header {
        width: 100%;
        height: 39px;
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 15px;
        box-sizing: border-box;

        // border-bottom: 1px solid#E9ECF2;
        background-image: linear-gradient(90deg, #dfeaff63 0%, #f5f7fa4d 100%);

        h2 {
            font-size: 14px;
            font-weight: 600;
            color: #223355;
        }
    }

    .card-body {
        width: 100%;
        height: calc(100% - 39px);
        position: relative;
        box-sizing: border-box;
    }
}
</style>