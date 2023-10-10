from pathlib import Path
import glob
import typer
import numpy as np
from mutagen.mp3 import MP3
from pydub import AudioSegment
from scipy.fft import fft, fftfreq


def check_bitrate(file_path, min_bitrate=128):
    audio = MP3(file_path)
    bitrate_kbps = audio.info.bitrate // 1000
    return bitrate_kbps, bitrate_kbps < min_bitrate


def check_volume(file_path, min_rms=-20):
    audio = AudioSegment.from_mp3(file_path)
    rms_db = audio.dBFS
    return rms_db, rms_db < min_rms


def check_spectrum(file_path, min_high_freq=14000, threshold_ratio=0.02):
    audio = AudioSegment.from_mp3(file_path)
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

    # Perform FFT
    fft_values = np.abs(fft(samples))
    freqs = fftfreq(len(fft_values), 1.0 / audio.frame_rate)

    # Positive frequencies only
    positive_freqs = freqs[: len(freqs) // 2]
    positive_fft = fft_values[: len(fft_values) // 2]

    # High-frequency energy
    high_freq_energy = positive_fft[positive_freqs > min_high_freq].sum()
    total_energy = positive_fft.sum()

    ratio = high_freq_energy / total_energy if total_energy > 0 else 0
    return ratio, ratio < threshold_ratio


def detect_fake_high_bitrate(bitrate, high_freq_ratio, suspicious_cutoff=0.02):
    """
    Warn if bitrate is high but high-frequency content is too low.
    Common for re-encoded low-quality audio.
    """
    if bitrate >= 256 and high_freq_ratio < suspicious_cutoff:
        return True
    return False


def analyze_mp3(file_path):
    print(f"Analyzing: {file_path}")

    bitrate, low_bitrate = check_bitrate(file_path)
    print(f"Bitrate: {bitrate} kbps {'(LOW)' if low_bitrate else ''}")

    rms_db, low_volume = check_volume(file_path)
    print(f"Volume (RMS): {rms_db:.2f} dBFS {'(LOW)' if low_volume else ''}")

    high_freq_ratio, bad_spectrum = check_spectrum(file_path)
    print(
        f"High-frequency energy ratio: {high_freq_ratio:.4f} {'(LOW)' if bad_spectrum else ''}"
    )

    fake_high_bitrate = detect_fake_high_bitrate(bitrate, high_freq_ratio)
    if fake_high_bitrate:
        print(
            "⚠ WARNING: High bitrate but suspiciously low high-frequency content — likely upsampled."
        )

    if (
        not low_bitrate
        and not low_volume
        and not bad_spectrum
        and not fake_high_bitrate
    ):
        print("\nOverall: ✅ Audio quality seems fine")
        return True

    print("\nOverall: ⚠ Potential quality issues detected")
    return False


def main(files: list[Path]):
    actual_files = []
    for path in files:
        if path.is_dir():
            for f in glob.glob(str(path / "*.mp3")):
                actual_files.append(Path(f))
        elif path.name.endswith(".mp3"):
            actual_files.append(path)
    bad = []
    for file in actual_files:
        if not analyze_mp3(str(file)):
            bad.append(file)
    for b in bad:
        print(b)


if __name__ == "__main__":
    typer.run(main)
