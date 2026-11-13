import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Link,
  ProgressBar,
} from '@carbon/react';
import type { RankedSupplier } from '../../types/proposal';
import './RankedSupplierTable.scss';

interface RankedSupplierTableProps {
  suppliers: RankedSupplier[];
}

export function RankedSupplierTable({ suppliers }: RankedSupplierTableProps) {
  const headers = [
    { key: 'rank', header: 'rank' },
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'panel_source', header: 'panel_source' },
    { key: 'evidence_citations', header: 'evidence_citations' },
    { key: 'rank_rationale', header: 'rank_rationale' },
    { key: 'confidence', header: 'confidence' },
  ];

  const rows = suppliers.map((supplier) => ({
    id: supplier.ranked_supplier_id,
    rank: supplier.rank,
    supplier_id: supplier.supplier_id,
    panel_source: supplier.panel_source,
    evidence_citations: supplier.evidence_citations,
    rank_rationale: supplier.rank_rationale,
    confidence: supplier.confidence,
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
            {rows.map((row) => {
              const supplier = suppliers[rows.indexOf(row)];
              return (
                <TableRow {...getRowProps({ row })} key={row.id}>
                  <TableCell>
                    <span className="ranked-supplier-rank">{supplier.rank}</span>
                  </TableCell>
                  <TableCell className="cds--table-column-menu">
                    {supplier.supplier_id}
                  </TableCell>
                  <TableCell>{supplier.panel_source}</TableCell>
                  <TableCell>
                    {supplier.evidence_citations.map((citation, idx) => (
                      <Link href="#" key={idx} className="cds--link citation-badge">
                        {citation.source_reference}
                      </Link>
                    ))}
                  </TableCell>
                  <TableCell>{supplier.rank_rationale}</TableCell>
                  <TableCell>
                    <div className="confidence-display">
                      <ProgressBar
                        value={supplier.confidence * 100}
                        max={100}
                        label=""
                        hideLabel
                        size="small"
                        className={supplier.confidence >= 0.8 ? 'confidence-high' : 'confidence-medium'}
                      />
                      <span className="confidence-value">{supplier.confidence.toFixed(2)}</span>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </DataTable>
  );
}
