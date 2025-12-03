<template>
  <Card title="MCP模板排名">
    <template #extra>
      <el-button-group>
        <el-button v-for="(value,key,i) of map" :key="key" :class="{ active: active === key }" @click="active = key">
          {{ value }}
        </el-button>
      </el-button-group>
    </template>

    <div class="abs">
      <div ref="barChartRef" :style="{ height: '100%', width: '100%' }"/>
    </div>
  </Card>
</template>

<script lang="ts" setup>
import { ref, reactive, toRaw, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import Card from './card.vue'
import * as echarts from 'echarts'
import { barOptionConfig, getBarSeriesData } from './options'
import mcpStatisticsApi from '@/api/mcp-statistics'

const { getMcpTemplateStat } = mcpStatisticsApi
const active = ref<any>('services_count')
const barChartRef = ref()
const barOption = reactive(barOptionConfig)

const map: any = {
  services_count: '服务发布',
  call_count: '服务调用'
}
const query = async () => {
  const param = {
    desc: true,
    limit: 10,
    order_by: active.value,
    paging: {page: 1, size: 10}
  }
  const res = await getMcpTemplateStat(param)
  let dataList = res?.data?.items ?? []
  createOption(dataList)
}

const createOption = (dataList: Array<any>) => {
  const xAxisData = dataList.map(g => g.module_name)
  barOption.xAxis[0].data = xAxisData
  const values = dataList.map(g => g[active.value])
  barOption.series = getBarSeriesData(map[active.value], values)
  initChart()
}

function initChart() {
  // @ts-ignore
  const dom: any = barChartRef.value
  let myChart = echarts?.getInstanceByDom(dom)
  if (myChart === null || myChart === undefined) {
    myChart = echarts.init(dom)
  }
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

watch(() => active.value, () => {
  query()
})
</script>

<style lang="scss">

</style>