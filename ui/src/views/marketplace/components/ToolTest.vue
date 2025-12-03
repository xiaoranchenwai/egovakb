<template>
  <div class="flex tool-test">
    <!-- 左侧工具列表 -->
    <div class="mcp-tool-list border-r">
      <div class="mb-4">
        <el-input v-model="toolSearchQuery" placeholder="搜索工具名称" suffix-icon="Search" clearable class="custom"/>
      </div>

      <div class="tools-list">
        <div v-for="tool in filteredTools" :key="tool.function_name" class="tool-card mb-3 cursor-pointer"
          :class="{ 'tool-card-active': currentTool && currentTool.function_name === tool.function_name }"
          @click="selectTool(tool)">
          <el-text truncated>
            <h3 class="text-lg font-bold mb-1">{{ tool.name }}</h3>
          </el-text>
          <el-text truncated>{{ tool.description }}</el-text>
        </div>

        <el-empty v-if="filteredTools.length === 0" description="没有找到工具" />
      </div>
    </div>

    <!-- 右侧工具详情和测试区域 -->
    <div class="tool-test-content">
      <div v-if="currentTool" class="tool-test-area">
        <div class="mb-6">
          <h2 class="text-xl font-bold mb-2 text-primary">{{ currentTool.name }}</h2>
          <p class="text-gray-600 mb-4 whitespace-pre-line">{{ currentTool.description }}</p>

          <!-- 参数输入表单 -->
          <el-card shadow="hover" class="mb-4 tool-params-card">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-medium">参数设置</span>
              </div>
            </template>

            <el-form :model="testParams" label-position="top">
              <el-form-item v-for="param in getToolParams()" :key="param.name"
                :label="param.name + (param.required ? ' (必填)' : '')">
                <div class="text-sm text-gray-500 mb-1">{{ param.type }}</div>
                <el-input v-model="testParams[param.name]" :placeholder="'请输入' + param.name" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="testTool" :loading="testing" class="w-full test-button">
                  执行测试
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 测试结果 -->
          <el-card v-if="testResult || testError" shadow="hover" class="result-card">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-medium">测试结果</span>
              </div>
            </template>

            <el-alert v-if="testError" :title="testError" type="error" show-icon class="mb-3" />
            <div v-else class="result-content-wrapper">
              <pre class="whitespace-pre-wrap result-content">{{ formatResult(testResult) }}</pre>
            </div>
          </el-card>
        </div>
      </div>

      <el-empty v-else description="请选择要测试的工具" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, ref, computed } from 'vue'
import type { McpToolInfo, McpToolParameter } from '@/api/type/mcp-square'
import mcpSquareApi from '@/api/mcp-square'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  moduleId: number
  moduleTools: McpToolInfo[]
}>()

// 本地状态
const toolSearchQuery = ref('')
const currentTool = ref<McpToolInfo | null>(null)
const testParams = ref<Record<string, any>>({})
const testResult = ref<any>(null)
const testError = ref<string | null>(null)
const testing = ref(false)

// 过滤工具列表
const filteredTools = computed(() => {
  if (!toolSearchQuery.value) return props.moduleTools
  
  const query = toolSearchQuery.value.toLowerCase()
  return props.moduleTools.filter(tool =>
    tool.name.toLowerCase().includes(query) ||
    (tool.description && tool.description.toLowerCase().includes(query))
  )
})

// 选择工具
function selectTool(tool: McpToolInfo) {
  currentTool.value = tool
  testParams.value = {}
  testResult.value = null
  testError.value = null
}

// 获取工具参数列表
function getToolParams(): McpToolParameter[] {
  if (!currentTool.value?.parameters) return []
  return currentTool.value.parameters
}

// 测试工具
async function testTool() {
  if (!currentTool.value) return
  
  testResult.value = null
  testError.value = null
  testing.value = true

  try {
    // 由于新的工具没有ID，我们需要使用模块ID和函数名来调用
    const toolName = currentTool.value.function_name
    const moduleId = props.moduleId

    // 构建调用参数对象
    const params: Record<string, any> = {}
    for (const param of getToolParams()) {
      // 如果有参数值，则添加到请求中
      if (testParams.value[param.name] !== undefined && testParams.value[param.name] !== '') {
        // 尝试将字符串转换为适当的类型
        let value = testParams.value[param.name]
        try {
          // 如果参数是数组类型且提供的是字符串，尝试解析成数组
          if ((param.type.includes('List') || param.type.includes('list')) && typeof value === 'string') {
            // 尝试解析为JSON数组
            if (value.trim().startsWith('[') && value.trim().endsWith(']')) {
              value = JSON.parse(value)
            }
            // 否则按逗号分隔处理
            else {
              value = value.split(',').map(item => {
                const trimmed = item.trim()
                // 尝试将数字字符串转换为数字
                if (!isNaN(Number(trimmed))) {
                  return Number(trimmed)
                }
                return trimmed
              })
            }
          }
          // 如果参数是数字类型且提供的是字符串，尝试解析成数字
          else if ((param.type.includes('int') || param.type.includes('float')) && typeof value === 'string') {
            value = Number(value)
          }
          // 如果参数是字典类型且提供的是字符串，尝试解析成对象
          else if ((param.type.includes('Dict') || param.type.includes('dict')) && typeof value === 'string') {
            if (value.trim().startsWith('{') && value.trim().endsWith('}')) {
              value = JSON.parse(value)
            }
          }
        } catch (e) {
          console.warn(`无法解析参数 ${param.name} 的值`, e)
          // 如果解析失败，使用原始值
        }

        params[param.name] = value
      }
    }

    // 直接使用marketplace API中提供的testModuleFunction方法
    const data = await mcpSquareApi.testModuleFunction(moduleId, toolName, params)
    testResult.value = data.data
  } catch (error: any) {
    console.error("工具测试失败", error)
    testError.value = error.response?.data?.detail || error.message || '执行失败'
  } finally {
    testing.value = false
  }
}

// 格式化结果显示
function formatResult(result: any) {
  if (typeof result === 'object') {
    return JSON.stringify(result, null, 2)
  }
  return result
}
</script>

<style scoped>
.mcp-tool-list {
  width: 400px;
  padding-right: 20px;
  height: 100%;
  overflow-y: auto;
}

.flex {
  display: flex;
  height: 100%;
}

.tool-test-content {
  flex: 1;
  padding-left: 20px;
  overflow-y: auto;
}

.tools-list {
  overflow-y: auto;
}

.tool-card {
  padding: 12px;
  border-radius: 4px;
  transition: all 0.2s ease;
  background-color: #FFFFFF;
  border: 1px solid #DDE1EB;
}

.tool-card:hover {
  background-color: #F0F9FF;
  transform: translateY(-2px);
  border-color: #F0F9FF;
}

.tool-card-active {
  background-color: #e6f0ff;
  border-color: #a0cfff;
  box-shadow: 0 2px 10px rgba(160, 207, 255, 0.3);
}

.tool-params-card {
  background-color: #FFFFFF;
  border-radius: 8px;
}

.test-button {
  margin-top: 8px;
}

.result-card {
  background-color: #fafafa;
  border-radius: 8px;
}

.result-content-wrapper {
  max-height: 300px;
  overflow-y: auto;
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 8px;
}

.result-content {
  font-family: monospace;
  font-size: 14px;
  color: #333;
}
</style> 
<style lang="scss">
.tool-test {
  .el-input {
    .el-input__wrapper {
      border-radius: 16px;
    }
  }
  
}  
#pane-tool-test {
  .tab-content-container {
    padding: 0px !important;
    .mcp-tool-list {
      padding: 8px !important;
    }
    .tool-test-content {
      padding: 20px !important;
    }
  }
}
</style>