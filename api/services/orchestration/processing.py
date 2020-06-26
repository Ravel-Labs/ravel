# Processing takes in a request and applies to correct audio processing to it.
# This is a wrapper around the Ravel API Library to expose it to a web server
# in a more usable and meaningful way.
# import librosa
import numpy as np
from ravel.api import db
from io import BytesIO
from ravel.api.services.effects import reverb, equalizer, compressor, deesser
from ravel.api import ADMINS_FROM_EMAIL_ADDRESS, mail, Q, Job
from ravel.ravellib.lib.effects import SignalAggregator
from ravel.api.services.firestore import retreive_from_file_store, publish_to_file_store
import scipy.io as sio
from scipy.io.wavfile import write, read
import pickle
import sys
from ravel.api.models.track_models import Track, TrackOut, Equalizer, Deesser
from os import remove
import librosa
class Processor():
    def __init__(self, num_signals):
        self.num_signals = num_signals
        self.sample_rate = 44100
        self.signal_aggregator = SignalAggregator(
            self.sample_rate, self.num_signals)

    def equalize(self, main_trackout, other_trackouts):
        eq = equalizer.Equalize(main_trackout, other_trackouts)
        processed = eq.equalize()
        print(f"Successful equalization: \n\t {type(processed)}")
        return processed

    def compress(self, all_trackouts):
        co = compressor.Compress(all_trackouts, self.signal_aggregator)
        processed = co.compress()
        print(f"Successful compression of type {type(processed)}: \n\t{processed}")
        return processed

    def deesser(self, main_trackout):
        de = deesser.Deesser(main_trackout)
        processed = de.deess()
        print(f"Successful deesser of type {type(processed)}: \n\t{processed}")
        return processed

    def reverb(self, main_trackout):
        re = reverb.Reverb(main_trackout)
        processed = re.reverb()
        print(f"Successful reverb of type {type(processed)}: \n\t{processed}")
        return processed


class Orchestrator():
    """
    The Handler is responsible for queueing and building the effects for each
    track.
    """

    def __init__(self, all_trackouts):
        """
        creates a new builder
        """
        num_signals = len(all_trackouts)
        self.processor = Processor(num_signals)
        self.all_trackouts = all_trackouts
        self.other_trackouts = list()
        self.mono_signal_trackouts = list()
        # TODO get this from DB model
        self.eq_params = {"trackout_id": 1, "freq": "1200",
                          "filter_type": 0, "gain": 1}
        self.co_params = {"trackout_id": 1, "ratio": 1.1, "threshold": 1.0,
                          "knee_width": 1, "attack": 1.1, "release": 1.2}
        self.de_params = {"sharpness_avg": 1}
    def orchestrate(self):
        try:
            self.convert_to_mono_signal()
            for i, raw_trackout in enumerate(self.all_trackouts):
                self.create_trackout_exclusive_list(i)
                # setup queue parameters and process
                base_processing_args = [raw_trackout]
                """Initiate Equalize"""
                eq_args = base_processing_args + ["equalize"]
                processing_job = Job(self.process_and_save, eq_args)
                print(f'processing job:  {processing_job}')
                Q.put(processing_job)  # currently cannot return
                
                """Initiate Compress"""
                # co_args = base_processing_args + ["compress"]
                # processing_job = Job(self.process_and_save, co_arguments)
                # print(f'processing job:  {processing_job}')
                # Q.put(processing_job) # currently cannot return
                
                """ Initiate Deessor """
                # de_args = base_processing_args + ["deesser"]
                # processing_job = Job(self.process_and_save, de_args)
                # print(f'processing job:  {processing_job}')
                # Q.put(processing_job) # currently cannot return
                
                """Initiate Reverb"""
                # rev_args = base_processing_args + ["reverb"]
                # processing_job = Job(self.process_and_save, rev_args)
                # print(f'processing job:  {processing_job}')
                # Q.put(processing_job) # currently cannot return

            # remove all trackouts stored on disk
            # TODO turn into function
            for i, _ in enumerate(self.all_trackouts):
                remove(f"trackout_{i}.wav")
            return True
        except Exception as err:
            raise Exception(f"Error occurred in orchestration:\n {err}")

    def Builder(self):
        """
        The Handler works with the builder instance to create the processing
        stack for each request.
        """
        return self._builder


    def convert_to_mono_signal(self):
        """
        Convert all of the trackouts for a track into mono signals
        """
        for index, trackout in enumerate(self.all_trackouts):
            # Fetch wavfile from firebase
            path = trackout.path
            retreive_from_file_store(path, str(index))
            trackout_mono_signal, sr = librosa.load(f"trackout_{index}.wav", sr=44100)
            self.mono_signal_trackouts.append(trackout_mono_signal)
    
    def create_trackout_exclusive_list(self, index):
        # Trackout to run processing on
        self.main_trackout = self.mono_signal_trackouts[index]
        # All other trackouts except main_trackout
        self.other_trackouts = \
            self.mono_signal_trackouts[:index-1] + self.mono_signal_trackouts[index:]
    
    def process_and_save(self, raw_trackout, effect):
        # def reverb_and_save(main_trackout, other_trackouts, all_trackouts, de_params, raw_trackout):
        print("Process and save effect")
        sample_rate = 44100
        trackout_id = raw_trackout.id
        trackout_name = raw_trackout.name
        if effect == "reverb":
            effect_prefix = "re"
            storage_name = f"{effect_prefix}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"

            processed_result = self.processor.reverb(self.main_trackout)
            # TODO Create db model
            # db_model = Reverb(
            #     sharpness_avg=de_params["sharpness_avg"],
            #     path=firestore_path,
            #     de=raw_trackout  # Relationship with raw_trackout
            # )
        elif effect == "deesser":
            effect_prefix = "de"
            storage_name = f"{effect_prefix}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"
            processed_result = self.processor.deesser(self.main_trackout)
        elif effect == "compress":
            effect_prefix = "co"
            storage_name = f"{effect_prefix}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"
            processed_result = self.processor.compress(self.all_trackouts)
            db_model = Compressor(
                freq=self.co_params["freq"],
                filter_type=self.co_params["filter_type"],
                gain=self.co_params["gain"],
                path=firestore_path,
                co=raw_trackout  # Relationship with raw_trackout
            )
        elif effect == "equalize":
            effect_prefix = "eq"
            storage_name = f"{effect_prefix}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"
            processed_result = self.processor.equalize(self.main_trackout, self.other_trackouts)
            db_model = Equalizer(
                freq=self.eq_params["freq"],
                filter_type=self.eq_params["filter_type"],
                gain=self.eq_params["gain"],
                path=firestore_path,
                eq=raw_trackout  # Relationship with raw_trackout
            )
        else:
            raise Exception("This effect function does not exist")
        write(storage_name, sample_rate, processed_result)
        print(f"Completed processing {effect}: {bool(processed_result.any())}")
        # publish_to_file_store and remove
        publish_to_file_store(firestore_path, storage_name)
        remove(storage_name)
        # save effect results to database
        db.session.add(db_model)
        db.session.commit()
