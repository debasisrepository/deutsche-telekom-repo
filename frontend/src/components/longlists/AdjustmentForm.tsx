import { useState } from 'react'
import { Form, Select, SelectItem, TextArea, Button } from '@carbon/react'

interface AdjustmentFormProps {
  suppliers: Array<{ supplier_id: number; supplier_name: string }>
  onSubmit: (adjustment: {
    supplier_id: number
    change_type: 'add' | 'remove'
    rationale: string
  }) => void
  disabled?: boolean
}

export function AdjustmentForm({ suppliers, onSubmit, disabled = false }: AdjustmentFormProps) {
  const [changeType, setChangeType] = useState<'add' | 'remove'>('remove')
  const [supplierId, setSupplierId] = useState<string>('')
  const [rationale, setRationale] = useState<string>('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!supplierId || !rationale.trim()) return

    onSubmit({
      supplier_id: parseInt(supplierId, 10),
      change_type: changeType,
      rationale: rationale.trim(),
    })

    // Reset form
    setRationale('')
  }

  return (
    <Form onSubmit={handleSubmit}>
      <div className="adjustment-form-fields">
        <Select
          id="change-type"
          labelText="Change type"
          value={changeType}
          onChange={(e) => setChangeType(e.target.value as 'add' | 'remove')}
          disabled={disabled}
        >
          <SelectItem value="remove" text="remove" />
          <SelectItem value="add" text="add" />
        </Select>

        <Select
          id="supplier"
          labelText="Supplier"
          value={supplierId}
          onChange={(e) => setSupplierId(e.target.value)}
          disabled={disabled}
        >
          <SelectItem value="" text="Select supplier" />
          {suppliers.map((supplier) => (
            <SelectItem
              key={supplier.supplier_id}
              value={supplier.supplier_id.toString()}
              text={supplier.supplier_name}
            />
          ))}
        </Select>

        <TextArea
          id="rationale"
          labelText="Rationale (required)"
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          rows={3}
          disabled={disabled}
        />

        <Button type="submit" disabled={disabled || !supplierId || !rationale.trim()}>
          Record adjustment
        </Button>
      </div>
    </Form>
  )
}
