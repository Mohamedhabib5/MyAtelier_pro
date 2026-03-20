import { Card, CardContent, Stack, Typography } from "@mui/material";

export function SectionCard({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Stack spacing={0.5}>
            <Typography variant="h6">{title}</Typography>
            {subtitle ? <Typography color="text.secondary">{subtitle}</Typography> : null}
          </Stack>
          {children}
        </Stack>
      </CardContent>
    </Card>
  );
}