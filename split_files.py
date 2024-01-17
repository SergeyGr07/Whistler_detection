from pydub import AudioSegment
import os


def split_audio(input_path, output_dir):
    # Создаем директории, если они не существуют
    processed_dir = os.path.join(output_dir, "processed_sounds1")
    unprocessed_dir = os.path.join(output_dir, "unprocessed_sounds")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(unprocessed_dir, exist_ok=True)

    # Получаем список звуковых файлов в директории
    sound_files = [f for f in os.listdir(input_path) if f.endswith(".mp3") or f.endswith(".wav")]

    for file_name in sound_files:
        input_file_path = os.path.join(input_path, file_name)

        # Загружаем звуковой файл
        sound = AudioSegment.from_file(input_file_path)

        # Разбиваем на отрезки по 15 секунд
        segment_length = 15 * 1000  # в миллисекундах
        segments = [sound[i:i + segment_length] for i in range(0, len(sound), segment_length)]

        for i, segment in enumerate(segments):
            # Создаем директорию и сохраняем отрезок
            output_subdir = processed_dir if i < len(segments) - 1 else unprocessed_dir
            output_file_name = f"{i}_{file_name.replace('.', '_')}"
            output_file_path = os.path.join(output_subdir, output_file_name)
            segment.export(output_file_path, format="mp3")


if __name__ == "__main__":
    input_directory = "sounds"
    output_directory = "output"
    split_audio(input_directory, output_directory)
