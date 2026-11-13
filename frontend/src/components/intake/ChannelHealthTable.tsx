import { DataTable, Table, TableHead, TableRow, TableHeader, TableBody, TableCell } from '@carbon/react';
import type { ChannelHealth } from '../../types/need';

interface ChannelHealthTableProps {
  channels: ChannelHealth[];
}

export function ChannelHealthTable({ channels }: ChannelHealthTableProps) {
  const headers = [
    { key: 'channel', header: 'Channel' },
    { key: 'today', header: 'Today' },
    { key: 'rejected', header: 'Rejected' },
  ];

  const rows = channels.map((channel, index) => ({
    id: `channel-${index}`,
    channel: channel.channel,
    today: String(channel.today),
    rejected: String(channel.rejected),
  }));

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
        <Table {...getTableProps()} size="sm" aria-label="Channel health table">
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
            {rows.map((row) => (
              <TableRow {...getRowProps({ row })}>
                {row.cells.map((cell) => (
                  <TableCell key={cell.id}>{cell.value}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </DataTable>
  );
}
