<template>
  <el-drawer
    :title="drawerTitle"
    v-model="drawerVisible"
    :size="500"
    :destroy-on-close="true"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      class="drawer-form"
    >
      <el-form-item :label="$t('views.template.templateForm.header.name')+':'" prop="name">
        <el-input v-model="form.name" :placeholder="$t('views.template.templateForm.header.namePlaceholder')" />
      </el-form-item>
      <el-form-item :label="$t('views.template.templateForm.header.value')+':'" prop="value">
        <el-input v-model="form.value" :placeholder="$t('views.template.templateForm.header.valuePlaceholder')" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="drawer-footer">
        <el-button @click="close">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'

const emit = defineEmits(['refresh'])

const loading = ref<boolean>(false)
const drawerVisible = ref<boolean>(false)
const formRef = ref()
const currentIndex = ref<number | null>(null)
const form = ref({
  name: '',
  value: ''
})

const drawerTitle = computed(() => {
  return currentIndex.value !== null
    ? t('views.template.templateForm.title.editHeader')
    : t('views.template.templateForm.title.addHeader')
})

const rules = {
  name: [
    { required: true, message: t('views.template.templateForm.header.nameRequired'), trigger: 'blur' },
    { pattern: /^[A-Za-z0-9-]+$/, message: t('views.template.templateForm.header.nameFormat'), trigger: 'blur' }
  ],
  value: [
    { required: true, message: t('views.template.templateForm.header.valueRequired'), trigger: 'blur' }
  ]
}

const open = (data?: any, index?: number) => {
  drawerVisible.value = true
  currentIndex.value = index ?? null
  if (data) {
    form.value = { ...data }
  } else {
    form.value = {
      name: '',
      value: ''
    }
  }
}

const close = () => {
  drawerVisible.value = false
  form.value = {
    name: '',
    value: ''
  }
  currentIndex.value = null
}

const submit = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      emit('refresh', { ...form.value }, currentIndex.value)
      close()
    }
  })
}

defineExpose({ open, close })
</script>

<style scoped lang="scss">
.drawer-form {
  padding: 20px;
}
.drawer-footer {
  padding: 10px 20px;
  text-align: right;
}
</style> 