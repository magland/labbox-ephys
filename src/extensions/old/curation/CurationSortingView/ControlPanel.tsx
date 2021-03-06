import { Grid, Paper } from '@material-ui/core';
import React, { FunctionComponent, useCallback } from 'react';
import { SortingCuration, SortingCurationDispatch, SortingSelection, SortingSelectionDispatch } from '../../../extensionInterface';

type Props = {
    width: number
    curation: SortingCuration
    curationDispatch: SortingCurationDispatch
    selection: SortingSelection
    selectionDispatch: SortingSelectionDispatch
}

const buttonStyle = {
    paddingTop: 3, paddingBottom: 3, border: 1, borderStyle: 'solid', borderColor: 'gray'
}

const ControlPanel: FunctionComponent<Props> = ({ width, selection, selectionDispatch, curation, curationDispatch }) => {
    const _handleApplyLabel = useCallback(
        (label: string) => {
            for (let unitId of (selection.selectedUnitIds || [])) {
                curationDispatch({
                    type: 'AddLabel',
                    unitId,
                    label
                })
            }
        },
        [curationDispatch, selection],
    )

    const _handleRemoveLabel = useCallback(
        (label: string) => {
            for (let unitId of (selection.selectedUnitIds || [])) {
                curationDispatch({
                    type: 'RemoveLabel',
                    unitId,
                    label
                })
            }
        },
        [curationDispatch, selection]
    )

    type LabelRecord = {
        label: string,
        partial: boolean
    }

    const labelCounts: {[key: string]: number} = {}
    for (const uid of (selection.selectedUnitIds || [])) {
        const labels = (curation.labelsByUnit || {})[uid + ''] || []
        for (const label of labels) {
            let c = labelCounts[label] || 0
            c ++
            labelCounts[label] = c
        }
    }
    const labels = Object.keys(labelCounts).sort()
    const labelRecords: LabelRecord[] = labels.map(label => ({
        label,
        partial: labelCounts[label] < (selection.selectedUnitIds || []).length ? true : false
    }))
    const paperStyle: React.CSSProperties = {
        marginTop: 25,
        marginBottom: 25,
        backgroundColor: '#f9f9ff'
    }
    const enableApply = (selection.selectedUnitIds || []).length > 0
    const standardChoices = ['accept', 'reject', 'noise', 'artifact', 'mua']
    const labelChoices = [...standardChoices, ...(curation.labelChoices || []).filter(l => (!standardChoices.includes(l)))]
    return (
        <div style={{width, position: 'relative'}}>
            <Paper style={paperStyle} key="selected">
                Selected units: {(selection.selectedUnitIds || []).join(', ')}
            </Paper>
            <Paper style={paperStyle} key="labels">
                Labels:
                <Grid container style={{flexFlow: 'wrap'}} spacing={0}>
                    {
                        labelRecords.map(r => (
                            <Grid item key={r.label}>
                                <Label label={r.label} partial={r.partial} onClick={() => {r.partial ? _handleApplyLabel(r.label) : _handleRemoveLabel(r.label)}} />
                            </Grid>
                        ))
                    }
                </Grid>
            </Paper>
            {
                <Paper style={paperStyle} key="apply">
                    Apply:
                    <Grid container style={{flexFlow: 'wrap'}} spacing={0}>
                        {
                            labelChoices.map(labelChoice => (
                                ((labelCounts[labelChoice] || 0) < (selection.selectedUnitIds || []).length) || (!enableApply)) ? (
                                    <Grid item key={labelChoice}>
                                        <button style={buttonStyle} disabled={!enableApply} onClick={() => {_handleApplyLabel(labelChoice)}}>{labelChoice}</button>
                                    </Grid>
                                ): <span />
                            )
                        }
                    </Grid>
                </Paper>
            }
        </div>
    )
}

const Label: FunctionComponent<{label: string, partial: boolean, onClick: () => void}> = ({label, partial, onClick}) => {
    const color = partial ? 'gray': 'black'
    return (
        <button style={{...buttonStyle, color}} onClick={onClick}>{label}</button>
    )
}

export default ControlPanel