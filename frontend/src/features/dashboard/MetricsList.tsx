import { List, ListItem, ListItemText, Typography } from '@mui/material';

import { useLanguage } from '../language/LanguageProvider';

export type SummaryValueItem = {
  label: string;
  value: string;
};

export function MetricsList({ items, emptyLabel }: { items: SummaryValueItem[]; emptyLabel: string }) {
  const { textAlign } = useLanguage();
  if (items.length === 0) {
    return <Typography color='text.secondary'>{emptyLabel}</Typography>;
  }

  return (
    <List disablePadding>
      {items.map((item) => (
        <ListItem key={`${item.label}-${item.value}`} disableGutters divider sx={{ py: 1.25 }}>
          <ListItemText primary={item.label} secondary={item.value} slotProps={{ primary: { sx: { textAlign, fontWeight: 600 } }, secondary: { sx: { textAlign } } }} />
        </ListItem>
      ))}
    </List>
  );
}
