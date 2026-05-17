import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Alert,
  Paper,
  Checkbox,
  IconButton,
  Tooltip,
} from "@mui/material";
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

import { listPaymentMethods } from "../../paymentMethods/api";
import { getPendingPayments, createReconciliation, listReconciliations, deleteReconciliation, ReconciliationRecord } from "../api";
import { useLanguage } from "../../language/LanguageProvider";
import { useLanguageFormatters } from "../../../text/common";
import { AppDialogShell } from "../../../components/AppDialogShell";

export function ReconciliationContent() {
  const { language } = useLanguage();
  const formatters = useLanguageFormatters();
  const queryClient = useQueryClient();

  // Dialog State
  const [isMatchingOpen, setIsMatchingOpen] = useState<boolean>(false);
  const [isViewOpen, setIsViewOpen] = useState<boolean>(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState<boolean>(false);
  
  // Selection / Matching Form State
  const [selectedMethodId, setSelectedMethodId] = useState<string>("");
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split("T")[0]);
  const [endDate, setEndDate] = useState<string>(new Date().toISOString().split("T")[0]);
  const [receiverName, setReceiverName] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [selectedPaymentIds, setSelectedPaymentIds] = useState<string[]>([]);
  const [singleActualAmount, setSingleActualAmount] = useState<number | "">("");

  // View / Delete Row State
  const [viewingRecon, setViewingRecon] = useState<ReconciliationRecord | null>(null);
  const [deletingReconId, setDeletingReconId] = useState<string>("");

  // UI Message State
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Queries
  const paymentMethodsQuery = useQuery({
    queryKey: ["paymentMethods", "active"],
    queryFn: () => listPaymentMethods("active"),
  });

  const reconciliationsQuery = useQuery({
    queryKey: ["reconciliations"],
    queryFn: listReconciliations,
  });

  // Automatically select first payment method if available
  useMemo(() => {
    if (paymentMethodsQuery.data && paymentMethodsQuery.data.length > 0 && !selectedMethodId) {
      setSelectedMethodId(paymentMethodsQuery.data[0].id);
    }
  }, [paymentMethodsQuery.data, selectedMethodId]);

  const selectedMethod = useMemo(() => {
    return paymentMethodsQuery.data?.find((m) => m.id === selectedMethodId);
  }, [paymentMethodsQuery.data, selectedMethodId]);

  const isCash = useMemo(() => {
    if (!selectedMethod) return false;
    const code = selectedMethod.code.toLowerCase();
    const name = selectedMethod.name;
    return code === "cash" || name === "نقدي" || name.toLowerCase() === "cash";
  }, [selectedMethod]);

  const pendingQuery = useQuery({
    queryKey: ["reconciliations", "pending", selectedMethodId, startDate, endDate],
    queryFn: () => getPendingPayments(selectedMethodId, startDate, endDate),
    enabled: !!selectedMethodId && !!startDate && !!endDate,
  });

  const pendingItems = pendingQuery.data ?? [];

  // Auto-select all loaded pending items when search criteria change
  const [hasAutoSelected, setHasAutoSelected] = useState<string>("");
  const currentQueryKey = `${selectedMethodId}-${startDate}-${endDate}`;
  useMemo(() => {
    if (pendingItems.length > 0 && hasAutoSelected !== currentQueryKey) {
      setSelectedPaymentIds(pendingItems.map((item) => item.id));
      setHasAutoSelected(currentQueryKey);
      
      // We removed the auto-filling of singleActualAmount to enforce a Blind Count (جرد أعمى)
    }
  }, [pendingItems, hasAutoSelected, currentQueryKey]);

  // Calculate dynamic totals for checked items
  const selectedPaymentsExpectedTotal = useMemo(() => {
    return pendingItems
      .filter((item) => selectedPaymentIds.includes(item.id))
      .reduce((sum, item) => sum + item.direct_amount, 0);
  }, [pendingItems, selectedPaymentIds]);

  const difference = useMemo(() => {
    const actual = singleActualAmount === "" ? 0 : singleActualAmount;
    return actual - selectedPaymentsExpectedTotal;
  }, [singleActualAmount, selectedPaymentsExpectedTotal]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: createReconciliation,
    onSuccess: () => {
      setSuccessMsg(language === "ar" ? "تم تسجيل تسوية الفترة بنجاح واكتملت العملية" : "Reconciliation committed successfully.");
      setErrorMsg(null);
      setReceiverName("");
      setNotes("");
      setSelectedPaymentIds([]);
      setSingleActualAmount("");
      setHasAutoSelected("");
      setIsMatchingOpen(false);
      queryClient.invalidateQueries({ queryKey: ["reconciliations"] });
    },
    onError: (err: any) => {
      setErrorMsg(err?.message || (language === "ar" ? "حدث خطأ أثناء حفظ التسوية" : "Error saving reconciliation."));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteReconciliation,
    onSuccess: () => {
      setSuccessMsg(language === "ar" ? "تم حذف وإلغاء التسوية بنجاح" : "Reconciliation deleted successfully.");
      setIsDeleteOpen(false);
      queryClient.invalidateQueries({ queryKey: ["reconciliations"] });
    },
    onError: (err: any) => {
      setErrorMsg(err?.message || (language === "ar" ? "حدث خطأ أثناء الحذف" : "Error deleting reconciliation."));
    },
  });

  const handleSubmit = () => {
    if (!selectedMethodId || !startDate || !endDate) return;

    if (isCash && !receiverName.trim()) {
      setErrorMsg(language === "ar" ? "يرجى كتابة اسم الشخص الذي استلم النقدية من الكاشير" : "Receiver name is required for Cash.");
      return;
    }

    if (selectedPaymentIds.length === 0) {
      setErrorMsg(language === "ar" ? "يجب اختيار دفعة واحدة على الأقل لإتمام التسوية" : "At least one payment must be selected.");
      return;
    }

    // Proportional Distribution
    let allocatedSum = 0;
    const actualVal = singleActualAmount === "" ? 0 : singleActualAmount;
    const itemsPayload = pendingItems
      .filter((item) => selectedPaymentIds.includes(item.id))
      .map((item, index, arr) => {
        let itemActual = 0;
        if (index === arr.length - 1) {
          itemActual = actualVal - allocatedSum;
        } else {
          if (selectedPaymentsExpectedTotal > 0) {
            itemActual = Math.round((item.direct_amount * (actualVal / selectedPaymentsExpectedTotal)) * 100) / 100;
          } else {
            itemActual = 0;
          }
          allocatedSum += itemActual;
        }
        return {
          payment_document_id: item.id,
          actual_amount: itemActual,
        };
      });

    createMutation.mutate({
      payment_method_id: selectedMethodId,
      start_date: startDate,
      end_date: endDate,
      receiver_name: isCash ? receiverName : null,
      notes: notes.trim() || null,
      items: itemsPayload,
    });
  };

  const text = {
    title: language === "ar" ? "تسوية النقدية والعهد" : "Cash Reconciliation",
    method: language === "ar" ? "طريقة الدفع" : "Payment Method",
    start: language === "ar" ? "من تاريخ" : "Start Date",
    end: language === "ar" ? "إلى تاريخ" : "End Date",
    receiver: language === "ar" ? "من استلم النقدية من الكاشير (اسم حر) *" : "Cash Recipient *",
    notes: language === "ar" ? "ملاحظات إضافية" : "Additional Notes",
    expectedTotal: language === "ar" ? "إجمالي المتوقع" : "Expected Total",
    actualTotal: language === "ar" ? "إجمالي الفعلي (العد)" : "Actual Total",
    diff: language === "ar" ? "الفارق" : "Difference",
    save: language === "ar" ? "تأكيد وحفظ التسوية" : "Commit Reconciliation",
    history: language === "ar" ? "سجل التسويات السابقة" : "Previous Reconciliations",
  };

  return (
    <Stack spacing={2} sx={{ mt: 1 }}>
      {/* High Density Header Row */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box display="flex" alignItems="center" gap={1}>
          <AccountBalanceWalletOutlinedIcon sx={{ color: "primary.main", fontSize: 24 }} />
          <Typography variant="subtitle1" fontWeight="bold">
            {text.title}
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          size="small"
          onClick={() => {
            setErrorMsg(null);
            setSuccessMsg(null);
            setIsMatchingOpen(true);
          }}
          startIcon={<AccountBalanceWalletOutlinedIcon />}
          sx={{ fontWeight: "bold", px: 2, borderRadius: 1.5 }}
        >
          {language === "ar" ? "بدء مطابقة وتسوية المدفوعات المعلقة" : "Start Reconciling Payments"}
        </Button>
      </Box>

      {/* Global notifications */}
      {successMsg && <Alert severity="success" onClose={() => setSuccessMsg(null)}>{successMsg}</Alert>}
      {errorMsg && !isMatchingOpen && !isViewOpen && !isDeleteOpen && <Alert severity="error" onClose={() => setErrorMsg(null)}>{errorMsg}</Alert>}

      {/* Reconciliations History Log Table */}
      <Card variant="outlined" sx={{ borderRadius: 1.5 }}>
        <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
          <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
            {text.history}
          </Typography>
          <Divider sx={{ mb: 1.5 }} />

          {reconciliationsQuery.isLoading ? (
            <Box display="flex" justifyContent="center" py={3}>
              <CircularProgress size={25} />
            </Box>
          ) : reconciliationsQuery.data?.length === 0 ? (
            <Typography color="text.secondary" align="center" py={2} variant="body2">
              {language === "ar" ? "لا توجد تسويات سابقة مسجلة" : "No previous reconciliations recorded."}
            </Typography>
          ) : (
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 1 }}>
              <Table size="small">
                <TableHead sx={{ backgroundColor: "action.hover" }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "الفترة الزمنية" : "Period"}</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>{text.method}</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "المستلم" : "Recipient"}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: "bold" }}>{language === "ar" ? "المتوقع" : "Expected"}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: "bold" }}>{language === "ar" ? "الفعلي" : "Actual"}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: "bold" }}>{text.diff}</TableCell>
                    <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "ملاحظات" : "Notes"}</TableCell>
                    <TableCell align="center" sx={{ fontWeight: "bold" }}>{language === "ar" ? "الإجراءات" : "Actions"}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reconciliationsQuery.data?.map((recon) => (
                    <TableRow key={recon.id} hover>
                      <TableCell>
                        {recon.start_date ? `${recon.start_date} ~ ${recon.end_date}` : recon.reconciliation_date}
                      </TableCell>
                      <TableCell>{recon.payment_method_name || "-"}</TableCell>
                      <TableCell>{recon.receiver_name || "-"}</TableCell>
                      <TableCell align="right">{formatters.formatDecimal(recon.total_expected_amount)}</TableCell>
                      <TableCell align="right">{formatters.formatDecimal(recon.total_actual_amount)}</TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          fontWeight: "bold",
                          color: recon.difference_amount === 0 ? "success.main" : "error.main",
                        }}
                      >
                        {recon.difference_amount > 0 ? "+" : ""}
                        {formatters.formatDecimal(recon.difference_amount)}
                      </TableCell>
                      <TableCell sx={{ maxWidth: 150, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {recon.notes || "-"}
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={0.5} justifyContent="center" alignItems="center">
                          <Tooltip title={language === "ar" ? "عرض تفاصيل التسوية" : "View Details"}>
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => {
                                setViewingRecon(recon);
                                setErrorMsg(null);
                                setIsViewOpen(true);
                              }}
                            >
                              <VisibilityOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>

                          {recon.is_latest ? (
                            <Tooltip title={language === "ar" ? "حذف وإلغاء التسوية" : "Delete Reconciliation"}>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => {
                                  setDeletingReconId(recon.id);
                                  setErrorMsg(null);
                                  setIsDeleteOpen(true);
                                }}
                              >
                                <DeleteOutlineOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          ) : (
                            <Tooltip title={language === "ar" ? "هذه التسوية مقفلة لحماية الدفاتر التاريخية" : "Locked (historical)"}>
                              <LockOutlinedIcon sx={{ color: "text.disabled" }} fontSize="small" />
                            </Tooltip>
                          )}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* POPUP MODAL DIALOG FOR MATCHING */}
      <AppDialogShell
        open={isMatchingOpen}
        onClose={() => setIsMatchingOpen(false)}
        title={language === "ar" ? "مطابقة وتسوية المدفوعات المعلقة" : "Pending Payments Reconcile"}
        subtitle={language === "ar" ? "حدد الفترة والنوع، وجرد المبالغ لتحديد المطابقات والفروقات." : "Select period, method and counted amounts to match."}
        maxWidth="lg"
        actions={
          <Stack direction="row" spacing={1} sx={{ width: "100%", justifyContent: "flex-end" }}>
            <Button variant="outlined" color="inherit" onClick={() => setIsMatchingOpen(false)} size="small">
              {language === "ar" ? "إلغاء" : "Cancel"}
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              size="small"
              disabled={createMutation.isPending || selectedPaymentIds.length === 0}
              startIcon={createMutation.isPending ? <CircularProgress size={16} color="inherit" /> : <CheckCircleOutlineIcon />}
            >
              {text.save}
            </Button>
          </Stack>
        }
      >
        <Stack spacing={2}>
          <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: "rgba(0, 0, 0, 0.01)" }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  select
                  size="small"
                  label={text.method}
                  value={selectedMethodId}
                  onChange={(e) => {
                    setSelectedMethodId(e.target.value);
                    setSelectedPaymentIds([]);
                    setSingleActualAmount("");
                    setHasAutoSelected("");
                  }}
                  fullWidth
                >
                  {paymentMethodsQuery.data?.map((m) => (
                    <MenuItem key={m.id} value={m.id}>
                      {m.name}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  type="date"
                  size="small"
                  label={text.start}
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(e.target.value);
                    setSelectedPaymentIds([]);
                    setSingleActualAmount("");
                    setHasAutoSelected("");
                  }}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid size={{ xs: 12, md: 4 }}>
                <TextField
                  type="date"
                  size="small"
                  label={text.end}
                  value={endDate}
                  onChange={(e) => {
                    setEndDate(e.target.value);
                    setSelectedPaymentIds([]);
                    setSingleActualAmount("");
                    setHasAutoSelected("");
                  }}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              {isCash && (
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    size="small"
                    label={text.receiver}
                    value={receiverName}
                    onChange={(e) => setReceiverName(e.target.value)}
                    placeholder={language === "ar" ? "مثال: أحمد المدير المالي" : "e.g. Finance team"}
                    fullWidth
                    required
                  />
                </Grid>
              )}

              <Grid size={{ xs: 12, md: isCash ? 6 : 12 }}>
                <TextField
                  type="number"
                  size="small"
                  label={text.actualTotal + " *"}
                  value={singleActualAmount}
                  placeholder="0"
                  onChange={(e) => {
                    const val = e.target.value;
                    if (val === "") {
                      setSingleActualAmount("");
                    } else {
                      const parsed = parseFloat(val);
                      setSingleActualAmount(isNaN(parsed) ? "" : parsed);
                    }
                  }}
                  inputProps={{ min: 0 }}
                  fullWidth
                  required
                />
              </Grid>

              <Grid size={{ xs: 12 }}>
                <TextField
                  label={text.notes}
                  size="small"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  multiline
                  rows={2}
                  fullWidth
                />
              </Grid>
            </Grid>
          </Paper>

          {errorMsg && isMatchingOpen && <Alert severity="error">{errorMsg}</Alert>}

          {pendingQuery.isLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={30} />
            </Box>
          ) : pendingItems.length === 0 ? (
            <Alert severity="info" icon={<InfoOutlinedIcon />}>
              {language === "ar" ? "لا توجد دفعات معلقة مطابقة للفترة الزمنية والتصفية المحددة." : "No pending payments found in this range."}
            </Alert>
          ) : (
            <Stack spacing={2}>
              <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 1 }}>
                <Table size="small">
                  <TableHead sx={{ backgroundColor: "action.hover" }}>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          size="small"
                          checked={pendingItems.length > 0 && selectedPaymentIds.length === pendingItems.length}
                          indeterminate={selectedPaymentIds.length > 0 && selectedPaymentIds.length < pendingItems.length}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedPaymentIds(pendingItems.map((item) => item.id));
                            } else {
                              setSelectedPaymentIds([]);
                            }
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "تاريخ الدفع" : "Date"}</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "رقم الدفعة" : "Payment #"}</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "اسم العميل" : "Customer"}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: "bold" }}>{language === "ar" ? "المبلغ المتوقع" : "Expected"}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pendingItems.map((item) => {
                      const isChecked = selectedPaymentIds.includes(item.id);
                      return (
                        <TableRow
                          key={item.id}
                          hover
                          selected={isChecked}
                          onClick={() => {
                            if (isChecked) {
                              setSelectedPaymentIds((prev) => prev.filter((id) => id !== item.id));
                            } else {
                              setSelectedPaymentIds((prev) => [...prev, item.id]);
                            }
                          }}
                          sx={{ cursor: "pointer" }}
                        >
                          <TableCell padding="checkbox">
                            <Checkbox
                              size="small"
                              checked={isChecked}
                              onChange={(e) => {
                                e.stopPropagation();
                                if (e.target.checked) {
                                  setSelectedPaymentIds((prev) => [...prev, item.id]);
                                } else {
                                  setSelectedPaymentIds((prev) => prev.filter((id) => id !== item.id));
                                }
                              }}
                            />
                          </TableCell>
                          <TableCell>{item.payment_date}</TableCell>
                          <TableCell>{item.payment_number}</TableCell>
                          <TableCell>{item.customer_name}</TableCell>
                          <TableCell align="right">{formatters.formatDecimal(item.direct_amount)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>

              <Grid container spacing={2} sx={{ p: 1.5, backgroundColor: "action.selected", borderRadius: 1 }}>
                <Grid size={{ xs: 4 }}>
                  <Typography color="text.secondary" variant="caption">{text.expectedTotal}</Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {formatters.formatDecimal(selectedPaymentsExpectedTotal)}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 4 }}>
                  <Typography color="text.secondary" variant="caption">{text.actualTotal}</Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {formatters.formatDecimal(singleActualAmount)}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 4 }}>
                  <Typography color="text.secondary" variant="caption">{text.diff}</Typography>
                  <Typography variant="body1" fontWeight="bold" color={difference === 0 ? "success.main" : "error.main"}>
                    {difference > 0 ? "+" : ""}
                    {formatters.formatDecimal(difference)}
                  </Typography>
                </Grid>
              </Grid>
            </Stack>
          )}
        </Stack>
      </AppDialogShell>

      {/* POPUP MODAL DIALOG FOR VIEW DETAILS (READ-ONLY) */}
      <AppDialogShell
        open={isViewOpen}
        onClose={() => setIsViewOpen(false)}
        title={language === "ar" ? "تفاصيل تسوية النقدية" : "Reconciliation Details"}
        subtitle={language === "ar" ? "عرض تفاصيل الحسابات والمدفوعات التي تم تسويتها في هذه العملية." : "Read-only details of matched transactions."}
        maxWidth="md"
        actions={
          <Button variant="outlined" color="primary" onClick={() => setIsViewOpen(false)} size="small">
            {language === "ar" ? "إغلاق" : "Close"}
          </Button>
        }
      >
        {viewingRecon && (
          <Stack spacing={2}>
            <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: "rgba(0, 0, 0, 0.01)" }}>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 4 }}>
                  <Typography color="text.secondary" variant="caption" display="block">{text.method}</Typography>
                  <Typography variant="body2" fontWeight="bold">{viewingRecon.payment_method_name || "-"}</Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <Typography color="text.secondary" variant="caption" display="block">{language === "ar" ? "الفترة الزمنية" : "Reconciliation Period"}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {viewingRecon.start_date ? `${viewingRecon.start_date} ~ ${viewingRecon.end_date}` : viewingRecon.reconciliation_date}
                  </Typography>
                </Grid>
                {viewingRecon.receiver_name && (
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Typography color="text.secondary" variant="caption" display="block">{language === "ar" ? "مستلم النقدية" : "Recipient"}</Typography>
                    <Typography variant="body2" fontWeight="bold">{viewingRecon.receiver_name}</Typography>
                  </Grid>
                )}
                <Grid size={{ xs: 12 }}>
                  <Typography color="text.secondary" variant="caption" display="block">{language === "ar" ? "الملاحظات" : "Notes"}</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>{viewingRecon.notes || "-"}</Typography>
                </Grid>
              </Grid>
            </Paper>

            {/* Matched Items List */}
            <Typography variant="subtitle2" fontWeight="bold" sx={{ mt: 1 }}>
              {language === "ar" ? "سندات الدفع التي تم تسويتها" : "Reconciled Payment Documents"}
            </Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 1 }}>
              <Table size="small">
                <TableHead sx={{ backgroundColor: "action.hover" }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: "bold" }}>{language === "ar" ? "رقم الدفعة" : "Payment #"}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: "bold" }}>{language === "ar" ? "المبلغ المتوقع" : "Expected"}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: "bold" }}>{language === "ar" ? "المبلغ الفعلي" : "Actual"}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {viewingRecon.items?.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell>{item.payment_number || "-"}</TableCell>
                      <TableCell align="right">{formatters.formatDecimal(item.expected_amount)}</TableCell>
                      <TableCell align="right">{formatters.formatDecimal(item.actual_amount)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Total Summaries */}
            <Grid container spacing={2} sx={{ p: 1.5, backgroundColor: "action.selected", borderRadius: 1 }}>
              <Grid size={{ xs: 4 }}>
                <Typography color="text.secondary" variant="caption">{text.expectedTotal}</Typography>
                <Typography variant="body1" fontWeight="bold">
                  {formatters.formatDecimal(viewingRecon.total_expected_amount)}
                </Typography>
              </Grid>
              <Grid size={{ xs: 4 }}>
                <Typography color="text.secondary" variant="caption">{text.actualTotal}</Typography>
                <Typography variant="body1" fontWeight="bold">
                  {formatters.formatDecimal(viewingRecon.total_actual_amount)}
                </Typography>
              </Grid>
              <Grid size={{ xs: 4 }}>
                <Typography color="text.secondary" variant="caption">{text.diff}</Typography>
                <Typography variant="body1" fontWeight="bold" color={viewingRecon.difference_amount === 0 ? "success.main" : "error.main"}>
                  {viewingRecon.difference_amount > 0 ? "+" : ""}
                  {formatters.formatDecimal(viewingRecon.difference_amount)}
                </Typography>
              </Grid>
            </Grid>
          </Stack>
        )}
      </AppDialogShell>

      {/* POPUP DIALOG FOR DELETION CONFIRMATION */}
      <AppDialogShell
        open={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        title={language === "ar" ? "حذف وإلغاء تسوية النقدية" : "Delete Reconciliation"}
        subtitle={language === "ar" ? "هل أنت متأكد من رغبتك في حذف وإلغاء هذه التسوية بالكامل؟" : "Are you sure you want to completely delete this reconciliation?"}
        maxWidth="sm"
        actions={
          <Stack direction="row" spacing={1} sx={{ width: "100%", justifyContent: "flex-end" }}>
            <Button variant="outlined" color="inherit" onClick={() => setIsDeleteOpen(false)} size="small">
              {language === "ar" ? "إلغاء" : "Cancel"}
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={() => deleteMutation.mutate(deletingReconId)}
              size="small"
              disabled={deleteMutation.isPending}
              startIcon={deleteMutation.isPending ? <CircularProgress size={16} color="inherit" /> : null}
            >
              {language === "ar" ? "نعم، احذف التسوية" : "Yes, Delete"}
            </Button>
          </Stack>
        }
      >
        <Stack spacing={1}>
          <Typography variant="body2" color="text.secondary">
            {language === "ar"
              ? "سيؤدي هذا الإجراء إلى حذف التسوية بالكامل وتحرير كافة سندات الدفع المرتبطة بها لتعود كمعلقة، مما يتيح لك إعادة جردها وتسويتها مرة أخرى."
              : "This will release all associated payment documents back to pending status for re-reconciliation."}
          </Typography>
          {errorMsg && isDeleteOpen && <Alert severity="error">{errorMsg}</Alert>}
        </Stack>
      </AppDialogShell>
    </Stack>
  );
}
