<template>
  <div class="code-editor-container">
    <div v-if="!code" class="p-4">
      <el-empty description="该模块暂无代码" />
    </div>
    <div v-else>
      <div class="code-editor-header">
        <h3 class="editor-title">模块代码</h3>
        <div class="editor-actions">
          <el-alert v-if="!hasEditPermission" type="warning" :closable="false" show-icon
            title="您只能查看代码，没有修改权限" class="mr-4" />
          <el-button size="default" @click="formatPythonCode" :loading="saving"
            v-if="hasEditPermission">
            格式化代码
          </el-button>
          <el-button type="primary" size="default" @click="saveModuleCode" :loading="saving"
            :disabled="!hasCodeChanged" v-if="hasEditPermission">
            保存修改
          </el-button>
        </div>
      </div>
      <div class="code-editor-wrapper">
        <CodemirrorEditor 
          v-model="codeContent" 
          :title="'模块代码'"
          @submitDialog="submitCodemirrorEditor"
          :style="editorStyle"
          :original-style="false"
          @ready="onReady"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, defineEmits, ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  moduleId: number
  code?: string
  hasEditPermission: boolean
}>()

const emit = defineEmits<{
  (e: 'saveCode', code: string): void
}>()

const codeContent = ref('')
const originalCode = ref('')
const saving = ref(false)

// 自定义编辑器样式
const editorStyle = {
  height: '100%'
}

// 检查代码是否已更改
const hasCodeChanged = computed(() => {
  return codeContent.value !== originalCode.value
})

// 初始化编辑器
onMounted(() => {
  if (props.code) {
    codeContent.value = props.code
    originalCode.value = props.code
  } else {
    codeContent.value = ''
    originalCode.value = ''
  }
})

// 监听代码变化
watch(() => props.code, (newCode) => {
  if (newCode !== undefined && newCode !== codeContent.value) {
    codeContent.value = newCode
    originalCode.value = newCode
  } else if (newCode === undefined) {
    codeContent.value = ''
    originalCode.value = ''
  }
})

// 格式化Python代码
function formatPythonCode() {
  // 这个功能需要后端支持或使用专门的库
  ElMessage.info('代码格式化功能即将推出')
}

// 从弹窗编辑器提交内容
function submitCodemirrorEditor(code: string) {
  codeContent.value = code
}

// 保存模块代码
async function saveModuleCode() {
  if (!hasCodeChanged.value) return
  
  // 检查权限
  if (!props.hasEditPermission) {
    ElMessage.warning('您没有权限编辑此MCP服务代码')
    return
  }

  saving.value = true
  
  try {
    // 触发保存事件到父组件
    emit('saveCode', codeContent.value)
    originalCode.value = codeContent.value
  } catch (error) {
    console.error("保存模块代码失败", error)
  } finally {
    saving.value = false
  }
}

const onReady = (cm: any) => {
  console.log(cm);
};
</script>

<style scoped>
.code-editor-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.code-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.editor-title {
  font-size: 18px;
  font-weight: 500;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.code-editor-wrapper {
  margin-top: 12px;
  flex: 1;
  overflow: hidden;
}
</style> 

<style lang="scss">
.code-editor-container {
  .editor-actions {
    .el-button+.el-button {
      margin-left: 0 !important;
    }
    .el-button.is-disabled {
      color: rgba(255,255,255,0.5) !important;
    }
  }
}
</style>