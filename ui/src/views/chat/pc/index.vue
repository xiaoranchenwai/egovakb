<template>
    <div class='app-chat-pc layout-bg custom-pc-chat' :class='classObj' v-loading='loading' :style="{
        '--el-color-primary': applicationDetail?.custom_theme?.theme_color,
        '--el-color-primary-light-9': hexToRgba(
            applicationDetail?.custom_theme?.theme_color,
            0.1
        )
    }">

        <div class='flex' :class='{ hidden: !showHistory }'>
            <div class='chat-pc__left border-r'>
                <div class='p-24 pb-0'>

                    <div class='flex align-center'>
                        <div class='mr-12 flex'>
                            <AppAvatar v-if='isAppIcon(applicationDetail?.icon)' shape='square' :size='48'
                                style='background: none'>
                                <img :src='applicationDetail?.icon' alt='' />
                            </AppAvatar>
                            <AppAvatar v-else-if='applicationDetail?.name' :name='applicationDetail?.name' pinyinColor
                                shape='square' :size='48' />
                        </div>
                        <div class='right'>
                            <div class='flex'>
                                <h4 class="ellipsis" style="max-width: 176px;" :title="applicationDetail?.name">{{
                                    applicationDetail?.name }}</h4>
                            </div>
                            <div class='flex'>
                                <!-- <div class='gray'>视频中心</div> -->
                                <span class='tag'>已发布</span>
                            </div>
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
                            }" :data='chatLogData' class='mt-8' v-loading='left_loading' :defaultActive='currentChatId'
                                @click='clickListHandle' @mouseenter='mouseenter' @mouseleave="mouseId = ''">
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

                <div v-html="media"></div>
            </div>
            <div class='chat-pc__right'>
                <div class='right-header border-b mb-24 p-16-24 flex align-center'>
                    <h4 class='ellipsis-1' style='flex:1'>
                        {{ currentChatName }}
                    </h4>
                    <span class='flex align-center' v-if='currentRecordList.length'>
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
                    </span>
                    <el-icon v-if='false' size='24' class='close-icon' @click.stop='onClose' title='关闭'>
                        <CloseBold />
                    </el-icon>
                </div>
                <div class='right-height chat-width'>
                    <AiChat ref='AiChatRef' v-model:applicationDetails='applicationDetail'
                        :available='applicationAvailable' type='ai-chat' :appId='applicationDetail?.id'
                        :record='currentRecordList' :chatId='currentChatId' @refresh='refresh' @scroll='handleScroll'>
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
    <EditTitleDialog ref="EditTitleDialogRef" @refresh="refreshFieldTitle" />
</template>

<script setup lang='ts'>
import { ref, onMounted, nextTick, computed } from 'vue'
import { marked } from 'marked'
import { saveAs } from 'file-saver'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
import useResize from '@/layout/hooks/useResize'
import { hexToRgba } from '@/utils/theme'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter();
const route = useRoute();

import EditTitleDialog from './EditTitleDialog.vue'
import { t } from '@/locales'
useResize()

const { query: { media } } = route as any;
const { user, log, common } = useStore()

const EditTitleDialogRef = ref()

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
    abstract: t('chat.createChat')
}
const props = defineProps<{
    application_profile: any
    applicationAvailable: boolean
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

const chatLogData = ref<any[]>([])

const paginationConfig = ref({
    current_page: 1,
    page_size: 20,
    total: 0
})

const currentRecordList = ref<any>([])
const currentChatId = ref('new') // 当前历史记录Id 默认为'new'
const currentChatName = ref(t('chat.createChat'))
const mouseId = ref('');
const showHistory = ref<boolean>(true);

function mouseenter(row: any) {
    mouseId.value = row.id
}

function editLogTitle(row: any) {
  EditTitleDialogRef.value.open(row, applicationDetail.value.id)
}
function refreshFieldTitle(chatId: string, abstract: string) {
  const find = chatLogData.value.find((item: any) => item.id == chatId)
  if (find) {
    find.abstract = abstract
  }
}
function deleteLog(row: any) {
    log.asyncDelChatClientLog(applicationDetail.value.id, row.id, left_loading).then(() => {
        if (currentChatId.value === row.id) {
            currentChatId.value = 'new'
            currentChatName.value = t('chat.createChat')
            paginationConfig.value.current_page = 1
            paginationConfig.value.total = 0
            currentRecordList.value = []
        }
        getChatLog(applicationDetail.value.id)
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
            currentRecordList.value = [...list, ...currentRecordList.value].sort((a, b) =>
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
    currentChatName.value = t('chat.createChat')
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
            currentChatName.value = chatLogData.value?.[0]?.abstract
        } else {
            paginationConfig.value.current_page = 1
            paginationConfig.value.total = 0
            currentRecordList.value = []
            currentChatId.value = chatLogData.value?.[0]?.id || 'new'
            currentChatName.value = chatLogData.value?.[0]?.abstract || t('chat.createChat')
            if (currentChatId.value !== 'new') {
                getChatRecord()
            }
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

      // 切换对话后，取消暂停的浏览器播放
      if (window.speechSynthesis.paused && window.speechSynthesis.speaking) {
        window.speechSynthesis.resume()
        nextTick(() => {
          window.speechSynthesis.cancel()
        })
      }
    }
  }
}

function refresh(id: string) {
    getChatLog(applicationDetail.value.id, true)
    currentChatId.value = id
}

async function exportMarkdown(): Promise<void> {
    const suggestedName: string = `${currentChatId.value}.md`
    const markdownContent: string = currentRecordList.value
        .map((record: any) => `# ${record.problem_text}\n\n${record.answer_text}\n\n`)
        .join('\n')

    const blob: Blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' })
    saveAs(blob, suggestedName)
}

async function exportHTML(): Promise<void> {
    const suggestedName: string = `${currentChatId.value}.html`
    const markdownContent: string = currentRecordList.value
        .map((record: any) => `# ${record.problem_text}\n\n${record.answer_text}\n\n`)
        .join('\n')
    const htmlContent: any = marked(markdownContent)

    const blob: Blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' })
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
const routeHandle = () => {
    console.log(route);
    console.log(route.query.hideHistory);
    const hideHistory = route.query.hideHistory;
    if (hideHistory === "1") {
        showHistory.value = false;
    } else {
        showHistory.value = true;
    }
}
onMounted(() => {
    init()
    routeHandle()
})

function onClose() {
    // router.go(-1);
    router.push({
        path: "/application/index",
        query: { reload: "1" },
        replace: true
    });
}

</script>
<style lang='scss'>
.custom-pc-chat {
    padding: 1vh 20px !important;

    box-sizing: border-box;

    .el-scrollbar__thumb {
        background-color: #A8B4C8 !important; // 滚动条颜色
    }
}

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

    .chat-pc__left,
    .chat-pc__right {
        transition: all 0.3s ease;
    }

    .chat-pc__left {
        background: #ffffff;
        width: 280px;
        height: 98vh;
        border-right-color: #E9ECF2;

        .add-button {
            margin-top: 20px;
            height: 44px;
            border-radius: 8px;
            background: var(--el-color-primary-light-9);
            border: none;
            transition: all 0.3s;

            &:hover {
                background: var(--el-color-primary-light-8);
            }
        }

        .common-list {
            .el-text {
                padding: 12px 16px;
                margin: 4px 0;
                border-radius: 6px;
                transition: all 0.3s;

                &:hover {
                    background: var(--el-color-primary-light-9);
                }

                &.active {
                    background: var(--el-color-primary-light-8);
                    color: var(--el-color-primary);
                }
            }
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
        height: 98vh;
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
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
            border-bottom-color: #E9ECF2;

            .avatar {
                width: 40px;
                height: 40px;
                position: relative;
                border-radius: 50%;
                background-color: rgba(51, 136, 255, 0.1);
                overflow: hidden;
                transition: transform 0.3s;

                &:hover {
                    transform: scale(1.05);
                }
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
            height: calc(100vh - var(--app-header-height) * 2 + 22px);
            max-width: 100%;
            margin: 0;

            .ai-chat__operate {
                padding: 0;
                border-top: 1px solid var(--el-border-color-light);
                background: #ffffff;
                box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);

                .operate-textarea {
                    padding: 16px;

                    .el-textarea__inner {
                        border: none;
                        background: #f5f7fa;
                        border-radius: 8px;
                        min-height: 80px;
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

    &.mobile.openLeft {
        .chat-pc__left {
            animation: slideIn 0.3s ease;
        }
    }
}

@keyframes slideIn {
    from {
        transform: translateX(-100%);
    }

    to {
        transform: translateX(0);
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
        padding: 0 16px;
    }

    .mobile {
        .chat-pc__right {
            .right-header {
                padding: 0 16px;
            }
        }

        .collapse {
            bottom: 120px;
            right: 16px;

            .el-button {
                border-radius: 50%;
                width: 40px;
                height: 40px;
                padding: 0;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
            }
        }
    }
}

.full-container {
    .app-chat-pc .chat-pc__right .right-height {
        height: calc(100vh - var(--app-header-height) * 2 - 32px);
    }
}

.app-chat-pc {
    .flex.hidden {
        .chat-pc__left {
            display: none !important;
        }

        .chat-pc__right {
            width: 100% !important;
        }
    }
}
</style>