<template>
  <el-dropdown trigger="click" type="primary">
    <div class="flex-center cursor">
      <AppAvatar>
        <img v-if="user.avatar" :src="user.avatar" alt="" />
        <img v-else src="@/assets/user-icon.png" alt="" />
      </AppAvatar>
      <span class="ml-8">{{ user.userInfo?.username }}</span>
      <el-icon class="el-icon--right">
        <CaretBottom color="#FFFFFF"/>
      </el-icon>
    </div>

    <template #dropdown>
      <el-dropdown-menu class="avatar-dropdown">
        <div class="userInfo">
          <p class="bold mb-4" style="font-size: 14px">{{ user.userInfo?.username }}</p>
          <p>
            <el-text type="info">
              {{ user.userInfo?.email }}
            </el-text>
          </p>
        </div>
        <el-dropdown-item class="border-t p-8" @click="openResetPassword">
          {{ $t('views.login.resetPassword') }}
        </el-dropdown-item>
        <el-dropdown-item class="border-t p-8" @click="openEditAvatar">
          {{ $t('修改头像') }}
        </el-dropdown-item>
        <div v-hasPermission="new ComplexPermission([], ['x-pack'], 'OR')">
          <el-dropdown-item class="border-t p-8" @click="openAPIKeyDialog">
            {{ $t('layout.apiKey') }}
          </el-dropdown-item>
        </div>
        <el-dropdown-item class="border-t" style="padding: 0" @click.stop>
          <el-dropdown class="w-full" trigger="hover" placement="left-start">
            <div class="flex-between w-full" style="line-height: 22px; padding: 12px 11px">
              <span> {{ $t('layout.language') }}</span>
              <el-icon><ArrowRight /></el-icon>
            </div>

            <template #dropdown>
              <el-dropdown-menu style="width: 180px">
                <el-dropdown-item
                  v-for="(lang, index) in langList"
                  :key="index"
                  :value="lang.value"
                  @click="changeLang(lang.value)"
                  class="flex-between"
                >
                  <span :class="lang.value === user.userInfo?.language ? 'primary' : ''">{{
                    lang.label
                  }}</span>

                  <el-icon
                    :class="lang.value === user.userInfo?.language ? 'primary' : ''"
                    v-if="lang.value === user.userInfo?.language"
                  >
                    <Check />
                  </el-icon>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-dropdown-item>
        <el-dropdown-item class="border-t" @click="openPlatformNameDialog">
          {{ $t('设置平台名称') }}
        </el-dropdown-item>
        <el-dropdown-item class="border-t" @click="openAbout">
          {{ $t('layout.about.title') }}
        </el-dropdown-item>

        <el-dropdown-item class="border-t" @click="logout">
          {{ $t('layout.logout') }}
        </el-dropdown-item>


      </el-dropdown-menu>
    </template>
  </el-dropdown>
  <ResetPassword ref="resetPasswordRef"></ResetPassword>
  <AboutDialog ref="AboutDialogRef"></AboutDialog>
  <APIKeyDialog :user-id="user.userInfo?.id" ref="APIKeyDialogRef" />
  <UserPwdDialog ref="UserPwdDialogRef" />
  <EditAvatarDialog ref="editAvatarDialogRef" @update:avatar="updateAvatar" />
  <el-dialog
    v-model="platformNameDialogVisible"
    :title="$t('设置平台名称')"
    width="500px"
  >
    <el-form :model="platformNameForm" ref="platformNameFormRef">
      <el-form-item :label="$t('平台名称')+':'" prop="name" label-width="auto">
        <el-input v-model="platformNameForm.name" :placeholder="$t('请输入平台名称')"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="platformNameDialogVisible = false">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="savePlatformName" :loading="savingPlatformName">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import ResetPassword from './ResetPassword.vue'
import AboutDialog from './AboutDialog.vue'
import UserPwdDialog from '@/views/user-manage/component/UserPwdDialog.vue'
import APIKeyDialog from './APIKeyDialog.vue'
import { ComplexPermission } from '@/utils/permission/type'
import { langList } from '@/locales/index'
import { useLocale } from '@/locales/useLocale'
import EditAvatarDialog from './EditAvatarDialog.vue'
import userSettingApi from '@/api/user-setting'
import { MsgSuccess } from '@/utils/message'

const { user } = useStore()
const router = useRouter()

const UserPwdDialogRef = ref()
const AboutDialogRef = ref()
const APIKeyDialogRef = ref()
const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>()
const editAvatarDialogRef = ref()

const platformNameDialogVisible = ref(false)
const platformNameForm = ref({ name: '' })
const savingPlatformName = ref(false)

const avatarUrl = computed(() => {
  console.log('avatarUrl', user.avatar)
  return user.avatar
})

const changeLang = (lang: string) => {
  user.postUserLanguage(lang)
}
const openAbout = () => {
  AboutDialogRef.value?.open()
}

function openAPIKeyDialog() {
  APIKeyDialogRef.value.open()
}

const openResetPassword = () => {
  resetPasswordRef.value?.open()
}

const logout = () => {
  user.logout().then(() => {
    router.push({ name: 'login' })
  })
}

const openEditAvatar = () => {
  editAvatarDialogRef.value?.open()
}

const updateAvatar = (url: string) => {
  console.log('updateAvatar', url)
  user.updateAvatar(url)
}

const openPlatformNameDialog = async () => {
  platformNameDialogVisible.value = true
  try {
    const res = await userSettingApi.getSetting({
      name: 'platformName',
      setting_type: 'config'
    })
    if (res.data?.value) {
      platformNameForm.value.name = res.data.value
    }
  } catch (error) {
    console.error('获取平台名称设置失败:', error)
  }
}

const savePlatformName = async () => {
  if (!platformNameForm.value.name) {
    return
  }
  
  savingPlatformName.value = true
  try {
    await userSettingApi.saveSetting({
      name: 'platformName',
      setting_type: 'config',
      value: platformNameForm.value.name
    })
    
    MsgSuccess('平台名称设置成功')
    platformNameDialogVisible.value = false
    
    // 刷新页面以更新平台名称
    window.location.reload()
  } catch (error) {
    console.error('保存平台名称设置失败:', error)
  } finally {
    savingPlatformName.value = false
  }
}

onMounted(() => {
  if (user.userInfo?.is_edit_password) {
    UserPwdDialogRef.value.open(user.userInfo)
  }
})
</script>
<style lang="scss" scoped>
.avatar-dropdown {
  min-width: 210px;

  .userInfo {
    padding: 12px 11px;
  }

  :deep(.el-dropdown-menu__item) {
    padding: 12px 11px;
    &:hover {
      background: var(--app-text-color-light-1);
    }
  }
}
.ml-8 {
  color: var(--app-header-text-color);
}
</style>
