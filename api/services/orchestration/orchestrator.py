from ravel.api.services.firestore import retreive_from_file_store, publish_to_file_store
from ravel.api.services.effects import reverb, equalizer, compressor, deesser
from ravel.api.models.track_models import Equalizer, Deesser, Compressor, Reverb
from ravel.api.services.orchestration.processing import Processor
from ravel.api.services.utility import create_trackout_exclusive_list, convert_to_mono_signal
from ravel.api import db, Q, Job
from scipy.io.wavfile import write
from os import remove


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
        self.sample_rate = 44100
        self.compressed_result = list()
        self.mono_signal_trackouts = list()
        # TODO get this from DB model
        self.eq_params = {"trackout_id": 1, "freq": "1200",
                          "filter_type": 0, "gain": 1}
        self.co_params = {"ratio": 1.1, "threshold": 1.0,
                          "knee_width": 1, "attack": 1.1, "release": 1.2}
        self.de_params = {"sharpness_avg": 1}


    def compress_trackouts(self):
        """ Initiate Compress """
        co_args = [self.all_trackouts]
        processing_job = Job(self.compress_and_save, co_args)
        print(f'processing job:  {processing_job}')
        Q.put(processing_job) # currently cannot return

    def engage_trackout_effects(self):
        for i, raw_trackout in enumerate(self.all_trackouts):
            self.main_trackout, self.other_trackouts = create_trackout_exclusive_list(self.mono_signal_trackouts, i)
            # setup queue parameters and process
            base_processing_args = [raw_trackout]

            """Initiate Equalize"""
            eq_args = base_processing_args + ["equalize"]
            processing_job = Job(self.process_and_save, eq_args)
            print(f'processing job:  {processing_job}')
            Q.put(processing_job)  # currently cannot return
            
            """ Initiate Deessor """
            de_args = base_processing_args + ["deesser"]
            processing_job = Job(self.process_and_save, de_args)
            print(f'processing job:  {processing_job}')
            Q.put(processing_job) # currently cannot return
            
            """ Initiate Reverb """
            rev_args = base_processing_args + ["reverb"]
            processing_job = Job(self.process_and_save, rev_args)
            print(f'processing job:  {processing_job}')
            Q.put(processing_job) # currently cannot return

    def orchestrate(self):
        try:
            self.mono_signal_trackouts = convert_to_mono_signal(self.all_trackouts, self.sample_rate)
            self.compress_trackouts()
            self.engage_trackout_effects()
            # remove all trackouts stored on disk
            # TODO turn into function
            for i, _ in enumerate(self.all_trackouts):
                remove(f"trackout_{i}.wav")
            return True
        except Exception as err:
            raise Exception(f"Error occurred in orchestration:\n {err}")

    def compress_and_save(self, all_trackouts):
        """
            Seperated method for effects that only needs to run once for all trackouts
        """
        effect_prefix = "co"
        self.compressed_result = self.processor.compress(self.mono_signal_trackouts)
        correlation = zip(all_trackouts, self.compressed_result)
        for index, (raw_trackout, processed_result) in enumerate(correlation):
            trackout_id = raw_trackout.id
            trackout_name = raw_trackout.name
            storage_name = f"{effect_prefix}_{index+1}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"
            write(storage_name, self.sample_rate, processed_result)
            print(f"Completed processing Compression: {bool(processed_result.any())}")
            # publish_to_file_store and remove
            publish_to_file_store(firestore_path, storage_name)
            remove(storage_name)
            db_model = Compressor(
                ratio=self.co_params["ratio"],
                threshold=self.co_params["threshold"],
                knee_width=self.co_params["knee_width"],
                attack=self.co_params["attack"],
                release=self.co_params["release"],
                path=firestore_path,
                co=raw_trackout  # Relationship with raw_trackout
            )
            db.session.add(db_model)
            db.session.commit()


    def process_and_save(self, raw_trackout, effect):
        # def reverb_and_save(main_trackout, other_trackouts, all_trackouts, de_params, raw_trackout):
        print("Process and save effect")
        trackout_id = raw_trackout.id
        trackout_name = raw_trackout.name
        if effect == "reverb":
            effect_prefix = "re"
            storage_name = f"{effect_prefix}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"

            processed_result = self.processor.reverb(self.main_trackout)
            # TODO Create db model
            db_model = Reverb(
                path=firestore_path,
                re=raw_trackout  # Relationship with raw_trackout
            )
        elif effect == "deesser":
            effect_prefix = "de"
            storage_name = f"{effect_prefix}_results.wav"
            firestore_path = f"{effect_prefix}/{trackout_id}/{storage_name}"
            processed_result = self.processor.deesser(self.main_trackout)
            db_model = Deesser(
                sharpness_avg=self.de_params["sharpness_avg"],
                path=firestore_path,
                de=raw_trackout  # Relationship with raw_trackout
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
        if effect != "compress":      
            write(storage_name, self.sample_rate, processed_result)
            print(f"Completed processing {effect}: {bool(processed_result.any())}")
            # publish_to_file_store and remove
            publish_to_file_store(firestore_path, storage_name)
            remove(storage_name)
        # save effect results to database
        if db_model:
            db.session.add(db_model)
            db.session.commit()
