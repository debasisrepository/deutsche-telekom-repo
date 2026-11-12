import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './lib/auth-context'
import { RequireAuth } from './components/auth/RequireAuth'
import { LoginPage } from './components/auth/LoginPage'
import { Layout } from './components/layout/Layout'
import { IntakeQueuePage } from './pages/IntakeQueuePage'
import { CasesListPage } from './pages/CasesListPage'
import { CaseOverviewPage } from './pages/CaseOverviewPage'
import { ExtractionReviewPage } from './pages/ExtractionReviewPage'
import { ClassificationReviewPage } from './pages/ClassificationReviewPage'
import { VmsRoutingPage } from './pages/VmsRoutingPage'
import { EvidenceMappingPage } from './pages/EvidenceMappingPage'
import { LonglistAdjustmentsPage } from './pages/LonglistAdjustmentsPage'
import { LockDispatchPage } from './pages/LockDispatchPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <Layout>
                  <IntakeQueuePage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases"
            element={
              <RequireAuth>
                <Layout>
                  <CasesListPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId"
            element={
              <RequireAuth>
                <Layout>
                  <CaseOverviewPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/extraction-review"
            element={
              <RequireAuth>
                <Layout>
                  <ExtractionReviewPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/classification-review"
            element={
              <RequireAuth>
                <Layout>
                  <ClassificationReviewPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/vms-routing"
            element={
              <RequireAuth>
                <Layout>
                  <VmsRoutingPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/evidence-mapping"
            element={
              <RequireAuth>
                <Layout>
                  <EvidenceMappingPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/longlist-adjustments"
            element={
              <RequireAuth>
                <Layout>
                  <LonglistAdjustmentsPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/lock-dispatch"
            element={
              <RequireAuth>
                <Layout>
                  <LockDispatchPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
