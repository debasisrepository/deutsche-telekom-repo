import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Link,
} from '@carbon/react';
import type { EvidenceItem } from '../../types/evidence';

interface EvidenceTableProps {
  items: EvidenceItem[];
}

export function EvidenceTable({ items }: EvidenceTableProps) {
  const headers = [
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'evidence_type', header: 'evidence_type' },
    { key: 'source_reference', header: 'source_reference (citation)' },
    { key: 'business_unit', header: 'Business unit' },
    { key: 'delivered', header: 'Delivered' },
    { key: 'quality_rating', header: 'quality_rating' },
  ];

  const rows = items.map((item, index) => ({
    id: `${item.supplier_id}-${index}`,
    supplier_id: item.supplier_id,
    evidence_type: item.evidence_type,
    source_reference: item.source_reference,
    citation_text: item.citation_text,
    business_unit: item.business_unit || 'N/A',
    delivered: item.delivery_period || 'N/A',
    quality_rating: item.quality_rating ? `${item.quality_rating} / 5` : 'Not rated',
  }));

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
        <Table {...getTableProps()}>
          <TableHead>
            <TableRow>
              {headers.map((header) => (
                <TableHeader {...getHeaderProps({ header })} key={header.key}>
                  {header.header}
                </TableHeader>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row, rowIndex) => (
              <TableRow {...getRowProps({ row })} key={row.id}>
                {row.cells.map((cell, cellIndex) => {
                  // Special handling for source_reference column to add citation link
                  if (cell.info.header === 'source_reference') {
                    return (
                      <TableCell key={cell.id}>
                        <Link href="#" className="cds--link">
                          {cell.value}
                        </Link>
                        <div className="cds--helper-text-01">
                          {items[rowIndex]?.citation_text || ''}
                        </div>
                      </TableCell>
                    );
                  }
                  // Regular cell
                  return (
                    <TableCell key={cell.id} className={cellIndex === 0 ? 'cds--table-column-menu' : ''}>
                      {cell.value}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </DataTable>
  );
}
