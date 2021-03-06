import os
import hither as hi
import kachery as ka
import labbox_ephys as le
import numpy as np


@le.register_sorting_view(name='SnippetsView')
def SnippetsView(*, sorting: le.LabboxEphysSortingExtractor, recording: le.LabboxEphysRecordingExtractor):
    import labbox_ephys_widgets_jp as lew
    return lew.create_sorting_view('SnippetsView', sorting=sorting, recording=recording)

@hi.function('createjob_get_sorting_unit_snippets', '0.1.0')
def createjob_get_sorting_unit_snippets(labbox, recording_object, sorting_object, unit_id, time_range, max_num_snippets):
    from labbox_ephys import prepare_snippets_h5
    jh = labbox.get_job_handler('partition1')
    jc = labbox.get_job_cache()
    with hi.Config(
        job_cache=jc,
        job_handler=jh,
        container=jh.is_remote
    ):
        snippets_h5 = prepare_snippets_h5.run(recording_object=recording_object, sorting_object=sorting_object)
        return get_sorting_unit_snippets.run(
            snippets_h5=snippets_h5,
            unit_id=unit_id,
            time_range=time_range,
            max_num_snippets=max_num_snippets
        )

@hi.function('get_sorting_unit_snippets', '0.1.7')
@hi.container('docker://magland/labbox-ephys-processing:0.3.19')
@hi.local_modules([os.getenv('LABBOX_EPHYS_PYTHON_MODULE_DIR')])
@le.serialize
def get_sorting_unit_snippets(snippets_h5, unit_id, time_range, max_num_snippets):
    import h5py
    h5_path = ka.load_file(snippets_h5)
    with h5py.File(h5_path, 'r') as f:
        unit_ids = np.array(f.get('unit_ids'))
        channel_ids = np.array(f.get('channel_ids'))
        channel_locations = np.array(f.get(f'channel_locations'))
        sampling_frequency = np.array(f.get('sampling_frequency'))[0].item()
        if np.isnan(sampling_frequency):
            print('WARNING: sampling frequency is nan. Using 30000 for now. Please correct the snippets file.')
            sampling_frequency = 30000
        unit_spike_train = np.array(f.get(f'unit_spike_trains/{unit_id}'))
        unit_waveforms = np.array(f.get(f'unit_waveforms/{unit_id}/waveforms'))
        unit_waveforms_channel_ids = np.array(f.get(f'unit_waveforms/{unit_id}/channel_ids'))
        print(unit_waveforms_channel_ids)
    
    snippets = [
        {
            'index': j,
            'unitId': unit_id,
            'waveform': unit_waveforms[j, :, :].astype(np.float32),
            'timepoint': float(unit_spike_train[j])
        }
        for j in range(unit_waveforms.shape[0])
    ]
    snippets = [s for s in snippets if time_range['min'] <= s['timepoint'] and s['timepoint'] < time_range['max']]
    channel_locations0 = []
    for ch_id in unit_waveforms_channel_ids:
        ind = np.where(channel_ids == ch_id)[0]
        channel_locations0.append(channel_locations[ind, :].ravel().tolist())

    return dict(
        channel_ids=unit_waveforms_channel_ids.astype(np.int32),
        channel_locations=channel_locations0,
        sampling_frequency=sampling_frequency,
        snippets=snippets[:max_num_snippets]
    )

@hi.function('createjob_get_sorting_unit_info', '0.1.0')
def createjob_get_sorting_unit_info(labbox, recording_object, sorting_object, unit_id):
    from labbox_ephys import prepare_snippets_h5
    jh = labbox.get_job_handler('partition1')
    jc = labbox.get_job_cache()
    with hi.Config(
        job_cache=jc,
        job_handler=jh,
        container=jh.is_remote
    ):
        snippets_h5 = prepare_snippets_h5.run(recording_object=recording_object, sorting_object=sorting_object)
        return get_sorting_unit_info.run(
            snippets_h5=snippets_h5,
            unit_id=unit_id
        )

@hi.function('get_sorting_unit_info', '0.1.0')
@hi.container('docker://magland/labbox-ephys-processing:0.3.19')
@hi.local_modules([os.getenv('LABBOX_EPHYS_PYTHON_MODULE_DIR')])
@le.serialize
def get_sorting_unit_info(snippets_h5, unit_id):
    import h5py
    h5_path = ka.load_file(snippets_h5)
    with h5py.File(h5_path, 'r') as f:
        unit_ids = np.array(f.get('unit_ids'))
        channel_ids = np.array(f.get('channel_ids'))
        channel_locations = np.array(f.get(f'channel_locations'))
        sampling_frequency = np.array(f.get('sampling_frequency'))[0].item()
        if np.isnan(sampling_frequency):
            print('WARNING: sampling frequency is nan. Using 30000 for now. Please correct the snippets file.')
            sampling_frequency = 30000
        unit_waveforms_channel_ids = np.array(f.get(f'unit_waveforms/{unit_id}/channel_ids'))
        print(unit_waveforms_channel_ids)
    
    channel_locations0 = []
    for ch_id in unit_waveforms_channel_ids:
        ind = np.where(channel_ids == ch_id)[0]
        channel_locations0.append(channel_locations[ind, :].ravel().tolist())

    return dict(
        channel_ids=unit_waveforms_channel_ids.astype(np.int32),
        channel_locations=channel_locations0,
        sampling_frequency=sampling_frequency
    )
