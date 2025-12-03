<template>
  <div class="marketplace-add-container">
    <header>
      <el-icon class="mr-8" @click="goBack">
        <ArrowLeftBold/>
      </el-icon>
      <h2>新增MCP模板</h2>

      <div class="btns">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="onCreate" :loading="loading">确定</el-button>
      </div>
    </header>
    <main>
      <div v-if="loading" class="py-10">
        <el-skeleton :rows="10" animated/>
      </div>
      <ModuleForm ref="moduleForm"
                  :categories="categories" :loading="creatingModule" :isEdit="false" @submit="createModule"
                  @cancel="goBack" @categoriesLoaded="updateCategories"/>

    </main>
  </div>
</template>

<script lang="ts" setup>

import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import mcpSquareApi from '@/api/mcp-square'
import mcpGroupApi from '@/api/mcp-group'
import { useRoute, useRouter } from 'vue-router'
import ModuleForm from '@/views/marketplace/components/ModuleForm.vue'

const route = useRoute()
const router = useRouter()
const categories = ref<Array<any>>([])
const loading = ref(false)
const moduleForm = ref()

const creatingModule = ref(false)

onMounted(() => {
  loadCategories()
})
const loadCategories = async () => {
  try {
    const res = await mcpGroupApi.listGroup()
    if (res.code === 200) {
      categories.value = res.data
    } else {
      ElMessage.error(res.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('加载分类失败:', error)
    ElMessage.error('加载分类失败')
  } finally {

  }
}

// 新建模板
const createModule = async (moduleForm: any) => {
  creatingModule.value = true
  try {
    const res = await mcpSquareApi.createModule(moduleForm, creatingModule)

    if (res.code === 200) {
      ElMessage.success('模板创建成功')
    } else {
      ElMessage.error(res.message || '创建模板失败')
    }
  } catch (error) {
    console.error('创建模板失败:', error)
    ElMessage.error('创建模板失败')
  } finally {
    creatingModule.value = false
  }
}

// 更新分类列表
const updateCategories = (newCategories: Array<any>) => {
  if (newCategories && newCategories.length > 0) {
    categories.value = newCategories
  }
}

const goBack = () => {
  router.push('/mcp/marketplace')
}

const onCreate = () => {
  console.log(moduleForm.value)
  // @ts-ignore
  moduleForm.value?.submitForm?.();
}
</script>

<style lang="scss">
.marketplace-add-container {
  width: 100%;
  height: 100%;
  position: relative;

  > header {
    width: 100%;
    height: 56px;
    position: relative;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding-left: calc(2 * var(--app-base-px) + 4px);
    border-bottom: 1px solid #e9ecf2;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: normal;
      color: #081126;
      font-weight: 600;
    }

    .btns {
      position: absolute;
      right: 20px;
    }
  }

  > main {
    width: 100%;
    height: calc(100% - 56px);
    position: relative;
    padding: 0 12px 12px 12px;
    box-sizing: border-box;
    overflow-y: auto;

    .module-form {
      .form-actions {
        display: none;
        //position: fixed;
        //z-index: 999;
        //top: 75px;
        //right: 40px;
      }
    }
  }
}

</style>