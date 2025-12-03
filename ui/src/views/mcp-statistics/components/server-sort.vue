<template>
  <Card title="MCP服务调用排名">
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

import mcpStatisticsApi from '@/api/mcp-statistics'

const { getMcpServiceStat } = mcpStatisticsApi
const barChartRef = ref()
const barOption = reactive(barOptionConfig)

const query = async () => {
  const res = await getMcpServiceStat()

  let dataList = res?.data?.items ?? []
  createOption(dataList)
}

const createOption = (dataList: Array<any>) => {
  const xAxisData = dataList.map(g => g.service_name)
  barOption.xAxis[0].data = xAxisData
  const values = dataList.map(g => g.call_count || 0) || []
  barOption.series = getBarSeriesData('服务调用', values)
  initChart()
}

function initChart() {
  // @ts-ignore
  const dom: any = barChartRef.value
  let myChart = echarts?.getInstanceByDom(dom)
  if (myChart === null || myChart === undefined) {
    myChart = echarts.init(dom)
  }
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