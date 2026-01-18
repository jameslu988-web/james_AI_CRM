import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material'
import { useState, useEffect } from 'react'
import VpnKeyIcon from '@mui/icons-material/VpnKey'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { useNavigate } from 'react-router-dom'
import { getApiUrl } from './config/api'

export const ProxySettings = () => {
  const navigate = useNavigate()
  const [proxyUrl, setProxyUrl] = useState('socks5://127.0.0.1:10808')
  const [testing, setTesting] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testResult, setTestResult] = useState<{success: boolean, message: string} | null>(null)
  const [saveResult, setSaveResult] = useState<{success: boolean, message: string} | null>(null)

  // 加载代理配置
  useEffect(() => {
    fetch(getApiUrl('crm', '/prospecting/proxy-config'))
      .then(r => r.json())
      .then(data => {
        if (data.proxy_url) {
          setProxyUrl(data.proxy_url)
        }
      })
      .catch(() => {})
  }, [])

  const handleTestProxy = async () => {
    setTesting(true)
    setTestResult(null)
    
    try {
      const response = await fetch(getApiUrl('crm', '/prospecting/test-proxy'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proxy_url: proxyUrl })
      })
      
      const result = await response.json()
      setTestResult(result)
    } catch (error: any) {
      setTestResult({
        success: false,
        message: `测试失败: ${error.message}`
      })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveResult(null)
    
    try {
      const response = await fetch(getApiUrl('crm', '/prospecting/proxy-config'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          proxy_url: proxyUrl,
          enabled: true 
        })
      })
      
      const result = await response.json()
      
      if (result.success) {
        setSaveResult({ success: true, message: '代理配置已保存' })
        // 也保存到localStorage作为备份
        localStorage.setItem('proxy_url', proxyUrl)
      } else {
        setSaveResult({ success: false, message: '保存失败' })
      }
    } catch (error: any) {
      setSaveResult({ success: false, message: `保存失败: ${error.message}` })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* 返回按钮 */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/system-settings')}
        sx={{ mb: 2 }}
      >
        返回系统配置
      </Button>

      {/* 页面标题 */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <VpnKeyIcon sx={{ fontSize: 32, mr: 1, color: 'primary.main' }} />
        <Typography variant="h4">代理配置</Typography>
      </Box>

      {/* 配置表单 */}
      <Card>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            配置代理服务器用于访问 Google 和其他国际服务，支持 SOCKS5 和 HTTP 代理。
          </Typography>
          
          <TextField
            fullWidth
            label="代理服务器地址"
            value={proxyUrl}
            onChange={(e) => setProxyUrl(e.target.value)}
            placeholder="socks5://127.0.0.1:10808"
            helperText="格式：socks5://IP:端口 或 http://IP:端口"
            sx={{ mb: 3 }}
          />
          
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              variant="outlined"
              onClick={handleTestProxy}
              disabled={testing || !proxyUrl}
            >
              {testing ? <CircularProgress size={24} /> : '测试连接'}
            </Button>
            <Button
              variant="contained"
              onClick={handleSave}
              disabled={saving || !proxyUrl}
            >
              {saving ? <CircularProgress size={24} /> : '保存配置'}
            </Button>
          </Box>
          
          {testResult && (
            <Alert 
              severity={testResult.success ? 'success' : 'error'}
              sx={{ mb: 2 }}
            >
              {testResult.message}
            </Alert>
          )}
          
          {saveResult && (
            <Alert 
              severity={saveResult.success ? 'success' : 'error'}
              sx={{ mb: 2 }}
            >
              {saveResult.message}
            </Alert>
          )}
          
          {/* 说明信息 */}
          <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
            <Typography variant="subtitle2" gutterBottom>
              常用代理软件配置：
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • V2RayN: 默认 socks5://127.0.0.1:10808<br/>
              • Clash: 默认 http://127.0.0.1:7890<br/>
              • Shadowsocks: 默认 socks5://127.0.0.1:1080<br/>
              • 其他: 请查看代理软件设置中的本地端口
            </Typography>
          </Paper>
        </CardContent>
      </Card>

      {/* 使用说明 */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            使用说明
          </Typography>
          <Typography variant="body2" color="text.secondary" component="div">
            1. 确保你的代理软件（如 V2RayN、Clash）已经启动<br/>
            2. 在上方输入框中填入代理地址<br/>
            3. 点击"测试连接"验证代理是否可用<br/>
            4. 测试成功后点击"保存配置"<br/>
            5. 保存后，系统将使用该代理访问 Google 等国际服务
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}
