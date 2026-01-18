import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Paper,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import SettingsApplicationsIcon from '@mui/icons-material/SettingsApplications'
import EmailIcon from '@mui/icons-material/Email'
import StorageIcon from '@mui/icons-material/Storage'
import SecurityIcon from '@mui/icons-material/Security'
import NotificationsIcon from '@mui/icons-material/Notifications'
import VpnKeyIcon from '@mui/icons-material/VpnKey'

export const SystemSettings = () => {
  const navigate = useNavigate()

  const handleEmailSystemClick = () => {
    navigate('/email_accounts')
  }

  const handleProxyClick = () => {
    navigate('/proxy-settings')
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SettingsApplicationsIcon sx={{ fontSize: 32, mr: 1 }} />
        <Typography variant="h4">系统配置</Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 邮件系统配置 */}
        <Grid item xs={12} md={6}>
          <Paper
            onClick={handleEmailSystemClick}
            sx={{
              p: 3,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.3s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <EmailIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h6">邮件系统</Typography>
                <Typography variant="body2" color="text.secondary">
                  配置SMTP、IMAP服务器及邮件账户
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* 数据库配置 */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.3s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <StorageIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
              <Box>
                <Typography variant="h6">数据库配置</Typography>
                <Typography variant="body2" color="text.secondary">
                  数据备份、清理及维护设置
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* 安全设置 */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.3s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <SecurityIcon sx={{ fontSize: 40, color: 'error.main', mr: 2 }} />
              <Box>
                <Typography variant="h6">安全设置</Typography>
                <Typography variant="body2" color="text.secondary">
                  用户权限、密码策略及访问控制
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* 通知配置 */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.3s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <NotificationsIcon
                sx={{ fontSize: 40, color: 'warning.main', mr: 2 }}
              />
              <Box>
                <Typography variant="h6">通知配置</Typography>
                <Typography variant="body2" color="text.secondary">
                  邮件提醒、系统通知及消息推送
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* 代理配置 */}
        <Grid item xs={12} md={6}>
          <Paper
            onClick={handleProxyClick}
            sx={{
              p: 3,
              cursor: 'pointer',
              '&:hover': {
                boxShadow: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.3s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <VpnKeyIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
              <Box>
                <Typography variant="h6">代理配置</Typography>
                <Typography variant="body2" color="text.secondary">
                  配置网络代理用于访问国际服务
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* 系统信息 */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            系统信息
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                系统版本
              </Typography>
              <Typography variant="body1">v1.0.0</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                数据库类型
              </Typography>
              <Typography variant="body1">SQLite</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                后端框架
              </Typography>
              <Typography variant="body1">FastAPI</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                前端框架
              </Typography>
              <Typography variant="body1">React Admin</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}
