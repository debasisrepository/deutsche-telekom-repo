import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
} from '@carbon/react';
import type { CandidateSupplier } from '../../types/evidence';

interface PanelMatchTableProps {
  candidates: CandidateSupplier[];
}

export function PanelMatchTable({ candidates }: PanelMatchTableProps) {
  const headers = [
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'panel_source', header: 'panel_source' },
    { key: 'functional_group', header: 'functional_group' },
    { key: 'provenance_ref', header: 'provenance_ref' },
  ];

  const rows = candidates.map((candidate) => ({
    id: candidate.panel_match_id,
    supplier_id: candidate.supplier_id,
    panel_source: candidate.panel_source,
    functional_group: candidate.functional_group,
    provenance_ref: candidate.provenance_ref,
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
            {rows.map((row) => (
              <TableRow {...getRowProps({ row })} key={row.id}>
                {row.cells.map((cell, cellIndex) => (
                  <TableCell key={cell.id} className={cellIndex === 0 ? 'cds--table-column-menu' : ''}>
                    {cell.value ?? ''}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </DataTable>
  );
}
