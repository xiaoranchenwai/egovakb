<template>
  <el-drawer
    v-model="visible" 
    title="服务参数设置" 
    width="50%" 
    :destroy-on-close="true"
    direction="rtl"
    @update:model-value="handleVisibleChange"
  >
    <div v-if="service">
      <div v-if="!service.config_params || Object.keys(service.config_params).length === 0"
        class="text-center py-4">
        <el-empty description="此服务没有配置参数" :image-size="60" />
      </div>
      <div v-else>
        <el-form ref="formRef" :model="form" label-width="120px" label-position="top">
          <div v-for="(value, key) in service.config_params" :key="key" class="mb-4">
            <el-form-item :label="getParamDisplay(String(key))" label-position="left">
              <div v-if="isNumeric(value)">
                <el-input v-model.number="form[key]" type="number" />
              </div>
              <div v-else-if="isBoolean(value)">
                <el-switch v-model="form[key]" />
              </div>
              <div v-else>
                <el-input 
                  v-if="isPassword(String(key))" 
                  v-model="form[key]" 
                  type="password" 
                  show-password 
                />
                <el-input v-else v-model="form[key]" />
              </div>
            </el-form-item>
          </div>
        </el-form>
      </div>
    </div>
    <div v-else class="text-center py-4">
      <el-empty description="无法加载服务参数" :image-size="60" />
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleConfirm" 
          :loading="loading"
          :disabled="!service?.can_edit"
        >
          更新参数
        </el-button>
      </span>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'

// 组件名称
defineOptions({
  name: 'MCPServiceParamsDialog'
})

// 定义服务信息接口
interface McpServiceInfo {
  id: number;
  service_uuid: string;
  name: string;
  description?: string;
  module_id: number;
  module_name: string;
  status: 'running' | 'stopped' | 'error';
  sse_url: string;
  config_params?: Record<string, any>;
  config_schema?: Record<string, any>;
  error_message?: string;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  can_edit: boolean;
  username?: string;
}

interface Props {
  modelValue: boolean
  service: McpServiceInfo | null
  configSchema?: Record<string, any>
  loading?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', params: Record<string, any>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

const visible = ref(false)
const form = ref<Record<string, any>>({})
const formRef = ref()

// 监听外部传入的visible状态
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal && props.service) {
    // 初始化表单数据
    form.value = { ...props.service.config_params }
  }
}, { immediate: true })

// 获取参数显示名称
const getParamDisplay = (key: string): string => {
  // 优先使用service中的config_schema
  const schema = props.service?.config_schema?.[key] || props.configSchema?.[key]
  if (schema && schema.title) {
    return schema.title
  }
  return key
}

// 判断值类型
const isNumeric = (value: any): boolean => {
  return typeof value === 'number'
}

const isBoolean = (value: any): boolean => {
  return typeof value === 'boolean'
}

const isPassword = (key: string): boolean => {
  // 优先使用service中的config_schema
  const schema = props.service?.config_schema?.[key] || props.configSchema?.[key]
  return schema && schema.type === 'password'
}

// 处理对话框显示状态变化
const handleVisibleChange = (value: boolean) => {
  emit('update:modelValue', value)
}

// 处理取消
const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

// 处理确认
const handleConfirm = () => {
  emit('confirm', form.value)
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 