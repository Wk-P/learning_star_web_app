from .models import Video, VideoFolder
from .serializers import VideoSerializer

    

def get_video_list() -> list[dict]:
    folder_objects = VideoFolder.objects.prefetch_related('videos_list').all()

    data = []

    for folder_object in folder_objects:
        path_id = folder_object.id
        path = folder_object.path
        videos = VideoSerializer(folder_object.videos_list.all(), many=True).data


        data.append({
            "id": path_id,
            "path": path,
            "videos": videos
        })
    

    return data


def get_video(pk: int):
    try:
        video = Video.objects.get(id=pk)
    except Video.DoesNotExist:
        return None

    data = VideoSerializer(video).data

    return data