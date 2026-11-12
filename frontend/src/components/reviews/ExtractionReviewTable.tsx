import { TextInput, Tag } from '@carbon/react'
import { ExtractedAttribute, ExtractionReviewPayload } from '../../types/review'
import styles from './ExtractionReviewTable.module.css'

interface ExtractionReviewTableProps {
  attributes: ExtractionReviewPayload
  editedAttributes: ExtractionReviewPayload
  onAttributeEdit: (attributeName: string, value: string) => void
}

function getProvenanceTag(lineage: ExtractedAttribute['lineage']) {
  switch (lineage) {
    case 'ai_generated':
      return <Tag type="purple">AI-generated</Tag>
    case 'human_corrected':
      return <Tag type="green">Human-corrected</Tag>
    case 'directly_sourced':
      return <Tag type="gray">Directly sourced</Tag>
    default:
      return null
  }
}

function formatAttributeValue(value: string | string[]): string {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return value
}

export function ExtractionReviewTable({
  attributes,
  editedAttributes,
  onAttributeEdit,
}: ExtractionReviewTableProps) {
  const attributeNames = Object.keys(attributes)

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table} aria-label="Extracted attributes">
        <thead>
          <tr>
            <th scope="col">Attribute</th>
            <th scope="col">Extracted value</th>
            <th scope="col">Provenance</th>
            <th scope="col">Confidence</th>
            <th scope="col">Source excerpt</th>
          </tr>
        </thead>
        <tbody>
          {attributeNames.map((attrName) => {
            const attr = attributes[attrName]
            const edited = editedAttributes[attrName]
            const isEdited = !!edited

            return (
              <tr key={attrName} className={isEdited ? styles.editRow : ''}>
                <td>{attrName}</td>
                <td>
                  {isEdited ? (
                    <TextInput
                      id={`edit-${attrName}`}
                      labelText="Edit value"
                      hideLabel
                      value={formatAttributeValue(edited.value)}
                      onChange={(e) => onAttributeEdit(attrName, e.target.value)}
                    />
                  ) : (
                    formatAttributeValue(attr.value)
                  )}
                </td>
                <td>
                  {getProvenanceTag(isEdited ? edited.lineage : attr.lineage)}
                </td>
                <td>
                  {attr.confidence !== undefined ? attr.confidence.toFixed(2) : '–'}
                  {isEdited && edited.confidence !== attr.confidence && (
                    <span className={styles.wasValue}>
                      {' '}
                      (was {attr.confidence?.toFixed(2)})
                    </span>
                  )}
                </td>
                <td>{attr.source_excerpt || '–'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
