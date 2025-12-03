<template>
  <div>
    <el-drawer v-model="visible" size="45%" :before-close="close">
      <template #header>
        <h4>{{ title }}</h4>
      </template>
      <template #default>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="schedule-form">
          <el-form-item :label="$t('views.schedule.form.name.label')+':'" prop="name">
            <el-input v-model="form.name" :placeholder="$t('views.schedule.form.name.placeholder')" />
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.desc.label')+':'" prop="desc" class='required-dot'>
            <el-input v-model="form.desc" type="textarea" :placeholder="$t('views.schedule.form.desc.placeholder')" />
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.cronExpression.label')+':'" prop="cron_expression">
            <div class="cron-expression-container">
              <el-input v-model="form.cron_expression"
                :placeholder="$t('views.schedule.form.cronExpression.placeholder')" @change="validateCronExpression" />
              <el-button type="primary" link class="ml-8" @click="showCronHelper = true">
                {{ $t('views.schedule.form.cronExpression.helper') }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item :label="$t('views.schedule.form.cronExpression.explanation')+':'" class='required-dot'>
            <div v-if="cronError" class="cron-error mt-4">
              <el-alert type="error" :title="cronError" :closable="false" show-icon />
            </div>
            <div v-if="cronValid && cronNextRun" class="cron-valid mt-4">
              <el-alert type="success" :title="$t('views.schedule.form.cronExpression.nextRun', { time: cronNextRun })"
                :closable="false" show-icon />
            </div>
          </el-form-item>
          <el-form-item :label="$t('views.schedule.form.cronExpression.rule')+':'" class='required-dot'>
            <div v-if="cronValid && cronDescription" class="cron-valid mt-4">
              <el-alert type="info" :title="cronDescription" :closable="false" show-icon />
            </div>
          </el-form-item>


          <el-form-item :label="$t('views.schedule.form.functionLib.label')+':'" prop="function_lib_id">
            <el-select v-model="form.function_lib_id" :placeholder="$t('views.schedule.form.functionLib.placeholder')"
              style="width: 100%" @change="handleFunctionLibChange">
              <el-option v-for="(item, index) in functionList" :key="item.id"
                :label="'(' + (index + 1) + ')' + item.name" :value="item.id" />
            </el-select>
          </el-form-item>

          <!-- 显示函数代码 -->
          <el-form-item v-if="selectedFunction" :label="$t('views.schedule.form.functionCode.label')+':'" class='required-dot'>
            <div class="function-CodemirrorEditor mb-8" v-if="showEditor">
              <CodemirrorEditor v-model="selectedFunction.code" :readonly="true" :title="$t('views.schedule.form.functionCode.label')" />
            </div>
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.params.label')+':'" prop="params" class='required-dot'>
            <div class="flex-between mb-8 align-center">
              <span>{{ $t('views.schedule.form.params.title') }}</span>
              <el-button link type="primary" @click="openAddParamDialog()">
                <el-icon class="mr-4">
                  <Plus />
                </el-icon> {{ $t('common.add') }}
              </el-button>
              <div class="function-debug-btn">
                <el-button type="primary" @click="debugFunction" size="small">
                  {{ $t('common.debug') }}
                </el-button>
              </div>
            </div>

            <el-table :data="paramsList" class="mb-16">
              <el-table-column prop="name" :label="$t('views.schedule.form.params.paramName')" />
              <el-table-column :label="$t('views.schedule.form.params.paramType')" width="120">
                <template #default="{ row }">
                  <el-select v-model="row.type" size="small" style="width: 100%">
                    <el-option value="string" label="字符串" />
                    <el-option value="number" label="数字" />
                    <el-option value="boolean" label="布尔值" />
                    <el-option value="object" label="对象" />
                    <el-option value="array" label="数组" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="value" :label="$t('views.schedule.form.params.paramValue')">
                <template #default="{ row }">
                  <el-input-number v-if="row.type === 'number'" v-model="row.value" :controls="false" />
                  <el-switch v-else-if="row.type === 'boolean'" v-model="row.value" />
                  <el-input v-else v-model="row.value"
                    :type="row.type === 'object' || row.type === 'array' ? 'textarea' : 'text'" />
                </template>
              </el-table-column>
              <el-table-column :label="$t('common.operation')" align="left" width="90">
                <template #default="{ $index }">
                  <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                    <el-button type="primary" text @click="deleteParam($index)">
                      <el-icon>
                        <Delete />
                      </el-icon>
                    </el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.isActive.label')+':'" prop="is_active" class='required-dot'>
            <el-switch v-model="form.is_active" />
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.dataset.label')+':'" prop="dataset_id" class='required-dot'>
            <el-select v-model="form.dataset_id" :placeholder="$t('views.schedule.form.dataset.placeholder')" clearable
              style="width: 100%">
              <el-option v-for="(item, index) in datasetList" :key="item.id"
                :label="'(' + (index + 1) + ')' + item.name" :value="item.id" />
            </el-select>
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.model.label')+':'" prop="model_id" class='required-dot'>
            <el-select v-model="form.model_id" :placeholder="$t('views.schedule.form.model.placeholder')" clearable
              style="width: 100%">
              <el-option v-for="(item, index) in modelList" :key="item.id" :label="'(' + (index + 1) + ')' + item.name"
                :value="item.id" />
            </el-select>
          </el-form-item>

          <el-form-item :label="$t('views.schedule.form.prompt.label')+':'" prop="prompt" class='required-dot'>
            <el-input v-model="form.prompt" type="textarea" :rows="5"
              :placeholder="promptPlaceholder" />
            <div class="help-text">
              {{ promptHelp }}
            </div>
            <div class="help-text mt-2" style="color: #909399;">
              <el-icon><InfoFilled /></el-icon> 示例：请根据下面的数据，分析。数据是：<span style="color: #409EFF;">{data}</span>
            </div>
          </el-form-item>

          <!-- 标题提示词输入框 -->
          <el-form-item :label="$t('views.schedule.form.titlePrompt.label')+':'" prop="title_prompt" class='required-dot'>
            <el-input v-model="form.title_prompt" type="textarea" :rows="3"
              :placeholder="titlePromptPlaceholder" />
            <div class="help-text">
              {{ titlePromptHelp }}
            </div>
            <!-- 添加示例提示 -->
            <div>
              <div class="help-text mt-2" style="color: #909399;">
                <el-icon><InfoFilled /></el-icon> 示例：请根据以下内容生成标题：<span style="color: #409EFF;">{content}</span>
              </div>
              <div class="help-text mt-2" style="color: #909399;">
                <el-icon><InfoFilled /></el-icon> 示例：请根据以下内容生成带时间的标题：<span style="color: #409EFF;">{content}</span>
              </div>
            </div>
          </el-form-item>

          <!-- 添加新的表单项 -->
          <el-form-item :label="$t('views.schedule.form.retainThinking.label')+':'" prop="retain_thinking" class='required-dot'>
            <el-switch v-model="form.retain_thinking" />
            <div class="help-text">
              {{ $t('views.schedule.form.retainThinking.help') }}
            </div>
          </el-form-item>
        </el-form>
      </template>
      <template #footer>
        <div style="flex: auto">
          <el-button @click="close">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submit" :loading="loading">
            {{ $t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-drawer>

    <!-- CRON表达式助手对话框 -->
    <el-dialog v-model="showCronHelper" :title="$t('views.schedule.form.cronExpression.helper')" width="60%"
      append-to-body>
      <div class="cron-helper-content">
        <h3>{{ $t('views.schedule.form.cronExpression.format') }}</h3>
        <p class="mb-16">
          {{ $t('views.schedule.form.cronExpression.formatDesc') }}
        </p>

        <!-- CRON可视化配置 -->
        <div class="cron-builder mb-16">
          <h3>{{ $t('views.schedule.form.cronExpression.builder') }}</h3>
          <div class="cron-builder-form">
            <el-form label-width="100px">
              <el-form-item :label="$t('views.schedule.form.cronExpression.minute')">
                <el-select v-model="cronBuilder.minute" @change="updateCronExpression">
                  <el-option value="*" :label="$t('views.schedule.form.cronExpression.every')" />
                  <el-option v-for="n in 60" :key="`min-${n - 1}`" :value="(n - 1).toString()"
                    :label="(n - 1).toString().padStart(2, '0')" />
                </el-select>
              </el-form-item>

              <el-form-item :label="$t('views.schedule.form.cronExpression.hour')">
                <el-select v-model="cronBuilder.hour" @change="updateCronExpression">
                  <el-option value="*" :label="$t('views.schedule.form.cronExpression.every')" />
                  <el-option v-for="n in 24" :key="`hour-${n - 1}`" :value="(n - 1).toString()"
                    :label="(n - 1).toString().padStart(2, '0')" />
                </el-select>
              </el-form-item>

              <el-form-item :label="$t('views.schedule.form.cronExpression.day')">
                <el-select v-model="cronBuilder.day" @change="updateCronExpression">
                  <el-option value="*" :label="$t('views.schedule.form.cronExpression.every')" />
                  <el-option v-for="n in 31" :key="`day-${n}`" :value="n.toString()" :label="n.toString()" />
                </el-select>
              </el-form-item>

              <el-form-item :label="$t('views.schedule.form.cronExpression.month')">
                <el-select v-model="cronBuilder.month" @change="updateCronExpression">
                  <el-option value="*" :label="$t('views.schedule.form.cronExpression.every')" />
                  <el-option value="1" label="1月" />
                  <el-option value="2" label="2月" />
                  <el-option value="3" label="3月" />
                  <el-option value="4" label="4月" />
                  <el-option value="5" label="5月" />
                  <el-option value="6" label="6月" />
                  <el-option value="7" label="7月" />
                  <el-option value="8" label="8月" />
                  <el-option value="9" label="9月" />
                  <el-option value="10" label="10月" />
                  <el-option value="11" label="11月" />
                  <el-option value="12" label="12月" />
                </el-select>
              </el-form-item>

              <el-form-item :label="$t('views.schedule.form.cronExpression.weekday')">
                <el-select v-model="cronBuilder.weekday" @change="updateCronExpression">
                  <el-option value="*" label="每天" />
                  <el-option value="?" label="不指定" />
                  <el-option value="1" label="周一" />
                  <el-option value="2" label="周二" />
                  <el-option value="3" label="周三" />
                  <el-option value="4" label="周四" />
                  <el-option value="5" label="周五" />
                  <el-option value="6" label="周六" />
                  <el-option value="7" label="周日" />
                </el-select>
              </el-form-item>
            </el-form>

            <div class="mt-16">
              <strong>表达式: </strong> 0 {{ cronBuilder.minute }} {{ cronBuilder.hour }} {{ cronBuilder.day }} {{
                cronBuilder.month }} {{ cronBuilder.weekday }}
            </div>

            <div class="mt-8" v-if="cronDescription">
              <strong>描述: </strong> {{ cronDescription }}
            </div>

            <!-- 添加应用按钮 -->
            <div class="mt-12 text-right">
              <el-button type="primary" @click="applyBuilderExpression">
                {{ $t('views.schedule.form.cronExpression.apply') }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 常用CRON表达式示例 -->
        <div class="cron-examples">
          <h3>{{ $t('views.schedule.form.cronExpression.examples') }}</h3>
          <el-table :data="cronExamples" stripe style="width: 100%">
            <el-table-column prop="expression" label="CRON表达式" width="200" />
            <el-table-column prop="description" :label="$t('views.schedule.form.cronExpression.description')" />
            <el-table-column :label="$t('views.schedule.form.cronExpression.action')" width="100">
              <template #default="scope">
                <el-button @click="applyCronExample(scope.row.expression)" type="primary" link>
                  {{ $t('views.schedule.form.cronExpression.apply') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 函数调试抽屉 -->
    <FunctionDebugDrawer ref="functionDebugDrawerRef" />

    <!-- 参数对话框 -->
    <el-dialog v-model="paramDialogVisible"
      :title="isEditParam ? $t('views.schedule.form.params.editParam') : $t('views.schedule.form.params.addParam')"
      width="30%" append-to-body>
      <el-form label-width="80px">
        <el-form-item :label="$t('views.schedule.form.params.paramName')">
          <el-input v-model="currentParam.name" />
        </el-form-item>
        <el-form-item :label="$t('views.schedule.form.params.paramType')">
          <el-select v-model="currentParam.type" style="width: 100%">
            <el-option value="string" label="字符串" />
            <el-option value="number" label="数字" />
            <el-option value="boolean" label="布尔值" />
            <el-option value="object" label="对象" />
            <el-option value="array" label="数组" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('views.schedule.form.params.paramValue')">
          <el-input-number v-if="currentParam.type === 'number'" v-model="currentParam.value" :controls="false" />
          <el-switch v-else-if="currentParam.type === 'boolean'" v-model="currentParam.value" />
          <el-input v-else v-model="currentParam.value"
            :type="currentParam.type === 'object' || currentParam.type === 'array' ? 'textarea' : 'text'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="paramDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="addParam">{{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { MsgSuccess, MsgError } from '@/utils/message'
import scheduleApi from '@/api/schedule'
import functionLibApi from '@/api/function-lib'
import datasetApi from '@/api/dataset'
import modelApi from '@/api/model'
import type { FormInstance, FormRules } from 'element-plus'
import type { ScheduleTaskData } from '@/api/type/schedule'
import FunctionDebugDrawer from '@/views/function-lib/component/FunctionDebugDrawer.vue'
import ExpressionDescriptor from 'cronstrue/i18n'
import CronExpressionParser from 'cron-parser'
import dayjs from 'dayjs'
import { Plus, Delete, InfoFilled, ZoomIn } from '@element-plus/icons-vue'
import CodemirrorEditor from '@/components/codemirror-editor/index.vue'
import AppIcon from '@/components/icons/AppIcon.vue'

const { t } = useI18n()
const emit = defineEmits(['refresh'])
const props = defineProps({
  title: {
    type: String,
    default: ''
  }
})

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const functionList = ref<any[]>([])
const currentId = ref('')
const selectedFunction = ref<any>(null)
const functionDebugDrawerRef = ref()
const cronError = ref('')
const cronValid = ref(false)
const cronNextRun = ref('')
const showCronHelper = ref(false)
const cronDescription = ref('')
const paramsList = ref<{ name: string, type: string, value: string }[]>([])

// 参数对话框
const paramDialogVisible = ref(false)
const currentParam = ref({ name: '', type: 'string', value: '' })
const isEditParam = ref(false)
const paramIndex = ref(-1)

// Cron构建器
const cronBuilder = reactive({
  minute: '*',
  hour: '*',
  day: '*',
  month: '*',
  weekday: '*'
})

const monthNames = [
  '1月', '2月', '3月', '4月', '5月', '6月',
  '7月', '8月', '9月', '10月', '11月', '12月'
]

const weekdayNames = [
  '星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'
]

// CRON表达式示例 - 增加更多常用示例
const cronExamples = [
  { expression: "0 0 * * * *", description: "每小时" },
  { expression: "0 0 0 * * *", description: "每天午夜零点" },
  { expression: "0 0 12 * * *", description: "每天中午12点" },
  { expression: "0 15 10 * * *", description: "每天上午10:15" },
  { expression: "0 0/30 8-10 * * *", description: "每天8点到10点每半小时" },
  { expression: "0 0 0 1 * *", description: "每月1日零点" },
  { expression: "0 0 0 * * 1", description: "每周一零点" },
  { expression: "0 0 9-17 * * 1-5", description: "工作日上午9点到下午5点每小时" },
  { expression: "0 0/5 * * * *", description: "每5分钟" },
  { expression: "0 0 0 1,15 * *", description: "每月1日和15日的零点" },
  { expression: "0 0 0 L * *", description: "每月最后一天的零点" },
  { expression: "0 0 0 ? * 6L", description: "每月最后一个星期五的零点" }
]

const datasetList = ref<any[]>([])
const modelList = ref<any[]>([])

const rules = reactive<FormRules>({
  name: [
    { required: true, message: t('views.schedule.form.name.required'), trigger: 'blur' }
  ],
  cron_expression: [
    {
      required: true,
      message: t('views.schedule.form.cronExpression.requiredMessage'),
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error(t('views.schedule.form.cronExpression.required')))
          return
        }

        // 确保有完整的cron表达式格式
        const cronExpr = value.trim().split(' ').length === 5
          ? `0 ${value}`
          : value

        try {
          // 使用正确的解析方法
          CronExpressionParser.parse(cronExpr)
          callback()
        } catch (e) {
          callback(new Error(t('views.schedule.form.cronExpression.invalid')))
        }
      },
      trigger: 'blur'
    }
  ],
  function_lib_id: [
    { required: true, message: t('views.schedule.form.functionLib.required'), trigger: 'change' }
  ],
  params: [
    {
      validator: (rule, value, callback) => {
        if (!value) return callback()

        try {
          JSON.parse(value)
          callback()
        } catch (e) {
          callback(new Error(t('views.schedule.form.params.invalid')))
        }
      },
      trigger: 'blur'
    }
  ]
})

const showEditor = ref(false)
const dialogVisible = ref(false)
const dialogCodeContent = ref('')

// 修改所有占位符文本，避免i18n嵌套占位符错误
const promptPlaceholder = '请输入提示词模板，可以使用{{data}}引用任务执行结果'
const promptHelp = '提示词中的{{data}}将被替换为任务执行结果，模型将根据提示词生成内容后保存到知识库'
const promptDefaultContent = '请根据下面的数据，分析。\n数据是：{{data}}'
const titlePromptPlaceholder = '请输入生成标题的提示词，可以使用{{content}}引用生成内容'
const titlePromptHelp = '提示词中的{{content}}将被替换为上面大模型回答的内容，模型将根据此提示词、内容生成标题并导入到知识库。因为函数运行结果通常是json或数据库查询结果，可读性差，可以让大模型总结为一段话或分析报表，便于阅读和理解。再让大模型基于总结的内容，生成标题、带时间的标题，便于检索'
const titlePromptDefaultContent = '请根据以下内容生成一个标题：\n{{content}}'


const form = reactive<any>({
  name: '',
  desc: '',
  cron_expression: '',
  function_lib_id: '',
  params: '{}',
  is_active: true,
  dataset_id: '',
  model_id: '',
  prompt: promptDefaultContent,
  title_prompt: titlePromptDefaultContent,
  retain_thinking: false,
  task_params: {}
})

watch(selectedFunction, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      showEditor.value = true
    }, 100)
  } else {
    showEditor.value = false
  }
})

function handleFunctionLibChange(functionId: string) {
  if (!functionId) {
    selectedFunction.value = null
    return
  }

  functionLibApi.getFunctionLibById(functionId, loading).then((res) => {
    selectedFunction.value = res.data
  })
}

function debugFunction() {
  if (!selectedFunction.value) return

  const debugData = {
    code: selectedFunction.value.code,
    input_field_list: selectedFunction.value.input_field_list,
    init_field_list: selectedFunction.value.init_field_list || [],
    debug_field_list: [] as any[]
  }

  // 准备参数值的映射，包含类型
  const paramsMap = paramsList.value.reduce((acc, param) => {
    acc[param.name] = {
      value: param.value,
      type: param.type
    }
    return acc
  }, {} as Record<string, { value: string, type: string }>)

  // 将参数添加到调试字段列表
  if (selectedFunction.value.input_field_list) {
    selectedFunction.value.input_field_list.forEach((field: any) => {
      const param = paramsMap[field.name]
      if (param) {
        let value = param.value

        // 根据类型转换值
        if (param.type === 'number') {
          value = String(Number(value))
        } else if (param.type === 'boolean') {
          value = String(Boolean(value))
        } else if (param.type === 'object' || param.type === 'array') {
          try {
            value = JSON.stringify(JSON.parse(value))
          } catch (e) {
            // 保持原始值
          }
        }

        debugData.debug_field_list.push({
          ...field,
          value
        })
      } else {
        debugData.debug_field_list.push({
          ...field,
          value: ''
        })
      }
    })
  }

  functionDebugDrawerRef.value.open(debugData)
  console.log('Debug function called with data:', debugData)
}

function validateCronExpression() {
  formRef.value?.validateField('cron_expression')
  if (!form.cron_expression) {
    cronError.value = t('views.schedule.form.cronExpression.required')
    cronValid.value = false
    cronNextRun.value = ''
    cronDescription.value = ''
    return
  }

  // 首先规范化CRON表达式，确保至少有5个部分
  let cronExpr = form.cron_expression.trim();
  const parts = cronExpr.split(' ');

  // 如果部分不足5个，添加缺失的部分
  if (parts.length < 5) {
    while (parts.length < 5) {
      parts.push('*');
    }
    cronExpr = parts.join(' ');
  }

  // 添加秒字段（如果需要）
  const cronExpression = parts.length === 5 ? `0 ${cronExpr}` : cronExpr;

  try {
    // 使用正确的解析方法
    const interval = CronExpressionParser.parse(cronExpression)
    cronError.value = ''
    cronValid.value = true
    const next = interval.next().toDate()
    cronNextRun.value = dayjs(next).format('YYYY-MM-DD HH:mm:ss')

    // 使用cronstrue库转换为描述文本
    try {
      console.log('解析CRON表达式:', cronExpression);
      cronDescription.value = ExpressionDescriptor.toString(cronExpression, { locale: 'zh_CN', use24HourTimeFormat: true, verbose: true });
      console.log('解析结果:', cronDescription.value);
    } catch (e) {
      console.error('解析CRON表达式失败:', cronExpression, e);
      cronDescription.value = '无法解析的表达式格式';
    }
  } catch (e) {
    console.error('验证CRON表达式失败:', cronExpression, e);
    cronError.value = t('views.schedule.form.cronExpression.invalid')
    cronValid.value = false
    cronNextRun.value = ''
    cronDescription.value = ''
  }
}

function updateCronExpression() {
  const { minute, hour, day, month, weekday } = cronBuilder
  form.cron_expression = `0 ${minute} ${hour} ${day} ${month} ${weekday}`
  validateCronExpression()
}

function applyCronExample(expression: string) {
  form.cron_expression = expression
  validateCronExpression()
  showCronHelper.value = false
}

// 应用生成器中配置的CRON表达式
function applyBuilderExpression() {
  const { minute, hour, day, month, weekday } = cronBuilder
  const expression = `0 ${minute} ${hour} ${day} ${month} ${weekday}`
  form.cron_expression = expression
  validateCronExpression()
  showCronHelper.value = false
}

function getFunctionList() {
  functionLibApi.getAllFunctionLib({}, loading).then((res) => {
    functionList.value = res.data
  })
}

function open(data?: ScheduleTaskData) {
  visible.value = true
  selectedFunction.value = null
  showEditor.value = false
  formRef.value?.clearValidate()

  // 获取数据集列表
  datasetApi.getAllDataset().then(res => {
    datasetList.value = res.data || []
  })

  // 获取模型列表
  modelApi.getModel({ model_type: 'LLM' }).then(res => {
    modelList.value = res.data || []
  })

  // 重置表单 
  Object.assign(form, {
    name: '',
    desc: '',
    cron_expression: '',
    function_lib_id: '',
    params: '{}',
    is_active: true,
    dataset_id: '',
    model_id: '',
    prompt: promptDefaultContent,
    title_prompt: titlePromptDefaultContent,
    retain_thinking: false,
    task_params: {}
  })

  paramsList.value = []

  if (data) {
    currentId.value = data.id
    Object.assign(form, data)
    // 确保params是字符串
    if (typeof form.params === 'object') {
      form.params = JSON.stringify(form.params, null, 2)
    }

    // 解析任务参数
    if (data.task_params) {
      if (typeof data.task_params === 'string') {
        try {
          form.task_params = JSON.parse(data.task_params);
        } catch (e) {
          form.task_params = {};
        }
      } else {
        form.task_params = data.task_params || {};
      }

      // 从task_params中提取标题提示词
      if (form.task_params.title_prompt) {
        form.title_prompt = form.task_params.title_prompt;
      }
    }

    // 解析参数
    parseParamsJson()

    // 如果是编辑状态，加载函数详情
    if (form.function_lib_id) {
      handleFunctionLibChange(form.function_lib_id)
    }

    // 验证CRON表达式
    validateCronExpression()

    // 解析CRON表达式，更新构建器
    if (form.cron_expression) {
      const parts = form.cron_expression.split(' ')
      if (parts.length >= 6) {
        cronBuilder.minute = parts[1]
        cronBuilder.hour = parts[2]
        cronBuilder.day = parts[3]
        cronBuilder.month = parts[4]
        cronBuilder.weekday = parts[5]
      }
    }

    // 加载选中的函数
    if (form.function_lib_id) {
      loadSelectedFunction(form.function_lib_id)
    }
  } else {
    // 重置CRON构建器
    cronBuilder.minute = '*'
    cronBuilder.hour = '*'
    cronBuilder.day = '*'
    cronBuilder.month = '*'
    cronBuilder.weekday = '*'
    // 重置参数列表
    paramsList.value = []
    form.params = '{}'
  }

  showEditor.value = false
}

function close() {
  visible.value = false
  formRef.value?.resetFields()
  currentId.value = ''
  selectedFunction.value = null
  cronError.value = ''
  cronValid.value = false
  cronNextRun.value = ''
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      
      // 更新参数
      updateParamsJson()

      // 确保params是JSON对象
      let paramsObject = {}
      try {
        paramsObject = JSON.parse(form.params)
      } catch (e) {
        paramsObject = {}
      }

      // 构建task_params对象
      const taskParams = {
        ...form.task_params,
        title_prompt: form.title_prompt
      }

      const submitData = { 
        ...form, 
        params: paramsObject,
        task_params: taskParams
      }

      if (currentId.value) {
        scheduleApi.putScheduleTask(currentId.value, submitData, loading).then(() => {
          MsgSuccess(t('common.updateSuccess'))
          close()
          emit('refresh')
        })
      } else {
        scheduleApi.createScheduleTask(submitData, loading).then(() => {
          MsgSuccess(t('common.createSuccess'))
          close()
          emit('refresh')
        })
      }
    }
  })
}

// 确保title_prompt中包含{content}占位符
function ensureTitlePromptContainsPlaceholder() {
  if (!form.title_prompt) {
    // 如果为空，设置为默认值
    form.title_prompt = titlePromptDefaultContent
    return
  }
  
  // 如果不包含{content}占位符，则在末尾添加
  if (!form.title_prompt.includes('{content}')) {
    form.title_prompt = form.title_prompt.trim() + '\n{content}'
  }
}

// 打开添加参数对话框
function openAddParamDialog(param?: any, index?: number) {
  if (param) {
    currentParam.value = { ...param }
    isEditParam.value = true
    paramIndex.value = index !== undefined ? index : -1
  } else {
    currentParam.value = { name: '', type: 'string', value: '' }
    isEditParam.value = false
    paramIndex.value = -1
  }
  paramDialogVisible.value = true
}

// 删除参数
function deleteParam(index: number) {
  paramsList.value.splice(index, 1)
  updateParamsJson()
}

// 添加参数
function addParam() {
  if (!currentParam.value.name) return

  if (isEditParam.value && paramIndex.value >= 0) {
    paramsList.value[paramIndex.value] = { ...currentParam.value }
  } else {
    paramsList.value.push({ ...currentParam.value })
  }

  paramDialogVisible.value = false
  updateParamsJson()
}

// 更新JSON字符串，考虑参数类型
function updateParamsJson() {
  const paramsObj = paramsList.value.reduce((acc, curr) => {
    // 根据类型转换值
    // let paramValue = curr.value;
    acc[curr.name] = curr.value;
    try {
      if (curr.type === 'number') {
        acc[curr.name] = Number(curr.value);
      } else if (curr.type === 'boolean') {
        acc[curr.name] = curr.value.toLowerCase() === 'true';
      } else if (curr.type === 'object' || curr.type === 'array') {
        acc[curr.name] = JSON.parse(curr.value);
      }
    } catch (e) {
      // 转换失败时保持原始字符串
      console.error('参数转换失败:', curr.name, e);
    }

    return acc;
  }, {} as Record<string, any>)

  form.params = JSON.stringify(paramsObj, null, 2)
}

// 解析JSON字符串到参数列表
function parseParamsJson() {
  try {
    if (!form.params) {
      paramsList.value = []
      return
    }

    const paramsObj = JSON.parse(form.params)
    paramsList.value = Object.entries(paramsObj).map(([name, value]) => {
      // 推断参数类型
      let type = 'string';
      let stringValue = '';

      if (value === null) {
        type = 'string';
        stringValue = '';
      } else if (typeof value === 'number') {
        type = 'number';
        stringValue = String(value);
      } else if (typeof value === 'boolean') {
        type = 'boolean';
        stringValue = String(value);
      } else if (typeof value === 'object') {
        if (Array.isArray(value)) {
          type = 'array';
        } else {
          type = 'object';
        }
        stringValue = JSON.stringify(value);
      } else {
        stringValue = String(value);
      }

      return {
        name,
        type,
        value: stringValue
      };
    })
  } catch (e) {
    console.error('解析参数失败:', e);
    paramsList.value = []
  }
}

// 添加代码全屏查看对话框
function openCodemirrorDialog() {
  if (selectedFunction.value) {
    dialogCodeContent.value = selectedFunction.value.code
    dialogVisible.value = true
  }
}

// 获取知识库列表
const loadDatasetList = async () => {
  const res = await datasetApi.getAllDataset()
  if (res.data) {
    datasetList.value = res.data
  }
  console.log('获取知识库列表', datasetList.value)
}

// 获取参数类型
function getParamType(value: any) {
  const type = typeof value
  if (type === 'object') {
    if (Array.isArray(value)) {
      return 'array'
    }
    return 'object'
  }
  return type
}

// 加载选中的函数
function loadSelectedFunction(functionId: any) {
  functionLibApi.getFunctionLibById(functionId).then(res => {
    selectedFunction.value = res.data
    showEditor.value = true
  }).catch(error => {
    console.error('加载函数详情出错', error)
  })
}

onMounted(() => {
  loadDatasetList()
  getFunctionList()
})

defineExpose({ open })
</script>

<style lang="scss" scoped>
.schedule-form {
  padding: 0 20px;
}

.function-debug-btn {
  margin-left: 10px;
  text-align: right;
}

.cron-expression-container {
  display: flex;
  align-items: center;
}

.cron-helper-content {
  max-height: 600px;
  overflow-y: auto;
}

.cron-builder-form {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.function-CodemirrorEditor {
  position: relative;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}
</style>