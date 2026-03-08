import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Plus,
  Minus,
  Trash2,
  Search,
  User,
  Package,
  Calculator,
  Star,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { partsApi, customersApi, invoicesApi, settingsApi } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function CreateInvoice() {
  const navigate = useNavigate();
  const [parts, setParts] = useState([]);
  const [frequentParts, setFrequentParts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  const [customerSearch, setCustomerSearch] = useState("");
  const [partSearch, setPartSearch] = useState("");
  const [partDialogOpen, setPartDialogOpen] = useState(false);

  const [invoiceData, setInvoiceData] = useState({
    customer_id: "",
    customer_name: "",
    customer_phone: "",
    customer_address: "",
    items: [],
    discount: 0,
    discount_percentage: 0,
    payment_method: "Cash",
    notes: "",
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [partsRes, customersRes, settingsRes, frequentRes] = await Promise.all([
        partsApi.getAll({}),
        customersApi.getAll({}),
        settingsApi.get(),
        partsApi.getFrequentlyUsed(6),
      ]);
      setParts(partsRes.data);
      setCustomers(customersRes.data);
      setSettings(settingsRes.data);
      setFrequentParts(frequentRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const selectCustomer = (customer) => {
    setInvoiceData({
      ...invoiceData,
      customer_id: customer.id,
      customer_name: customer.name,
      customer_phone: customer.phone || "",
      customer_address: customer.address || "",
    });
    setCustomerSearch("");
  };

  const addPart = (part) => {
    const existingIndex = invoiceData.items.findIndex(
      (item) => item.part_id === part.id
    );

    if (existingIndex >= 0) {
      const updated = [...invoiceData.items];
      if (updated[existingIndex].quantity < part.quantity) {
        updated[existingIndex].quantity += 1;
        updated[existingIndex].total =
          updated[existingIndex].quantity * updated[existingIndex].unit_price;
        setInvoiceData({ ...invoiceData, items: updated });
      } else {
        toast.error("Not enough stock available");
      }
    } else {
      if (part.quantity < 1) {
        toast.error("Part is out of stock");
        return;
      }
      const newItem = {
        part_id: part.id,
        part_number: part.part_number,
        name: part.name,
        quantity: 1,
        unit_price: part.price,
        total: part.price,
        max_quantity: part.quantity,
      };
      setInvoiceData({ ...invoiceData, items: [...invoiceData.items, newItem] });
    }
    setPartDialogOpen(false);
    setPartSearch("");
  };

  const updateItemQuantity = (index, delta) => {
    const updated = [...invoiceData.items];
    const newQty = updated[index].quantity + delta;

    if (newQty < 1) {
      removeItem(index);
      return;
    }

    if (newQty > updated[index].max_quantity) {
      toast.error("Not enough stock available");
      return;
    }

    updated[index].quantity = newQty;
    updated[index].total = newQty * updated[index].unit_price;
    setInvoiceData({ ...invoiceData, items: updated });
  };

  const removeItem = (index) => {
    const updated = invoiceData.items.filter((_, i) => i !== index);
    setInvoiceData({ ...invoiceData, items: updated });
  };

  const calculateSubtotal = () => {
    return invoiceData.items.reduce((sum, item) => sum + item.total, 0);
  };

  const calculateDiscount = () => {
    const subtotal = calculateSubtotal();
    if (invoiceData.discount_percentage > 0) {
      return (subtotal * invoiceData.discount_percentage) / 100;
    }
    return invoiceData.discount;
  };

  const calculateTax = () => {
    const subtotal = calculateSubtotal();
    const discount = calculateDiscount();
    const taxRate = settings?.company?.tax_rate || 15;
    return ((subtotal - discount) * taxRate) / 100;
  };

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const discount = calculateDiscount();
    const tax = calculateTax();
    return subtotal - discount + tax;
  };

  const handleSubmit = async () => {
    if (!invoiceData.customer_name) {
      toast.error("Please enter customer name");
      return;
    }

    if (invoiceData.items.length === 0) {
      toast.error("Please add at least one item");
      return;
    }

    const subtotal = calculateSubtotal();
    const discount = calculateDiscount();
    const taxAmount = calculateTax();
    const total = calculateTotal();

    const payload = {
      customer_id: invoiceData.customer_id || null,
      customer_name: invoiceData.customer_name,
      customer_phone: invoiceData.customer_phone || null,
      customer_address: invoiceData.customer_address || null,
      items: invoiceData.items.map((item) => ({
        part_id: item.part_id,
        part_number: item.part_number,
        name: item.name,
        quantity: item.quantity,
        unit_price: item.unit_price,
        total: item.total,
      })),
      subtotal,
      discount,
      discount_percentage: invoiceData.discount_percentage,
      tax_rate: settings?.company?.tax_rate || 15,
      tax_amount: taxAmount,
      total,
      payment_method: invoiceData.payment_method,
      notes: invoiceData.notes || null,
      status: "paid",
    };

    try {
      const res = await invoicesApi.create(payload);
      toast.success(`Invoice ${res.data.invoice_number} created!`);
      // Open print view
      window.open(`/invoice/print/${res.data.id}`, "_blank");
      navigate("/invoices");
    } catch (error) {
      console.error("Error creating invoice:", error);
      toast.error("Failed to create invoice");
    }
  };

  const filteredParts = parts.filter(
    (p) =>
      p.name.toLowerCase().includes(partSearch.toLowerCase()) ||
      p.part_number.toLowerCase().includes(partSearch.toLowerCase())
  );

  const filteredCustomers = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(customerSearch.toLowerCase()) ||
      (c.phone && c.phone.includes(customerSearch))
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6 fade-in" data-testid="create-invoice-page">
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
          Create Invoice
        </h1>
        <p className="text-muted-foreground text-sm md:text-base mt-1">
          Create a new invoice for a customer
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Left Column - Customer & Items */}
        <div className="lg:col-span-2 space-y-4 md:space-y-6">
          {/* Customer Selection */}
          <Card>
            <CardHeader className="p-4 md:p-6">
              <CardTitle className="flex items-center gap-2 text-base md:text-lg">
                <User className="h-4 w-4 md:h-5 md:w-5" />
                Customer Information
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0 md:p-6 md:pt-0 space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search existing customer..."
                  value={customerSearch}
                  onChange={(e) => setCustomerSearch(e.target.value)}
                  className="pl-10"
                  data-testid="customer-search"
                />
                {customerSearch && filteredCustomers.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-card border rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {filteredCustomers.map((customer) => (
                      <button
                        key={customer.id}
                        className="w-full px-4 py-2 text-left hover:bg-muted flex justify-between items-center"
                        onClick={() => selectCustomer(customer)}
                        data-testid={`select-customer-${customer.id}`}
                      >
                        <span className="font-medium">{customer.name}</span>
                        <span className="text-sm text-muted-foreground">
                          {customer.phone}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Customer Name *</Label>
                  <Input
                    value={invoiceData.customer_name}
                    onChange={(e) =>
                      setInvoiceData({
                        ...invoiceData,
                        customer_name: e.target.value,
                      })
                    }
                    data-testid="invoice-customer-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Phone</Label>
                  <Input
                    value={invoiceData.customer_phone}
                    onChange={(e) =>
                      setInvoiceData({
                        ...invoiceData,
                        customer_phone: e.target.value,
                      })
                    }
                    data-testid="invoice-customer-phone"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Address</Label>
                <Textarea
                  value={invoiceData.customer_address}
                  onChange={(e) =>
                    setInvoiceData({
                      ...invoiceData,
                      customer_address: e.target.value,
                    })
                  }
                  rows={2}
                  data-testid="invoice-customer-address"
                />
              </div>
            </CardContent>
          </Card>

          {/* Frequently Used Parts - Quick Add */}
          {frequentParts.length > 0 && (
            <Card className="border-dashed border-2 bg-muted/30">
              <CardHeader className="pb-3 p-4 md:p-6 md:pb-3">
                <CardTitle className="flex items-center gap-2 text-base md:text-lg">
                  <Zap className="h-4 w-4 md:h-5 md:w-5 text-amber-500" />
                  Quick Add
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0 md:p-6 md:pt-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 md:gap-3">
                  {frequentParts.map((part) => (
                    <button
                      key={part.id}
                      onClick={() => addPart(part)}
                      disabled={part.quantity < 1}
                      className="flex items-center gap-2 md:gap-3 p-2 md:p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed"
                      data-testid={`quick-add-${part.id}`}
                    >
                      {part.image_url ? (
                        <img
                          src={part.image_url}
                          alt={part.name}
                          className="w-8 h-8 md:w-10 md:h-10 object-cover rounded"
                        />
                      ) : (
                        <div className="w-8 h-8 md:w-10 md:h-10 bg-muted rounded flex items-center justify-center flex-shrink-0">
                          <Package className="h-4 w-4 md:h-5 md:w-5 text-muted-foreground" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-xs md:text-sm truncate">{part.name}</p>
                        <p className="text-xs md:text-sm font-semibold text-primary">
                          {formatCurrency(part.price)}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Items */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between p-4 md:p-6">
              <CardTitle className="flex items-center gap-2 text-base md:text-lg">
                <Package className="h-4 w-4 md:h-5 md:w-5" />
                Invoice Items
              </CardTitle>
              <Button
                size="sm"
                onClick={() => setPartDialogOpen(true)}
                data-testid="add-item-btn"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Part
              </Button>
            </CardHeader>
            <CardContent>
              {invoiceData.items.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No items added yet</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => setPartDialogOpen(true)}
                  >
                    Add your first item
                  </Button>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Part</TableHead>
                      <TableHead className="text-center">Qty</TableHead>
                      <TableHead className="text-right">Unit Price</TableHead>
                      <TableHead className="text-right">Total</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {invoiceData.items.map((item, index) => (
                      <TableRow key={index} data-testid={`invoice-item-${index}`}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{item.name}</p>
                            <p className="text-xs text-muted-foreground font-mono">
                              {item.part_number}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center justify-center gap-2">
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => updateItemQuantity(index, -1)}
                              data-testid={`decrease-qty-${index}`}
                            >
                              <Minus className="h-4 w-4" />
                            </Button>
                            <span className="w-8 text-center font-medium">
                              {item.quantity}
                            </span>
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() => updateItemQuantity(index, 1)}
                              data-testid={`increase-qty-${index}`}
                            >
                              <Plus className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(item.unit_price)}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {formatCurrency(item.total)}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-destructive"
                            onClick={() => removeItem(index)}
                            data-testid={`remove-item-${index}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Invoice Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Payment Method</Label>
                <Select
                  value={invoiceData.payment_method}
                  onValueChange={(value) =>
                    setInvoiceData({ ...invoiceData, payment_method: value })
                  }
                >
                  <SelectTrigger data-testid="payment-method">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Cash">Cash</SelectItem>
                    <SelectItem value="Card">Card</SelectItem>
                    <SelectItem value="Bank Transfer">Bank Transfer</SelectItem>
                    <SelectItem value="Credit">Credit</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Discount (%)</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={invoiceData.discount_percentage}
                  onChange={(e) =>
                    setInvoiceData({
                      ...invoiceData,
                      discount_percentage: parseFloat(e.target.value) || 0,
                      discount: 0,
                    })
                  }
                  data-testid="discount-percentage"
                />
              </div>

              <div className="space-y-2">
                <Label>Or Fixed Discount (JMD)</Label>
                <Input
                  type="number"
                  min="0"
                  value={invoiceData.discount}
                  onChange={(e) =>
                    setInvoiceData({
                      ...invoiceData,
                      discount: parseFloat(e.target.value) || 0,
                      discount_percentage: 0,
                    })
                  }
                  data-testid="discount-fixed"
                />
              </div>

              <div className="space-y-2">
                <Label>Notes</Label>
                <Textarea
                  value={invoiceData.notes}
                  onChange={(e) =>
                    setInvoiceData({ ...invoiceData, notes: e.target.value })
                  }
                  rows={2}
                  placeholder="Optional notes..."
                  data-testid="invoice-notes"
                />
              </div>

              <div className="border-t pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Subtotal</span>
                  <span>{formatCurrency(calculateSubtotal())}</span>
                </div>
                {calculateDiscount() > 0 && (
                  <div className="flex justify-between text-sm text-destructive">
                    <span>Discount</span>
                    <span>-{formatCurrency(calculateDiscount())}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span>
                    {settings?.company?.tax_name || "GCT"} (
                    {settings?.company?.tax_rate || 15}%)
                  </span>
                  <span>{formatCurrency(calculateTax())}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Total</span>
                  <span>{formatCurrency(calculateTotal())}</span>
                </div>
              </div>

              <Button
                className="w-full"
                size="lg"
                onClick={handleSubmit}
                disabled={
                  !invoiceData.customer_name || invoiceData.items.length === 0
                }
                data-testid="create-invoice-submit"
              >
                Create Invoice
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Part Selection Dialog */}
      <Dialog open={partDialogOpen} onOpenChange={setPartDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Select Part</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search parts..."
                value={partSearch}
                onChange={(e) => setPartSearch(e.target.value)}
                className="pl-10"
                data-testid="part-search"
              />
            </div>
            <div className="max-h-96 overflow-y-auto">
              {filteredParts.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No parts found
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredParts.map((part) => (
                    <button
                      key={part.id}
                      className="w-full p-3 text-left border rounded-lg hover:bg-muted flex justify-between items-center disabled:opacity-50"
                      onClick={() => addPart(part)}
                      disabled={part.quantity < 1}
                      data-testid={`select-part-${part.id}`}
                    >
                      <div className="flex items-center gap-3">
                        {part.image_url ? (
                          <img
                            src={part.image_url}
                            alt={part.name}
                            className="w-12 h-12 object-cover rounded"
                          />
                        ) : (
                          <div className="w-12 h-12 bg-muted rounded flex items-center justify-center">
                            <Package className="h-6 w-6 text-muted-foreground" />
                          </div>
                        )}
                        <div>
                          <p className="font-medium">{part.name}</p>
                          <p className="text-xs text-muted-foreground font-mono">
                            {part.part_number}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">
                          {formatCurrency(part.price)}
                        </p>
                        <p
                          className={`text-xs ${
                            part.quantity < 1
                              ? "text-destructive"
                              : "text-muted-foreground"
                          }`}
                        >
                          {part.quantity} in stock
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
