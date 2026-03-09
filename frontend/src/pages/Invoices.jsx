import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Plus, Search, FileText, Printer, Eye, Trash2, XCircle, CheckCircle, DollarSign } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { invoicesApi, authApi } from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/utils";

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  
  // Dialog states
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [actionType, setActionType] = useState(null); // 'delete' or 'cancel'
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState(0);

  useEffect(() => {
    fetchInvoices();
  }, [statusFilter]);

  const fetchInvoices = async () => {
    try {
      const res = await invoicesApi.getAll({
        status: statusFilter || undefined,
      });
      setInvoices(res.data);
    } catch (error) {
      console.error("Error fetching invoices:", error);
    } finally {
      setLoading(false);
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
      case "overdue":
        return <Badge className="bg-red-500 text-white">Overdue</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const handleDeleteOrCancel = (invoice, type) => {
    setSelectedInvoice(invoice);
    setActionType(type);
    setPassword("");
    setPasswordDialogOpen(true);
  };

  const confirmDeleteOrCancel = async () => {
    try {
      // Verify invoice password
      await authApi.verifyInvoicePassword(password);
      
      if (actionType === 'delete') {
        await invoicesApi.delete(selectedInvoice.id, password);
        toast.success("Invoice deleted successfully");
      } else {
        await invoicesApi.cancel(selectedInvoice.id, password);
        toast.success("Invoice cancelled successfully");
      }
      
      setPasswordDialogOpen(false);
      setSelectedInvoice(null);
      setPassword("");
      fetchInvoices();
    } catch (error) {
      toast.error("Invalid password");
    }
  };

  const handleMarkAsPaid = async (invoice) => {
    try {
      await invoicesApi.markPaid(invoice.id);
      toast.success("Invoice marked as paid");
      fetchInvoices();
    } catch (error) {
      toast.error("Failed to update invoice");
    }
  };

  const openPaymentDialog = (invoice) => {
    setSelectedInvoice(invoice);
    setPaymentAmount(invoice.balance_due || invoice.total);
    setPaymentDialogOpen(true);
  };

  const handleAddPayment = async () => {
    if (!paymentAmount || paymentAmount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }
    
    try {
      await invoicesApi.addPayment(selectedInvoice.id, paymentAmount);
      toast.success("Payment recorded successfully");
      setPaymentDialogOpen(false);
      setSelectedInvoice(null);
      fetchInvoices();
    } catch (error) {
      toast.error("Failed to add payment");
    }
  };

  return (
    <div className="space-y-6 fade-in" data-testid="invoices-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
            Invoices
          </h1>
          <p className="text-muted-foreground mt-1">
            View and manage your invoices
          </p>
        </div>
        <Link to="/invoices/create">
          <Button data-testid="create-invoice-btn">
            <Plus className="mr-2 h-4 w-4" />
            Create Invoice
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <Select value={statusFilter || "all"} onValueChange={(val) => setStatusFilter(val === "all" ? "" : val)}>
              <SelectTrigger className="w-48" data-testid="status-filter">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Invoices Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-muted-foreground">Loading...</div>
            </div>
          ) : invoices.length === 0 ? (
            <div className="empty-state">
              <FileText className="h-16 w-16" />
              <h3 className="text-lg font-semibold mt-4">No invoices found</h3>
              <p className="text-sm">Create your first invoice to get started</p>
              <Link to="/invoices/create">
                <Button className="mt-4" data-testid="create-first-invoice-btn">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Invoice
                </Button>
              </Link>
            </div>
          ) : (
            <Table className="data-table">
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice #</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Items</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead className="text-right">Balance</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((invoice) => (
                  <TableRow
                    key={invoice.id}
                    data-testid={`invoice-row-${invoice.id}`}
                    className={invoice.status === 'cancelled' ? 'opacity-50' : ''}
                  >
                    <TableCell className="font-mono font-semibold">
                      {invoice.invoice_number}
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{invoice.customer_name}</p>
                        {invoice.customer_phone && (
                          <p className="text-xs text-muted-foreground">
                            {invoice.customer_phone}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDateTime(invoice.created_at)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {invoice.items?.length || 0} items
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      {formatCurrency(invoice.total)}
                    </TableCell>
                    <TableCell className="text-right">
                      {invoice.balance_due > 0 ? (
                        <span className="text-red-600 font-semibold">
                          {formatCurrency(invoice.balance_due)}
                        </span>
                      ) : (
                        <span className="text-green-600">Paid</span>
                      )}
                    </TableCell>
                    <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" data-testid={`invoice-actions-${invoice.id}`}>
                            ...
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link to={`/invoice/print/${invoice.id}`} target="_blank">
                              <Eye className="mr-2 h-4 w-4" />
                              View Invoice
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <Link to={`/invoice/print/${invoice.id}`} target="_blank">
                              <Printer className="mr-2 h-4 w-4" />
                              Print Invoice
                            </Link>
                          </DropdownMenuItem>
                          
                          {invoice.status !== 'cancelled' && invoice.status !== 'paid' && (
                            <>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem onClick={() => handleMarkAsPaid(invoice)}>
                                <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
                                Mark as Paid
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => openPaymentDialog(invoice)}>
                                <DollarSign className="mr-2 h-4 w-4 text-blue-600" />
                                Add Payment
                              </DropdownMenuItem>
                            </>
                          )}
                          
                          {invoice.status !== 'cancelled' && (
                            <>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="text-orange-600"
                                onClick={() => handleDeleteOrCancel(invoice, 'cancel')}
                              >
                                <XCircle className="mr-2 h-4 w-4" />
                                Cancel Invoice
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="text-destructive"
                                onClick={() => handleDeleteOrCancel(invoice, 'delete')}
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete Invoice
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Password Dialog for Delete/Cancel */}
      <Dialog open={passwordDialogOpen} onOpenChange={setPasswordDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-destructive">
              {actionType === 'delete' ? 'Delete Invoice' : 'Cancel Invoice'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p>
              {actionType === 'delete' 
                ? `Are you sure you want to permanently delete invoice ${selectedInvoice?.invoice_number}? This will restore the stock for all items.`
                : `Are you sure you want to cancel invoice ${selectedInvoice?.invoice_number}? The invoice will be marked as cancelled and stock will be restored.`
              }
            </p>
            <div className="space-y-2">
              <Label>Enter Invoice Password</Label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password..."
                data-testid="invoice-password-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPasswordDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteOrCancel}
              disabled={!password}
              data-testid="confirm-invoice-action-btn"
            >
              {actionType === 'delete' ? 'Delete' : 'Cancel Invoice'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={paymentDialogOpen} onOpenChange={setPaymentDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Payment</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="bg-muted p-4 rounded-lg">
              <div className="flex justify-between text-sm mb-2">
                <span>Invoice Total:</span>
                <span className="font-semibold">{formatCurrency(selectedInvoice?.total || 0)}</span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span>Already Paid:</span>
                <span className="text-green-600">{formatCurrency((selectedInvoice?.amount_paid || 0) + (selectedInvoice?.down_payment || 0))}</span>
              </div>
              <div className="flex justify-between text-lg font-bold border-t pt-2">
                <span>Balance Due:</span>
                <span className="text-red-600">{formatCurrency(selectedInvoice?.balance_due || 0)}</span>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Payment Amount (JMD)</Label>
              <Input
                type="number"
                min="0"
                max={selectedInvoice?.balance_due || 0}
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(parseFloat(e.target.value) || 0)}
                data-testid="payment-amount-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPaymentDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddPayment} data-testid="confirm-payment-btn">
              Record Payment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
