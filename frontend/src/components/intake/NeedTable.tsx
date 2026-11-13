import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  Button,
} from '@carbon/react';
import { useNavigate } from 'react-router-dom';
import type { Need } from '../../types/need';
import './NeedTable.scss';

interface NeedTableProps {
  needs: Need[];
  onRowClick?: (need: Need) => void;
  selectedNeedId?: string;
  showActions?: boolean;
}

export function NeedTable({ needs, onRowClick, selectedNeedId, showActions = true }: NeedTableProps) {
  const navigate = useNavigate();
  
  const getStatusTagType = (status: string) => {
    if (status.startsWith('error')) return 'red';
    if (status === 'normalized') return 'green';
    return 'gray';
  };

  const headers = [
    { key: 'need_id', header: 'need_id' },
    { key: 'business_unit_id', header: 'business_unit_id' },
    { key: 'channel_type', header: 'channel_type' },
    { key: 'arrival_timestamp', header: 'arrival_timestamp (UTC)' },
    { key: 'status', header: 'status' },
    ...(showActions ? [{ key: 'actions', header: 'Actions' }] : []),
  ];

  const rows = needs.map((need) => ({
    id: need.id,
    need_id: need.id,
    business_unit_id: need.business_unit_id,
    channel_type: need.channel_type,
    arrival_timestamp: new Date(need.arrival_timestamp).toISOString().replace('T', ' ').substring(0, 19),
    status: need.status,
    actions: showActions ? (
      <Button
        size="sm"
        kind="tertiary"
        onClick={(e: React.MouseEvent) => {
          e.stopPropagation();
          navigate(`/reviews/${need.id}/attributes`);
        }}
      >
        View
      </Button>
    ) : null,
    need,
  }));

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
        <Table {...getTableProps()} aria-label="Need submissions table">
          <TableHead>
            <TableRow>
              {headers.map((header) => (
                <TableHeader {...getHeaderProps({ header })}>
                  {header.header}
                </TableHeader>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => {
              const need = needs.find((n) => n.id === row.id);
              const isSelected = selectedNeedId === row.id;
              return (
                <TableRow
                  {...getRowProps({ row })}
                  className={isSelected ? 'need-table-row-selected' : 'need-table-row'}
                  onClick={() => need && onRowClick?.(need)}
                  onKeyDown={(e) => {
                    if ((e.key === 'Enter' || e.key === ' ') && need) {
                      e.preventDefault();
                      onRowClick?.(need);
                    }
                  }}
                  tabIndex={onRowClick ? 0 : undefined}
                  role={onRowClick ? 'button' : undefined}
                >
                  {row.cells.map((cell, cellIndex) => {
                    // Special handling for status column
                    if (cell.info.header === 'status') {
                      return (
                        <TableCell key={cell.id}>
                          {need && <Tag type={getStatusTagType(need.status)}>{need.status}</Tag>}
                        </TableCell>
                      );
                    }
                    // Regular cell
                    return (
                      <TableCell 
                        key={cell.id} 
                        className={(cellIndex === 0 || cellIndex === 3) ? 'cds--type-mono' : ''}
                      >
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
