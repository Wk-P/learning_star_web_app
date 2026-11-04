import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from .services import get_pdf_list


class GetPdfListTests(TestCase):
    """「学习资料」扫描：PDF 之外也包含常见文档，跳过临时/隐藏文件。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        folder = self.root / 'TOPIK_文档资料'
        folder.mkdir()
        for name in [
            '真题.pdf', '词汇表.xlsx', '同形词.hwp', '大写.PDF',  # 应列出
            '~$词汇表.xlsx', '.hidden.pdf', 'notes.txt', 'track.mp3',  # 应跳过
        ]:
            (folder / name).write_bytes(b'x')

    def tearDown(self):
        self.tmp.cleanup()

    def scan(self):
        with override_settings(PDF_ROOT=str(self.root)):
            return get_pdf_list()

    def test_lists_documents_and_skips_others(self):
        result = self.scan()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['path'], ['TOPIK_文档资料'])
        names = sorted(f"{p['title']}.{p['ext']}" for p in result[0]['pdfs'])
        self.assertEqual(names, ['同形词.hwp', '大写.pdf', '真题.pdf', '词汇表.xlsx'])

    def test_item_fields(self):
        item = next(p for p in self.scan()[0]['pdfs'] if p['ext'] == 'xlsx')
        self.assertEqual(item['title'], '词汇表')
        self.assertTrue(item['url'].endswith('pdfs/TOPIK_文档资料/词汇表.xlsx'))
