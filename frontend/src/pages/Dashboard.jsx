import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Package,
  Users,
  FileText,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  ArrowRight,
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
import { dashboardApi } from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/utils";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [lowStock, setLowStock] = useState([]);
  const [recentInvoices, setRecentInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, lowStockRes, invoicesRes] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getLowStock(),
        dashboardApi.getRecentInvoices(5),
      ]);
      setStats(statsRes.data);
      setLowStock(lowStockRes.data);
      setRecentInvoices(invoicesRes.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6 fade-in" data-testid="dashboard">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
            Dashboard
          </h1>
          <p className="text-muted-foreground text-sm md:text-base mt-1">
            Welcome to Timeless Parts & Accessories
          </p>
        </div>
        <Link to="/invoices/create" className="w-full sm:w-auto">
          <Button className="w-full sm:w-auto" data-testid="dashboard-new-invoice-btn">
            <FileText className="mr-2 h-4 w-4" />
            New Invoice
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <Card className="stat-card" data-testid="stat-inventory-value">
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 md:p-6 md:pb-2">
            <CardTitle className="text-xs md:text-sm font-medium text-muted-foreground">
              Inventory Value
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground hidden sm:block" />
          </CardHeader>
          <CardContent className="p-3 pt-0 md:p-6 md:pt-0">
            <div className="text-lg md:text-2xl font-bold">
              {formatCurrency(stats?.total_inventory_value || 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats?.total_parts || 0} parts
            </p>
          </CardContent>
        </Card>

        <Card className="stat-card" data-testid="stat-monthly-sales">
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 md:p-6 md:pb-2">
            <CardTitle className="text-xs md:text-sm font-medium text-muted-foreground">
              Monthly Sales
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground hidden sm:block" />
          </CardHeader>
          <CardContent className="p-3 pt-0 md:p-6 md:pt-0">
            <div className="text-lg md:text-2xl font-bold">
              {formatCurrency(stats?.monthly_sales || 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Today: {formatCurrency(stats?.today_sales || 0)}
            </p>
          </CardContent>
        </Card>

        <Card className="stat-card" data-testid="stat-customers">
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 md:p-6 md:pb-2">
            <CardTitle className="text-xs md:text-sm font-medium text-muted-foreground">
              Customers
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground hidden sm:block" />
          </CardHeader>
          <CardContent className="p-3 pt-0 md:p-6 md:pt-0">
            <div className="text-lg md:text-2xl font-bold">
              {stats?.total_customers || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Total registered
            </p>
          </CardContent>
        </Card>

        <Card className="stat-card" data-testid="stat-invoices">
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 md:p-6 md:pb-2">
            <CardTitle className="text-xs md:text-sm font-medium text-muted-foreground">
              Total Invoices
            </CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground hidden sm:block" />
          </CardHeader>
          <CardContent className="p-3 pt-0 md:p-6 md:pt-0">
            <div className="text-lg md:text-2xl font-bold">
              {stats?.total_invoices || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">All time</p>
          </CardContent>
        </Card>
      </div>

      {/* Low Stock Alert & Recent Invoices */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Low Stock Alert */}
        <Card data-testid="low-stock-card">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              Low Stock Alerts
            </CardTitle>
            {lowStock.length > 0 && (
              <Badge variant="destructive">{lowStock.length}</Badge>
            )}
          </CardHeader>
          <CardContent>
            {lowStock.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>All items are well stocked</p>
              </div>
            ) : (
              <div className="space-y-3">
                {lowStock.slice(0, 5).map((part) => (
                  <div
                    key={part.id}
                    className="flex items-center justify-between p-3 rounded-lg low-stock-alert"
                    data-testid={`low-stock-item-${part.id}`}
                  >
                    <div>
                      <p className="font-medium text-sm">{part.name}</p>
                      <p className="text-xs opacity-80">{part.part_number}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{part.quantity} left</p>
                      <p className="text-xs opacity-80">
                        Min: {part.min_stock_level}
                      </p>
                    </div>
                  </div>
                ))}
                {lowStock.length > 5 && (
                  <Link
                    to="/inventory?low_stock=true"
                    className="flex items-center justify-center gap-1 text-sm text-primary hover:underline pt-2"
                  >
                    View all {lowStock.length} items
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Invoices */}
        <Card data-testid="recent-invoices-card">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Invoices</CardTitle>
            <Link to="/invoices">
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {recentInvoices.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No invoices yet</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Invoice #</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentInvoices.map((invoice) => (
                    <TableRow
                      key={invoice.id}
                      data-testid={`recent-invoice-${invoice.id}`}
                    >
                      <TableCell className="font-mono text-sm">
                        {invoice.invoice_number}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{invoice.customer_name}</p>
                          <p className="text-xs text-muted-foreground">
                            {formatDateTime(invoice.created_at)}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(invoice.total)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
