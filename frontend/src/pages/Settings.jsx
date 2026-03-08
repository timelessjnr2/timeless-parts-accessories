import { useState, useEffect } from "react";
import {
  Building2,
  FileText,
  Percent,
  Save,
  Plus,
  Trash2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { settingsApi } from "@/lib/api";
import { usePassword } from "@/contexts/PasswordContext";

export default function Settings() {
  const { requirePassword } = usePassword();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [companyForm, setCompanyForm] = useState({
    company_name: "",
    address: "",
    phone: "",
    email: "",
    logo_url: "",
    tax_rate: 15,
    tax_name: "GCT",
    currency: "JMD",
    invoice_prefix: "TPA",
  });

  const [policiesForm, setPoliciesForm] = useState({
    sales_return_policy: [],
    privacy_policy: [],
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await settingsApi.get();
      setSettings(res.data);
      if (res.data.company) {
        setCompanyForm(res.data.company);
      }
      if (res.data.policies) {
        setPoliciesForm(res.data.policies);
      }
    } catch (error) {
      console.error("Error fetching settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCompany = async () => {
    try {
      await requirePassword("Enter password to save company settings", async () => {
        setSaving(true);
        try {
          await settingsApi.updateCompany(companyForm);
          toast.success("Company settings saved");
        } finally {
          setSaving(false);
        }
      });
    } catch (error) {
      if (error.message !== "Cancelled") {
        toast.error("Failed to save company settings");
      }
    }
  };

  const handleSavePolicies = async () => {
    try {
      await requirePassword("Enter password to save policies", async () => {
        setSaving(true);
        try {
          await settingsApi.updatePolicies(policiesForm);
          toast.success("Policies saved");
        } finally {
          setSaving(false);
        }
      });
    } catch (error) {
      if (error.message !== "Cancelled") {
        toast.error("Failed to save policies");
      }
    }
  };

  const addPolicyItem = (type) => {
    setPoliciesForm({
      ...policiesForm,
      [type]: [...policiesForm[type], ""],
    });
  };

  const updatePolicyItem = (type, index, value) => {
    const updated = [...policiesForm[type]];
    updated[index] = value;
    setPoliciesForm({ ...policiesForm, [type]: updated });
  };

  const removePolicyItem = (type, index) => {
    const updated = policiesForm[type].filter((_, i) => i !== index);
    setPoliciesForm({ ...policiesForm, [type]: updated });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in" data-testid="settings-page">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
          Settings
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage your company information and policies
        </p>
      </div>

      <Tabs defaultValue="company" className="space-y-6">
        <TabsList>
          <TabsTrigger value="company" data-testid="company-tab">
            <Building2 className="mr-2 h-4 w-4" />
            Company
          </TabsTrigger>
          <TabsTrigger value="tax" data-testid="tax-tab">
            <Percent className="mr-2 h-4 w-4" />
            Tax Settings
          </TabsTrigger>
          <TabsTrigger value="policies" data-testid="policies-tab">
            <FileText className="mr-2 h-4 w-4" />
            Policies
          </TabsTrigger>
        </TabsList>

        {/* Company Settings */}
        <TabsContent value="company">
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Company Name</Label>
                  <Input
                    value={companyForm.company_name}
                    onChange={(e) =>
                      setCompanyForm({
                        ...companyForm,
                        company_name: e.target.value,
                      })
                    }
                    data-testid="company-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Invoice Prefix</Label>
                  <Input
                    value={companyForm.invoice_prefix}
                    onChange={(e) =>
                      setCompanyForm({
                        ...companyForm,
                        invoice_prefix: e.target.value,
                      })
                    }
                    placeholder="e.g., TPA"
                    data-testid="invoice-prefix-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Address</Label>
                <Textarea
                  value={companyForm.address}
                  onChange={(e) =>
                    setCompanyForm({ ...companyForm, address: e.target.value })
                  }
                  rows={2}
                  data-testid="company-address-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Phone</Label>
                  <Input
                    value={companyForm.phone}
                    onChange={(e) =>
                      setCompanyForm({ ...companyForm, phone: e.target.value })
                    }
                    data-testid="company-phone-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={companyForm.email}
                    onChange={(e) =>
                      setCompanyForm({ ...companyForm, email: e.target.value })
                    }
                    data-testid="company-email-input"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Logo URL</Label>
                <Input
                  value={companyForm.logo_url}
                  onChange={(e) =>
                    setCompanyForm({ ...companyForm, logo_url: e.target.value })
                  }
                  placeholder="https://..."
                  data-testid="company-logo-input"
                />
                {companyForm.logo_url && (
                  <div className="mt-2">
                    <img
                      src={companyForm.logo_url}
                      alt="Logo Preview"
                      className="h-20 object-contain"
                    />
                  </div>
                )}
              </div>

              <Button
                onClick={handleSaveCompany}
                disabled={saving}
                data-testid="save-company-btn"
              >
                <Save className="mr-2 h-4 w-4" />
                Save Company Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tax Settings */}
        <TabsContent value="tax">
          <Card>
            <CardHeader>
              <CardTitle>Tax Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Tax Name</Label>
                  <Input
                    value={companyForm.tax_name}
                    onChange={(e) =>
                      setCompanyForm({
                        ...companyForm,
                        tax_name: e.target.value,
                      })
                    }
                    placeholder="e.g., GCT, VAT"
                    data-testid="tax-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Tax Rate (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={companyForm.tax_rate}
                    onChange={(e) =>
                      setCompanyForm({
                        ...companyForm,
                        tax_rate: parseFloat(e.target.value) || 0,
                      })
                    }
                    data-testid="tax-rate-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Currency</Label>
                  <Input
                    value={companyForm.currency}
                    onChange={(e) =>
                      setCompanyForm({
                        ...companyForm,
                        currency: e.target.value,
                      })
                    }
                    placeholder="e.g., JMD, USD"
                    data-testid="currency-input"
                  />
                </div>
              </div>

              <div className="bg-muted/50 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  <strong>Note:</strong> The tax rate will be applied to all new
                  invoices. Current rate:{" "}
                  <span className="font-semibold">
                    {companyForm.tax_rate}% {companyForm.tax_name}
                  </span>
                </p>
              </div>

              <Button
                onClick={handleSaveCompany}
                disabled={saving}
                data-testid="save-tax-btn"
              >
                <Save className="mr-2 h-4 w-4" />
                Save Tax Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Policies */}
        <TabsContent value="policies">
          <div className="space-y-6">
            {/* Sales Return Policy */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Sales Return Policy</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => addPolicyItem("sales_return_policy")}
                  data-testid="add-return-policy-btn"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Item
                </Button>
              </CardHeader>
              <CardContent className="space-y-3">
                {policiesForm.sales_return_policy.map((item, index) => (
                  <div key={index} className="flex gap-2">
                    <span className="text-sm text-muted-foreground mt-2 w-6">
                      {index + 1}.
                    </span>
                    <Textarea
                      value={item}
                      onChange={(e) =>
                        updatePolicyItem(
                          "sales_return_policy",
                          index,
                          e.target.value
                        )
                      }
                      rows={2}
                      className="flex-1"
                      data-testid={`return-policy-${index}`}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive"
                      onClick={() =>
                        removePolicyItem("sales_return_policy", index)
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Privacy Policy */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Privacy Policy</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => addPolicyItem("privacy_policy")}
                  data-testid="add-privacy-policy-btn"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Item
                </Button>
              </CardHeader>
              <CardContent className="space-y-3">
                {policiesForm.privacy_policy.map((item, index) => (
                  <div key={index} className="flex gap-2">
                    <span className="text-sm text-muted-foreground mt-2 w-6">
                      {index + 1}.
                    </span>
                    <Textarea
                      value={item}
                      onChange={(e) =>
                        updatePolicyItem("privacy_policy", index, e.target.value)
                      }
                      rows={2}
                      className="flex-1"
                      data-testid={`privacy-policy-${index}`}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive"
                      onClick={() => removePolicyItem("privacy_policy", index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Button
              onClick={handleSavePolicies}
              disabled={saving}
              data-testid="save-policies-btn"
            >
              <Save className="mr-2 h-4 w-4" />
              Save Policies
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
