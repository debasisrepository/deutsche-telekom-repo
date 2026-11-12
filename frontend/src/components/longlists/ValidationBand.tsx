import { Button, InlineNotification } from '@carbon/react'
import type { ValidationResult } from '../../types/longlist'
import './ValidationBand.module.css'

interface ValidationBandProps {
  validation: ValidationResult | null
  currentCount: number
  onRevalidate: () => void
  onLock: () => void
  isRevalidating?: boolean
  isLocking?: boolean
}

export function ValidationBand({
  validation,
  currentCount,
  onRevalidate,
  onLock,
  isRevalidating = false,
  isLocking = false,
}: ValidationBandProps) {
  const minSuppliers = 3
  const maxSuppliers = 6
  const validationResult = validation?.validation_result || 'unknown'
  const isValid = validationResult === 'valid'

  return (
    <div className="validation-section">
      <h2>Supplier-count validation</h2>
      <p className="validation-policy">Policy band: {minSuppliers} to {maxSuppliers} suppliers</p>

      <div className="validation-band" role="img" aria-label={`Count ${currentCount} is ${validationResult}`}>
        <div className={`band-segment band-low ${currentCount < minSuppliers ? 'band-current' : ''}`}>
          &lt; {minSuppliers}
        </div>
        <div className={`band-segment band-ok ${currentCount >= minSuppliers && currentCount <= maxSuppliers ? 'band-current' : ''}`}>
          {minSuppliers}–{maxSuppliers}
        </div>
        <div className={`band-segment band-high ${currentCount > maxSuppliers ? 'band-current' : ''}`}>
          {currentCount} · &gt; {maxSuppliers}
        </div>
      </div>

      <table className="validation-details cds--data-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Current count</td>
            <td>
              <strong>{currentCount}</strong>
            </td>
          </tr>
          <tr>
            <td>Result code</td>
            <td>
              <span className={`validation-tag validation-tag-${validationResult}`}>
                {validationResult}
              </span>
            </td>
          </tr>
          {validation && (
            <tr>
              <td>Validated</td>
              <td>{new Date(validation.validated_at).toLocaleString('en-GB', { 
                timeZone: 'UTC', 
                timeZoneName: 'short' 
              })}</td>
            </tr>
          )}
        </tbody>
      </table>

      {!isValid && validation && (
        <InlineNotification
          kind="error"
          title="Lock blocked."
          subtitle={
            validationResult === 'invalid_high'
              ? `${currentCount} suppliers exceed the maximum of ${maxSuppliers}. Remove at least one supplier, then validate again.`
              : `${currentCount} suppliers is below the minimum of ${minSuppliers}. Add more suppliers, then validate again.`
          }
          hideCloseButton
          role="alert"
        />
      )}

      <div className="validation-actions">
        <Button kind="tertiary" onClick={onRevalidate} disabled={isRevalidating}>
          {isRevalidating ? 'Validating...' : 'Re-validate count'}
        </Button>
        <Button onClick={onLock} disabled={!isValid || isLocking}>
          {isLocking ? 'Locking...' : 'Lock longlist'}
        </Button>
      </div>
    </div>
  )
}
