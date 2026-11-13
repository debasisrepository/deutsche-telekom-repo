import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './lib/auth-context';
import { RequireAuth } from './components/auth/RequireAuth';
import { Layout } from './components/layout/Layout';
import { LoginPage } from './pages/LoginPage';
import { Dashboard } from './pages/Dashboard';
import { NeedsPage } from './pages/NeedsPage';
import { ReviewsPage } from './pages/ReviewsPage';
import { DispatchPage } from './pages/DispatchPage';
import { NeedIntakePage } from './pages/NeedIntakePage';
import { AttributeReviewPage } from './pages/AttributeReviewPage';
import { ClassificationReviewPage } from './pages/ClassificationReviewPage';
import { VmsHandoffPage } from './pages/VmsHandoffPage';
import { VmsHandoffListPage } from './pages/VmsHandoffListPage';
import { EvidenceListPage } from './pages/EvidenceListPage';
import { EvidenceAndPanelPage } from './pages/EvidenceAndPanelPage';
import { ResearchListPage } from './pages/ResearchListPage';
import { ResearchAndProposalPage } from './pages/ResearchAndProposalPage';
import { ValidationListPage } from './pages/ValidationListPage';
import { ValidationAndAdjustmentPage } from './pages/ValidationAndAdjustmentPage';
import { LockDispatchListPage } from './pages/LockDispatchListPage';
import { LockAndDispatchPage } from './pages/LockAndDispatchPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <Layout>
                  <Dashboard />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/needs"
            element={
              <RequireAuth>
                <Layout>
                  <NeedsPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/intake"
            element={
              <RequireAuth>
                <Layout>
                  <NeedIntakePage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/reviews"
            element={
              <RequireAuth>
                <Layout>
                  <ReviewsPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/reviews/:needId/attributes"
            element={
              <RequireAuth>
                <Layout>
                  <AttributeReviewPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/reviews/:needId/classification"
            element={
              <RequireAuth>
                <Layout>
                  <ClassificationReviewPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/evidence"
            element={
              <RequireAuth>
                <Layout>
                  <EvidenceListPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/evidence/:needId"
            element={
              <RequireAuth>
                <Layout>
                  <EvidenceAndPanelPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/research"
            element={
              <RequireAuth>
                <Layout>
                  <ResearchListPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/research/:needId"
            element={
              <RequireAuth>
                <Layout>
                  <ResearchAndProposalPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/vms-handoff"
            element={
              <RequireAuth>
                <Layout>
                  <VmsHandoffListPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/vms-handoff/:needId"
            element={
              <RequireAuth>
                <Layout>
                  <VmsHandoffPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/validation"
            element={
              <RequireAuth>
                <Layout>
                  <ValidationListPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/validation/:longlistId"
            element={
              <RequireAuth>
                <Layout>
                  <ValidationAndAdjustmentPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/lock-dispatch"
            element={
              <RequireAuth>
                <Layout>
                  <LockDispatchListPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/lock-dispatch/:longlistId"
            element={
              <RequireAuth>
                <Layout>
                  <LockAndDispatchPage />
                </Layout>
              </RequireAuth>
            }
          />
          <Route
            path="/dispatch"
            element={
              <RequireAuth>
                <Layout>
                  <DispatchPage />
                </Layout>
              </RequireAuth>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
