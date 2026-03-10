import { useState, useEffect } from 'react';
import { 
  Users, 
  UserPlus, 
  Shield, 
  ShieldCheck,
  Clock,
  Circle,
  Activity,
  Power,
  Trash2,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { toast } from 'sonner';
import { userAuthApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { formatDateTime } from '@/lib/utils';

export default function UserManagement() {
  const { user: currentUser, onlineUsers } = useAuth();
  const [users, setUsers] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [deletePassword, setDeletePassword] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    role: 'staff',
  });

  useEffect(() => {
    fetchData();
  }, [onlineUsers]);

  const fetchData = async () => {
    try {
      const [usersRes, logsRes] = await Promise.all([
        userAuthApi.getAllUsers(),
        userAuthApi.getActivityLogs(100),
      ]);
      setUsers(usersRes.data);
      setActivityLogs(logsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password || !formData.full_name) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      await userAuthApi.register(formData);
      toast.success('User created successfully');
      setDialogOpen(false);
      setFormData({ username: '', password: '', full_name: '', role: 'staff' });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleToggleActive = async (userId) => {
    try {
      await userAuthApi.toggleUserActive(userId);
      toast.success('User status updated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update user status');
    }
  };

  const handleDeleteUser = (user) => {
    setUserToDelete(user);
    setDeletePassword('');
    setDeleteDialogOpen(true);
  };

  const confirmDeleteUser = async () => {
    if (!deletePassword) {
      toast.error('Please enter password');
      return;
    }
    
    try {
      await userAuthApi.deleteUser(userToDelete.id, deletePassword);
      toast.success(`User ${userToDelete.username} deleted successfully`);
      setDeleteDialogOpen(false);
      setUserToDelete(null);
      setDeletePassword('');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const getActionBadge = (action) => {
    const colors = {
      login: 'bg-green-100 text-green-800',
      logout: 'bg-gray-100 text-gray-800',
      create_invoice: 'bg-blue-100 text-blue-800',
      delete_invoice: 'bg-red-100 text-red-800',
      cancel_invoice: 'bg-orange-100 text-orange-800',
      refund_invoice: 'bg-purple-100 text-purple-800',
      uncancel_invoice: 'bg-teal-100 text-teal-800',
      delete_user: 'bg-red-100 text-red-800',
      user_registered: 'bg-blue-100 text-blue-800',
      create_part: 'bg-green-100 text-green-800',
      update_part: 'bg-yellow-100 text-yellow-800',
      delete_part: 'bg-red-100 text-red-800',
      increase_stock: 'bg-green-100 text-green-800',
      decrease_stock: 'bg-orange-100 text-orange-800',
      create_customer: 'bg-green-100 text-green-800',
      update_customer: 'bg-yellow-100 text-yellow-800',
      delete_customer: 'bg-red-100 text-red-800',
      update_settings: 'bg-purple-100 text-purple-800',
      mark_invoice_paid: 'bg-green-100 text-green-800',
      add_payment: 'bg-blue-100 text-blue-800',
      check_off_invoice: 'bg-teal-100 text-teal-800',
      uncheck_invoice: 'bg-gray-100 text-gray-800',
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  const formatTimeAgo = (date) => {
    if (!date) return 'Never';
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diff = Math.floor((now - d) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return formatDateTime(date);
  };

  return (
    <div className="space-y-6 fade-in" data-testid="user-management-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight uppercase font-['Barlow_Condensed']">
            User Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage users and view activity logs
          </p>
        </div>
        {currentUser?.role === 'admin' && (
          <Button onClick={() => setDialogOpen(true)} data-testid="add-user-btn">
            <UserPlus className="mr-2 h-4 w-4" />
            Add User
          </Button>
        )}
      </div>

      {/* Online Users Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {users.map((u) => (
          <Card key={u.id} className={u.is_online ? 'border-green-300 bg-green-50' : ''}>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-lg font-bold text-primary">
                      {u.full_name?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <Circle 
                    className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 ${
                      u.is_online ? 'text-green-500 fill-green-500' : 'text-gray-300 fill-gray-300'
                    }`}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{u.full_name}</p>
                  <p className="text-xs text-muted-foreground">
                    {u.is_online ? 'Online' : formatTimeAgo(u.last_seen)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">
            <Users className="mr-2 h-4 w-4" />
            Users
          </TabsTrigger>
          <TabsTrigger value="activity">
            <Activity className="mr-2 h-4 w-4" />
            Activity Log
          </TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-muted-foreground">Loading...</div>
                </div>
              ) : users.length === 0 ? (
                <div className="empty-state">
                  <Users className="h-16 w-16" />
                  <h3 className="text-lg font-semibold mt-4">No users yet</h3>
                  <p className="text-sm">Add your first user to get started</p>
                </div>
              ) : (
                <Table className="data-table">
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Username</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Last Seen</TableHead>
                      {currentUser?.role === 'admin' && (
                        <TableHead className="text-right">Actions</TableHead>
                      )}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((u) => (
                      <TableRow key={u.id} data-testid={`user-row-${u.id}`}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className="relative">
                              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                <span className="font-bold text-primary">
                                  {u.full_name?.charAt(0).toUpperCase()}
                                </span>
                              </div>
                              <Circle 
                                className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 ${
                                  u.is_online ? 'text-green-500 fill-green-500' : 'text-gray-300 fill-gray-300'
                                }`}
                              />
                            </div>
                            <span className="font-medium">{u.full_name}</span>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-sm">{u.username}</TableCell>
                        <TableCell>
                          {u.role === 'admin' ? (
                            <Badge className="bg-purple-100 text-purple-800">
                              <ShieldCheck className="mr-1 h-3 w-3" />
                              Admin
                            </Badge>
                          ) : (
                            <Badge variant="outline">
                              <Shield className="mr-1 h-3 w-3" />
                              Staff
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          {u.is_active !== false ? (
                            <Badge className="bg-green-100 text-green-800">Active</Badge>
                          ) : (
                            <Badge variant="destructive">Disabled</Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {u.is_online ? (
                              <span className="text-green-600">Online now</span>
                            ) : (
                              formatTimeAgo(u.last_seen)
                            )}
                          </div>
                        </TableCell>
                        {currentUser?.role === 'admin' && (
                          <TableCell className="text-right">
                            {u.id !== currentUser?.id && (
                              <div className="flex items-center justify-end gap-1">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleToggleActive(u.id)}
                                  title={u.is_active !== false ? 'Disable user' : 'Enable user'}
                                >
                                  <Power className={`h-4 w-4 ${u.is_active !== false ? 'text-green-600' : 'text-red-600'}`} />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDeleteUser(u)}
                                  title="Delete user"
                                  data-testid={`delete-user-${u.id}`}
                                >
                                  <Trash2 className="h-4 w-4 text-red-600" />
                                </Button>
                              </div>
                            )}
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table className="data-table">
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activityLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="text-muted-foreground text-sm">
                        {formatDateTime(log.timestamp)}
                      </TableCell>
                      <TableCell className="font-medium">{log.username}</TableCell>
                      <TableCell>
                        <Badge className={getActionBadge(log.action)}>
                          {log.action.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground max-w-md truncate">
                        {log.details}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add User Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="font-['Barlow_Condensed'] text-2xl uppercase">
              Add New User
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddUser} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name *</Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="John Smith"
                data-testid="new-user-fullname"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">Username *</Label>
              <Input
                id="username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="jsmith"
                data-testid="new-user-username"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password *</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Enter password"
                data-testid="new-user-password"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select
                value={formData.role}
                onValueChange={(value) => setFormData({ ...formData, role: value })}
              >
                <SelectTrigger data-testid="new-user-role">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="staff">Staff</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" data-testid="create-user-btn">
                Create User
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete User Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-destructive">Delete User Account</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p>
              Are you sure you want to permanently delete <strong>{userToDelete?.full_name}</strong>'s account ({userToDelete?.username})?
            </p>
            <p className="text-sm text-muted-foreground">
              This action cannot be undone. All of the user's session data will be removed.
            </p>
            <div className="space-y-2">
              <Label>Enter Password to Confirm</Label>
              <Input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Enter password..."
                data-testid="delete-user-password"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteUser}
              disabled={!deletePassword}
              data-testid="confirm-delete-user-btn"
            >
              Delete Account
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
