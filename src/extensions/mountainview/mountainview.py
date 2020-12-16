import labbox_ephys as le


@le.register_sorting_view(name='MVSortingView')
def MVSortingView(*, sorting: le.LabboxEphysSortingExtractor, recording: le.LabboxEphysRecordingExtractor):
    import labbox_ephys_widgets_jp as lew
    return lew.create_sorting_view('MVSortingView', sorting=sorting, recording=recording)
