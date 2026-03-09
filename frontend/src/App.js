import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { PasswordProvider } from "@/contexts/PasswordContext";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Inventory from "@/pages/Inventory";
import Customers from "@/pages/Customers";
import Invoices from "@/pages/Invoices";
import CreateInvoice from "@/pages/CreateInvoice";
import InvoicePrint from "@/pages/InvoicePrint";
import Reports from "@/pages/Reports";
import Settings from "@/pages/Settings";
import SalesJournal from "@/pages/SalesJournal";
import "@/App.css";

function App() {
  return (
    <div className="App">
      <PasswordProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/invoice/print/:id" element={<InvoicePrint />} />
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/invoices" element={<Invoices />} />
              <Route path="/invoices/create" element={<CreateInvoice />} />
              <Route path="/sales-journal" element={<SalesJournal />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" richColors />
      </PasswordProvider>
    </div>
  );
}

export default App;
