import sys
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedule'
    
    def ready(self):
        """应用启动时初始化调度器"""
        # 避免在开发环境下重复加载            
        # 导入放在这里防止循环导入
        from .services.scheduler import SchedulerService
        try:
            logger.info("正在初始化定时任务调度器...")
            scheduler = SchedulerService()
            logger.info("正在启动定时任务调度器...")
            scheduler.start()
            logger.info("定时任务调度器已启动")
        except Exception as e:
            logger.error(f"启动定时任务调度器失败: {str(e)}")
            # 打印更详细的错误信息，包括堆栈跟踪
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}") 