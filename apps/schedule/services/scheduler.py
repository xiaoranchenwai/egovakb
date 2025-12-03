import logging
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from django.db import transaction
import re

from schedule.models import ScheduleTask, ScheduleTaskRecord
from function_lib.models.function import FunctionLib
from common.util.function_code import FunctionExecutor
from dataset.models import DataSet, Document, Paragraph

# logger = logging.getLogger(__name__)
max_kb = logging.getLogger(__file__)

class SchedulerService:
    _instance = None
    _scheduler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
            cls._instance._init_scheduler()
        return cls._instance
    
    def _init_scheduler(self):
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        self._scheduler.start()
        max_kb.info("任务调度器已启动")
    
    def start(self):
        """启动所有活跃的定时任务"""
        active_tasks = ScheduleTask.objects.filter(is_active=True)
        active_count = 0
        for task in active_tasks:
            if self.add_task(task):
                active_count += 1
        max_kb.info(f"已加载 {active_count} 个活跃的定时任务")
    
    def add_task(self, task):
        """添加一个定时任务到调度器"""
        job_id = f"task_{task.id}"
        
        # 如果任务已存在且需要更新，先移除旧任务
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
        
        if task.is_active:
            # 校验cron表达式
            try:
                # 检查cron表达式格式（5位或6位）
                cron_parts = task.cron_expression.split()
                if len(cron_parts) == 6:
                    # 6位cron表达式（带秒）：直接使用CronTrigger构造函数
                    trigger = CronTrigger(
                        second=cron_parts[0],
                        minute=cron_parts[1], 
                        hour=cron_parts[2],
                        day=cron_parts[3], 
                        month=cron_parts[4], 
                        day_of_week=cron_parts[5]
                    )
                elif len(cron_parts) == 5:
                    # 5位标准cron表达式：使用from_crontab
                    trigger = CronTrigger.from_crontab(task.cron_expression)
                else:
                    raise ValueError(
                        f"Cron表达式必须包含5或6个字段，当前有{len(cron_parts)}个"
                    )
            except Exception as e:
                max_kb.error(
                    f"任务 {task.name} (ID: {task.id}) 的cron表达式 "
                    f"'{task.cron_expression}' 无效: {str(e)}"
                )
                return False
                
            self._scheduler.add_job(
                self._execute_task,
                trigger,  # 使用上面创建的trigger
                id=job_id,
                args=[task.id],
                replace_existing=True
            )
            max_kb.info(f"任务已添加: {task.name} (ID: {task.id})")
            return True
        return False
    
    def remove_task(self, task_id):
        """从调度器中移除一个定时任务"""
        job_id = f"task_{task_id}"
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
            max_kb.info(f"任务已移除: {task_id}")
    
    def get_job_status(self, task_id):
        """获取任务的状态"""
        job_id = f"task_{task_id}"
        job = self._scheduler.get_job(job_id)
        if job:
            next_run = job.next_run_time
            return {
                "status": "SCHEDULED",
                "next_run_time": timezone.localtime(next_run).strftime("%Y-%m-%d %H:%M:%S") 
                if next_run else None
            }
        return {"status": "NOT_SCHEDULED"}
    
    def _execute_task(self, task_id):
        """执行一个定时任务"""
        try:
            task = ScheduleTask.objects.get(id=task_id)
            function = FunctionLib.objects.get(id=task.function_lib_id)
            
            # 创建执行记录
            with transaction.atomic():
                record = ScheduleTaskRecord(
                    task=task,
                    start_time=timezone.now(),
                    status="RUNNING"
                )
                record.save()
            
            try:
                # 执行函数
                executor = FunctionExecutor()
                result = executor.exec_code(function.code, task.params)
                
                # 如果任务有关联的数据集ID，将结果存储到数据集中
                if hasattr(task, 'dataset') and task.dataset:
                    ret, e = self._save_result_to_dataset(task.dataset.id, task.name, result)
                    if not ret:
                        raise Exception(e)
                
                # 更新执行记录
                with transaction.atomic():
                    record.status = "SUCCESS"
                    record.end_time = timezone.now()
                    record.result = str(result)
                    record.save()
                    
                max_kb.info(f"任务执行成功: {task.name} (ID: {task.id})")
                
            except Exception as e:
                # 执行失败
                with transaction.atomic():
                    record.status = "FAILED"
                    record.end_time = timezone.now()
                    record.error_message = str(e)
                    record.save()
                    
                max_kb.error(
                    f"任务执行失败: {task.name} (ID: {task.id}), 错误: {str(e)}"
                )
                
        except Exception as e:
            max_kb.error(f"执行任务 {task_id} 时发生错误: {str(e)}") 
    
    def _save_result_to_dataset(self, dataset_id, task_name, result):
        """将任务执行结果保存到数据集中"""
        try:
            from dataset.serializers.document_serializers import DocumentSerializers
            from common.config.embedding_config import ModelManage
            from langchain_core.messages import HumanMessage
            from setting.models_provider import get_model
            from setting.models import Model
            from django.db.models import QuerySet
            
            # 将UTC时间转换为本地时间
            local_time = timezone.localtime(timezone.now())
            time = local_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 准备文档数据
            document_data = {
                'name': f"{task_name} {time}",
                'paragraphs': [{
                    'content': str(result),
                    'title': f"{task_name} {time}"
                }]
            }
            
            # 获取关联任务
            task = ScheduleTask.objects.filter(name=task_name).first()
            
            # 如果配置了模型和提示词，使用模型生成结果
            if task and task.model_id and task.prompt:
                try:
                    max_kb.info(f"使用模型 {task.model_id} 生成内容")
                    
                    # 获取模型
                    model = QuerySet(Model).filter(id=task.model_id).first()
                    llm_model = ModelManage.get_model(task.model_id, lambda _id: get_model(model))
                    
                    # 用提示词替换结果内容生成新内容
                    prompt = task.prompt.replace('{data}', str(result))
                    res = llm_model.invoke([HumanMessage(content=prompt)])
                    
                    if res.content and len(res.content) > 0:
                        # 根据设置处理内容，移除思考部分
                        processed_content = self.process_response_content(res.content, task.retain_thinking)
                        # 更新文档内容为处理后的内容
                        document_data['paragraphs'][0]['content'] = processed_content
                        # 生成标题
                        title_prompt = "请根据以下内容生成一个标题：\n{content}"
                        
                        # 检查是否有自定义标题提示词
                        if task.task_params and 'title_prompt' in task.task_params:
                            title_prompt = task.task_params['title_prompt']
                        
                        # 替换标题提示词中的内容占位符
                        title_prompt = title_prompt.replace('{content}', processed_content)
                        
                        title_res = llm_model.invoke([HumanMessage(content=title_prompt)])
                        if title_res.content and len(title_res.content) > 0:    
                            processed_title = self.process_response_content(title_res.content, False, True)
                            document_data['paragraphs'][0]['title'] = processed_title
                            document_data['name'] = processed_title
                        max_kb.info("模型成功生成内容")
                except Exception as e:
                    max_kb.error(f"使用模型生成内容失败: {str(e)}")
                    return False, e
            
            # 使用批量保存方法保存文档
            DocumentSerializers.Batch(
                data={'dataset_id': dataset_id}
            ).batch_save([document_data])
            
            max_kb.info(f"已将任务 {task_name} 的执行结果保存到数据集 {dataset_id}")
            return True, None
        except Exception as e:
            max_kb.error(f"保存任务结果到数据集时出错: {str(e)}")
            return False, e
    
    def execute_task_manually(self, task_id):
        """手动执行一个定时任务"""
        try:
            # 执行任务
            self._execute_task(task_id)
            return True
        except Exception as e:
            max_kb.error(f"手动执行任务 {task_id} 失败: {str(e)}")
            return False 

    def process_response_content(self, content, retain_thinking=False, is_title=False):
        """处理响应内容，根据需要移除思考部分"""
        if not retain_thinking:
            # 移除 <think>...</think> 标签及其内容，以及</think>后面可能跟着的换行符
            content = re.sub(r'<think>.*?</think>\n?', '', content, flags=re.DOTALL)
            # 移除多余的空行
            content = re.sub(r'\n\s*\n', '\n\n', content)
            # 移除开头的换行符
            content = content.lstrip('\n')
        
        # 如果是标题，移除markdown符号
        if is_title:
            # 移除标题符号 ###
            content = re.sub(r'^#{1,6}\s*', '', content)
            # 移除加粗符号 **
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
            # 移除斜体符号 *
            content = re.sub(r'\*(.*?)\*', r'\1', content)
            # 移除其他可能的markdown符号
            content = re.sub(r'`(.*?)`', r'\1', content)  # 代码块
            content = re.sub(r'~~(.*?)~~', r'\1', content)  # 删除线
            content = re.sub(r'^\s*>\s*', '', content, flags=re.MULTILINE)  # 引用
            # 移除多余空格
            content = content.strip()
        
        return content 