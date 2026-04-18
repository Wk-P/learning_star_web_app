from rest_framework.test import APITestCase
from rest_framework import status
from .models import Audio, AudioFolder


class AudioFolderModelTest(APITestCase):
    def setUp(self):
        self.folder = AudioFolder.objects.create(path=["root", "music"])

    def test_folder_creation(self):
        self.assertEqual(AudioFolder.objects.count(), 1)
        self.assertEqual(self.folder.path, ["root", "music"])

    def test_folder_default_path(self):
        folder = AudioFolder.objects.create()
        self.assertEqual(folder.path, [])


class AudioModelTest(APITestCase):
    def setUp(self):
        self.folder = AudioFolder.objects.create(path=["root"])
        self.audio = Audio.objects.create(
            title="Test Audio",
            url="https://example.com/audio.mp3",
            path=self.folder,
        )

    def test_audio_creation(self):
        self.assertEqual(Audio.objects.count(), 1)
        self.assertEqual(self.audio.title, "Test Audio")
        self.assertEqual(self.audio.url, "https://example.com/audio.mp3")

    def test_audio_belongs_to_folder(self):
        self.assertEqual(self.audio.path, self.folder)
        self.assertIn(self.audio, self.folder.audios_list.all())

    def test_audio_folder_deleted_sets_null(self):
        self.folder.delete()
        self.audio.refresh_from_db()
        self.assertIsNone(self.audio.path)


class AudioListViewTest(APITestCase):
    def setUp(self):
        self.folder1 = AudioFolder.objects.create(path=["root", "jazz"])
        self.folder2 = AudioFolder.objects.create(path=["root", "rock"])
        Audio.objects.create(title="Jazz Track", url="https://example.com/jazz.mp3", path=self.folder1)
        Audio.objects.create(title="Rock Track", url="https://example.com/rock.mp3", path=self.folder2)

    def test_list_returns_200(self):
        response = self.client.get("/api/audio/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_all_folders(self):
        response = self.client.get("/api/audio/list/")
        self.assertEqual(len(response.data), 2)

    def test_list_folder_structure(self):
        response = self.client.get("/api/audio/list/")
        folder_data = response.data[0]
        self.assertIn("id", folder_data)
        self.assertIn("path", folder_data)
        self.assertIn("audios", folder_data)

    def test_list_contains_audios(self):
        response = self.client.get("/api/audio/list/")
        all_audios = [a for folder in response.data for a in folder["audios"]]
        self.assertEqual(len(all_audios), 2)

    def test_empty_folders(self):
        Audio.objects.all().delete()
        response = self.client.get("/api/audio/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for folder in response.data:
            self.assertEqual(folder["audios"], [])


class AudioDetailViewTest(APITestCase):
    def setUp(self):
        self.folder = AudioFolder.objects.create(path=["root"])
        self.audio = Audio.objects.create(
            title="Detail Audio",
            url="https://example.com/detail.mp3",
            path=self.folder,
        )

    def test_detail_returns_200(self):
        response = self.client.get(f"/api/audio/detail/?id={self.audio.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_returns_correct_audio(self):
        response = self.client.get(f"/api/audio/detail/?id={self.audio.id}")
        self.assertEqual(response.data["id"], self.audio.id)
        self.assertEqual(response.data["title"], "Detail Audio")
        self.assertEqual(response.data["url"], "https://example.com/detail.mp3")

    def test_detail_not_found(self):
        response = self.client.get("/api/audio/detail/?id=9999")
        self.assertEqual(response.data["code"], 404)
        self.assertEqual(response.data["status"], "Failed")

    def test_detail_missing_id(self):
        response = self.client.get("/api/audio/detail/")
        self.assertIn("code", response.data)
        self.assertEqual(response.data["status"], "Failed")
