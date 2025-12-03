<template>
  <Panel title="MCP服务运行及调用数量变化趋势">
    <template #extra>
      <el-button-group>
        <el-button :class="{ active: active === 7 }" @click="active = 7">近一周</el-button>
        <el-button :class="{ active: active === 30 }" @click="active = 30">近一月</el-button>
      </el-button-group>
    </template>
    <div class="abs">
      <div ref="lineChartRef" :style="{ height: '100%', width: '100%' }"/>
    </div>
  </Panel>
</template>

<script lang="ts" setup>
import { nextTick, onBeforeUnmount, onMounted, ref, toRaw, reactive, watch } from 'vue'
import Panel from './panel.vue'
import * as echarts from 'echarts'
import { lineOptionConfig, getLineLegendData, getLineSeriesData, DATE_FORMAT } from './options'
import mcpStatisticsApi from '@/api/mcp-statistics'
import moment from 'moment'

const { getTotalTrend } = mcpStatisticsApi
const active = ref<any>(7)
const lineChartRef = ref()

const map: any = {
  total_service_calls: '服务调用',
  total_tools_calls: '工具调用',
  running_services: '运行中服务',
  stopped_services: '已停止服务',
  error_services: '异常服务'
}

const lineOption = reactive<any>(lineOptionConfig)

const query = async () => {
  const param = {
    start_date: moment().subtract(+active.value, 'day').format(DATE_FORMAT),
    end_date: moment().format(DATE_FORMAT)
  }
  const res = await getTotalTrend(param)
  let dataList = res?.data ?? []
  createOption(dataList)
}

const createOption = (dataList: Array<any>) => {
  const aAxisDatas = dataList.map((g: any) => g.statistics_date)
  lineOption.xAxis.data = aAxisDatas
  const keys = Object.keys(map)
  const values = Object.values(map)
  lineOption.legend.data = values.map((name: any, i: number) => getLineLegendData(name, i))
  lineOption.series = []
  for (let i = 0, len = keys.length; i < len; i++) {
    const key = keys[i]
    const name = map[key]
    lineOption.series.push(getLineSeriesData(name + '', dataList.map(g => g[key] || 0), i))
  }
  initChart()
}

function initChart() {
  // @ts-ignore
  const dom: any = lineChartRef.value
  let myChart = echarts?.getInstanceByDom(dom)
  if (myChart === null || myChart === undefined) {
    myChart = echarts.init(dom)
  }
  // 渲染数据
  myChart.setOption(toRaw(lineOption), true, false)
}

function changeChartSize() {
  const dom: any = lineChartRef.value
  echarts.getInstanceByDom(dom)?.resize()
}

onMounted(() => {
  nextTick(() => {
    query()
    window.addEventListener('resize', changeChartSize)
  })
})

onBeforeUnmount(() => {
  const dom: any = lineChartRef.value
  echarts.getInstanceByDom(dom)?.dispose()
  window.removeEventListener('resize', changeChartSize)
})

watch(() => active.value, () => {
  query()
})
</script>

<style lang="scss">
.abs {
  width: 100%;
  height: 100%;
  position: absolute;
}
</style>