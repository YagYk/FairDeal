import { createBrowserRouter } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { AnalyzePage } from './pages/AnalyzePage';
import { ResultsPage } from './pages/ResultsPage';
import { KBExplorerPage } from './pages/KBExplorerPage';
import { KBContractPage } from './pages/KBContractPage';
import { KBSearchPage } from './pages/KBSearchPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFound } from './pages/NotFound';

export const router = createBrowserRouter([
    {
        path: '/',
        element: <AppShell />,
        children: [
            { index: true, element: <AnalyzePage /> },
            { path: 'results', element: <ResultsPage /> },
            { path: 'kb', element: <KBExplorerPage /> },
            { path: 'kb/contracts/:contractId', element: <KBContractPage /> },
            { path: 'kb/search', element: <KBSearchPage /> },
            { path: 'settings', element: <SettingsPage /> },
            { path: '*', element: <NotFound /> },
        ],
    },
]);
