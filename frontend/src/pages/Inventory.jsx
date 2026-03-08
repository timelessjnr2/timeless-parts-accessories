import { useState, useEffect } from "react";
import {
  Plus,
  Search,
  Edit2,
  Trash2,
  Package,
  Filter,
  Upload,
  Link as LinkIcon,
  X,
  Car,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
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
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import { partsApi, uploadApi, vehiclesApi } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { usePassword } from "@/contexts/PasswordContext";

export default function Inventory() {
  const { requirePassword } = usePassword();
  const [parts, setParts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [lowStockFilter, setLowStockFilter] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editingPart, setEditingPart] = useState(null);
  const [partToDelete, setPartToDelete] = useState(null);
  const [imageMode, setImageMode] = useState("upload");

  const [formData, setFormData] = useState({
    name: "",
    part_number: "",
    description: "",
    price: "",
    cost_price: "",
    quantity: "",
    min_stock_level: "5",
    category: "",
    image_url: "",
    compatible_vehicles: [],
  });

  useEffect(() => {
    fetchData();
  }, [search, categoryFilter, lowStockFilter]);

  const fetchData = async () => {
    try {
      const [partsRes, categoriesRes, vehiclesRes] = await Promise.all([
        partsApi.getAll({
          search: search || undefined,
          category: categoryFilter || undefined,
          low_stock: lowStockFilter || undefined,
        }),
        partsApi.getCategories(),
        vehiclesApi.getAll(),
      ]);
      setParts(partsRes.data);
      setCategories(categoriesRes.data);
      setVehicles(vehiclesRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load inventory");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = async (part = null) => {
    if (part) {
      // Require password for editing
      try {
        await requirePassword("Enter password to edit this part");
        setEditingPart(part);
        setFormData({
          name: part.name,
          part_number: part.part_number,
          description: part.description || "",
          price: part.price.toString(),
          cost_price: part.cost_price?.toString() || "",
          quantity: part.quantity.toString(),
          min_stock_level: part.min_stock_level.toString(),
          category: part.category || "",
          image_url: part.image_url || "",
          compatible_vehicles: part.compatible_vehicles || [],
        });
        setDialogOpen(true);
      } catch (error) {
        // User cancelled or wrong password - do nothing
        return;
      }
    } else {
      setEditingPart(null);
      setFormData({
        name: "",
        part_number: "",
        description: "",
        price: "",
        cost_price: "",
        quantity: "",
        min_stock_level: "5",
        category: "",
        image_url: "",
        compatible_vehicles: [],
      });
      setDialogOpen(true);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const res = await uploadApi.uploadImage(file);
      setFormData({ ...formData, image_url: res.data.image_url });
      toast.success("Image uploaded");
    } catch (error) {
      toast.error("Failed to upload image");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = {
      ...formData,
      price: parseFloat(formData.price),
      cost_price: formData.cost_price ? parseFloat(formData.cost_price) : null,
      quantity: parseInt(formData.quantity),
      min_stock_level: parseInt(formData.min_stock_level),
    };

    try {
      if (editingPart) {
        await partsApi.update(editingPart.id, data);
        toast.success("Part updated successfully");
      } else {
        await partsApi.create(data);
        toast.success("Part added successfully");
      }
      setDialogOpen(false);
      fetchData();
    } catch (error) {
      toast.error(editingPart ? "Failed to update part" : "Failed to add part");
    }
  };

  const handleDelete = async () => {
    if (!partToDelete) return;

    try {
      await requirePassword("Enter password to delete this part");
      await partsApi.delete(partToDelete.id);
      toast.success("Part deleted successfully");
      setDeleteDialogOpen(false);
      setPartToDelete(null);
      fetchData();
    } catch (error) {
      if (error.message !== "Cancelled") {
        toast.error("Failed to delete part");
      }
      setDeleteDialogOpen(false);
    }
  };

  const addVehicleCompatibility = () => {
    setFormData({
      ...formData,
      compatible_vehicles: [
        ...formData.compatible_vehicles,
        { make: "", model: "", year_start: null, year_end: null },
      ],
    });
  };

  const removeVehicleCompatibility = (index) => {
    const updated = formData.compatible_vehicles.filter((_, i) => i !== index);
    setFormData({ ...formData, compatible_vehicles: updated });
  };

  const updateVehicleCompatibility = (index, field, value) => {
    const updated = [...formData.compatible_vehicles];
    updated[index] = { ...updated[index], [field]: value };
    setFormData({ ...formData, compatible_vehicles: updated });
  };

  return (
    <div className="space-y-6 fade-in" data-testid="inventory-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
            Inventory
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage your parts inventory
          </p>
        </div>
        <Button onClick={() => handleOpenDialog()} data-testid="add-part-btn">
          <Plus className="mr-2 h-4 w-4" />
          Add Part
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, part number..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
                data-testid="search-input"
              />
            </div>
            <Select value={categoryFilter || "all"} onValueChange={(val) => setCategoryFilter(val === "all" ? "" : val)}>
              <SelectTrigger className="w-full md:w-48" data-testid="category-filter">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant={lowStockFilter ? "default" : "outline"}
              onClick={() => setLowStockFilter(!lowStockFilter)}
              data-testid="low-stock-filter"
            >
              <Filter className="mr-2 h-4 w-4" />
              Low Stock
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Parts Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-muted-foreground">Loading...</div>
            </div>
          ) : parts.length === 0 ? (
            <div className="empty-state">
              <Package className="h-16 w-16" />
              <h3 className="text-lg font-semibold mt-4">No parts found</h3>
              <p className="text-sm">
                {search || categoryFilter || lowStockFilter
                  ? "Try adjusting your filters"
                  : "Add your first part to get started"}
              </p>
              {!search && !categoryFilter && !lowStockFilter && (
                <Button
                  onClick={() => handleOpenDialog()}
                  className="mt-4"
                  data-testid="add-first-part-btn"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Part
                </Button>
              )}
            </div>
          ) : (
            <Table className="data-table">
              <TableHeader>
                <TableRow>
                  <TableHead>Image</TableHead>
                  <TableHead>Part Details</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Compatible Vehicles</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                  <TableHead className="text-center">Stock</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {parts.map((part) => (
                  <TableRow key={part.id} data-testid={`part-row-${part.id}`}>
                    <TableCell>
                      {part.image_url ? (
                        <img
                          src={part.image_url}
                          alt={part.name}
                          className="part-image"
                        />
                      ) : (
                        <div className="part-image-placeholder">
                          <Package className="h-5 w-5" />
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-semibold">{part.name}</p>
                        <p className="text-xs text-muted-foreground font-mono">
                          {part.part_number}
                        </p>
                        {part.description && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                            {part.description}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {part.category ? (
                        <Badge variant="secondary">{part.category}</Badge>
                      ) : (
                        <span className="text-muted-foreground text-sm">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {part.compatible_vehicles?.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {part.compatible_vehicles.slice(0, 2).map((v, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {v.make} {v.model}
                            </Badge>
                          ))}
                          {part.compatible_vehicles.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{part.compatible_vehicles.length - 2}
                            </Badge>
                          )}
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-sm">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      {formatCurrency(part.price)}
                    </TableCell>
                    <TableCell className="text-center">
                      <span
                        className={`stock-badge ${
                          part.quantity <= part.min_stock_level ? "low" : "ok"
                        }`}
                      >
                        {part.quantity}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" data-testid={`part-actions-${part.id}`}>
                            ...
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleOpenDialog(part)}>
                            <Edit2 className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => {
                              setPartToDelete(part);
                              setDeleteDialogOpen(true);
                            }}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
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

      {/* Add/Edit Part Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-['Barlow_Condensed'] text-2xl uppercase">
              {editingPart ? "Edit Part" : "Add New Part"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Part Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  required
                  data-testid="part-name-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="part_number">Part Number *</Label>
                <Input
                  id="part_number"
                  value={formData.part_number}
                  onChange={(e) =>
                    setFormData({ ...formData, part_number: e.target.value })
                  }
                  required
                  data-testid="part-number-input"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={2}
                data-testid="part-description-input"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="price">Selling Price (JMD) *</Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) =>
                    setFormData({ ...formData, price: e.target.value })
                  }
                  required
                  data-testid="part-price-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cost_price">Cost Price (JMD)</Label>
                <Input
                  id="cost_price"
                  type="number"
                  step="0.01"
                  value={formData.cost_price}
                  onChange={(e) =>
                    setFormData({ ...formData, cost_price: e.target.value })
                  }
                  data-testid="part-cost-input"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity *</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({ ...formData, quantity: e.target.value })
                  }
                  required
                  data-testid="part-quantity-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="min_stock_level">Min Stock Level</Label>
                <Input
                  id="min_stock_level"
                  type="number"
                  value={formData.min_stock_level}
                  onChange={(e) =>
                    setFormData({ ...formData, min_stock_level: e.target.value })
                  }
                  data-testid="part-min-stock-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                  placeholder="e.g., Brakes, Engine"
                  data-testid="part-category-input"
                />
              </div>
            </div>

            {/* Image Upload */}
            <div className="space-y-2">
              <Label>Part Image</Label>
              <div className="flex gap-2 mb-2">
                <Button
                  type="button"
                  variant={imageMode === "upload" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setImageMode("upload")}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </Button>
                <Button
                  type="button"
                  variant={imageMode === "url" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setImageMode("url")}
                >
                  <LinkIcon className="mr-2 h-4 w-4" />
                  URL
                </Button>
              </div>
              {imageMode === "upload" ? (
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  data-testid="part-image-upload"
                />
              ) : (
                <Input
                  placeholder="Enter image URL"
                  value={formData.image_url}
                  onChange={(e) =>
                    setFormData({ ...formData, image_url: e.target.value })
                  }
                  data-testid="part-image-url-input"
                />
              )}
              {formData.image_url && (
                <div className="mt-2 relative w-24 h-24">
                  <img
                    src={formData.image_url}
                    alt="Preview"
                    className="w-full h-full object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    className="absolute -top-2 -right-2 bg-destructive text-white rounded-full p-1"
                    onClick={() => setFormData({ ...formData, image_url: "" })}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
            </div>

            {/* Vehicle Compatibility */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Compatible Vehicles</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addVehicleCompatibility}
                  data-testid="add-vehicle-btn"
                >
                  <Car className="mr-2 h-4 w-4" />
                  Add Vehicle
                </Button>
              </div>
              {formData.compatible_vehicles.map((vehicle, index) => (
                <div
                  key={index}
                  className="flex gap-2 items-center bg-muted/50 p-2 rounded-lg"
                >
                  <Input
                    placeholder="Make (e.g., Toyota)"
                    value={vehicle.make}
                    onChange={(e) =>
                      updateVehicleCompatibility(index, "make", e.target.value)
                    }
                    className="flex-1"
                    data-testid={`vehicle-make-${index}`}
                  />
                  <Input
                    placeholder="Model (e.g., Corolla)"
                    value={vehicle.model}
                    onChange={(e) =>
                      updateVehicleCompatibility(index, "model", e.target.value)
                    }
                    className="flex-1"
                    data-testid={`vehicle-model-${index}`}
                  />
                  <Input
                    placeholder="Year Start"
                    type="number"
                    value={vehicle.year_start || ""}
                    onChange={(e) =>
                      updateVehicleCompatibility(
                        index,
                        "year_start",
                        e.target.value ? parseInt(e.target.value) : null
                      )
                    }
                    className="w-24"
                    data-testid={`vehicle-year-start-${index}`}
                  />
                  <Input
                    placeholder="Year End"
                    type="number"
                    value={vehicle.year_end || ""}
                    onChange={(e) =>
                      updateVehicleCompatibility(
                        index,
                        "year_end",
                        e.target.value ? parseInt(e.target.value) : null
                      )
                    }
                    className="w-24"
                    data-testid={`vehicle-year-end-${index}`}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeVehicleCompatibility(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" data-testid="save-part-btn">
                {editingPart ? "Update Part" : "Add Part"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Part</DialogTitle>
          </DialogHeader>
          <p>
            Are you sure you want to delete "{partToDelete?.name}"? This action
            cannot be undone.
          </p>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              data-testid="confirm-delete-btn"
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
