import { Checkmark } from '@carbon/icons-react'
import styles from './WorkflowStepper.module.css'

interface WorkflowStep {
  id: string
  label: string
  description: string
  status: 'done' | 'current' | 'pending' | 'closed'
}

interface WorkflowStepperProps {
  workflowState: string
}

export function WorkflowStepper({ workflowState }: WorkflowStepperProps) {
  const getSteps = (state: string): WorkflowStep[] => {
    const stateOrder = [
      'intake_pending',
      'intake_normalized',
      'extraction_pending',
      'extraction_approved',
      'classification_pending',
      'classification_approved',
      'evidence_pending',
      'mapping_pending',
      'longlist_pending',
      'locked',
      'dispatched',
    ]

    const currentIndex = stateOrder.indexOf(state)

    const steps: WorkflowStep[] = [
      {
        id: 'intake',
        label: 'Intake',
        description: currentIndex >= stateOrder.indexOf('intake_normalized') ? 'Complete' : 'In progress',
        status: currentIndex >= stateOrder.indexOf('intake_normalized') ? 'done' : currentIndex >= 0 ? 'current' : 'pending',
      },
      {
        id: 'extraction',
        label: 'Extraction',
        description:
          currentIndex >= stateOrder.indexOf('extraction_approved')
            ? 'Complete'
            : currentIndex >= stateOrder.indexOf('extraction_pending')
              ? 'Review required'
              : 'Not started',
        status:
          currentIndex >= stateOrder.indexOf('extraction_approved')
            ? 'done'
            : currentIndex >= stateOrder.indexOf('extraction_pending')
              ? 'current'
              : 'pending',
      },
      {
        id: 'classification',
        label: 'Classification',
        description:
          currentIndex >= stateOrder.indexOf('classification_approved')
            ? 'Complete'
            : currentIndex >= stateOrder.indexOf('classification_pending')
              ? 'Review required'
              : 'Not started',
        status:
          currentIndex >= stateOrder.indexOf('classification_approved')
            ? 'done'
            : currentIndex >= stateOrder.indexOf('classification_pending')
              ? 'current'
              : 'pending',
      },
      {
        id: 'evidence',
        label: 'Evidence and mapping',
        description:
          currentIndex >= stateOrder.indexOf('mapping_pending')
            ? 'Complete'
            : currentIndex >= stateOrder.indexOf('evidence_pending')
              ? 'In progress'
              : 'Not started',
        status:
          currentIndex >= stateOrder.indexOf('mapping_pending')
            ? 'done'
            : currentIndex >= stateOrder.indexOf('evidence_pending')
              ? 'current'
              : 'pending',
      },
      {
        id: 'longlist',
        label: 'Longlist',
        description:
          currentIndex >= stateOrder.indexOf('locked')
            ? 'Complete'
            : currentIndex >= stateOrder.indexOf('longlist_pending')
              ? 'In progress'
              : 'Not started',
        status:
          currentIndex >= stateOrder.indexOf('locked')
            ? 'done'
            : currentIndex >= stateOrder.indexOf('longlist_pending')
              ? 'current'
              : 'pending',
      },
      {
        id: 'lock',
        label: 'Lock',
        description:
          currentIndex >= stateOrder.indexOf('dispatched')
            ? 'Complete'
            : currentIndex >= stateOrder.indexOf('locked')
              ? 'Locked'
              : 'Not started',
        status:
          currentIndex >= stateOrder.indexOf('dispatched')
            ? 'done'
            : currentIndex >= stateOrder.indexOf('locked')
              ? 'current'
              : 'pending',
      },
      {
        id: 'dispatch',
        label: 'Dispatch',
        description: currentIndex >= stateOrder.indexOf('dispatched') ? 'Complete' : 'Not started',
        status: currentIndex >= stateOrder.indexOf('dispatched') ? 'done' : 'pending',
      },
    ]

    return steps
  }

  const steps = getSteps(workflowState)

  return (
    <ol className={styles.stepper} aria-label="Case progress">
      {steps.map((step) => (
        <li
          key={step.id}
          className={`${styles.step} ${styles[step.status]}`}
          aria-current={step.status === 'current' ? 'step' : undefined}
        >
          {step.status === 'done' && (
            <Checkmark size={16} className={styles.icon} aria-hidden="true" />
          )}
          {step.status === 'current' && (
            <span className={styles.ringCurrent} aria-hidden="true" />
          )}
          {step.status === 'pending' && (
            <span className={styles.ring} aria-hidden="true" />
          )}
          <b className={`${styles.stepLabel} cds--label-02`}>{step.label}</b>
          <span className={`${styles.stepDescription} cds--label-01`}>{step.description}</span>
        </li>
      ))}
    </ol>
  )
}
