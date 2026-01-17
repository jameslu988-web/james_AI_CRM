import { useState } from 'react'
import { useLogin, useNotify } from 'react-admin'
import { 
  Box, 
  Card, 
  CardContent, 
  TextField, 
  Button, 
  Typography, 
  InputAdornment,
  IconButton,
  Avatar,
  Stack,
  Alert
} from '@mui/material'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import PersonIcon from '@mui/icons-material/Person'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import BusinessIcon from '@mui/icons-material/Business'

export const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const login = useLogin()
  const notify = useNotify()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await login({ username, password })
    } catch (error) {
      notify('登录失败，请检查用户名和密码', { type: 'error' })
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%)',
        }
      }}
    >
      <Box
        sx={{
          margin: 'auto',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          zIndex: 1,
          width: '100%',
          maxWidth: '450px',
          padding: 3
        }}
      >
        {/* Logo和标题 */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            mb: 4,
            animation: 'fadeInDown 0.8s ease-out'
          }}
        >
          <Avatar
            sx={{
              width: 60,
              height: 60,
              bgcolor: 'white',
              color: '#667eea',
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
              mr: 2
            }}
          >
            <BusinessIcon sx={{ fontSize: 35 }} />
          </Avatar>
          <Box>
            <Typography
              variant="h4"
              sx={{
                color: 'white',
                fontWeight: 700,
                textShadow: '0 2px 10px rgba(0,0,0,0.2)'
              }}
            >
              外贸CRM系统
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: 'rgba(255,255,255,0.9)',
                mt: 0.5
              }}
            >
              Foreign Trade CRM System
            </Typography>
          </Box>
        </Box>

        {/* 登录卡片 */}
        <Card
          sx={{
            width: '100%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            borderRadius: 3,
            animation: 'fadeInUp 0.8s ease-out'
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Avatar
                sx={{
                  width: 56,
                  height: 56,
                  margin: '0 auto',
                  bgcolor: 'primary.main',
                  mb: 2
                }}
              >
                <LockOutlinedIcon />
              </Avatar>
              <Typography variant="h5" sx={{ fontWeight: 600, color: 'text.primary' }}>
                欢迎登录
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                请输入您的账号密码
              </Typography>
            </Box>

            {/* 演示账号提示 */}
            <Alert severity="info" sx={{ mb: 3, fontSize: '0.875rem' }}>
              <strong>演示账号：</strong>
              <br />
              管理员：admin / admin123
              <br />
              业务员：sales01 / sales123
            </Alert>

            <form onSubmit={handleSubmit}>
              <Stack spacing={2.5}>
                <TextField
                  fullWidth
                  label="用户名"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      '&:hover fieldset': {
                        borderColor: 'primary.main',
                      },
                    },
                  }}
                />

                <TextField
                  fullWidth
                  label="密码"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LockOutlinedIcon color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      '&:hover fieldset': {
                        borderColor: 'primary.main',
                      },
                    },
                  }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={loading}
                  sx={{
                    height: 48,
                    fontSize: '1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      boxShadow: '0 6px 20px rgba(102, 126, 234, 0.6)',
                      transform: 'translateY(-2px)',
                      transition: 'all 0.3s ease',
                    },
                    '&:disabled': {
                      background: '#ccc',
                    }
                  }}
                >
                  {loading ? '登录中...' : '登 录'}
                </Button>
              </Stack>
            </form>
          </CardContent>
        </Card>

        {/* 页脚 */}
        <Typography
          variant="body2"
          sx={{
            color: 'rgba(255,255,255,0.8)',
            mt: 4,
            textAlign: 'center'
          }}
        >
          © 2026 外贸CRM系统. All rights reserved.
        </Typography>
      </Box>

      {/* CSS动画 */}
      <style>{`
        @keyframes fadeInDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </Box>
  )
}
