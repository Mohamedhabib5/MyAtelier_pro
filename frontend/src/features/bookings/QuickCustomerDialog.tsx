import { useState } from 'react';
import { useLanguage } from '../language/LanguageProvider';
import { CustomerFormDialog, type CustomerFormState } from '../customers/CustomerFormDialog';
import type { CustomerPayload } from '../customers/api';

const emptyForm = (): CustomerFormState => {
  const today = new Date().toISOString().split('T')[0];
  return { 
    full_name: '', 
    registration_date: today,
    groom_name: '', 
    bride_name: '', 
    phone: '', 
    phone_2: '', 
    email: '', 
    address: '', 
    notes: '', 
    is_active: true 
  };
};

export function QuickCustomerDialog({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: CustomerPayload) => Promise<void>;
}) {
  const { language } = useLanguage();
  const [form, setForm] = useState<CustomerFormState>(emptyForm());

  async function handleSubmit() {
    if (!form.bride_name.trim() && !form.groom_name.trim()) {
      alert(language === 'ar' ? 'يجب إدخال اسم العروسة أو العريس على الأقل' : 'At least Bride or Groom name is required');
      return;
    }
    if (!form.address || form.address.trim().length < 2) {
      alert('Address is required / العنوان مطلوب');
      return;
    }
    if (!form.phone || form.phone.trim().length < 3) {
      alert('Phone number is required / رقم الهاتف مطلوب');
      return;
    }

    const calculatedFullName = form.full_name || (form.groom_name && form.bride_name ? `${form.groom_name} & ${form.bride_name}` : (form.groom_name || form.bride_name || 'Customer'));
    
    await onSubmit({
      full_name: calculatedFullName,
      registration_date: form.registration_date || null,
      groom_name: form.groom_name || null,
      bride_name: form.bride_name || null,
      phone: form.phone,
      phone_2: form.phone_2 || null,
      email: form.email || null,
      address: form.address,
      notes: form.notes || null,
    });
    setForm(emptyForm());
  }

  return (
    <CustomerFormDialog 
      open={open} 
      editing={false} 
      form={form} 
      onChange={setForm} 
      onClose={onClose} 
      onSave={() => void handleSubmit()} 
    />
  );
}
