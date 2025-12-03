export default {
  title: '定时任务',
  createTask: '创建任务',
  editTask: '编辑任务',
  taskName: '任务名称',
  taskDesc: '任务描述',
  cronExpression: 'Cron表达式',
  deleteConfirm: '确定要删除此任务吗？',
  searchBar: {
    placeholder: '按任务名称搜索'
  },
  executionRule: '执行规则',
  nextExecution: '下次执行',
  description: '描述',
  function: '关联函数',
  parameters: '函数参数',
  status: '状态',
  nextRun: '下次执行时间',
  taskDetail: '任务详情',
  taskInfo: '任务信息',
  executionRecords: '执行记录',
  recordStatus: '执行状态',
  startTime: '开始时间',
  endTime: '结束时间',
  result: '执行结果',
  errorMessage: '错误信息',
  viewDetail: '查看详情',
  updateTime: '更新时间',
  scheduled: '已调度',
  notScheduled: '未调度',
  tip: {
    taskNamePlaceholder: '请输入任务名称',
    descriptionPlaceholder: '请输入任务描述（可选）',
    cronExpressionPlaceholder: '例如: */5 * * * *',
    cronExpressionHelp: 'Cron格式: 分 时 日 月 星期，例如：*/5 * * * * 表示每5分钟执行一次',
    selectFunction: '请选择要执行的函数',
    paramsPlaceholder: '请输入JSON格式的函数参数，例如: {"key": "value"}',
    nameRequired: '任务名称不能为空',
    cronRequired: 'Cron表达式不能为空',
    functionRequired: '请选择要执行的函数',
    invalidJson: '参数不是有效的JSON格式',
    valueRequired: '字段值不能为空',
    taskEnabled: '任务已启用',
    taskDisabled: '任务已禁用'
  },
  delete: {
    confirmTitle: '确认删除任务',
    confirmMessage: '删除后将无法恢复，确认继续吗？'
  },
  form: {
    name: {
      label: '任务名称',
      placeholder: '请输入任务名称',
      requiredMessage: '请输入任务名称'
    },
    desc: {
      label: '任务描述', 
      placeholder: '请输入任务描述'
    },
    cronExpression: {
      label: 'Cron表达式',
      placeholder: '请输入Cron表达式',
      requiredMessage: '请输入Cron表达式',
      helper: 'CRON表达式助手',
      format: 'CRON表达式格式',
      formatDesc: 'CRON表达式由6个字段组成，表示：秒 分 时 日 月 星期。例如：0 0 12 * * ? 表示每天12点运行。',
      builder: 'CRON表达式生成器',
      examples: '常用示例',
      description: '描述',
      action: '操作',
      apply: '应用',
      minute: '分钟',
      hour: '小时',
      day: '日',
      month: '月',
      weekday: '星期',
      every: '每',
      nextRun: '下次执行时间: {time}',
      invalid: '无效的CRON表达式',
      required: '请输入CRON表达式',
      explanation: '执行说明',
      rule: '执行规则'
    },
    functionLib: {
      label: '执行函数',
      placeholder: '请选择执行函数',
      requiredMessage: '请选择执行函数',
      required: '请选择执行函数'
    },
    functionCode: {
      label: '函数代码'
    },
    params: {
      label: '函数参数',
      placeholder: '请输入函数参数',
      title: '参数列表',
      paramName: '参数名称',
      paramType: '参数类型',
      paramValue: '参数值',
      addParam: '添加参数',
      editParam: '编辑参数',
      invalid: '参数格式不正确，请输入有效的JSON格式',
      typeString: '字符串',
      typeNumber: '数字',
      typeBoolean: '布尔值',
      typeObject: '对象',
      typeArray: '数组'
    },
    isActive: {
      label: '是否启用'
    },
    dataset: {
      label: '关联知识库',
      placeholder: '请选择知识库',
      requiredMessage: '请选择知识库'
    },
    model: {
      label: '关联模型',
      placeholder: '请选择大语言模型',
      requiredMessage: '请选择模型'
    },
    prompt: {
      label: '提示词模板'
    },
    retainThinking: {
      label: '保留思考内容',
      help: '是否保留模型的思考过程'
    },
    titlePrompt: {
      label: '标题提示词'
    }
  },
  execute: '执行一次',
  executeConfirm: '确定要执行该任务吗？',
  executeSuccess: '执行成功',
  lastExecution: '上次执行时间',
} 