import { faWater } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Box, CircularProgress } from '@material-ui/core'
import React, { FunctionComponent } from 'react'
import { HitherJob } from './HitherInterface'


const HitherJobStatusView: FunctionComponent<{job?: HitherJob, message?: string, width?: number, height?: number}> = ({job, message='', width=200, height=200}) => {
    if (!job) return <div>No job</div>
    return (
        <Box display="flex" width={width} height={height}>
            <Box m="auto">
                {
                    job.status === 'running' ? (
                        <span>[{message}] <CircularProgress /></span>
                    ): job.status === 'error' ? (
                        <span>Error: {job.error_message} [{message}]</span>
                    ) : job.status === 'pending' ? (
                        <span>[{message}]<FontAwesomeIcon icon={faWater} /></span>
                    ) : (
                        <span>[{message}] {job.status}</span>
                    )
                }
            </Box>
        </Box>
    )
}

export default HitherJobStatusView