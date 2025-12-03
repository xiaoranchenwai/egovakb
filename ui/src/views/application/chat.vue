<template>
  <div class='app-chat-pc layout-bg' :class='classObj' v-loading='loading' :style="{
    '--el-color-primary': applicationDetail?.custom_theme?.theme_color,
    '--el-color-primary-light-9': hexToRgba(
      applicationDetail?.custom_theme?.theme_color,
      0.1
    )
  }">

    <div class='flex'>
      <div class='chat-pc__left border-r'>
        <div class='p-24 pb-0'>

          <div class='flex align-center'>
            <div class='mr-12 flex'>
              <AppAvatar v-if='isAppIcon(applicationDetail?.icon)' shape='square' :size='48' style='background: none'>
                <img :src='applicationDetail?.icon' alt='' />
              </AppAvatar>
              <AppAvatar v-else-if='applicationDetail?.name' :name='applicationDetail?.name' pinyinColor shape='square'
                         :size='48' />
            </div>
            <div class='right'>
              <div class='flex'>
                <h4>{{ applicationDetail?.name }}</h4>
                <span class='tag'>未发布</span>
              </div>
              <div class='gray'>Agent 网格化</div>
            </div>

          </div>

          <el-button class='add-button w-full primary' @click='newChat'>
            <el-icon>
              <ChatDotRound />
            </el-icon>
            <span class='ml-4'>新建对话</span>
          </el-button>
          <p class='mt-20 mb-8'>历史记录</p>
        </div>
        <div class='left-height pt-0'>
          <el-scrollbar>
            <div class='p-8 pt-0'>
              <common-list :style="{
    '--el-color-primary':
      applicationDetail?.custom_theme?.theme_color,
    '--el-color-primary-light-9': hexToRgba(
      applicationDetail?.custom_theme?.theme_color,
      0.1
    )
  }" :data='chatLogData' class='mt-8' v-loading='left_loading' :defaultActive='currentChatId' @click='clickListHandle'
                           @mouseenter='mouseenter' @mouseleave="mouseId = ''">
                <template #default='{ row }'>
                  <div class='flex-between'>
                    <auto-tooltip :content='row.abstract'>
                      {{ row.abstract }}
                    </auto-tooltip>
                    <div @click.stop v-if="mouseId === row.id && row.id !== 'new'">
                      <el-button style='padding: 0' link @click.stop='deleteLog(row)'>
                        <el-icon>
                          <Delete />
                        </el-icon>
                      </el-button>
                    </div>
                  </div>
                </template>

                <template #empty>
                  <div class='text-center'>
                    <el-text type='info'>暂无历史记录</el-text>
                  </div>
                </template>
              </common-list>
            </div>
            <div v-if='chatLogData?.length' class='gradient-divider lighter mt-8'>
              <span>仅显示最近 20 条对话</span>
            </div>
          </el-scrollbar>
        </div>
      </div>
      <div class='chat-pc__right'>
        <div class='right-header border-b mb-24 p-16-24 flex-between'>
          <!--          <h4 class='ellipsis-1' style='width: 70%'>-->
          <!--            {{ currentChatName }}-->
          <!--          </h4>-->
          <div class='flex'>
            <div class='avatar'>
              <el-image src='/ui/src/assets/logo/ai.png' alt='' fit='cover'
                        style='width: 40px; height: 40px; display: block'></el-image>
            </div>
            <div class='infos'>
              <p>小智机器人</p>
            </div>
          </div>

          <span class='flex align-center'>
            <template v-if='currentRecordList.length'>
              <AppIcon v-if='paginationConfig.total' iconName='app-chat-record' class='info mr-8'
                       style='font-size: 16px'>
              </AppIcon>
              <span v-if='paginationConfig.total' class='lighter'>{{ paginationConfig.total }} 条提问</span>
              <el-dropdown class='ml-8'>
                <AppIcon iconName='app-export' class='cursor' title='导出聊天记录'></AppIcon>
                <template #dropdown>
                  <el-dropdown-menu>
                  <el-dropdown-item @click='exportMarkdown'>导出 Markdown</el-dropdown-item>
                  <el-dropdown-item @click='exportHTML'>导出 HTML</el-dropdown-item>
                </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>

            <el-icon size='24' class='close-icon' @click.stop='onClose' title='关闭'><CloseBold /></el-icon>
          </span>

        </div>

        <div class='right-height chat-width'>
          <AiChat ref='AiChatRef' v-model:applicationDetails='applicationDetail' :available='applicationAvailable'
                  type='ai-chat' :appId='applicationDetail?.id' :record='currentRecordList' :chatId='currentChatId'
                  @refresh='refresh' @scroll='handleScroll'>
          </AiChat>
        </div>
      </div>
    </div>
    <div class='collapse'>
      <el-button @click='isCollapse = !isCollapse'>
        <el-icon>
          <component :is="isCollapse ? 'Fold' : 'Expand'" />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang='ts'>
import { ref, onMounted, nextTick, computed } from 'vue'
import { marked } from 'marked'
import { saveAs } from 'file-saver'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
import useResize from '@/layout/hooks/useResize'
import { hexToRgba } from '@/utils/theme'

const emit = defineEmits([ 'update:visible' ])

useResize()

const { user, log, common } = useStore()

const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})

const isCollapse = ref(false)

const customStyle = computed(() => {
  return {
    background: applicationDetail.value?.custom_theme?.theme_color,
    color: applicationDetail.value?.custom_theme?.header_font_color
  }
})

const classObj = computed(() => {
  return {
    mobile: common.isMobile(),
    hideLeft: !isCollapse.value,
    openLeft: isCollapse.value
  }
})

const newObj = {
  id: 'new',
  abstract: '新建对话'
}
const props = defineProps<{
  application_profile: any
  applicationAvailable: boolean,
  visible: boolean
}>()
const AiChatRef = ref()
const loading = ref(false)
const left_loading = ref(false)

const applicationDetail = computed({
  get: () => {
    return props.application_profile
  },
  set: (v) => {
  }
})

const show = computed({
  get() {
    return props.visible
  },
  set(val: boolean) {
    emit('update:visible', val)
  }
})

const chatLogData = ref<any[]>([])

const paginationConfig = ref({
  current_page: 1,
  page_size: 20,
  total: 0
})

const currentRecordList = ref<any>([])
const currentChatId = ref('new') // 当前历史记录Id 默认为'new'
const currentChatName = ref('新建对话')
const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}

function deleteLog(row: any) {
  log.asyncDelChatClientLog(applicationDetail.value.id, row.id, left_loading).then(() => {
    if (currentChatId.value === row.id) {
      currentChatId.value = 'new'
      currentChatName.value = '新建对话'
      paginationConfig.value.current_page = 1
      paginationConfig.value.total = 0
      currentRecordList.value = []
    }
    getChatLog(applicationDetail.value.id)
  })
}

function handleScroll(event: any) {
  if (
      currentChatId.value !== 'new' &&
      event.scrollTop === 0 &&
      paginationConfig.value.total > currentRecordList.value.length
  ) {
    const history_height = event.dialogScrollbar.offsetHeight
    paginationConfig.value.current_page += 1
    getChatRecord().then(() => {
      event.scrollDiv.setScrollTop(event.dialogScrollbar.offsetHeight - history_height)
    })
  }
}

function newChat() {
  if (!chatLogData.value.some((v) => v.id === 'new')) {
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
    chatLogData.value.unshift(newObj)
  } else {
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
  }
  currentChatId.value = 'new'
  currentChatName.value = '新建对话'
  if (common.isMobile()) {
    isCollapse.value = false
  }
}

function getChatLog(id: string, refresh?: boolean) {
  const page = {
    current_page: 1,
    page_size: 20
  }

  log.asyncGetChatLogClient(id, page, left_loading).then((res: any) => {
    chatLogData.value = res.data.records
    if (refresh) {
      currentChatName.value = chatLogData.value?.[0].abstract
    }
  })
}

function getChatRecord() {
  return log
      .asyncChatRecordLog(
          applicationDetail.value.id,
          currentChatId.value,
          paginationConfig.value,
          loading,
          false
      )
      .then((res: any) => {
        paginationConfig.value.total = res.data.total
        const list = res.data.records
        list.map((v: any) => {
          v['write_ed'] = true
          v['record_id'] = v.id
        })
        currentRecordList.value = [ ...list, ...currentRecordList.value ].sort((a, b) =>
            a.create_time.localeCompare(b.create_time)
        )
        if (paginationConfig.value.current_page === 1) {
          nextTick(() => {
            // 将滚动条滚动到最下面
            AiChatRef.value.setScrollBottom()
          })
        }
      })
}

const clickListHandle = (item: any) => {
  if (item.id !== currentChatId.value) {
    paginationConfig.value.current_page = 1
    paginationConfig.value.total = 0
    currentRecordList.value = []
    currentChatId.value = item.id
    currentChatName.value = item.abstract
    if (currentChatId.value !== 'new') {
      getChatRecord()
    }
  }
  if (common.isMobile()) {
    isCollapse.value = false
  }
}

function refresh(id: string) {
  getChatLog(applicationDetail.value.id, true)
  currentChatId.value = id
}

async function exportMarkdown(): Promise<void> {
  const suggestedName: string = `${ currentChatId.value }.md`
  const markdownContent: string = currentRecordList.value
      .map((record: any) => `# ${ record.problem_text }\n\n${ record.answer_text }\n\n`)
      .join('\n')

  const blob: Blob = new Blob([ markdownContent ], { type: 'text/markdown;charset=utf-8' })
  saveAs(blob, suggestedName)
}

async function exportHTML(): Promise<void> {
  const suggestedName: string = `${ currentChatId.value }.html`
  const markdownContent: string = currentRecordList.value
      .map((record: any) => `# ${ record.problem_text }\n\n${ record.answer_text }\n\n`)
      .join('\n')
  const htmlContent: any = marked(markdownContent)

  const blob: Blob = new Blob([ htmlContent ], { type: 'text/html;charset=utf-8' })
  saveAs(blob, suggestedName)
}

/**
 *初始化历史对话记录
 */
const init = () => {
  if (
      (applicationDetail.value.show_history || !user.isEnterprise()) &&
      props.applicationAvailable
  ) {
    getChatLog(applicationDetail.value.id)
  }
}
onMounted(() => {
  init()
})

function onClose() {
  show.value = false;
}
</script>
<style lang='scss'>
.app-chat-pc {
  overflow: hidden;

  .chat-pc__header {
    background: var(--app-header-bg-color);
    position: absolute;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 100;
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-border-color);
  }

  .chat-pc__left {
    //padding-top: calc(var(--app-header-height) - 8px);
    background: #ffffff;
    width: 280px;

    .add-button {
      height: 40px;
      line-height: 38px;
      text-align: left;
      border: 1px solid #E9ECF2; // var(--el-color-primary);
      margin-top: 24px;
      color: #223355;
      font-size: 14px;
      font-weight: 400;
      padding-left: 12px;
      justify-content: center;
    }

    .p-24 {
      padding: 20px !important;
    }

    .left-height {
      height: calc(100vh - var(--app-header-height) - 230px);
    }

    .right {
      width: 100%;

      .flex {
        height: 24px;
        line-height: 24px;
        position: relative;
      }

      .tag {
        font-weight: 400;
        font-size: 14px;
        color: #3388FF;
        text-align: center;
        line-height: 22px;
        padding: 0 5px;
        background-color: rgba(51, 136, 255, 0.1);
        position: absolute;
        right: 0;
      }

      .gray {
        font-weight: 400;
        font-size: 14px;
        color: #6B7A99;
        line-height: 24px;
        height: 24px;
      }
    }

  }

  .chat-pc__right {
    width: calc(100% - 280px);
    // padding-top: calc(var(--app-header-height));
    overflow: hidden;
    position: relative;
    box-sizing: border-box;
    background-color: var(--app-view-bg-color);

    .right-header {
      background: #ffffff;
      box-sizing: border-box;
      height: 56px;
      line-height: 56px;
      padding: 0 calc(var(--app-base-px) * 3);

      .avatar {
        width: 40px;
        height: 40px;
        position: relative;
        border-radius: 50%;
        background-color: rgba(51, 136, 255, 0.1);
      }

      .infos {
        padding-left: 8px;

        p {
          font-weight: 400;
          font-size: 12px;
          color: #A8B4C8;
          line-height: 18px;

          &:first-child {
            height: 22px;
            font-weight: 600;
            font-size: 14px;
            color: #223355;
            line-height: 22px;
          }

        }
      }

      .close-icon {
        margin-left: 15px;
        cursor: pointer;
      }
    }

    .right-height {
      height: calc(100vh - var(--app-header-height) * 2 - 52px);
      max-width: 100%;
      margin: 0;

      .ai-chat__operate {
        padding: 0;
        height: 195px;

        .operate-textarea {
          border-radius: 0;
          height: 100%;
          //border-top: 1px solid #E9ECF2;

          .el-scrollbar {
            height: 1px;
          }

          .flex {
            height: 100%;
          }
        }
      }
    }
  }

  .gradient-divider {
    position: relative;
    text-align: center;
    color: var(--el-color-info);

    ::before {
      content: '';
      width: 17%;
      height: 1px;
      background: linear-gradient(90deg, rgba(222, 224, 227, 0) 0%, #dee0e3 100%);
      position: absolute;
      left: 16px;
      top: 50%;
    }

    ::after {
      content: '';
      width: 17%;
      height: 1px;
      background: linear-gradient(90deg, #dee0e3 0%, rgba(222, 224, 227, 0) 100%);
      position: absolute;
      right: 16px;
      top: 50%;
    }
  }

  .collapse {
    display: none;
  }
}

// 适配移动端
.mobile {
  .chat-pc {
    &__right {
      width: 100%;
    }

    &__left {
      display: none;
      width: 0;
    }
  }

  .collapse {
    display: block;
    position: fixed;
    bottom: 90px;
    z-index: 99;
  }

  &.openLeft {
    .chat-pc {
      &__left {
        display: block;
        position: fixed;
        width: 100%;
        z-index: 99;
        height: calc(100vh - var(--app-header-height) + 6px);
      }
    }

    .collapse {
      display: block;
      position: absolute;
      bottom: 90px;
      right: 0;
      z-index: 99;
    }
  }
}

.chat-width {
  max-width: 80%;
  margin: 0 auto;
}

@media only screen and (max-width: 1000px) {
  .chat-width {
    max-width: 100% !important;
    margin: 0 auto;
  }
}
</style>
