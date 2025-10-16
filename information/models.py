# information/models.py

from django.db import models
from django.conf import settings  # 导入 settings 来安全地引用项目激活的 User 模型


class Information(models.Model):
    # --- 核心修正：使用 OneToOneField 建立与 User 模型的一对一关系 ---
    # 这确保了一个用户只能有一条个人信息记录，并且数据是关联的，而不是简单的文本。
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # 安全地引用在 settings.py 中定义的 AUTH_USER_MODEL
        on_delete=models.CASCADE,  # 级联删除：当 User 被删除时，这条 Information 记录也一起被删除
        primary_key=True,  # 将此关系字段设为主键，性能更好，也从数据库层面保证了一对一
        verbose_name="所属用户",  # 在 Admin 后台显示的字段名
    )

    # --- 优化其他数据字段 ---

    # 使用 FloatField 更适合存储可能带小数的身高和体重
    height = models.FloatField(
        default=170.0, verbose_name="身高 (cm)", help_text="单位为厘米"
    )

    weight = models.FloatField(
        default=55.0, verbose_name="体重 (kg)", help_text="单位为千克"
    )

    age = models.IntegerField(default=21, verbose_name="年龄")

    # 新增：性别字段（用于计算基础代谢）
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='male',
        verbose_name="性别"
    )

    target = models.TextField(blank=True, verbose_name="目标")
    Information = models.TextField(blank=True, verbose_name="个人简介")

    # --- 计算属性方法 ---

    @property
    def bmi(self) -> float:
        """
        计算BMI（身体质量指数）
        公式：BMI = 体重(kg) / (身高(m))²
        """
        if self.height > 0:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return 0.0

    @property
    def bmi_category(self) -> str:
        """
        根据BMI值返回健康状况分类
        """
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "偏瘦"
        elif 18.5 <= bmi_value < 24:
            return "正常"
        elif 24 <= bmi_value < 28:
            return "偏胖"
        else:
            return "肥胖"

    @property
    def bmr(self) -> float:
        """
        计算基础代谢率（BMR）- 使用Mifflin-St Jeor公式
        男性：BMR = 10 × 体重(kg) + 6.25 × 身高(cm) - 5 × 年龄 + 5
        女性：BMR = 10 × 体重(kg) + 6.25 × 身高(cm) - 5 × 年龄 - 161
        """
        bmr_value = 10 * self.weight + 6.25 * self.height - 5 * self.age
        if self.gender == 'male':
            bmr_value += 5
        else:
            bmr_value -= 161
        return round(bmr_value, 2)

    @property
    def daily_calories(self) -> float:
        """
        计算每日推荐热量摄入
        使用默认活动水平系数 1.2（久坐）
        """
        return round(self.bmr * 1.2, 2)

    # --- 添加模型元数据，提升可用性 ---

    def __str__(self):
        """
        定义当模型对象被转换为字符串时的显示方式。
        这在 Django Admin 和调试中非常有用。
        """
        return f"{self.user.username} 的个人信息"

    class Meta:
        """
        定义模型的元数据选项。
        """

        verbose_name = "个人信息"  # 在 Admin 中，模型的单数名称
        verbose_name_plural = "个人信息"  # 在 Admin 中，模型的复数名称
