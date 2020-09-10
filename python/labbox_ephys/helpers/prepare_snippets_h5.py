from typing import Dict
import hither as hi
import numpy as np
import kachery as ka
import spikeextractors as se
import spiketoolkit as st

@hi.function('prepare_snippets_h5', '0.2.4')
@hi.container('docker://magland/labbox-ephys-processing:0.3.19')
@hi.local_modules(['../../labbox_ephys'])
def prepare_snippets_h5(
    recording_object,
    sorting_object,
    start_frame=None,
    end_frame=None,
    max_events_per_unit=1000,
    max_neighborhood_size=15
):
    import h5py
    from labbox_ephys import get_unit_waveforms, SubsampledSortingExtractor, find_unit_neighborhoods, find_unit_peak_channels
    import labbox_ephys as le
    recording = le.LabboxEphysRecordingExtractor(recording_object)
    sorting = le.LabboxEphysSortingExtractor(sorting_object)

    if start_frame is not None:
        recording = se.SubRecordingExtractor(parent_recording=recording, start_frame=start_frame, end_frame=end_frame)
        sorting = se.SubSortingExtractor(parent_sorting=sorting, start_frame=start_frame, end_frame=end_frame)

    unit_ids = sorting.get_unit_ids()
    samplerate = sorting.get_sampling_frequency()
    
    # Use this optimized function rather than spiketoolkit's version
    # for efficiency with long recordings and/or many channels, units or spikes
    # we should submit this to the spiketoolkit project as a PR
    print('Subsampling sorting')
    sorting_subsampled = SubsampledSortingExtractor(parent_sorting=sorting, max_events_per_unit=max_events_per_unit, method='random')
    print('Finding unit peak channels')
    peak_channels_by_unit = find_unit_peak_channels(recording=recording, sorting=sorting, unit_ids=unit_ids)
    print('Finding unit neighborhoods')
    channel_ids_by_unit = find_unit_neighborhoods(recording=recording, peak_channels_by_unit=peak_channels_by_unit, max_neighborhood_size=max_neighborhood_size)
    print(f'Getting unit waveforms for {len(unit_ids)} units')
    unit_waveforms = get_unit_waveforms(
        recording=recording,
        sorting=sorting_subsampled,
        unit_ids=unit_ids,
        channel_ids_by_unit=channel_ids_by_unit,
        snippet_len=(50, 80)
    )
    # unit_waveforms = st.postprocessing.get_unit_waveforms(
    #     recording=recording,
    #     sorting=sorting,
    #     unit_ids=unit_ids,
    #     ms_before=1,
    #     ms_after=1.5,
    #     max_spikes_per_unit=500
    # )
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
                f.create_dataset(f'unit_waveforms/{unit_id}/channel_ids', data=np.array(channel_ids_by_unit[int(unit_id)]).astype(int))
        return ka.store_file(save_path)