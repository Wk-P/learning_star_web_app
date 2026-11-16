from django.db import models


class Subject(models.Model):
    name = models.CharField('名称', max_length=100)
    description = models.TextField('简介', blank=True, default='')
    icon = models.CharField('图标', max_length=10, blank=True, default='📖')
    color = models.CharField('颜色', max_length=7, blank=True, default='#6366f1')
    keywords = models.CharField('B 站搜索关键词', max_length=200, blank=True, default='')  # 逗号分隔

    class Meta:
        ordering = ['id']
        verbose_name = verbose_name_plural = '科目'

    def __str__(self):
        return self.name


class CourseVideo(models.Model):
    """科目下的一条视频链接（原 bilibili/<科目>.txt 的一行）。"""
    LEVELS = ['入门', '基础', '进阶']

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos', verbose_name='科目')
    title = models.CharField('标题', max_length=500)
    url = models.CharField('链接', max_length=1000)
    level = models.CharField('阶段', max_length=10, blank=True, default='', choices=[(x, x) for x in LEVELS])
    tags = models.JSONField('标签', default=list, blank=True)  # 第一个为平台标签（B站 / YouTube），自动维护
    video_key = models.CharField('查重键', max_length=300, db_index=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject_id', 'sort_order', 'id']
        verbose_name = verbose_name_plural = '课程视频'
        constraints = [
            models.UniqueConstraint(fields=['subject', 'video_key'], name='uniq_subject_video'),
        ]

    def __str__(self):
        return self.title
