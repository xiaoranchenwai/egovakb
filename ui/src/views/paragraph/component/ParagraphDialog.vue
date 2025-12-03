<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="80%"
    class="paragraph-dialog aa"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-row v-loading="loading">
      <el-col :span="18">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="p-24" style="padding-bottom: 8px">
            <div style="position: absolute; right: 20px; top: 20px; ">
              <el-button text @click="isEdit = true" v-if="problemId && !isEdit">
                <el-icon><EditPen /></el-icon>
              </el-button>
            </div>

            <!-- 当非编辑模式且存在分块数据时展示分块 -->
            <ParagraphChunk 
              v-if="!isEdit && chunkList.length > 0" 
              :chunkList="chunkList" 
              :chunkData="chunkData" 
              @refresh-chunks="onRefreshChunks"
            />
            
            <!-- 编辑模式或无分块数据时展示表单 -->
            <ParagraphForm ref="paragraphFormRef" v-else :data="detail" :isEdit="isEdit" />
          </div>
        </el-scrollbar>
        <div class="text-right p-24 pt-0" v-if="problemId && isEdit">
          <el-switch v-model="regenerateChunk" :active-text="$t('views.paragraph.regenerateChunk')" style="margin-right: 10px;" :active-value="true" :inactive-value="false" />
          <el-button @click.prevent="cancelEdit"> {{$t('common.cancel')}} </el-button>
          <el-button type="primary" :disabled="loading" @click="handleDebounceClick">
            {{$t('common.save')}}
          </el-button>
        </div>
      </el-col>
      <el-col :span="6" class="border-l" style="width: 300px">
        <!-- 关联问题 -->
        <ProblemComponent
          :problemId="problemId"
          :docId="document_id"
          :datasetId="dataset_id"
          ref="ProblemRef"
        />
      </el-col>
    </el-row>
    <template #footer v-if="!problemId">
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{$t('common.cancel')}} </el-button>
        <el-button :disabled="loading" type="primary" @click="handleDebounceClick">
          {{$t('common.submit')}}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep, debounce } from 'lodash'
import { ElMessage } from 'element-plus'

import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'
import ParagraphChunk from '@/views/paragraph/component/ParagraphChunk.vue'
import ProblemComponent from '@/views/paragraph/component/ProblemComponent.vue'
import paragraphApi from '@/api/paragraph'
import useStore from '@/stores'
import chunkApi from '@/api/chunk'

const props = defineProps({
  title: String
})

const { paragraph } = useStore()

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const emit = defineEmits(['refresh'])

const ProblemRef = ref()
const paragraphFormRef = ref<any>()

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const problemId = ref('')
const detail = ref<any>({})
const isEdit = ref(false)
const document_id = ref('')
const dataset_id = ref('')
const cloneData = ref<any>({})
const chunkList = ref<any[]>([])
const chunkData = ref<any>({})
const regenerateChunk = ref(true)

watch(dialogVisible, (bool) => {
  if (!bool) {
    problemId.value = ''
    detail.value = {}
    isEdit.value = false
    document_id.value = ''
    dataset_id.value = ''
    cloneData.value = null
    chunkList.value = []
    chunkData.value = {}
  }
})

const cancelEdit = () => {
  isEdit.value = false
  detail.value = cloneDeep(cloneData.value)
}

const refreshParagraph = () => {
  if (problemId.value) {
    paragraphApi.getParagraphById(dataset_id.value, document_id.value, problemId.value, loading)
      .then(res => {
        if (res.code === 200 || res.code === 0) { 
          console.log('refreshParagraph res', res)
          // 更新表单数据
          detail.value.title = res.data.title
          detail.value.content = res.data.content
          cloneData.value = cloneDeep(detail.value)
        }
      })  
  }
}

// 处理刷新事件
const onRefreshChunks = () => {
  loadChunkList()
}

// 加载分块列表
const loadChunkList = () => {
  if (problemId.value) {
    loading.value = true
    // 先清空列表，避免显示旧数据
    chunkList.value = []
    
    chunkApi.getChunkList(problemId.value, loading)
      .then(res => {
        loading.value = false
        if (res.code === 200 || res.code === 0) {
          // 保存分块列表到状态变量
          chunkList.value = res.data || []
          
          // 如果删除后没有分块了，设置为编辑模式
          if (chunkList.value.length === 0 && !isEdit.value) {
            ElMessage.info('所有分块已删除，进入编辑模式')
            isEdit.value = true
          }
        } else {
          console.error('获取分块列表失败:', res.message)
        }
      })
      .catch(err => {
        loading.value = false
        console.error('获取分块列表异常:', err)
      })
  }
}

const open = (data: any) => {
  if (data) {
    detail.value.title = data.title
    detail.value.content = data.content
    cloneData.value = cloneDeep(detail.value)
    problemId.value = data.id
    document_id.value = data.document_id
    dataset_id.value = data.dataset_id || id
    
    // 如果段落ID存在，获取段落下的分块列表
    if (data?.id) {
      loadChunkList()
    }

    if (data?.chunk_data) {
      chunkData.value.content = data.chunk_data
      chunkData.value.score = data.similarity
      chunkData.value.id = data.chunk_id
    }
  } else {
    isEdit.value = true
  }
  dialogVisible.value = true
}
const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    loading.value = true
    if (problemId.value) {
      console.log('submitHandle problemId.value', problemId.value)
      const obj = { 
        ...paragraphFormRef.value?.form,
        regenerateChunk: regenerateChunk.value,
      }
      paragraph
        .asyncPutParagraph(
          dataset_id.value,
          documentId || document_id.value,
          problemId.value,
          obj,
          loading
        )
        .then((res: any) => {
          detail.value.title = res.data.title
          detail.value.content = res.data.content
          loadChunkList()
          isEdit.value = false
          emit('refresh', res.data)
        })
    } else {
      console.log('submitHandle else')
      const obj =
        ProblemRef.value.problemList.length > 0
          ? {
              problem_list: ProblemRef.value.problemList,
              ...paragraphFormRef.value?.form,
              regenerateChunk: regenerateChunk.value
            }
          : {
              ...paragraphFormRef.value?.form,  
              regenerateChunk: regenerateChunk.value
            }
      paragraphApi.postParagraph(id, documentId, obj, loading).then((res) => {
        dialogVisible.value = false
        emit('refresh')
      })
    }
  }
}
const handleDebounceClick = debounce(() => {
  submitHandle()
}, 200)

defineExpose({ open })
</script>
<style lang="scss" scoped>
.paragraph-scrollbar {
  padding: 0;
}

.p-24 {
  padding: 24px;
}

.pt-0 {
  padding-top: 0;
}

.border-l {
  border-left: 1px solid #E9ECF2;
}

.text-right {
  text-align: right;
}
</style>
