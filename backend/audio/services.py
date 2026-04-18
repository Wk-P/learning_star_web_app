from .models import Audio, AudioFolder
from .serializers import AudioSerializer

    

def get_audio_list() -> list[dict]:
    folder_objects = AudioFolder.objects.prefetch_related('audios_list').all()

    data = []

    for folder_object in folder_objects:
        path_id = folder_object.id
        path = folder_object.path
        audios = AudioSerializer(folder_object.audios_list.all(), many=True).data


        data.append({
            "id": path_id,
            "path": path,
            "audios": audios
        })
    

    return data


def get_audio(pk: int):
    try:
        audio = Audio.objects.get(id=pk)
    except Audio.DoesNotExist:
        return { "message": "Not found required audio.", "status": "Failed", "code": 404 }

    data = AudioSerializer(audio).data

    return data