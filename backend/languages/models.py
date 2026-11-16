from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

# 资源类型 → 媒体子目录。目录结构：MEDIA_ROOT/languages/<语言 slug>/<子目录>/<顶层目录>/...
MEDIA_KINDS = {
    'video': 'videos',
    'audio': 'audios',
    'file': 'files',
}
MEDIA_KIND_CHOICES = [('video', '视频'), ('audio', '音频'), ('file', '资料')]


class LanguageCategory(models.Model):
    """语言分类，如「东亚语言」。"""
    name = models.CharField('名称', max_length=50, unique=True)
    description = models.CharField('简介', max_length=200, blank=True, default='')
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = verbose_name_plural = '语言分类'

    def __str__(self):
        return self.name


class Language(models.Model):
    """具体语言，如「韩语」。slug 决定网址与媒体目录名，创建后不建议修改。"""
    category = models.ForeignKey(LanguageCategory, on_delete=models.PROTECT, related_name='languages', verbose_name='分类')
    name = models.CharField('名称', max_length=50, unique=True)
    slug = models.CharField(
        '标识', max_length=20, unique=True,
        validators=[RegexValidator(r'^[a-z][a-z0-9-]*$', '只能使用小写字母、数字和连字符，且以字母开头')],
        help_text='用于网址与媒体目录，例如 ko、ja、en',
    )
    native_name = models.CharField('本地名称', max_length=50, blank=True, default='')
    description = models.CharField('简介', max_length=200, blank=True, default='')
    color = models.CharField('主题色', max_length=7, blank=True, default='#2ec4c0')
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = verbose_name_plural = '语言'

    def __str__(self):
        return self.name

    def media_dir(self, kind: str):
        return settings.MEDIA_ROOT / 'languages' / self.slug / MEDIA_KINDS[kind]


class MediaPermission(models.Model):
    """（已停用，2026-11-16 起登录用户可看全部资料；表与旧数据保留，便于以后恢复按目录授权）
    普通用户能看到的目录：某语言、某类资源下的顶层目录（或更深的子路径，用 / 分隔）。"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media_permissions')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='permissions')
    media_type = models.CharField(max_length=10, choices=MEDIA_KIND_CHOICES)
    root_dir = models.CharField(max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'language', 'media_type', 'root_dir'], name='uniq_media_permission'),
        ]

    def __str__(self):
        return f'{self.user} → {self.language.slug}/{self.media_type}:{self.root_dir}'
