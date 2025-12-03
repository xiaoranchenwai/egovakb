<template>
  <Card title="MCP工具调用排名">
    <div class="abs">
      <div ref="barChartRef" :style="{ height: '100%', width: '100%' }"/>
    </div>
  </Card>
</template>

<script lang="ts" setup>
import { ref, reactive, toRaw, onMounted, nextTick, onBeforeUnmount } from 'vue'
import Card from './card.vue'
import * as echarts from 'echarts'
import { barOptionConfig, getBarSeriesData } from './options'

const barChartRef = ref()
const barOption = reactive(barOptionConfig)
import mcpStatisticsApi from '@/api/mcp-statistics'

const { getMcpToolStat } = mcpStatisticsApi

const query = async () => {
  const res = await getMcpToolStat()

  let dataList = res?.data?.items ?? []
  createOption(dataList)
}

const createOption = (dataList: Array<any>) => {
  const xAxisData = dataList.map(g => g.tool_name)
  barOption.xAxis[0].data = xAxisData
  const values = dataList.map(g => g.call_count || 0) || []
  barOption.series = getBarSeriesData('工具调用', values)
  initChart()
}

function initChart() {
  // @ts-ignore
  const dom: any = barChartRef.value
  let myChart = echarts?.getInstanceByDom(dom)
  if (myChart === null || myChart === undefined) {
    myChart = echarts.init(dom)
  }
  const series: any = []

  // 渲染数据
  myChart.setOption(toRaw(barOption), true, false)
}

function changeChartSize() {
  const dom: any = barChartRef.value
  echarts.getInstanceByDom(dom)?.resize()
}

onMounted(() => {
  nextTick(() => {
    query()
    window.addEventListener('resize', changeChartSize)
  })
})

onBeforeUnmount(() => {
  const dom: any = barChartRef.value
  echarts.getInstanceByDom(dom)?.dispose()
  window.removeEventListener('resize', changeChartSize)
})
</script>

<style lang="scss">

</style>