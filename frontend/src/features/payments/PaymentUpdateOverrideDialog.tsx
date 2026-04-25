import { PeriodLockOverrideDialog } from '../../components/PeriodLockOverrideDialog';

type Props = {
  open: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => Promise<void>;
};

export function PaymentUpdateOverrideDialog({ open, onClose, onConfirm }: Props) {
  return (
    <PeriodLockOverrideDialog
      open={open}
      titleAr='Override لتعديل سند الدفع'
      titleEn='Override payment update'
      descriptionAr='الفترة مقفولة. أدخل سبب Override لإتمام تعديل سند الدفع.'
      descriptionEn='Period is locked. Enter override reason to continue payment update.'
      onClose={onClose}
      onConfirm={onConfirm}
    />
  );
}
