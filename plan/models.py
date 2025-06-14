# plan/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class Plan(models.Model):
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='plans',
        verbose_name="所属用户"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="计划标题"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="详细描述"
    )

    class Weekday(models.IntegerChoices):
        MONDAY = 1, "星期一"
        TUESDAY = 2, "星期二"
        WEDNESDAY = 3, "星期三"
        THURSDAY = 4, "星期四"
        FRIDAY = 5, "星期五"
        SATURDAY = 6, "星期六"
        SUNDAY = 7, "星期日"

    day_of_week = models.IntegerField(
        choices=Weekday.choices,
        verbose_name="星期几"
    )

    start_time = models.TimeField(
        verbose_name="开始时间"
    )

    end_time = models.TimeField(
        verbose_name="结束时间"
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name="是否完成"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    @property
    def duration_minutes(self) -> int:
        """计算计划的持续分钟数"""
        # TimeField 可以直接进行减法运算，但结果是 timedelta 对象
        # 为了方便计算，我们将它们转换为 datetime 对象再相减
        dummy_date = datetime.date.today()
        start_datetime = datetime.datetime.combine(dummy_date, self.start_time)
        end_datetime = datetime.datetime.combine(dummy_date, self.end_time)
        
        # 处理跨天的情况
        if end_datetime < start_datetime:
            end_datetime += datetime.timedelta(days=1)
            
        delta = end_datetime - start_datetime
        return int(delta.total_seconds() / 60)

    # --- 模型元数据 ---
    def __str__(self):
        # 让对象在后台显示得更清晰
        start_str = self.start_time.strftime('%H:%M')
        return f"{self.get_day_of_week_display()} {start_str} - {self.user.username} 的计划: {self.title}"#type:ignore

    class Meta:
        # 默认按星期几，然后按开始时间排序
        ordering = ['day_of_week', 'start_time']
        verbose_name = "周常计划"
        verbose_name_plural = "周常计划"
