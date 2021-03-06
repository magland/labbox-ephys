import React, { FunctionComponent, useCallback, useState } from 'react';
import Markdown from '../extensions/common/Markdown';
import Expandable from '../extensions/old/curation/CurationSortingView/Expandable';
import import_example_simulated_recording_py from './importExamples/import_example_simulated_recording.py.gen';
import import_nwb_recording_py from './importExamples/import_nwb_recording.py.gen';
import import_spikeforest_recording_py from './importExamples/import_spikeforest_recording.py.gen';
import instructionsMd from './ImportRecordingsInstructions.md.gen';

type Props = {
}

const ImportRecordingsInstructions: FunctionComponent<Props> = () => {
    return (
        <div>
            <Markdown
                source={instructionsMd}
            />
            <Expandable label="Import example simulated recording">
                <CopyToClipboardButton text={import_example_simulated_recording_py} />
                <Markdown source={mdWrapPy(import_example_simulated_recording_py)} />
            </Expandable>
            <Expandable label="Import SpikeForest recordings">
                <CopyToClipboardButton text={import_spikeforest_recording_py} />
                <Markdown source={mdWrapPy(import_spikeforest_recording_py)} />
            </Expandable>
            <Expandable label="Import NWB recordings">
                <CopyToClipboardButton text={import_nwb_recording_py} />
                <Markdown source={mdWrapPy(import_nwb_recording_py)} />
            </Expandable>
        </div>
    )
}

const mdWrapPy = (py: string) => {
    return "```python\n" + py + '\n```'
}

type CopyToClipboardButtonProps = {
    text: string
}

const CopyToClipboardButton: FunctionComponent<CopyToClipboardButtonProps> = ({ text }) => {
    const [copied, setCopied] = useState(false)
    const handleClick = useCallback(() => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => {
            setCopied(false)
        }, 3000)
    }, [text])
    return (
        <button onClick={handleClick}>{copied ? `Copied` : `Copy to clipboard`}</button>
    )
}

export default ImportRecordingsInstructions