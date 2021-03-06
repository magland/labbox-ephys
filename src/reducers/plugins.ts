import { Reducer } from 'react'
import { Plugins, RecordingViewPlugin, SortingUnitMetricPlugin, SortingUnitViewPlugin, SortingViewPlugin } from '../extensions/extensionInterface'

export type State = Plugins
export const initialState: State = {
    sortingViews: {},
    sortingUnitViews: {},
    recordingViews: {},
    sortingUnitMetrics: {}
}
export interface RegisterSortingViewAction {
    type: 'REGISTER_SORTING_VIEW'
    sortingView: SortingViewPlugin
}
const isRegisterSortingViewAction = (x: any): x is RegisterSortingViewAction => (
    x.type === 'REGISTER_SORTING_VIEW'
)

export interface RegisterSortingUnitViewAction {
    type: 'REGISTER_SORTING_UNIT_VIEW'
    sortingUnitView: SortingUnitViewPlugin
}
const isRegisterSortingUnitViewAction = (x: any): x is RegisterSortingUnitViewAction => (
    x.type === 'REGISTER_SORTING_UNIT_VIEW'
)

export interface RegisterRecordingViewAction {
    type: 'REGISTER_RECORDING_VIEW'
    recordingView: RecordingViewPlugin
}
const isRegisterRecordingViewAction = (x: any): x is RegisterRecordingViewAction => (
    x.type === 'REGISTER_RECORDING_VIEW'
)

export interface RegisterSortingUnitMetricAction {
    type: 'REGISTER_SORTING_UNIT_METRIC'
    sortingUnitMetric: SortingUnitMetricPlugin
}
const isRegisterSortingUnitMetricAction = (x: any): x is RegisterSortingUnitMetricAction => (
    x.type === 'REGISTER_SORTING_UNIT_METRIC'
)

export type Action = RegisterSortingViewAction | RegisterSortingUnitViewAction | RegisterRecordingViewAction | RegisterSortingUnitMetricAction

// the reducer
const extensionContext: Reducer<State, Action> = (state: State = initialState, action: Action): State => {
    if (isRegisterSortingViewAction(action)) {
        if (state.sortingViews[action.sortingView.name]) throw Error(`Sorting view already registered: ${action.sortingView.name}`)
        return {
            ...state,
            sortingViews: {
                ...state.sortingViews,
                [action.sortingView.name]: action.sortingView
            }
        }
    }
    else if (isRegisterSortingUnitViewAction(action)) {
        if (state.sortingUnitViews[action.sortingUnitView.name]) throw Error(`Sorting unit view already registered: ${action.sortingUnitView.name}`)
        return {
            ...state,
            sortingUnitViews: {
                ...state.sortingUnitViews,
                [action.sortingUnitView.name]: action.sortingUnitView
            }
        }
    }
    else if (isRegisterRecordingViewAction(action)) {
        if (state.recordingViews[action.recordingView.name]) throw Error(`Recording view already registered: ${action.recordingView.name}`)
        return {
            ...state,
            recordingViews: {
                ...state.recordingViews,
                [action.recordingView.name]: action.recordingView
            }
        }
    }
    else if (isRegisterSortingUnitMetricAction(action)) {
        if (state.sortingUnitMetrics[action.sortingUnitMetric.name]) throw Error(`Sorting unit metric already registered: ${action.sortingUnitMetric.name}`)
        return {
            ...state,
            sortingUnitMetrics: {
                ...state.sortingUnitMetrics,
                [action.sortingUnitMetric.name]: action.sortingUnitMetric
            }
        }
    }
    else {
        return state
    }
}

export default extensionContext