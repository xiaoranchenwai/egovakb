<template>
  <Card title="MCP服务调用排名" class="no-header-margin-bottom">

    <div class="abs" ref="dom">
      <div class="content-box">
        <div class="table-box">
          <el-loading v-model="loading">
            <el-table :data="dataList" :table-layout="'auto'" :height="height">
              <el-table-column type="index" label="序号" width="55"/>
              <el-table-column prop="service_name" label="服务名称" show-overflow-tooltip/>
              <el-table-column prop="module_name" label="模板名称" show-overflow-tooltip/>
              <el-table-column prop="group_name" label="模板分类" show-overflow-tooltip/>
              <el-table-column prop="call_count" label="服务调用次数" show-overflow-tooltip/>
              <el-table-column prop="rate" label="调用成功率" show-overflow-tooltip/>
              <el-table-column prop="updated_at" label="更新时间" show-overflow-tooltip/>
            </el-table>
          </el-loading>
        </div>
        <div class="pagination-box">
          <el-config-provider :locale="zhCn">
            <el-pagination
                :current-page="paging.pageIndex" :page-size="paging.pageSize" :page-sizes="[5, 10, 15, 20]"
                :background="true" layout="total, sizes, prev, pager, next, jumper" :total="paging.total" size="small"
                @size-change="handleSizeChange" @current-change="handleCurrentChange" class="pagination"/>
          </el-config-provider>
        </div>
      </div>

    </div>
  </Card>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, nextTick, onBeforeUnmount } from 'vue'
import Card from './card.vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import mcpStatisticsApi from '@/api/mcp-statistics'

const { getMcpServiceStat } = mcpStatisticsApi
const loading = ref<boolean>(false)
const height = ref<number>(250)
const dataList = ref<Array<any>>([])
const dom = ref()
const paging = reactive({
  pageIndex: 1,
  pageSize: 5,
  total: 0
})

const query = async () => {
  const res = await getMcpServiceStat(paging.pageIndex, paging.pageSize, loading)
  const list = res?.data?.items ?? []
  dataList.value = list.map((g: any) => {
    const rate = g.call_count > 0 ? ((g.success_count / g.call_count) * 100).toFixed(1) + '%' : '0%'
    return { ...g, rate }
  })
  paging.total = res?.data.total ?? 0
}
const handleSizeChange = (pageSize: number) => {
  paging.pageSize = pageSize
  query()
}

const handleCurrentChange = (pageIndex: number) => {
  paging.pageIndex = pageIndex
  query()
}
const changeSize = () => {
  height.value = (dom.value.clientHeight || 250) - 60
}
onMounted(() => {
  paging.pageIndex = 1
  paging.pageSize = 5
  query()
  nextTick(() => {
    changeSize()
    window.addEventListener('resize', changeSize)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', changeSize)
})
</script>

<style lang="scss" scoped>

</style>