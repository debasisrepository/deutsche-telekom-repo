import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  Link,
} from '@carbon/react';
import type { NicheResearchDossierItem } from '../../types/proposal';

interface NicheCandidateTableProps {
  candidates: NicheResearchDossierItem[];
}

export function NicheCandidateTable({ candidates }: NicheCandidateTableProps) {
  const headers = [
    { key: 'candidate_name', header: 'Candidate' },
    { key: 'supplier_id', header: 'supplier_id' },
    { key: 'source_citations', header: 'source_citations' },
    { key: 'review_decision', header: 'Reviewer decision' },
  ];

  const rows = candidates.map((candidate) => ({
    id: candidate.provider_candidate_id,
    candidate_name: candidate.candidate_name,
    supplier_id: candidate.supplier_id,
    source_citations: candidate.source_citations,
    review_status: candidate.review_status,
  }));

  const getReviewStatusTag = (status: string) => {
    if (status === 'accepted' || status.toLowerCase().includes('accept')) {
      return <Tag type="green">Accepted</Tag>;
    }
    if (status.toLowerCase().includes('modify')) {
      return <Tag type="warm-gray">Modify: confirm scope</Tag>;
    }
    if (status.toLowerCase().includes('reject')) {
      return <Tag type="red">Rejected: uncited</Tag>;
    }
    return <Tag type="gray">{status}</Tag>;
  };

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
            {rows.map((row, rowIndex) => {
              const candidate = candidates[rowIndex];
              return (
                <TableRow {...getRowProps({ row })} key={row.id}>
                  {row.cells.map((cell) => {
                    // Special handling for source_citations column
                    if (cell.info.header === 'source_citations') {
                      return (
                        <TableCell key={cell.id}>
                          {candidate.source_citations.length > 0 ? (
                            candidate.source_citations.map((citation, idx) => (
                              <Link href="#" key={idx} className="cds--link citation-link">
                                {citation}
                              </Link>
                            ))
                          ) : (
                            <span className="cds--helper-text-01">No governed source available</span>
                          )}
                        </TableCell>
                      );
                    }
                    // Special handling for review_decision column
                    if (cell.info.header === 'review_decision') {
                      return (
                        <TableCell key={cell.id}>
                          {getReviewStatusTag(candidate.review_status)}
                        </TableCell>
                      );
                    }
                    // Regular cell
                    return (
                      <TableCell 
                        key={cell.id} 
                        className={cell.info.header === 'supplier_id' ? 'cds--table-column-menu' : ''}
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
