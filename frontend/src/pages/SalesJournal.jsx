import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  Calendar, 
  Check, 
  CheckCircle2, 
  Circle, 
  DollarSign, 
  FileText, 
  Package, 
  Printer,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { salesJournalApi } from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/utils";

export default function SalesJournal() {
  const [journalData, setJournalData] = useState(null);
  const [availableDates, setAvailableDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAvailableDates();
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchJournalData();
    }
  }, [selectedDate]);

  const fetchAvailableDates = async () => {
    try {
      const res = await salesJournalApi.getDates(60);
      setAvailableDates(res.data);
    } catch (error) {
      console.error("Error fetching dates:", error);
    }
  };

  const fetchJournalData = async () => {
    setLoading(true);
    try {
      const res = await salesJournalApi.getJournal(selectedDate);
      setJournalData(res.data);
    } catch (error) {
      console.error("Error fetching journal:", error);
      toast.error("Failed to load sales journal");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCheckOff = async (invoiceId) => {
    try {
      await salesJournalApi.toggleCheckOff(invoiceId);
      fetchJournalData();
    } catch (error) {
      toast.error("Failed to update check-off status");
    }
  };

  const navigateDate = (direction) => {
    const currentIndex = availableDates.findIndex(d => d.date === selectedDate);
    if (direction === 'prev' && currentIndex < availableDates.length - 1) {
      setSelectedDate(availableDates[currentIndex + 1].date);
    } else if (direction === 'next' && currentIndex > 0) {
      setSelectedDate(availableDates[currentIndex - 1].date);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "paid":
        return <Badge className="bg-green-500 text-white">Paid</Badge>;
      case "pending":
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case "cancelled":
        return <Badge variant="destructive">Cancelled</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 fade-in" data-testid="sales-journal-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
            Sales Journal
          </h1>
          <p className="text-muted-foreground mt-1">
            Daily transaction summary and check-off
          </p>
        </div>
        <Button variant="outline" onClick={handlePrint} className="no-print" data-testid="print-journal-btn">
          <Printer className="mr-2 h-4 w-4" />
          Print Journal
        </Button>
      </div>

      {/* Date Selector */}
      <Card className="no-print">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => navigateDate('prev')}
              disabled={availableDates.findIndex(d => d.date === selectedDate) >= availableDates.length - 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            
            <Select value={selectedDate} onValueChange={setSelectedDate}>
              <SelectTrigger className="w-64" data-testid="date-selector">
                <Calendar className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Select date" />
              </SelectTrigger>
              <SelectContent>
                {availableDates.map((dateInfo) => (
                  <SelectItem key={dateInfo.date} value={dateInfo.date}>
                    {dateInfo.date} ({dateInfo.invoice_count} invoices)
                  </SelectItem>
                ))}
                {!availableDates.find(d => d.date === selectedDate) && (
                  <SelectItem value={selectedDate}>{selectedDate}</SelectItem>
                )}
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => navigateDate('next')}
              disabled={availableDates.findIndex(d => d.date === selectedDate) <= 0}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>

            <Button
              variant="outline"
              onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
            >
              Today
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading...</div>
        </div>
      ) : journalData ? (
        <>
          {/* Date Header for Print */}
          <div className="print-only text-center mb-4">
            <h2 className="text-2xl font-bold">{formatDate(selectedDate)}</h2>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Total Invoices</p>
                </div>
                <p className="text-2xl font-bold mt-1">{journalData.summary.total_invoices}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Total Sales</p>
                </div>
                <p className="text-2xl font-bold mt-1">{formatCurrency(journalData.summary.total_sales)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <p className="text-xs text-muted-foreground">Total Paid</p>
                </div>
                <p className="text-2xl font-bold mt-1 text-green-600">{formatCurrency(journalData.summary.total_paid)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Circle className="h-4 w-4 text-yellow-500" />
                  <p className="text-xs text-muted-foreground">Pending</p>
                </div>
                <p className="text-2xl font-bold mt-1 text-yellow-600">{formatCurrency(journalData.summary.total_pending)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Package className="h-4 w-4 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">Items Sold</p>
                </div>
                <p className="text-2xl font-bold mt-1">{journalData.summary.total_items_sold}</p>
              </CardContent>
            </Card>
          </div>

          {/* Check-off Progress */}
          <Card className="no-print">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Check-off Progress</p>
                  <p className="text-lg font-semibold">
                    {journalData.summary.checked_off_count} of {journalData.summary.total_invoices} checked off
                  </p>
                </div>
                <div className="w-48 bg-muted rounded-full h-3">
                  <div 
                    className="bg-green-500 h-3 rounded-full transition-all"
                    style={{ 
                      width: `${journalData.summary.total_invoices > 0 
                        ? (journalData.summary.checked_off_count / journalData.summary.total_invoices) * 100 
                        : 0}%` 
                    }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Transactions Table */}
          <Card>
            <CardHeader>
              <CardTitle className="font-['Barlow_Condensed'] text-2xl uppercase">
                Transactions - {formatDate(selectedDate)}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {journalData.invoices.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">No transactions for this date</p>
                </div>
              ) : (
                <Table className="data-table">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12 no-print">Check</TableHead>
                      <TableHead>Invoice #</TableHead>
                      <TableHead>Time</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Items Purchased</TableHead>
                      <TableHead className="text-right">Total</TableHead>
                      <TableHead className="text-right">Paid</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {journalData.invoices.map((invoice) => (
                      <TableRow
                        key={invoice.id}
                        data-testid={`journal-invoice-${invoice.id}`}
                        className={invoice.checked_off ? 'bg-green-50' : ''}
                      >
                        <TableCell className="no-print">
                          <button
                            onClick={() => handleToggleCheckOff(invoice.id)}
                            className="p-1 hover:bg-muted rounded"
                            data-testid={`check-off-${invoice.id}`}
                          >
                            {invoice.checked_off ? (
                              <CheckCircle2 className="h-5 w-5 text-green-500" />
                            ) : (
                              <Circle className="h-5 w-5 text-muted-foreground" />
                            )}
                          </button>
                        </TableCell>
                        <TableCell className="font-mono font-semibold">
                          <Link 
                            to={`/invoice/print/${invoice.id}`} 
                            target="_blank"
                            className="hover:underline text-primary"
                          >
                            {invoice.invoice_number}
                          </Link>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {new Date(invoice.created_at).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </TableCell>
                        <TableCell>
                          <p className="font-medium">{invoice.customer_name}</p>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            {invoice.items?.slice(0, 3).map((item, idx) => (
                              <div key={idx} className="text-xs text-muted-foreground">
                                {item.quantity}x {item.name}
                              </div>
                            ))}
                            {invoice.items?.length > 3 && (
                              <div className="text-xs text-muted-foreground">
                                +{invoice.items.length - 3} more items
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {formatCurrency(invoice.total)}
                        </TableCell>
                        <TableCell className="text-right">
                          <span className={invoice.status === 'paid' ? 'text-green-600' : 'text-muted-foreground'}>
                            {formatCurrency((invoice.amount_paid || 0) + (invoice.down_payment || 0))}
                          </span>
                        </TableCell>
                        <TableCell>
                          {getStatusBadge(invoice.status)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Print Summary */}
          <div className="print-only mt-8 pt-4 border-t">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="font-semibold">Total Invoices: {journalData.summary.total_invoices}</p>
                <p className="font-semibold">Items Sold: {journalData.summary.total_items_sold}</p>
              </div>
              <div>
                <p className="font-semibold">Total Sales: {formatCurrency(journalData.summary.total_sales)}</p>
                <p className="font-semibold text-green-600">Total Paid: {formatCurrency(journalData.summary.total_paid)}</p>
              </div>
              <div>
                <p className="font-semibold text-yellow-600">Pending: {formatCurrency(journalData.summary.total_pending)}</p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <p>Select a date to view the sales journal</p>
        </div>
      )}
    </div>
  );
}
