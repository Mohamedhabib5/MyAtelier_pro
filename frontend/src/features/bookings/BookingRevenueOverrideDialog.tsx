import { PeriodLockOverrideDialog } from '../../components/PeriodLockOverrideDialog';

type Props = {
  open: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => Promise<void>;
};

export function BookingRevenueOverrideDialog({ open, onClose, onConfirm }: Props) {
  return (
    <PeriodLockOverrideDialog
      open={open}
      titleAr='Override لعكس الإيراد'
      titleEn='Override revenue reversal'
      descriptionAr='الفترة مقفولة. أدخل سبب Override لتنفيذ عكس الإيراد.'
      descriptionEn='Period is locked. Enter override reason to reverse revenue.'
      onClose={onClose}
      onConfirm={onConfirm}
    />
  );
}
