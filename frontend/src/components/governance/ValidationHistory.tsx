import {
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
} from '@carbon/react';
import styles from './ValidationHistory.module.scss';

interface ValidationRun {
  id: string;
  run: number;
  trigger: string;
  count: number;
  verdict: 'pass' | 'fail';
}

interface ValidationHistoryProps {
  validationRuns: ValidationRun[];
}

const headers = [
  { key: 'run', header: 'Run' },
  { key: 'trigger', header: 'Trigger' },
  { key: 'count', header: 'Count' },
  { key: 'verdict', header: 'Verdict' },
];

export function ValidationHistory({ validationRuns }: ValidationHistoryProps) {
  return (
    <div className={styles.card}>
      <h3 className={styles.heading}>Validation history for this longlist</h3>
      <DataTable rows={validationRuns} headers={headers}>
        {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
          <TableContainer>
            <Table {...getTableProps()} className={styles.smallTable}>
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
                    {row.cells.map((cell) => {
                      if (cell.info.header === 'verdict') {
                        return (
                          <TableCell key={cell.id}>
                            <Tag type={cell.value === 'pass' ? 'green' : 'red'}>
                              {cell.value}
                            </Tag>
                          </TableCell>
                        );
                      }
                      return <TableCell key={cell.id}>{cell.value}</TableCell>;
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DataTable>
      <p className={styles.annotation}>
        Validation reruns after every ATS10 change and again before ATS11 if the supplier set has changed.
      </p>
    </div>
  );
}
