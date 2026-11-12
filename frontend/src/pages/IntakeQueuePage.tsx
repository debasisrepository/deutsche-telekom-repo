import { useState, useEffect } from 'react'
import { Theme, Search, InlineNotification } from '@carbon/react'
import { IntakeForm } from '../components/cases/IntakeForm'
import { CaseListTable } from '../components/cases/CaseListTable'
import { apiClient } from '../lib/api-client'
import type { CaseListResponse } from '../types/case'
import styles from './IntakeQueuePage.module.css'

export function IntakeQueuePage() {
  const [cases, setCases] = useState<CaseListResponse>({ items: [], total: 0, page: 1, page_size: 20 })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const loadCases = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient.get<CaseListResponse>('/cases')
      const data = Array.isArray(response) ? { items: response, total: response.length, page: 1, page_size: 20 } : response
      setCases(data)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load cases'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadCases()
  }, [])

  const handleIntakeSuccess = () => {
    loadCases()
  }

  const filteredCases = searchQuery
    ? cases.items.filter((caseItem) =>
        caseItem.case_number.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : cases.items

  return (
    <Theme theme="white">
      <main className={styles.main} id="main-content">
        <p className={`${styles.breadcrumb} cds--body-compact-01`}>
          <a href="/" className={styles.breadcrumbLink}>
            Cases
          </a>{' '}
          / Need intake
        </p>

        <h1 className={`${styles.heading} cds--productive-heading-05`}>
          Need intake and case list
        </h1>
        <p className={`${styles.subheading} cds--body-compact-01`}>
          Capture a new supplier-selection need from any intake channel. Every need receives a unique case ID and is
          stored with its channel, timestamp and source artifact. Screens 01–08 show the working-tier path from intake to
          tender dispatch.
        </p>

        <InlineNotification
          kind="info"
          title="Scope of this increment:"
          subtitle="need intake through tender dispatch. Confidential internal commercial information – access is logged."
          hideCloseButton
          lowContrast
          className={styles.notification}
        />

        <div className={styles.grid}>
          <section className={styles.column6}>
            <IntakeForm onSuccess={handleIntakeSuccess} />
          </section>

          <section className={styles.column10}>
            <h2 className={`${styles.sectionHeading} cds--productive-heading-03`}>
              Intake work queue
            </h2>

            <div className={styles.searchRow}>
              <Search
                id="case-search"
                labelText="Search cases"
                placeholder="CASE-2026"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={styles.searchInput}
              />
              <span className={`${styles.caseCount} cds--label-01`}>
                {filteredCases.length} cases found
              </span>
            </div>

            {error && (
              <InlineNotification
                kind="error"
                title="Failed to load cases"
                subtitle={error}
                hideCloseButton
                lowContrast
                className={styles.errorNotification}
              />
            )}

            <CaseListTable cases={filteredCases} isLoading={isLoading} />
          </section>
        </div>

        <p className={`${styles.footer} cds--label-01`}>
          Wireframe 01 of 08 · Covers FR-001, FR-003 · IBM Carbon White theme · Working tier
        </p>
      </main>
    </Theme>
  )
}
