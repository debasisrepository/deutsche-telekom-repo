import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
} from '@carbon/react';
import './ExemplarTable.scss';

interface Exemplar {
  id: string;
  verdict: 'single_resource' | 'it_service';
  similarity: number;
  description?: string;
}

interface ExemplarTableProps {
  exemplars: Exemplar[];
}

export function ExemplarTable({ exemplars }: ExemplarTableProps) {
  const headers = [
    { key: 'id', header: 'Exemplar' },
    { key: 'verdict', header: 'Confirmed verdict' },
    { key: 'similarity', header: 'Similarity' },
  ];

  const rows = exemplars.map((exemplar) => ({
    id: exemplar.id,
    verdict: exemplar.verdict,
    similarity: exemplar.similarity.toFixed(2),
  }));

  return (
    <div className="exemplar-table">
      <DataTable rows={rows} headers={headers}>
        {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
          <Table {...getTableProps()} size="sm">
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
                  {row.cells.map((cell) => (
                    <TableCell 
                      key={cell.id}
                      className={cell.info.header === 'id' ? 'exemplar-table__id' : ''}
                    >
                      {cell.value}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </DataTable>
    </div>
  );
}
