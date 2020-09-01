import hither as hi
import numpy as np
import kachery as ka
import spikeextractors as se
import spiketoolkit as st

@hi.function('createjob_fetch_average_waveform_plot_data', '')
def createjob_fetch_average_waveform_plot_data(labbox, recording_object, sorting_object, unit_id):
    jh = labbox.get_job_handler('partition2')
    jc = labbox.get_default_job_cache()
    with hi.Config(
        job_cache=jc,
        job_handler=jh,
        container=jh.is_remote
    ):
        snippets_h5 = prepare_snippets_h5.run(recording_object=recording_object, sorting_object=sorting_object)
        return fetch_average_waveform_plot_data.run(
            snippets_h5=snippets_h5,
            unit_id=unit_id
        )

@hi.function('prepare_snippets_h5', '0.1.3')
@hi.container('docker://magland/labbox-ephys-processing:0.2.18')
@hi.local_modules(['../../../python/labbox_ephys'])
def prepare_snippets_h5(recording_object, sorting_object):
    import h5py
    import labbox_ephys as le
    recording = le.LabboxEphysRecordingExtractor(recording_object)
    sorting = le.LabboxEphysSortingExtractor(sorting_object)
    unit_ids = sorting.get_unit_ids()
    samplerate = sorting.get_sampling_frequency()
    unit_waveforms = st.postprocessing.get_unit_waveforms(
        recording=recording,
        sorting=sorting,
        unit_ids=unit_ids,
        ms_before=1,
        ms_after=1.5,
        max_spikes_per_unit=500
    )
    with hi.TemporaryDirectory() as tmpdir:
        save_path = tmpdir + '/snippets.h5'
        with h5py.File(save_path, 'w') as f:
            f.create_dataset('unit_ids', data=np.array(unit_ids).astype(np.int32))
            f.create_dataset('sampling_frequency', data=np.array([samplerate]).astype(np.float64))
            f.create_dataset('channel_ids', data=np.array(recording.get_channel_ids()))
            for ii, unit_id in enumerate(unit_ids):
                x = sorting.get_unit_spike_train(unit_id=unit_id)
                f.create_dataset(f'unit_spike_trains/{unit_id}', data=np.array(x).astype(np.float64))
                f.create_dataset(f'unit_waveforms/{unit_id}/waveforms', data=unit_waveforms[ii].astype(np.float32))
                f.create_dataset(f'unit_waveforms/{unit_id}/channel_ids', data=recording.get_channel_ids())
        return ka.store_file(save_path)
                

@hi.function('fetch_average_waveform_plot_data', '0.1.14')
@hi.container('docker://magland/labbox-ephys-processing:0.2.18')
@hi.local_modules(['../../../python/labbox_ephys'])
def fetch_average_waveform_plot_data(snippets_h5, unit_id):
    import h5py
    h5_path = ka.load_file(snippets_h5)
    with h5py.File(h5_path, 'r') as f:
        unit_ids = np.array(f.get('unit_ids'))
        sampling_frequency = np.array(f.get('sampling_frequency'))[0]
        unit_spike_train = np.array(f.get(f'unit_spike_trains/{unit_id}'))
        unit_waveforms = np.array(f.get(f'unit_waveforms/{unit_id}/waveforms'))
        unit_waveforms_channel_ids = np.array(f.get(f'unit_waveforms/{unit_id}/channel_ids'))
    
    average_waveform = np.median(unit_waveforms, axis=0)
    channel_maximums = np.max(np.abs(average_waveform), axis=1)
    maxchan_index = np.argmax(channel_maximums)
    maxchan_id = unit_waveforms_channel_ids[maxchan_index]

    return dict(
        channel_id=maxchan_id,
        average_waveform=average_waveform[maxchan_id, :].tolist()
    )

@hi.function('old_fetch_average_waveform_plot_data', '0.1.13')
@hi.container('docker://magland/labbox-ephys-processing:0.2.18')
@hi.local_modules(['../../../python/labbox_ephys'])
def old_fetch_average_waveform_plot_data(recording_object, sorting_object, unit_id):
    import labbox_ephys as le
    R = le.LabboxEphysRecordingExtractor(recording_object)
    S = le.LabboxEphysSortingExtractor(sorting_object)

    start_frame = 0
    end_frame = R.get_sampling_frequency() * 30
    R0 = se.SubRecordingExtractor(parent_recording=R, start_frame=start_frame, end_frame=end_frame)
    S0 = se.SubSortingExtractor(parent_sorting=S, start_frame=start_frame, end_frame=end_frame)

    times0 = S0.get_unit_spike_train(unit_id=unit_id)
    if len(times0) == 0:
        # no waveforms found
        return dict(
            channel_id=None,
            average_waveform = None
        )
    try:
        average_waveform = st.postprocessing.get_unit_templates(
            recording=R0,
            sorting=S0,
            unit_ids=[unit_id]
        )[0]
    except:
        raise Exception(f'Error getting unit templates for unit {unit_id}')

    channel_maximums = np.max(np.abs(average_waveform), axis=1)
    maxchan_index = np.argmax(channel_maximums)
    maxchan_id = R0.get_channel_ids()[maxchan_index]

    return dict(
        channel_id=maxchan_id,
        average_waveform=average_waveform[maxchan_id, :].tolist()
    )