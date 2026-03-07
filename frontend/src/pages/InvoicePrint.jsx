import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui/button";
import { invoicesApi, settingsApi } from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/utils";

export default function InvoicePrint() {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [invoiceRes, settingsRes] = await Promise.all([
        invoicesApi.getById(id),
        settingsApi.get(),
      ]);
      setInvoice(invoiceRes.data);
      setSettings(settingsRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-muted-foreground">Invoice not found</div>
      </div>
    );
  }

  const company = settings?.company || {};
  const policies = settings?.policies || {};

  return (
    <div className="min-h-screen bg-gray-100 py-8 print:bg-white print:py-0">
      {/* Print Button */}
      <div className="no-print fixed top-4 right-4 z-50">
        <Button onClick={handlePrint} data-testid="print-btn">
          <Printer className="mr-2 h-4 w-4" />
          Print Invoice
        </Button>
      </div>

      {/* Invoice Container */}
      <div
        className="invoice-container bg-white max-w-[800px] mx-auto shadow-lg print:shadow-none"
        data-testid="invoice-print-container"
      >
        {/* Header */}
        <div className="p-6 border-b-2 border-red-600">
          <div className="flex justify-between items-start">
            {/* Logo & Company Info */}
            <div className="flex items-start gap-4">
              {company.logo_url && (
                <img
                  src={company.logo_url}
                  alt={company.company_name}
                  className="w-24 h-24 object-contain"
                />
              )}
              <div>
                <h1 className="text-xl font-bold uppercase tracking-tight font-['Barlow_Condensed']">
                  {company.company_name || "Timeless Parts and Accessories"}
                </h1>
                <p className="text-xs text-slate-600 mt-1">
                  {company.address || "Lot 36 Bustamante Highway, May Pen, Clarendon"}
                </p>
                <p className="text-xs text-slate-600">
                  Tel: {company.phone || "876-403-8436"}
                </p>
                <p className="text-xs text-slate-600">
                  Email: {company.email || "timelessautoimportslimited@gmail.com"}
                </p>
              </div>
            </div>

            {/* Invoice Details */}
            <div className="text-right">
              <h2 className="text-2xl font-bold uppercase tracking-tight font-['Barlow_Condensed']">
                PARTS INVOICE
              </h2>
              <p className="text-xs text-slate-500 mt-2">CUSTOMER COPY</p>
            </div>
          </div>
        </div>

        {/* Invoice Info Grid */}
        <div className="p-6 grid grid-cols-2 gap-6 border-b">
          {/* Left - Customer */}
          <div>
            <div className="bg-slate-50 p-4 rounded">
              <table className="w-full text-sm">
                <tbody>
                  <tr>
                    <td className="font-semibold text-slate-600 py-1 w-28">
                      Invoice #
                    </td>
                    <td className="font-mono font-bold">
                      {invoice.invoice_number}
                    </td>
                  </tr>
                  <tr>
                    <td className="font-semibold text-slate-600 py-1">Date</td>
                    <td>{formatDateTime(invoice.created_at)}</td>
                  </tr>
                  <tr>
                    <td className="font-semibold text-slate-600 py-1">User</td>
                    <td>{invoice.user || "Admin"}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Right - Ship To */}
          <div>
            <div className="bg-slate-50 p-4 rounded">
              <p className="text-xs font-semibold text-slate-500 mb-2">BILL TO</p>
              <p className="font-bold text-lg">{invoice.customer_name}</p>
              {invoice.customer_address && (
                <p className="text-sm text-slate-600">{invoice.customer_address}</p>
              )}
              {invoice.customer_phone && (
                <p className="text-sm text-slate-600 mt-1">
                  Tel: {invoice.customer_phone}
                </p>
              )}
              <div className="mt-2 pt-2 border-t">
                <span className="text-xs text-slate-500">Payment: </span>
                <span className="text-sm font-medium">
                  {invoice.payment_method}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Items Table */}
        <div className="p-6">
          <table className="invoice-table">
            <thead>
              <tr>
                <th className="text-left">QTY</th>
                <th className="text-left">PART NUMBER</th>
                <th className="text-left">DESCRIPTION</th>
                <th className="text-right">UNIT PRICE</th>
                <th className="text-right">TOTAL</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items?.map((item, index) => (
                <tr key={index}>
                  <td>{item.quantity}</td>
                  <td className="font-mono text-xs">{item.part_number}</td>
                  <td>{item.name}</td>
                  <td className="text-right">{formatCurrency(item.unit_price)}</td>
                  <td className="text-right font-semibold">
                    {formatCurrency(item.total)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals & Payment */}
        <div className="px-6 pb-6">
          <div className="flex justify-between items-start">
            {/* Payment Status */}
            <div>
              {invoice.status === "paid" && (
                <div className="paid-stamp">PAID</div>
              )}
            </div>

            {/* Totals */}
            <div className="invoice-totals-table">
              <table className="w-full">
                <tbody>
                  <tr>
                    <td className="text-right text-slate-600">PARTS SALE</td>
                    <td className="text-right font-semibold">
                      {formatCurrency(invoice.subtotal)}
                    </td>
                  </tr>
                  {invoice.discount > 0 && (
                    <tr>
                      <td className="text-right text-slate-600">
                        Discount
                        {invoice.discount_percentage > 0 &&
                          ` (${invoice.discount_percentage}%)`}
                      </td>
                      <td className="text-right text-destructive">
                        ({formatCurrency(invoice.discount)})
                      </td>
                    </tr>
                  )}
                  <tr>
                    <td className="text-right text-slate-600">TOTAL PARTS SALES</td>
                    <td className="text-right font-semibold">
                      {formatCurrency(invoice.subtotal - invoice.discount)}
                    </td>
                  </tr>
                  <tr>
                    <td className="text-right text-slate-600">
                      {company.tax_name || "GCT"} ({invoice.tax_rate || 15}%)
                    </td>
                    <td className="text-right">
                      {formatCurrency(invoice.tax_amount)}
                    </td>
                  </tr>
                  <tr className="total-row">
                    <td className="text-right font-bold">TOTAL INVOICE</td>
                    <td className="text-right font-bold text-lg">
                      {formatCurrency(invoice.total)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Notes */}
        {invoice.notes && (
          <div className="px-6 pb-4">
            <p className="text-xs text-slate-500">Notes:</p>
            <p className="text-sm">{invoice.notes}</p>
          </div>
        )}

        {/* Policies Section */}
        <div className="policies-section px-6 pb-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Sales Return Policy */}
            <div>
              <h4>SALES RETURN POLICY</h4>
              <ol>
                {(policies.sales_return_policy || []).map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ol>
            </div>

            {/* Privacy Policy */}
            <div>
              <h4>PRIVACY POLICY</h4>
              <ol>
                {(policies.privacy_policy || []).slice(0, 3).map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ol>
            </div>
          </div>

          {/* Signature Line */}
          <div className="mt-6 pt-4 border-t">
            <div className="flex justify-between items-end">
              <div>
                <p className="text-xs text-slate-500 mb-8">Customer Signature</p>
                <div className="w-48 border-b border-slate-400"></div>
              </div>
              <div className="text-right text-xs text-slate-500">
                <p>{company.tax_name || "GCT"} # 000-000-000</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
