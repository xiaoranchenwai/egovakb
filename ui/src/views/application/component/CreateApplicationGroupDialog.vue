<template>
  <el-dialog :title="$t('views.application.group.create')" v-model="dialogVisible" width="638" append-to-body
    :close-on-click-modal="false" :close-on-press-escape="false">
    <el-form ref="applicationGroupFormRef" label-width="6em" require-asterisk-position="left" @submit.prevent>
      <el-form-item :label="$t('views.application.group.label')+':'" prop="name">
        <el-input v-model="groupName" maxlength="64"
          :placeholder="$t('views.application.applicationForm.form.appName.placeholder')" show-word-limit />
      </el-form-item>
      <el-form-item :label="$t('views.application.group.parent')+':'">
        <el-select v-model="parentId" placeholder="请选择" size="large" style="width: 240px">
          <el-option v-for="item in groupList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle" :loading="loading">
          {{ $t('common.create') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { ApplicationFormType } from '@/api/type/application'
import type { FormInstance, FormRules } from 'element-plus'
import applicationApi from '@/api/application'
import http from '@/api/http-utils'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { isWorkFlow } from '@/utils/application'
import { t } from '@/locales'
import useStore from '@/stores'
import { ValidType, ValidCount } from '@/enums/common'

const { common, user } = useStore()
const router = useRouter()
const emit = defineEmits(['refresh'])

// @ts-ignore
const defaultPrompt = t('views.application.prompt.defaultPrompt', {
  data: '{data}',
  question: '{question}'
})
const applicationFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const groupList = ref<any>([])
const parentId = ref<string>('')
const groupName = ref<string>('')

watch(dialogVisible, (bool) => {
  if (!bool) {
  }
})


const getGroupList = () => {
}

onMounted(() => {
  getGroupList()
})

const open = () => {
  dialogVisible.value = true
}

const submitHandle = async () => {
  const body = {
    name: groupName.value,
    parent_id: parentId.value
  }
  await http.postRequest('/application/group/save', body)
  MsgSuccess(`添加分组：${groupName.value} 成功`)
  emit('refresh')
}

defineExpose({ open })
</script>
<style lang="scss">
.el-overlay-dialog {
  .el-dialog {
    --el-dialog-padding-primary: 20px;
    padding: 0 !important;

    .el-textarea {
      height: 120px;

      .el-textarea__inner {
        height: 100%;
      }
    }

    .el-dialog__header {
      height: 56px;
      line-height: 56px;
      margin-bottom: var(--el-dialog-padding-primary);
      padding-bottom: 0;
      border-bottom: 1px solid #E9ECF2;
      padding: 0 var(--el-dialog-padding-primary);
    }

    .el-dialog__body {
      padding: 0 var(--el-dialog-padding-primary);
    }

    .el-dialog__footer {
      height: 56px;
      line-height: 56px;
      border-top: 1px solid #E9ECF2;
      padding: 0 var(--el-dialog-padding-primary);
    }
  }
}
</style>
