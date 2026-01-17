import { Card, CardContent, Typography, Box } from '@mui/material'

export const CustomerSettings = () => {
  return (
    <Box sx={{ pl: 3, pt: 2 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            客户设置
          </Typography>
          <Typography variant="body2" color="text.secondary">
            客户设置功能开发中...
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}
