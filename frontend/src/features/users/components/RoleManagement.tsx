import React, { useEffect, useState } from 'react';
import { 
  Box, Button, Card, CardContent, Checkbox, 
  FormControlLabel, Grid, IconButton, Stack, 
  TextField, Typography, Divider, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Alert, Tooltip, Paper, useTheme, Zoom, Fade
} from '@mui/material';
import { 
  Plus, Edit, Trash, Copy, Shield, 
  Settings, Database, CreditCard, ShoppingBag, 
  Users, BarChart, Calendar, ShieldCheck,
  Search, CheckCircle2, AlertCircle, Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  fetchRoles, fetchPermissions, createRole, 
  updateRole, deleteRole, cloneRole, 
  type Role, type Permission 
} from '../rolesApi';
import { useUsersText } from '../../../text/users';

const CATEGORIES = [
  { key: 'system', prefix: ['audit', 'destructive', 'period_lock', 'users', 'settings', 'security'], icon: <Shield size={18} /> },
  { key: 'finance', prefix: ['finance', 'reports', 'exports', 'accounting'], icon: <BarChart size={18} /> },
  { key: 'data', prefix: ['customers', 'catalog', 'dresses', 'branches'], icon: <Database size={18} /> },
  { key: 'atelier', prefix: ['atelier'], icon: <ShoppingBag size={18} /> },
  { key: 'salon', prefix: ['salon'], icon: <Users size={18} /> },
  { key: 'operations', prefix: ['bookings', 'payments', 'custody'], icon: <CreditCard size={18} /> },
];

export const RoleManagement: React.FC = () => {
  const theme = useTheme();
  const usersText = useUsersText();
  const text = usersText.roleManagement;
  
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [open, setOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '', permission_keys: [] as string[] });
  const [permSearch, setPermSearch] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [r, p] = await Promise.all([fetchRoles(), fetchPermissions()]);
      setRoles(r);
      setPermissions(p);
    } catch (err: unknown) {
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
        setSuccess('تم تحديث الدور بنجاح');
      } else {
        await createRole(formData);
        setSuccess('تم إنشاء الدور بنجاح');
      }
      setOpen(false);
      loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: unknown) {
      setError(err.message || text.errorSave);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(text.deleteConfirm)) return;
    try {
      await deleteRole(id);
      setSuccess('تم حذف الدور');
      loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: unknown) {
      setError(err.message);
    }
  };

  const handleClone = async (role: Role) => {
    const newName = window.prompt(text.clonePrompt, `${role.name}_copy`);
    if (!newName) return;
    try {
      await cloneRole(role.id, newName);
      setSuccess('تم نسخ الدور بنجاح');
      loadData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: unknown) {
      setError(err.message);
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
    return permissions.filter(p => {
      const matchesPrefix = prefix.some(pr => p.key.startsWith(pr));
      const matchesSearch = p.key.toLowerCase().includes(permSearch.toLowerCase());
      return matchesPrefix && (permSearch ? matchesSearch : true);
    });
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight="800" sx={{ mb: 0.5 }}>{text.title}</Typography>
          <Typography variant="body2" color="text.secondary">إدارة صلاحيات الوصول والأدوار الأمنية للنظام</Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<Plus size={18} />} 
          onClick={() => handleOpen()}
          sx={{ borderRadius: 3, py: 1, px: 3, fontWeight: 'bold' }}
        >
          {text.addRole}
        </Button>
      </Stack>

      <AnimatePresence>
        {success && (
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <Alert severity="success" icon={<CheckCircle2 size={18} />} sx={{ mb: 3, borderRadius: 3 }}>{success}</Alert>
          </motion.div>
        )}
        {error && (
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <Alert severity="error" icon={<AlertCircle size={18} />} sx={{ mb: 3, borderRadius: 3 }} onClose={() => setError(null)}>{error}</Alert>
          </motion.div>
        )}
      </AnimatePresence>

      <Grid container spacing={3}>
        {roles.map((role, index) => (
          <Grid size={{ xs: 12, md: 6, lg: 4 }} key={role.id}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card 
                sx={{ 
                  height: '100%', 
                  borderRadius: 4,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.shadows[8]
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box>
                      <Stack direction="row" alignItems="center" gap={1}>
                        <Typography variant="h6" fontWeight="bold">{role.name}</Typography>
                        {role.is_preset && (
                          <Chip 
                            label="نظام" 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                            sx={{ fontWeight: 'bold', fontSize: '0.65rem', height: 20 }} 
                          />
                        )}
                      </Stack>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1, minHeight: 40 }}>
                        {role.description || "لا يوجد وصف متوفر"}
                      </Typography>
                    </Box>
                    <Stack direction="row">
                      <Tooltip title={text.editTooltip}>
                        <IconButton size="small" onClick={() => handleOpen(role)} sx={{ color: theme.palette.info.main }}><Edit size={18} /></IconButton>
                      </Tooltip>
                      <Tooltip title={text.cloneTooltip}>
                        <IconButton size="small" onClick={() => handleClone(role)} sx={{ color: theme.palette.warning.main }}><Copy size={18} /></IconButton>
                      </Tooltip>
                      {!role.is_preset && (
                        <Tooltip title={text.deleteTooltip}>
                          <IconButton size="small" color="error" onClick={() => handleDelete(role.id)}><Trash size={18} /></IconButton>
                        </Tooltip>
                      )}
                    </Stack>
                  </Stack>
                  
                  <Divider sx={{ my: 2, borderStyle: 'dashed' }} />
                  
                  <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1.5 }}>
                    <ShieldCheck size={16} color={theme.palette.primary.main} />
                    <Typography variant="caption" fontWeight="bold" color="primary">
                      {role.permissions.length} صلاحية مفعلة
                    </Typography>
                  </Stack>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.6 }}>
                    {role.permissions.slice(0, 4).map(p => (
                      <Chip key={p.key} label={p.key} size="small" sx={{ fontSize: '0.7rem', bgcolor: 'rgba(0,0,0,0.03)' }} />
                    ))}
                    {role.permissions.length > 4 && (
                      <Chip 
                        label={`+${role.permissions.length - 4}`} 
                        size="small" 
                        variant="outlined" 
                        sx={{ fontSize: '0.7rem', fontWeight: 'bold' }} 
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Role Editor Dialog */}
      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: 4, p: 1 }
        }}
      >
        <DialogTitle sx={{ fontWeight: 'bold', fontSize: '1.25rem' }}>
          {editingRole ? `تعديل دور: ${editingRole.name}` : 'إنشاء دور جديد'}
        </DialogTitle>
        <DialogContent dividers sx={{ bgcolor: '#fbfbfb' }}>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField 
                  label="اسم الدور" 
                  fullWidth 
                  value={formData.name} 
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  disabled={editingRole?.is_preset}
                  InputProps={{ sx: { borderRadius: 3, bgcolor: 'white' } }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField 
                  label="الوصف" 
                  fullWidth 
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  InputProps={{ sx: { borderRadius: 3, bgcolor: 'white' } }}
                />
              </Grid>
            </Grid>

            <Paper sx={{ p: 2, borderRadius: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Search size={20} color={theme.palette.text.disabled} />
              <TextField 
                placeholder="ابحث عن صلاحية محددة..."
                variant="standard"
                fullWidth
                value={permSearch}
                onChange={e => setPermSearch(e.target.value)}
                InputProps={{ disableUnderline: true }}
              />
              <Box sx={{ px: 2, borderLeft: '1px solid #eee' }}>
                <Typography variant="caption" fontWeight="bold">
                  {formData.permission_keys.length} مختارة
                </Typography>
              </Box>
            </Paper>
            
            <Box sx={{ maxHeight: 500, overflowY: 'auto', pr: 1 }}>
              {CATEGORIES.map(cat => {
                const perms = getPermissionsByCategory(cat.prefix);
                if (perms.length === 0 && permSearch) return null;
                
                return (
                  <Box key={cat.key} sx={{ mb: 4 }}>
                    <Stack direction="row" alignItems="center" gap={1} sx={{ mb: 1.5, color: 'primary.main' }}>
                      {cat.icon}
                      <Typography variant="subtitle1" fontWeight="bold">
                        {text.categories[cat.key as keyof typeof text.categories]}
                      </Typography>
                      <Typography variant="caption" color="text.disabled">({perms.length})</Typography>
                    </Stack>
                    <Grid container spacing={1}>
                      {perms.map(perm => (
                        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={perm.key}>
                          <Paper 
                            elevation={0}
                            sx={{ 
                              p: 0.5, 
                              px: 1,
                              borderRadius: 2, 
                              border: '1px solid',
                              borderColor: formData.permission_keys.includes(perm.key) ? 'primary.light' : 'transparent',
                              bgcolor: formData.permission_keys.includes(perm.key) ? 'primary.lighter' : 'transparent',
                              '&:hover': { bgcolor: 'rgba(0,0,0,0.02)' }
                            }}
                          >
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
                                  <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>{perm.key}</Typography>
                                </Tooltip>
                              }
                              sx={{ m: 0, width: '100%' }}
                            />
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                );
              })}
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2.5 }}>
          <Button onClick={() => setOpen(false)} color="inherit" sx={{ borderRadius: 3 }}>إلغاء</Button>
          <Button 
            variant="contained" 
            onClick={handleSave} 
            disabled={loading}
            sx={{ borderRadius: 3, px: 4, fontWeight: 'bold' }}
          >
            {text.save}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
