import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { JobsPage } from './pages/JobsPage'
import { JobDetailPage } from './pages/JobDetailPage'
import { InterviewPage } from './pages/InterviewPage'
import { ReportPage } from './pages/ReportPage'
import { LoginPage } from './pages/LoginPage'
import { CandidatePortalPage } from './pages/CandidatePortalPage'

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<LoginPage role="recruiter" redirectTo="/" />} />
        <Route path="/apply/login" element={<LoginPage role="candidate" redirectTo="/apply" />} />

        <Route element={<ProtectedRoute role="recruiter" />}>
          <Route path="/" element={<JobsPage />} />
          <Route path="/jobs/:jobId" element={<JobDetailPage />} />
          <Route path="/interviews/:interviewId/report" element={<ReportPage />} />
        </Route>

        <Route element={<ProtectedRoute role="candidate" />}>
          <Route path="/apply" element={<CandidatePortalPage />} />
          <Route path="/candidates/:candidateId/interview" element={<InterviewPage />} />
        </Route>
      </Route>
    </Routes>
  )
}
