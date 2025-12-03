<template>
  <div class="mcp-statistic-page">
    <div class="content-container">
      <div class="content-header">
        <h2>统计分析</h2>
      </div>
      <div class="content-body">
        <el-row :gutter="0" class="stats-cards mb-36">
          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <Panel title="MCP统计">
              <MCPStatOverview></MCPStatOverview>
            </Panel>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <MetricsTrend></MetricsTrend>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <ServerCountTrend></ServerCountTrend>
          </el-col>
        </el-row>

        <Panel title="MCP统计">
          <template #extra>
            <el-button-group>
              <el-button :class="{ active: active === '1' }" @click="active = '1'">图表</el-button>
              <el-button :class="{ active: active === '2' }" @click="active = '2'">表格</el-button>
            </el-button-group>
          </template>
          <div class="grid-container" v-if="showChart">
            <GroupSort></GroupSort>

            <TemplateSort></TemplateSort>

            <ServerSort></ServerSort>

            <ToolSort></ToolSort>
          </div>

          <div class="grid-container" v-else>
            <GroupSortTable></GroupSortTable>

            <TemplateSortTable></TemplateSortTable>

            <ServerSortTable></ServerSortTable>

            <ToolSortTable></ToolSortTable>
          </div>
        </Panel>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import Panel from './components/panel.vue'
import Card from './components/card.vue'
import MCPStatOverview from './components/mcp-overview.vue'
import MetricsTrend from './components/metrics-trend.vue'
import ServerCountTrend from './components/server-count-trend.vue'

import GroupSort from './components/group-sort.vue'
import TemplateSort from './components/template-sort.vue'
import ServerSort from './components/server-sort.vue'
import ToolSort from './components/tool-sort.vue'

import GroupSortTable from './components/group-sort-table.vue'
import TemplateSortTable from './components/template-sort-table.vue'
import ServerSortTable from './components/server-sort-table.vue'
import ToolSortTable from './components/tool-sort-table.vue'

const active = ref('1')
const showChart = computed(() => {
  return active.value === '1'
})
const showTable = computed(() => {
  return active.value === '2'
})
</script>
<style lang="scss">
.mcp-statistic-page {
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  position: relative;
  padding: 20px;
  box-sizing: border-box;

  .content-container {
    width: 100%;
    height: 100%;
    background-color: #FFFFFF;
  }

  .content-header {
    width: 100%;
    height: 56px;
    position: relative;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding-left: 20px;
    box-sizing: border-box;
    border-bottom: 1px solid #E9ECF2;

    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #081126;
    }
  }

  .content-body {
    width: 100%;
    height: calc(100% - 56px);
    position: relative;
    overflow-y: auto;

    .abs {
      width: 100%;
      height: 100%;
      position: absolute;
    }

    .stats-cards {
      width: 100%;
      height: 475px;
      position: relative;

      .mcp-panel-container {
        height: 100%;
        border-right: 1px solid #E9ECF2;
        border-bottom: 1px solid #E9ECF2;
      }

      .el-col {
        height: 100%;

        &:last-child {
          .mcp-panel-container {
            border-right: none;
          }
        }
      }
    }

    .grid-container {
      width: 100%;
      height: 741px;
      position: relative;
      padding: 0 20px 0 20px;
      box-sizing: border-box;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      grid-template-rows: repeat(2, 1fr);
      gap: 16px;

      .grid-item {
        border: 1px solid #E9ECF2;
      }
      .no-header-margin-bottom {
        .card-header {
          margin-bottom: 0;
        }        
      }
      .content-box {
        width: 100%;
        height: 100%;
        position: relative;
        padding: 8px 16px 0;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;      

        .table-box {
          flex: 1;
          width: 100%;
          position: relative;
        }

        .pagination-box {
          width: 100%;
          height: 60px;
          position: relative;
          display: flex;
          flex-direction: row;
          justify-content: flex-end;
          align-items: center;
        }
      }
    }

    .el-button-group {
      --el-border-radius-base: 4px;

      .el-button {
        width: 74px;
        border-color: #F5F7FA;
        background-color: #F5F7FA;
        cursor: pointer;

        &:hover, &.active {
          background-color: #F0F9FF;
          color: #3388FF;
          border-radius: 4px;
          z-index: 1;
        }

        &.active {
          z-index: 2;
          font-weight: 500;
          border-color: #3388FF !important;
        }
      }
    }
  }
}
</style>