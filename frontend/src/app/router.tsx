import { createBrowserRouter } from 'react-router';
import { ForgotPasswordPage } from '@/features/auth/ForgotPasswordPage';
import { LoginPage } from '@/features/auth/LoginPage';
import { AccountPage } from '@/features/shared/AccountPage';
import { OwnerHomePage } from '@/features/owner/OwnerHomePage';
import { PropertiesPage } from '@/features/owner/PropertiesPage';
import { PropertyPage } from '@/features/owner/PropertyPage';
import { LeasePage } from '@/features/owner/LeasePage';
import { OwnerInvoicePage } from '@/features/owner/OwnerInvoicePage';
import { TenantHomePage } from '@/features/tenant/TenantHomePage';
import { MyLeasePage } from '@/features/tenant/MyLeasePage';
import { TenantInvoicesPage } from '@/features/tenant/TenantInvoicesPage';
import { TenantInvoicePage } from '@/features/tenant/TenantInvoicePage';
import { TenantIssuesPage } from '@/features/tenant/TenantIssuesPage';
import { NewIssuePage } from '@/features/tenant/NewIssuePage';
import { TenantIssuePage } from '@/features/tenant/TenantIssuePage';
import { APP_ROUTE } from '@/layouts/navigation';
import { IndexRedirect, RoleSpace } from './guards';
import { Root } from './Root';
import { NotFoundPage } from './StatusPages';

export const router = createBrowserRouter(
  [
    {
      element: <Root />,
      children: [
        { index: true, element: <IndexRedirect /> },
        { path: 'connexion', element: <LoginPage /> },
        { path: 'mot-de-passe-oublie', element: <ForgotPasswordPage /> },
        {
          // Landlords, and staff who open the app (mode B): same screens, wider scope.
          path: 'proprietaire',
          element: <RoleSpace space="owner" />,
          children: [
            { index: true, element: <OwnerHomePage /> },
            { path: 'biens', element: <PropertiesPage /> },
            { path: 'biens/:id', element: <PropertyPage /> },
            { path: 'baux/:id', element: <LeasePage /> },
            { path: 'factures/:id', element: <OwnerInvoicePage /> },
            { path: 'compte', element: <AccountPage /> },
          ],
        },
        {
          path: 'locataire',
          element: <RoleSpace space="tenant" />,
          children: [
            { index: true, element: <TenantHomePage /> },
            { path: 'bail', element: <MyLeasePage /> },
            { path: 'bail/:id', element: <MyLeasePage /> },
            { path: 'factures', element: <TenantInvoicesPage /> },
            { path: 'factures/:id', element: <TenantInvoicePage /> },
            { path: 'maintenance', element: <TenantIssuesPage /> },
            { path: 'maintenance/nouvelle', element: <NewIssuePage /> },
            { path: 'maintenance/:id', element: <TenantIssuePage /> },
            { path: 'compte', element: <AccountPage /> },
          ],
        },
        { path: '*', element: <NotFoundPage /> },
      ],
    },
  ],
  { basename: APP_ROUTE },
);
