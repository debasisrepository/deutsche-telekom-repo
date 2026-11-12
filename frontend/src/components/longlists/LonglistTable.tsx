import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell, Tag, Button } from '@carbon/react'
import type { RankedSupplier } from '../../types/longlist'

interface LonglistTableProps {
  suppliers: RankedSupplier[]
  onRemove?: (supplier: RankedSupplier) => void
  readOnly?: boolean
}

export function LonglistTable({ suppliers, onRemove, readOnly = false }: LonglistTableProps) {
  const headers = [
    { key: 'rank_position', header: 'Rank' },
    { key: 'supplier_name', header: 'Supplier' },
    { key: 'source', header: 'Source' },
    { key: 'evidence_citations', header: 'Evidence citations' },
    { key: 'origin', header: 'Origin' },
    ...(readOnly ? [] : [{ key: 'action', header: 'Action' }]),
  ]

  const rows = suppliers.map((supplier) => ({
    id: supplier.supplier_id.toString(),
    ...supplier,
  }))

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps }) => (
        <Table {...getTableProps()} aria-label="Ranked suppliers longlist">
          <TableHead>
            <TableRow>
              {headers.map((header) => (
                <TableHeader key={header.key}>{header.header}</TableHeader>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => {
              const supplier = row as unknown as RankedSupplier & { id: string }
              const sourceTag = supplier.recommendation_status === 'panel' ? 'Panel' : 'Research-derived'
              const originTag = supplier.origin === 'human_added' ? 'Human-added' : 'AI-generated'
              const isHumanAdded = supplier.origin === 'human_added'

              return (
                <TableRow key={row.id} className={isHumanAdded ? 'cds--data-table--selected' : ''}>
                  <TableCell>{supplier.rank_position}</TableCell>
                  <TableCell>
                    <strong>{supplier.supplier_name}</strong>
                  </TableCell>
                  <TableCell>
                    <Tag type={sourceTag === 'Panel' ? 'blue' : 'gray'} size="sm">
                      {sourceTag}
                    </Tag>
                  </TableCell>
                  <TableCell>
                    <div className="citation-list">
                      {supplier.evidence_citations.map((citation, idx) => (
                        <a
                          key={idx}
                          href="#"
                          onClick={(e) => e.preventDefault()}
                          className="citation-link"
                        >
                          {citation.citation_label}
                        </a>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag type={originTag === 'Human-added' ? 'green' : 'purple'} size="sm">
                      {originTag}
                    </Tag>
                  </TableCell>
                  {!readOnly && (
                    <TableCell>
                      <Button kind="danger--tertiary" size="sm" onClick={() => onRemove?.(supplier)}>
                        Remove
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      )}
    </DataTable>
  )
}
