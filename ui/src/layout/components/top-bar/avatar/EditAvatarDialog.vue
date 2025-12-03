<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('修改头像')"
    width="400px"
    :close-on-click-modal="false"
  >
    <div class="avatar-upload">
      <el-upload
        class="avatar-uploader"
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleChange"
      >
        <img v-if="imageUrl" :src="imageUrl" class="avatar" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
      <div class="tip mt-8">{{ t('请选择图片文件') }}</div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleUpload" :loading="loading">
          {{ t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { MsgSuccess } from '@/utils/message'
import imageApi from '@/api/image'
import userSettingApi from '@/api/user-setting'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const emit = defineEmits(['update:avatar'])
const dialogVisible = ref(false)
const imageUrl = ref('')
const loading = ref(false)
const uploadFile = ref<File | null>(null)

const handleChange = (file: { raw: File }) => {
  imageUrl.value = URL.createObjectURL(file.raw)
  file.raw && (uploadFile.value = file.raw)
}

const handleUpload = async () => {
  if (!uploadFile.value) {
    return
  }
  
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('file', uploadFile.value)

    const res = await imageApi.postImage(fd)
    // 保存头像设置
    const settingData = {
      name: 'avatar',
      setting_type: 'config',
      value: res.data
    }
    await userSettingApi.saveSetting(settingData)
    
    emit('update:avatar', res.data)
    MsgSuccess('头像修改成功')
    dialogVisible.value = false
  } catch (error) {
    console.error('Upload failed:', error)
  } finally {
    loading.value = false
  }
}

const open = () => {
  dialogVisible.value = true
  imageUrl.value = ''
  uploadFile.value = null
}

defineExpose({ open })
</script>

<style lang="scss" scoped>
.avatar-upload {
  text-align: center;
  
  .avatar-uploader {
    :deep(.el-upload) {
      border: 1px dashed var(--el-border-color);
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: var(--el-transition-duration);
      
      &:hover {
        border-color: var(--el-color-primary);
      }
    }
  }
  
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 120px;
    height: 120px;
    text-align: center;
    line-height: 120px;
  }
  
  .avatar {
    width: 120px;
    height: 120px;
    display: block;
  }
}
</style> 