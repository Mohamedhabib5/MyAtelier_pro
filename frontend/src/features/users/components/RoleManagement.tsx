import React, { useEffect, useState } from 'react';
import { 
  Box, Button, Card, CardContent, Checkbox, 
  FormControlLabel, Grid, IconButton, Stack, 
  TextField, Typography, Divider, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Alert, Tooltip
} from '@mui/material';
import { 
  Plus, Edit, Trash, Copy, Shield, 
  Settings, Database, CreditCard, ShoppingBag, 
  Users, BarChart, Calendar
} from 'lucide-react';
import { 
  fetchRoles, fetchPermissions, createRole, 
  updateRole, deleteRole, cloneRole, 
  type Role, type Permission 
} from '../rolesApi';
import { useUsersText } from '../../../text/users';

const CATEGORIES = [
  // Categories labels will be mapped using text translations during render
  { key: 'system', prefix: ['audit', 'destructive', 'period_lock', 'users', 'settings', 'security'], icon: <Shield size={18} /> },
  { key: 'finance', prefix: ['finance', 'reports', 'exports', 'accounting'], icon: <BarChart size={18} /> },
  { key: 'data', prefix: ['customers', 'catalog', 'dresses', 'branches'], icon: <Database size={18} /> },
  { key: 'atelier', prefix: ['atelier'], icon: <ShoppingBag size={18} /> },
  { key: 'salon', prefix: ['salon'], icon: <Users size={18} /> },
  { key: 'crm', prefix: ['crm'], icon: <Users size={18} /> },
  { key: 'inventory', prefix: ['inventory'], icon: <Settings size={18} /> },
  { key: 'operations', prefix: ['bookings', 'payments', 'custody'], icon: <CreditCard size={18} /> },
];

export const RoleManagement: React.FC = () => {
  const usersText = useUsersText();
  const text = usersText.roleManagement;
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [open, setOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '', permission_keys: [] as string[] });

  const loadData = async () => {
    setLoading(true);
    try {
      const [r, p] = await Promise.all([fetchRoles(), fetchPermissions()]);
      setRoles(r);
      setPermissions(p);
    } catch (err: any) {
      setError(err.message || text.errorLoad);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpen = (role: Role | null = null) => {
    if (role) {
      setEditingRole(role);
      setFormData({ 
        name: role.name, 
        description: role.description || '', 
        permission_keys: role.permissions.map(p => p.key) 
      });
    } else {
      setEditingRole(null);
      setFormData({ name: '', description: '', permission_keys: [] });
    }
    setOpen(true);
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      if (editingRole) {
        await updateRole(editingRole.id, formData);
      } else {
        await createRole(formData);
      }
      setOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.message || text.errorSave);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(text.deleteConfirm)) return;
    try {
      await deleteRole(id);
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleClone = async (role: Role) => {
    const newName = window.prompt(text.clonePrompt, `${role.name}_copy`);
    if (!newName) return;
    try {
      await cloneRole(role.id, newName);
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const togglePermission = (key: string) => {
    setFormData(prev => ({
      ...prev,
      permission_keys: prev.permission_keys.includes(key)
        ? prev.permission_keys.filter(k => k !== key)
        : [...prev.permission_keys, key]
    }));
  };

  const getPermissionsByCategory = (prefix: string[]) => {
    return permissions.filter(p => prefix.some(pr => p.key.startsWith(pr)));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight="bold">{text.title}</Typography>
        <Button variant="contained" startIcon={<Plus />} onClick={() => handleOpen()}>
          {text.addRole}
        </Button>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>{error}</Alert>}

      <Grid container spacing={3}>
        {roles.map(role => (
          <Grid size={{ xs: 12, md: 6, lg: 4 }} key={role.id}>
            <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Stack direction="row" alignItems="center" gap={1}>
                      <Typography variant="h6" fontWeight="bold">{role.name}</Typography>
                      {role.is_preset && <Chip label={text.system} size="small" color="primary" variant="outlined" />}
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {role.description || text.noDescription}
                    </Typography>
                  </Box>
                  <Box>
                    <Tooltip title={text.editTooltip}>
                      <IconButton size="small" onClick={() => handleOpen(role)}><Edit size={18} /></IconButton>
                    </Tooltip>
                    <Tooltip title={text.cloneTooltip}>
                      <IconButton size="small" onClick={() => handleClone(role)}><Copy size={18} /></IconButton>
                    </Tooltip>
                    {!role.is_preset && (
                      <Tooltip title={text.deleteTooltip}>
                        <IconButton size="small" color="error" onClick={() => handleDelete(role.id)}><Trash size={18} /></IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </Stack>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="caption" fontWeight="bold" color="primary">
                  {role.permissions.length} {text.activePermissions}
                </Typography>
                
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {role.permissions.slice(0, 5).map(p => (
                    <Chip key={p.key} label={p.key} size="small" sx={{ fontSize: '0.7rem' }} />
                  ))}
                  {role.permissions.length > 5 && <Chip label={`+${role.permissions.length - 5}`} size="small" />}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Role Editor Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRole ? `${text.dialogEdit} ${editingRole.name}` : text.dialogCreate}
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={3}>
            <TextField 
              label={text.roleName} 
              fullWidth 
              value={formData.name} 
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              disabled={editingRole?.is_preset}
            />
            <TextField 
              label={text.description} 
              fullWidth 
              multiline 
              rows={2} 
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
            />
            
            <Typography variant="subtitle1" fontWeight="bold">{text.permissionsCount.replace('{count}', '58')}</Typography>
            
            {CATEGORIES.map(cat => (
              <Box key={cat.key} sx={{ mb: 2 }}>
                <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1, color: 'primary.main' }}>
                  {cat.icon}
                  <Typography variant="subtitle2" fontWeight="bold">{text.categories[cat.key as keyof typeof text.categories]}</Typography>
                </Stack>
                <Grid container spacing={1}>
                  {getPermissionsByCategory(cat.prefix).map(perm => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={perm.key}>
                      <FormControlLabel
                        control={
                          <Checkbox 
                            size="small"
                            checked={formData.permission_keys.includes(perm.key)}
                            onChange={() => togglePermission(perm.key)}
                          />
                        }
                        label={
                          <Tooltip title={perm.description}>
                            <Typography variant="body2">{perm.key}</Typography>
                          </Tooltip>
                        }
                      />
                    </Grid>
                  ))}
                </Grid>
                <Divider sx={{ mt: 2 }} />
              </Box>
            ))}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>{text.cancel}</Button>
          <Button variant="contained" onClick={handleSave} disabled={loading}>{text.save}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
