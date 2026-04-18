from rest_framework.test import APITestCase
from rest_framework import status
from .models import Video, VideoFolder


class VideoFolderModelTest(APITestCase):
    def setUp(self):
        self.folder = VideoFolder.objects.create(path=["root", "movies"])

    def test_folder_creation(self):
        self.assertEqual(VideoFolder.objects.count(), 1)
        self.assertEqual(self.folder.path, ["root", "movies"])

    def test_folder_default_path(self):
        folder = VideoFolder.objects.create()
        self.assertEqual(folder.path, [])


class VideoModelTest(APITestCase):
    def setUp(self):
        self.folder = VideoFolder.objects.create(path=["root"])
        self.video = Video.objects.create(
            title="Test Video",
            url="https://example.com/video.mp4",
            path=self.folder,
        )

    def test_video_creation(self):
        self.assertEqual(Video.objects.count(), 1)
        self.assertEqual(self.video.title, "Test Video")
        self.assertEqual(self.video.url, "https://example.com/video.mp4")

    def test_video_belongs_to_folder(self):
        self.assertEqual(self.video.path, self.folder)
        self.assertIn(self.video, self.folder.videos_list.all())

    def test_video_folder_deleted_sets_null(self):
        self.folder.delete()
        self.video.refresh_from_db()
        self.assertIsNone(self.video.path)


class VideoListViewTest(APITestCase):
    def setUp(self):
        self.folder1 = VideoFolder.objects.create(path=["root", "action"])
        self.folder2 = VideoFolder.objects.create(path=["root", "comedy"])
        Video.objects.create(title="Action Film", url="https://example.com/action.mp4", path=self.folder1)
        Video.objects.create(title="Comedy Film", url="https://example.com/comedy.mp4", path=self.folder2)

    def test_list_returns_200(self):
        response = self.client.get("/api/video/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_all_folders(self):
        response = self.client.get("/api/video/list/")
        self.assertEqual(len(response.data), 2)

    def test_list_folder_structure(self):
        response = self.client.get("/api/video/list/")
        folder_data = response.data[0]
        self.assertIn("id", folder_data)
        self.assertIn("path", folder_data)
        self.assertIn("videos", folder_data)

    def test_list_contains_videos(self):
        response = self.client.get("/api/video/list/")
        all_videos = [v for folder in response.data for v in folder["videos"]]
        self.assertEqual(len(all_videos), 2)

    def test_empty_folders(self):
        Video.objects.all().delete()
        response = self.client.get("/api/video/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for folder in response.data:
            self.assertEqual(folder["videos"], [])


class VideoDetailViewTest(APITestCase):
    def setUp(self):
        self.folder = VideoFolder.objects.create(path=["root"])
        self.video = Video.objects.create(
            title="Detail Video",
            url="https://example.com/detail.mp4",
            path=self.folder,
        )

    def test_detail_returns_200(self):
        response = self.client.get(f"/api/video/detail/?id={self.video.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_returns_correct_video(self):
        response = self.client.get(f"/api/video/detail/?id={self.video.id}")
        self.assertEqual(response.data["id"], self.video.id)
        self.assertEqual(response.data["title"], "Detail Video")
        self.assertEqual(response.data["url"], "https://example.com/detail.mp4")

    def test_detail_not_found(self):
        response = self.client.get("/api/video/detail/?id=9999")
        self.assertEqual(response.data["code"], 404)
        self.assertEqual(response.data["status"], "Failed")

    def test_detail_missing_id(self):
        response = self.client.get("/api/video/detail/")
        self.assertIn("code", response.data)
        self.assertEqual(response.data["status"], "Failed")
