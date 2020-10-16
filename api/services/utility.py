from api.services.firestore import retreive_from_file_store, publish_to_file_store
from flask import current_app as app
import librosa
import re
import wave

def emailValidator(email):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if(re.search(regex, email)):
        return True
    else:
        return False


def passwordValidator(password):
    if (len(password) < 8):
        return False
    elif not re.search(r"[a-z]", password):
        return False
    elif not re.search(r"[A-Z]", password):
        return False
    elif not re.search(r"[0-9]", password):
        return False
    elif not re.search(r"[_@$]", password):
        return False
    elif re.search(r"\s", password):
        return False
    else:
        return True


def convert_to_mono_signal(all_trackouts, sample_rate):
    """
    Convert all of the trackouts for a track into mono signals
    """
    try:
        app.logger.info(f"convert_to_mono_signal helper funciton {len(all_trackouts)}")
        mono_signal_trackouts = []
        for index, trackout in enumerate(all_trackouts):
            # Fetch wavfile from firebase
            path = trackout.path
            retreive_from_file_store(path, i)
            trackout_mono_signal, sr = librosa.load(f"{trackout.uuid}.wav", sr=sample_rate)
            mono_signal_trackouts.append(trackout_mono_signal)
        app.logger.info(f"Mono trackouts length {len(mono_signal_trackouts)}#")
        return mono_signal_trackouts
    except Exception as err:
        app.logger.error(f"Error occurred in convert_to_mono_signal fx: {err}")
        raise Exception(f"Error occurred in convert_to_mono_signal fx: {err}")


def convert_to_stereo_signal(all_trackouts):
    try:
        stereo_signal_trackouts = []
        i = str(1)
        seed_path = all_trackouts[0].path
        main_trackout_uuid = all_trackouts[0].uuid
        retreive_from_file_store(seed_path, main_trackout_uuid)
        with wave.open(f"wav_tmp/{main_trackout_uuid}.wav", "rb") as wave_file:
            sample_rate = wave_file.getframerate()
        trackout_stereo_signal, _ = librosa.load(f"wav_tmp/{main_trackout_uuid}.wav", sr=sample_rate, mono=False)
        stereo_signal_trackouts.append(trackout_stereo_signal)
        for index, trackout in enumerate(all_trackouts[1:], 1):   
            path = trackout.path
            trackout_uuid = trackout.uuid
            retreive_from_file_store(path, trackout_uuid)
            trackout_stereo_signal, _ = librosa.load(f"wav_tmp/{trackout_uuid}.wav", sr=sample_rate, mono=False)
            stereo_signal_trackouts.append(trackout_stereo_signal)
        app.logger.info(f"Stereo trackouts length: {len(stereo_signal_trackouts)}")
        return stereo_signal_trackouts, sample_rate
    except Exception as err:
        app.logger.error(f"Error occurred in convert_to_stereo_signal fx: {err}")
        raise Exception(f"Error occurred in convert_to_stereo_signal fx: {err}")           


def create_trackout_exclusive_list(all_trackouts, index):
    # Trackout to run processing on
    main_trackout = all_trackouts[index]
    # All other trackouts except main_trackout
    other_trackouts = \
        all_trackouts[:index] + all_trackouts[index+1:]
    return (main_trackout, other_trackouts)
