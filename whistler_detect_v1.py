import pywt
import numpy as np
import scipy
import librosa
import os
import matplotlib.pyplot as plt
import warnings
from pydub import AudioSegment
import shutil
from config import add_logger

script_name = os.path.splitext(os.path.basename(__file__))[0]
logger = add_logger(f'# logger_{script_name}', script_name)


warnings.filterwarnings("ignore")


def filter_audio(audio_data, sample_rate, low_freq, high_freq):
    nyquist = 0.5 * sample_rate
    low = low_freq / nyquist
    high = high_freq / nyquist
    b, a = scipy.signal.butter(8, [low, high], btype='band')
    filtered_audio = scipy.signal.lfilter(b, a, audio_data)
    logger.info(f"Filtered audio:{filtered_audio}")
    return filtered_audio


def extract_wavelet_features(audio_file):
    audio = AudioSegment.from_file(audio_file)
    # sample_rate = audio.frame_rate
    audio_data = audio.get_array_of_samples()
    print(len(audio_data))
    logger.info(audio_data)

    coeffs = pywt.wavedec(audio_data, 'db10', level=6)
    logger.info(f"Coeffs: {coeffs}")
    wavelet = pywt.Wavelet('db10')

    wavelet_data = wavelet.wavefun(level=6)
    time = np.arange(0, len(wavelet_data[1]))
    data = wavelet_data[1]

    plt.figure(figsize=(8, 4))
    plt.plot(time, data)
    plt.title('Wavelet Shape (db10)')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

    features = []
    for coef in coeffs:
        features.extend([np.mean(coef), np.std(coef)])
    print('wavelets features: ', features, '\n')
    return features


def extract_spectrogram_features(audio_file):
    audio_data, sample_rate = librosa.load(audio_file)

    spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)

    features = []

    mean_amplitude = np.mean(spectrogram)

    features.append(mean_amplitude)

    std_amplitude = np.std(spectrogram)
    features.append(std_amplitude)
    print('spec features: ', features)
    return features


def save_spectrogram_plot(spectrogram, title, output_filename):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), y_axis='mel', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"Spectrograms/{output_filename}")
    plt.close()


def main():
    threshold = 25000

    audio_folder = "output/processed_sounds1"
    # audio_folder = "Whist_sounds/"

    for i, filename in enumerate(os.listdir(audio_folder)):
        if filename.endswith(".wav"):
            print(filename, '\n')
            logger.info(filename, '\n')
            audio_file = os.path.join(audio_folder, filename)

            wavelet_features = extract_wavelet_features(audio_file)

            # spectrogram_features = extract_spectrogram_features(audio_file)

            combined_features = wavelet_features
            print(sum(combined_features))
            if sum(combined_features) > threshold:
                print(f"File '{filename}' is included whistlers.\n")

                audio_data, sample_rate = librosa.load(audio_file)

                logger.info(f"audio_data: {audio_data}")
                low_freq = 200
                high_freq = 7000
                filtered_audio = filter_audio(audio_data, sample_rate, low_freq, high_freq)
                spectrogram = librosa.feature.melspectrogram(y=filtered_audio, sr=sample_rate)
                print(f"spectrogram: {spectrogram}")
                logger.info(f"spectrogram: {spectrogram}")
                plt.figure(figsize=(10, 4))
                time = np.arange(0, len(audio_data)) / sample_rate
                plt.plot(time, audio_data)
                plt.title('Waveform')
                plt.xlabel('Time (s)')
                plt.ylabel('Amplitude')
                plt.tight_layout()
                plt.show()

                save_spectrogram_plot(spectrogram, f'Mel spectrogram of whistlers {i}', f'{filename}.png')
                target_path = os.path.join("whist_include/")
                shutil.copy(audio_file, target_path)
            else:
                audio_data, sample_rate = librosa.load(audio_file)
                spectrogram = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
                plt.figure(figsize=(10, 4))
                librosa.display.specshow(librosa.power_to_db(spectrogram, ref=np.max), y_axis='mel', x_axis='time')
                plt.colorbar(format='%+2.0f dB')
                plt.title('Mel spectrogram of non-whistlers')
                plt.tight_layout()
                plt.show()
                print(f"File '{filename}' isn't included whistlers.\n")


if __name__ == '__main__':
    main()
