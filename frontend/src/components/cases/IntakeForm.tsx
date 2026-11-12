import { useState } from 'react'
import { Button, Select, SelectItem, TextInput, TextArea, InlineNotification, Stack } from '@carbon/react'
import { apiClient } from '../../lib/api-client'
import type { CreateCaseRequest } from '../../types/case'
import styles from './IntakeForm.module.css'

interface IntakeFormProps {
  onSuccess?: (caseNumber: string) => void
}

export function IntakeForm({ onSuccess }: IntakeFormProps) {
  const [channel, setChannel] = useState('rfp_document')
  const [title, setTitle] = useState('')
  const [businessUnit, setBusinessUnit] = useState('')
  const [artifactRef, setArtifactRef] = useState('')
  const [intakeNote, setIntakeNote] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleClear = () => {
    setChannel('rfp_document')
    setTitle('')
    setBusinessUnit('')
    setArtifactRef('')
    setIntakeNote('')
    setSuccessMessage(null)
    setErrorMessage(null)
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    setSuccessMessage(null)
    setErrorMessage(null)

    try {
      const request: CreateCaseRequest = {
        channel,
        title,
        business_unit: businessUnit,
        description: intakeNote || 'No additional notes provided',
        artifact_type: 'document',
        artifact_ref: artifactRef || 'No artifact reference',
        submitted_via: channel,
      }

      const response = await apiClient.post<{ case_number: string; workflow_state: string; next_action: string }>('/cases', request)
      
      setSuccessMessage(
        `Case created: ${response.case_number}. State: ${response.workflow_state}. Next required action: ${response.next_action}.`
      )
      
      if (onSuccess) {
        onSuccess(response.case_number)
      }
      
      handleClear()
    } catch (error) {
      const errorDetail = error instanceof Error ? error.message : 'Failed to create case'
      setErrorMessage(errorDetail)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={styles.container}>
      <h2 className={`${styles.heading} cds--productive-heading-03`}>
        Capture new need
      </h2>

      <Stack gap={5}>
        <Select
          id="channel-select"
          labelText="Intake channel (required)"
          value={channel}
          onChange={(e) => setChannel(e.target.value)}
        >
          <SelectItem value="rfp_document" text="rfp_document" />
          <SelectItem value="email" text="email" />
          <SelectItem value="phone_note" text="phone_note" />
          <SelectItem value="supplier_offer" text="supplier_offer" />
        </Select>

        <TextInput
          id="title-input"
          labelText="Need title (required)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter need title"
        />

        <TextInput
          id="business-unit-input"
          labelText="Requesting business unit"
          value={businessUnit}
          onChange={(e) => setBusinessUnit(e.target.value)}
          placeholder="Enter business unit"
        />

        <div>
          <TextInput
            id="artifact-ref-input"
            labelText="Source artifact"
            value={artifactRef}
            onChange={(e) => setArtifactRef(e.target.value)}
            placeholder="Enter artifact reference"
          />
          <p className={`${styles.helperText} cds--label-01`}>
            The original artifact is preserved and linked to the case.
          </p>
        </div>

        <TextArea
          id="intake-note-input"
          labelText="Intake note (optional)"
          value={intakeNote}
          onChange={(e) => setIntakeNote(e.target.value)}
          placeholder="Enter intake note"
          rows={3}
        />

        <div className={styles.buttonGroup}>
          <Button
            kind="primary"
            size="md"
            onClick={handleSubmit}
            disabled={isSubmitting || !title}
          >
            {isSubmitting ? 'Creating...' : 'Create case'}
          </Button>
          <Button
            kind="tertiary"
            size="md"
            onClick={handleClear}
            disabled={isSubmitting}
          >
            Clear form
          </Button>
        </div>

        {successMessage && (
          <InlineNotification
            kind="success"
            title="Case created"
            subtitle={successMessage}
            hideCloseButton
            lowContrast
          />
        )}

        {errorMessage && (
          <InlineNotification
            kind="error"
            title="Intake error state"
            subtitle={errorMessage}
            hideCloseButton
            lowContrast
          />
        )}
      </Stack>
    </div>
  )
}
