from api.services.firestore import retreive_from_file_store, publish_to_file_store
from api.services.effects import reverb, equalizer, compressor, deesser
from api.models.track_models import Equalizer, Deesser, Compressor, Reverb, TrackOut
from api.services.orchestration.processing import Processor
from api.services.email.email import email_proxy
from api.services.utility import create_trackout_exclusive_list, convert_to_stereo_signal
from api import db, Q, Job
from scipy.io.wavfile import write
from os import remove
from ravellib.lib.effects import Mixer
from flask import current_app as app

class Orchestrator():
    """
    The Handler is responsible for queueing and building the effects for each
    track.
    """

    def __init__(self, current_user, all_trackouts, track, toggle_effects_params):
        """
        creates a new builder
        """
        self.track = track
        self.current_user = current_user
        self.files_to_remove = list()
        self.processed_signals = list()
        self.toggle_effects_params = toggle_effects_params
        num_signals = len(all_trackouts)
        self.processor = Processor(num_signals)
        self.all_trackouts = all_trackouts
        self.other_trackouts = list()
        self.sample_rate = None
        self.compressed_result = list()
        self.stereo_signal_trackouts = list()
        # TODO get this from DB model
        self.eq_params = {"freq": "1200", "filter_type": 0, "gain": 1}
        self.co_params = {"ratio": 1.1, "threshold": 1.0,
                          "knee_width": 1, "attack": 1.1, "release": 1.2}
        self.de_params = {"sharpness_avg": 1}
        app.logger.info(f'creating new track builder: {self}')

    def compress_trackouts(self):
        """ Initiate Compress """
        try:
            co_args = [[trackout.uuid for trackout in self.all_trackouts]]
            processing_job = Job(self.compress_and_save, co_args)
            app.logger.info(f'processing job: {processing_job}')
            Q.put(processing_job) # currently cannot return
        except Exception as err:
            app.logger.error(f"error in process_and_save for trackID {self.track.id}:", err)
            raise Exception(f"Error occurred in process_and_save:\n {err}")


    def engage_trackout_effects(self):
        try:
            for i, raw_trackout in enumerate(self.all_trackouts):
                main_trackout, other_trackouts = create_trackout_exclusive_list(self.stereo_signal_trackouts, i)
                # setup queue parameters and process
                base_processing_args = [raw_trackout.id]
                
                """Initiate Equalize"""
                if self.toggle_effects_params.get('eq'):
                    eq_args = base_processing_args + ["equalize", main_trackout, other_trackouts]
                    processing_job = Job(self.process_and_save, eq_args)
                    app.logger.info(f'processing job: {processing_job}')
                    Q.put(processing_job)  # currently cannot return
                
                """ Initiate Deessor """
                # Blocked by drop down trackout type enforecement 
                #raw_trackout.type == "vocals" and 
                if self.toggle_effects_params.get('de'):
                    de_args = base_processing_args + ["deesser", main_trackout, other_trackouts]
                    processing_job = Job(self.process_and_save, de_args)
                    app.logger.info(f'processing job: {processing_job}')
                    Q.put(processing_job)  # currently cannot return
                
                """ Initiate Reverb """
                #raw_trackout.type == "vocals" and 
                if self.toggle_effects_params.get('re'):
                    rev_args = base_processing_args + ["reverb", main_trackout, other_trackouts]
                    processing_job = Job(self.process_and_save, rev_args)
                    app.logger.info(f'processing job: {processing_job}')
                    Q.put(processing_job)  # currently cannot return
        except Exception as err:
            app.logger.error(f"Error occurred in track fx: {err}")
            raise Exception(f"Error occurred in track fx: {err}")

    def orchestrate(self):
        try:
            app.logger.info(f"Orchestrator.orchestrate()")
            self.stereo_signal_trackouts, self.sample_rate = convert_to_stereo_signal(self.all_trackouts)
            if self.sample_rate != 44100:
                self.processor.sample_rate = self.sample_rate
            if self.toggle_effects_params.get('co'):
                self.compress_trackouts()
            self.engage_trackout_effects()
            Q.join()
            storage_name = f"{self.track.uuid}_results.wav"

            # every track has for settings for all of the equations
            mixer = Mixer(self.processed_signals, storage_name, self.sample_rate)
            raise Exception("HAHAHA")
            app.logger.info(f'processed signals')
            app.logger.info(self.processed_signals)

            mixed_result = mixer.mix()
            app.logger.info(f'mixed_results')
            mixer.output_wav(mixed_result)
            
            firestore_path = f"track/{self.track.uuid}/song/{self.track.uuid}.wav"
            download_url = publish_to_file_store(firestore_path, storage_name)
            with open(storage_name, 'rb') as fin:
                data = fin.read()
            if not data:
                app.logger.error(f'Error reading result file')
            # email_proxy(
            #     title="Audio Processing Complete",
            #     template_type="status",
            #     user_to_email_address=self.current_user.email,
            #     user_name=self.current_user.name,
            #     button_title="Processed Results",
            #     button_link=download_url,
            #     sound_file=data)
            # TODO this needs to happen on exception remove all trackouts stored on disk
            remove(storage_name)
            for file in self.files_to_remove:
                remove(file)
            for i, _ in enumerate(self.all_trackouts):
                remove(f"trackout_{i+1}.wav")
            return True
        except Exception as err:
            remove(storage_name)
            for file in self.files_to_remove:
                remove(file)
            for i, _ in enumerate(self.all_trackouts):
                remove(f"trackout_{i+1}.wav")
            app.logger.error(f"error in orchestration for trackID {self.track.id}:", err)
            raise Exception(f"Error occurred in orchestration:\n {err}")

    def compress_and_save(self, all_trackouts_uuids):
        """
            Seperated method for effects that only needs to run once for all trackouts
        """
        try:

            effect_prefix = "co"
            self.compressed_result = self.processor.compress(self.stereo_signal_trackouts)
            correlation = zip(all_trackouts_uuids, self.compressed_result)
            for index, (raw_trackout_uuid, processed_result) in enumerate(correlation):
                raw_trackout = TrackOut.query.filter_by(uuid=raw_trackout_uuid).first()

                self.processed_signals.append(processed_result)
                # TODO add a dict to keep track of each trackouts processed results
                track_uuid = raw_trackout.track_id
                trackout_uuid = raw_trackout.uuid
                storage_name = f"{trackout_uuid}.wav"
                firestore_path = f"track/{track_uuid}/{effect_prefix}/{storage_name}"
                write(storage_name, self.sample_rate, processed_result)
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
                local_object = db.session.merge(db_model)
                db.session.add(local_object)
                db.session.commit()
        except Exception as err:
            app.logger.error(f"error in compress_and_save for trackID {self.track.id}:", err)
            raise Exception(f"Error occurred in compress_and_save:\n {err}") 

    def process_and_save(self, raw_trackout_id, effect, main_trackout, other_trackouts):
        # def reverb_and_save(main_trackout, other_trackouts, all_trackouts, de_params, raw_trackout):
        try:
            raw_trackout = TrackOut.query.filter_by(uuid=raw_trackout_uuid).first()
            print(f"raw_trackout {raw_trackout}")
            app.logger.info(f"process_and_save: {effect}")
            track_uuid = raw_trackout.trackouts.uuid
            trackout_uuid = raw_trackout.uuid
            storage_name = f"{trackout_uuid}.wav"

            if effect == "reverb":
                effect_prefix = "re"
                firestore_path = f"track/{track_uuid}/{effect_prefix}/{storage_name}"
                processed_result = self.processor.reverb(main_trackout)
                db_model = Reverb(
                    path=firestore_path,
                    re=raw_trackout  # Relationship with raw_trackout
                )
            elif effect == "deesser":
                effect_prefix = "de"
                firestore_path = f"track/{track_uuid}/{effect_prefix}/{storage_name}"
                processed_result = self.processor.deesser(main_trackout)
                db_model = Deesser(
                    sharpness_avg=self.de_params["sharpness_avg"],
                    path=firestore_path,
                    de=raw_trackout  # Relationship with raw_trackout
                )
            #TODO test subject
            elif effect == "equalize":
                effect_prefix = "eq"
                firestore_path = f"track/{track_uuid}/{effect_prefix}/{storage_name}"
                processed_result = self.processor.equalize(main_trackout, other_trackouts)
                db_model = Equalizer(
                    freq=self.eq_params["freq"],
                    filter_type=self.eq_params["filter_type"],
                    gain=self.eq_params["gain"],
                    path=firestore_path,
                    eq=raw_trackout  # Relationship with raw_trackout
                )
            else:
                app.logger.info(f"This effect function does not exist")

            write(storage_name, self.sample_rate, processed_result)
            print(f"Completed processing {effect}: {bool(processed_result.any())}")
            app.logger.info(f'completed processing for {effect}')
            app.logger.info(f'processed result:  {bool(processed_result.any())}')
            # publish_to_file_store and remove
            publish_to_file_store(firestore_path, storage_name)
            if bool(processed_result.any()):
                self.processed_signals.append(processed_result)
            self.files_to_remove.append(storage_name)
            # save effect results to database
            local_object = db.session.merge(db_model)
            db.session.add(local_object)
            db.session.commit()
        except Exception as err:
            app.logger.error(f"error in process_and_save for trackID {self.track.id}:", err)
            raise Exception(f"Error occurred in process_and_save:\n {err}")