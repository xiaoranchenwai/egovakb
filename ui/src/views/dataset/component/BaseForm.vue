<template>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="left"
    label-width="8em"
    require-asterisk-position="left"
    v-loading="loading"
  >
    <el-form-item :label="$t('views.dataset.datasetForm.form.datasetName.label')+':'" prop="name">
      <el-input
        v-model="form.name"
        :placeholder="$t('views.dataset.datasetForm.form.datasetName.placeholder')"
        maxlength="64"
        show-word-limit
        @blur="form.name = form.name.trim()"
      />
    </el-form-item>
    <el-form-item
      :label="$t('views.dataset.datasetForm.form.datasetDescription.label')+':'"
      prop="desc"
    >
      <el-input
        v-model="form.desc"
        type="textarea"
        :placeholder="$t('views.dataset.datasetForm.form.datasetDescription.placeholder')"
        maxlength="256"
        show-word-limit
        :autosize="{ minRows: 3 }"
        @blur="form.desc = form.desc.trim()"
      />
    </el-form-item>
    <el-form-item
      :label="$t('views.dataset.datasetForm.form.EmbeddingModel.label')+':'"
      prop="embedding_mode_id"
    >
      <ModelSelect
        v-model="form.embedding_mode_id"
        :placeholder="$t('views.dataset.datasetForm.form.EmbeddingModel.placeholder')"
        :options="modelOptions"
        :model-type="'EMBEDDING'"
        showFooter
      ></ModelSelect>
    </el-form-item>
    <el-form-item
      :label="$t('views.dataset.datasetForm.form.QuestionModel.label')+':'"
      prop="question_model_id"
    >
      <ModelSelect
        v-model="form.question_model_id"
        :placeholder="$t('views.dataset.datasetForm.form.QuestionModel.placeholder')"
        :options="questionModelOptions"
      ></ModelSelect>
    </el-form-item>
    <el-form-item :label="$t('views.dataset.datasetForm.form.createDefaultApp')+':'" class="required-dot">
      <el-switch v-model="form.create_default_app" active-text="是" inactive-text="否" inline-prompt/>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { groupBy } from 'lodash'
import useStore from '@/stores'
import type { datasetData } from '@/api/type/dataset'
import { t } from '@/locales'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})
const { model } = useStore()
const form = ref<datasetData>({
  name: '',
  desc: '',
  embedding_mode_id: '',
  question_model_id: '',
  create_default_app: true
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.datasetName.requiredMessage'),
      trigger: 'blur'
    }
  ],
  desc: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.datasetDescription.requiredMessage'),
      trigger: 'blur'
    }
  ],
  embedding_mode_id: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.EmbeddingModel.requiredMessage'),
      trigger: 'change'
    }
  ],
  question_model_id: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.QuestionModel.requiredMessage'),
      trigger: 'change'
    }
  ]
})

const FormRef = ref()
const loading = ref(false)
const modelOptions = ref<any>([])
const questionModelOptions = ref<any>([])

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.name = value.name
      form.value.desc = value.desc
      form.value.embedding_mode_id = value.embedding_mode_id
      form.value.question_model_id = value.question_model_id
      form.value.create_default_app = value.create_default_app
    }
  },
  {
    immediate: true
  }
)
/*
  表单校验
*/
function validate() {
  if (!FormRef.value) return
  return FormRef.value.validate((valid: any) => {
    return valid
  })
}

function getModel() {
  loading.value = true
  Promise.all([
    model.asyncGetModel({ model_type: 'EMBEDDING' }),
    model.asyncGetModel({ model_type: 'LLM' })
  ])
    .then(([embeddingRes, questionRes]: any) => {
      modelOptions.value = groupBy(embeddingRes?.data, 'provider')
      questionModelOptions.value = groupBy(questionRes?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  getModel()
})
onUnmounted(() => {
  form.value = {
    name: '',
    desc: '',
    embedding_mode_id: '',
    question_model_id: ''
  }
  FormRef.value?.clearValidate()
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
