import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell, Tag } from '@carbon/react';
import { ConfidenceBar } from './ConfidenceBar';
import type { NeedAttribute } from '../../types/review';
import './AttributeTable.scss';

interface AttributeTableProps {
  attributes: NeedAttribute[];
}

export function AttributeTable({ attributes }: AttributeTableProps) {
  const headers = [
    { key: 'field', header: 'Field' },
    { key: 'value', header: 'Extracted value' },
    { key: 'confidence', header: 'field_confidence' },
    { key: 'action', header: 'Reviewer action' },
  ];

  const rows = attributes.map((attr) => ({
    id: attr.field,
    field: attr.field,
    value: attr.value,
    confidence: attr.confidence,
    action: attr.action,
    attr,
  }));

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
        <Table {...getTableProps()} aria-label="Need attributes table">
          <TableHead>
            <TableRow>
              <TableHeader {...getHeaderProps({ header: headers[0] })} className="attr-table-field-col">
                {headers[0].header}
              </TableHeader>
              <TableHeader {...getHeaderProps({ header: headers[1] })}>
                {headers[1].header}
              </TableHeader>
              <TableHeader {...getHeaderProps({ header: headers[2] })} className="attr-table-confidence-col">
                {headers[2].header}
              </TableHeader>
              <TableHeader {...getHeaderProps({ header: headers[3] })} className="attr-table-action-col">
                {headers[3].header}
              </TableHeader>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => {
              const attr = attributes.find((a) => a.field === row.id);
              return (
                <TableRow {...getRowProps({ row })}>
                  {row.cells.map((cell) => {
                    // Special handling for confidence column
                    if (cell.info.header === 'confidence') {
                      return (
                        <TableCell key={cell.id}>
                          {attr && <ConfidenceBar value={attr.confidence} />}
                        </TableCell>
                      );
                    }
                    // Special handling for action column
                    if (cell.info.header === 'action') {
                      return (
                        <TableCell key={cell.id}>
                          <Tag type={attr?.action === 'modify' ? 'warm-gray' : 'outline'}>
                            {attr?.action === 'modify' ? 'Modify' : 'Keep'}
                          </Tag>
                        </TableCell>
                      );
                    }
                    // Regular cell
                    return (
                      <TableCell key={cell.id} className={cell.info.header === 'field' ? 'cds--type-mono' : ''}>
                        {cell.value ?? ''}
                      </TableCell>
                    );
                  })}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </DataTable>
  );
}
