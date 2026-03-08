import { createContext, useContext, useState, useCallback } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Lock } from "lucide-react";
import { toast } from "sonner";
import api from "@/lib/api";

const PasswordContext = createContext(null);

export function PasswordProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [resolveRef, setResolveRef] = useState(null);
  const [rejectRef, setRejectRef] = useState(null);
  const [actionDescription, setActionDescription] = useState("");

  const requirePassword = useCallback((description) => {
    return new Promise((resolve, reject) => {
      setActionDescription(description);
      setResolveRef(() => resolve);
      setRejectRef(() => reject);
      setPassword("");
      setIsOpen(true);
    });
  }, []);

  const handleVerify = async () => {
    if (!password.trim()) {
      toast.error("Please enter password");
      return;
    }

    setLoading(true);
    try {
      await api.post("/verify-password", { password });
      setIsOpen(false);
      if (resolveRef) {
        resolveRef(true);
      }
      setResolveRef(null);
      setRejectRef(null);
    } catch (error) {
      toast.error("Invalid password");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsOpen(false);
    if (rejectRef) {
      rejectRef(new Error("Cancelled"));
    }
    setResolveRef(null);
    setRejectRef(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleVerify();
    }
  };

  return (
    <PasswordContext.Provider value={{ requirePassword }}>
      {children}
      <Dialog open={isOpen} onOpenChange={(open) => !open && handleCancel()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-red-600" />
              Password Required
            </DialogTitle>
            <DialogDescription>
              {actionDescription || "Enter admin password to continue"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="admin-password">Password</Label>
              <Input
                id="admin-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter password"
                autoFocus
                data-testid="admin-password-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button 
              onClick={handleVerify} 
              disabled={loading}
              data-testid="verify-password-btn"
            >
              {loading ? "Verifying..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </PasswordContext.Provider>
  );
}

export function usePassword() {
  const context = useContext(PasswordContext);
  if (!context) {
    throw new Error("usePassword must be used within a PasswordProvider");
  }
  return context;
}
