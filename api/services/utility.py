from ravel.api.services.firestore import retreive_from_file_store, publish_to_file_store
import librosa
import re

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
    mono_signal_trackouts = []
    for index, trackout in enumerate(all_trackouts):
        # Fetch wavfile from firebase
        path = trackout.path
        retreive_from_file_store(path, str(index))
        trackout_mono_signal, sr = librosa.load(f"trackout_{index}.wav", sr=sample_rate)
        mono_signal_trackouts.append(trackout_mono_signal)
    return mono_signal_trackouts


def create_trackout_exclusive_list(all_trackouts, index):
    # Trackout to run processing on
    main_trackout = all_trackouts[index]
    # All other trackouts except main_trackout
    other_trackouts = \
        all_trackouts[:index-1] + all_trackouts[index:]
    return (main_trackout, other_trackouts)
