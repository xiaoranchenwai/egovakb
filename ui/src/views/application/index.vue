<template>
    <div class="full-container">
        <el-row :gutter="0">
            <el-col :span="expand ? 4 : 0" class="h-full">
                <div class="left-container">
                    <GroupDrawer v-model:selectedGroup="selectedGroup"></GroupDrawer>
                </div>
            </el-col>
            <el-col :span="expand ? 20 : 24" :class="{ expand: !expand }">
                <div class="toggle-btn" @click="onToggleShow">
                    <el-icon>
                        <CaretLeft v-if="expand" />
                        <CaretRight v-else />
                    </el-icon>
                </div>

                <router-view :selectedGroup="selectedGroup"></router-view>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import GroupDrawer from "./component/GroupDrawer.vue";

const expand = ref<boolean>(true);
const selectedGroup = ref<any>(null)

const span = computed(() => {
    if (expand.value) {
        return 4;
    } else {
        return 0;
    }
});

const restSpan = computed(() => {
    return (24 - span.value);
});

const onToggleShow = () => {
    expand.value = !expand.value;
};

watch(selectedGroup, (newVal) => {
    // console.log('index selectedGroup', newVal)
})
</script>

<style scoped lang="scss">
.full-container {
    width: 100%;
    height: 100%;
    position: relative;

    .el-row {
        height: 100%;

        .el-col {
            position: relative;
            transition: all 0.2s;
        }

        .el-col-24 {
            .icon {
                left: 0;
            }
        }
    }

    .left-container {
        width: 100%;
        height: 100%;
        position: relative;
        background-color: var(--app-view-bg-color);
    }

    .toggle-btn {
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 16px;
        height: 64px;
        background: #A8B4C8;
        border-radius: 0 8px 8px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 10;
        color: #fff;

        &:hover {
            background: var(--el-color-primary);
        }
    }
}
</style>