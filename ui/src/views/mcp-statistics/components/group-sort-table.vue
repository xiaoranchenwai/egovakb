<template>
  <Card title="MCP模板分类排名" class="no-header-margin-bottom">
    <template #extra>
      <el-button-group>
        <el-button v-for="(value,key,i) of map" :key="key" :class="{ active: active === key }" @click="active = key">
          {{ value }}
        </el-button>
      </el-button-group>
    </template>

    <div class="abs" ref="dom">
      <div class="content-box">
        <div class="table-box">
          <el-loading v-model="loading">
            <el-table :data="dataList" :table-layout="'auto'" :height="height">
              <el-table-column type="index" label="序号" width="55"/>
              <el-table-column prop="group_name" label="模板分类" show-overflow-tooltip/>
              <el-table-column prop="templates_count" label="模板数量" show-overflow-tooltip/>
              <el-table-column prop="services_count" label="服务发布数据" show-overflow-tooltip/>
              <el-table-column prop="call_count" label="服务调用次数" show-overflow-tooltip/>
              <el-table-column prop="rank_value" label="工具调用次数" show-overflow-tooltip/>
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
import { ref, reactive, toRaw, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import Card from './card.vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import mcpStatisticsApi from '@/api/mcp-statistics'
const map = {
  templates_count: '模板数量',
  services_count: '服务发布',
  call_count: '服务调用'
}
const { getMcpGroupStat } = mcpStatisticsApi
const active = ref<string>('templates_count')
const loading = ref<boolean>(false)
const height = ref<number>(250)
const dataList = ref<Array<any>>([])
const dom = ref()
const paging = reactive({
  pageIndex: 1,
  pageSize: 5,
  total: 0
})
const reset = ()=> {
  paging.pageIndex = 1
  paging.pageSize = 5
  query()
};
const query = async () => {
  const param = {
    desc: true,
    order_by: active.value,
    paging: {page: paging.pageIndex, size: paging.pageSize}
  }
  const res = await getMcpGroupStat(param)
  let list = res?.data?.items ?? []
  dataList.value = list;
  paging.total = res?.data?.total ?? 0
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
  reset()
  nextTick(() => {
    changeSize()
    window.addEventListener('resize', changeSize)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', changeSize)
})

watch(() => active.value, () => {
  reset()
})
</script>

<style lang="scss" scoped>
.content-box {
  width: 100%;
  height: 100%;
  position: relative;
  padding: 8px 16px;
  box-sizing: border-box;

  .table-box {

  }

  .pagination-box {

  }
}
</style>