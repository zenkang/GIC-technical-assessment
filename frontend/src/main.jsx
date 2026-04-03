import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ModuleRegistry, ClientSideRowModelModule } from "ag-grid-community";

import App from "./App";
import CafesPage from "./pages/CafesPage";
import EmployeesPage from "./pages/EmployeesPage";
import AddEditCafePage from "./pages/AddEditCafePage";
import AddEditEmployeePage from "./pages/AddEditEmployeePage";

// AG Grid v32+ requires explicit module registration before any <AgGridReact> renders
ModuleRegistry.registerModules([ClientSideRowModelModule]);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
});

// createBrowserRouter (data router) is required for useBlocker to work in form pages
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <CafesPage /> },
      { path: "cafes/add", element: <AddEditCafePage /> },
      { path: "cafes/edit/:id", element: <AddEditCafePage /> },
      { path: "employees", element: <EmployeesPage /> },
      { path: "employees/add", element: <AddEditEmployeePage /> },
      { path: "employees/edit/:id", element: <AddEditEmployeePage /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);
