import { useState, useRef } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Stack,
  Typography,
} from '@mui/material';
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useMutation } from '@tanstack/react-query';

import { SectionCard } from '../../components/SectionCard';
import { importChartOfAccounts } from './api';
import { queryClient } from '../../lib/queryClient';

type Props = {
  language: 'ar' | 'en';
  onSuccess?: (message: string) => void;
  onError?: (message: string) => void;
};

export function CustomChartUpload({ language, onSuccess, onError }: Props) {
  const isAr = language === 'ar';
  const [coaType, setCoaType] = useState<'default' | 'custom'>('default');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useMutation({
    mutationFn: importChartOfAccounts,
    onSuccess: async (data) => {
      const msg = data.message || (isAr ? 'تم استيراد شجرة الحسابات بنجاح.' : 'Chart of accounts imported successfully.');
      setSuccessMsg(msg);
      setErrorMsg(null);
      setSelectedFile(null);
      await queryClient.invalidateQueries({ queryKey: ['accounting-bridges'] });
      await queryClient.invalidateQueries({ queryKey: ['chart-of-accounts'] });
      if (onSuccess) onSuccess(msg);
    },
    onError: (err: Error) => {
      setErrorMsg(err.message);
      setSuccessMsg(null);
      if (onError) onError(err.message);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (!file.name.endsWith('.csv')) {
        setErrorMsg(isAr ? '⚠️ يجب اختيار ملف بصيغة CSV فقط.' : '⚠️ You must choose a CSV file only.');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleUpload = () => {
    if (!selectedFile) return;
    uploadMutation.mutate(selectedFile);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setErrorMsg(null);
    setSuccessMsg(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <SectionCard
      title={isAr ? 'إعداد شجرة الحسابات (COA)' : 'Chart of Accounts (COA) Setup'}
      subtitle={isAr ? 'اختر الطريقة المفضلة لبناء الهيكل المالي والمحاسبي لشركتك' : 'Choose the preferred method to build your financial & accounting structure'}
    >
      <Stack spacing={2.5}>
        <FormControl component="fieldset">
          <RadioGroup
            value={coaType}
            onChange={(e) => {
              setCoaType(e.target.value as 'default' | 'custom');
              handleReset();
            }}
          >
            <FormControlLabel
              value="default"
              control={<Radio size="small" />}
              label={
                <Box sx={{ my: 0.5 }}>
                  <Typography variant="body1" fontWeight={coaType === 'default' ? 'bold' : 'normal'}>
                    {isAr ? 'استخدام الشجرة الافتراضية للنظام' : 'Use System Default Chart'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {isAr
                      ? 'شجرة حسابات جاهزة متكاملة تغطي متطلبات الورش ودور الأزياء (موصى بها).'
                      : 'A ready-to-use standard chart of accounts optimized for ateliers & fashion houses (Recommended).'}
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              value="custom"
              control={<Radio size="small" />}
              label={
                <Box sx={{ my: 0.5 }}>
                  <Typography variant="body1" fontWeight={coaType === 'custom' ? 'bold' : 'normal'}>
                    {isAr ? 'رفع شجرة حسابات مخصصة (CSV)' : 'Upload Custom Chart of Accounts (CSV)'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {isAr
                      ? 'استورد شجرة حسابات خاصة بشركتك من ملف CSV لتخصيص الهيكل المالي بالكامل.'
                      : 'Import your own custom chart of accounts structure directly from a CSV file.'}
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>

        {coaType === 'custom' && (
          <Stack spacing={2}>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv"
              style={{ display: 'none' }}
            />

            {!selectedFile ? (
              <Box
                onClick={triggerFileInput}
                sx={{
                  border: '2px dashed',
                  borderColor: 'divider',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  bgcolor: 'action.hover',
                  transition: 'all 0.2s',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: 'action.selected',
                  },
                }}
              >
                <CloudUploadOutlinedIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                <Typography variant="body2" fontWeight="medium">
                  {isAr ? 'انقر هنا لاختيار ملف شجرة الحسابات' : 'Click here to choose Chart of Accounts file'}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                  {isAr ? 'يجب أن يكون الملف بصيغة CSV فقط' : 'File must be in CSV format only'}
                </Typography>
              </Box>
            ) : (
              <Box
                sx={{
                  p: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  bgcolor: 'background.paper',
                }}
              >
                <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <DescriptionOutlinedIcon color="primary" />
                    <Box>
                      <Typography variant="body2" fontWeight="bold" noWrap sx={{ maxWidth: 250 }}>
                        {selectedFile.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </Typography>
                    </Box>
                  </Stack>
                  <Button size="small" color="error" onClick={handleReset}>
                    {isAr ? 'إلغاء' : 'Cancel'}
                  </Button>
                </Stack>
              </Box>
            )}

            {errorMsg && <Alert severity="error">{errorMsg}</Alert>}
            {successMsg && (
              <Alert severity="success" icon={<CheckCircleOutlineIcon fontSize="inherit" />}>
                {successMsg}
              </Alert>
            )}

            {selectedFile && (
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={uploadMutation.isPending}
                startIcon={
                  uploadMutation.isPending ? <CircularProgress size={20} color="inherit" /> : <CloudUploadOutlinedIcon />
                }
              >
                {isAr ? 'رفع واستيراد الشجرة المخصصة' : 'Upload & Import Custom Chart'}
              </Button>
            )}
          </Stack>
        )}
      </Stack>
    </SectionCard>
  );
}
