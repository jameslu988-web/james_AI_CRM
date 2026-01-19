import {
  List,
  Datagrid,
  TextField,
  BooleanField,
  DateField,
  Edit,
  SimpleForm,
  TextInput,
  BooleanInput,
  NumberInput,
  SelectInput,
  required,
  useRecordContext,
  FunctionField,
  TopToolbar,
  ExportButton,
  useNotify,
  useRefresh,
  Button as RAButton,
  Show,
  SimpleShowLayout,
  NumberField,
  EditButton,
} from 'react-admin'
import { Card, CardContent, Chip, Box, Button, Drawer, IconButton, TextField as MuiTextField, MenuItem, Typography, Switch, FormControlLabel } from '@mui/material'
import { useState, useEffect } from 'react'
import SyncIcon from '@mui/icons-material/Sync'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import EmailIcon from '@mui/icons-material/Email'
import ToggleOnIcon from '@mui/icons-material/ToggleOn'
import ToggleOffIcon from '@mui/icons-material/ToggleOff'
import CloseIcon from '@mui/icons-material/Close'
import SendIcon from '@mui/icons-material/Send'

// 邮箱服务商选项
const providerChoices = [
  { id: 'gmail', name: 'Gmail' },
  { id: 'outlook', name: 'Outlook/Hotmail' },
  { id: 'qq', name: 'QQ邮箱' },
  { id: '163', name: '163邮箱' },
  { id: 'aliyun', name: '阿里云邮箱' },
  { id: 'yahoo', name: 'Yahoo邮箱' },
  { id: 'custom', name: '自定义IMAP' },
]

// 同步状态徽章
const SyncStatusField = () => {
  const record = useRecordContext()
  if (!record) return null

  const statusColors: any = {
    active: 'success',
    paused: 'warning',
    error: 'error',
  }

  const statusLabels: any = {
    active: '正常',
    paused: '暂停',
    error: '错误',
  }

  return (
    <Chip
      label={statusLabels[record.sync_status] || record.sync_status}
      color={statusColors[record.sync_status] || 'default'}
      size="small"
    />
  )
}

// 同步按钮
const SyncButton = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const refresh = useRefresh()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [syncConfig, setSyncConfig] = useState({
    limit: 100,
    only_unseen: true,  // 默认只同步未读
    since_date: '',
  })
  const [syncing, setSyncing] = useState(false)

  const handleSync = async () => {
    setSyncing(true)
    try {
      const token = localStorage.getItem('token')
      
      // 构建查询参数
      const params = new URLSearchParams({
        limit: syncConfig.limit.toString(),
        only_unseen: syncConfig.only_unseen.toString(),
      })
      
      if (syncConfig.since_date) {
        params.append('since_date', syncConfig.since_date)
      }
      
      const response = await fetch(
        `http://127.0.0.1:8001/api/email_accounts/${record.id}/sync?${params}`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('同步失败')
      }

      const result = await response.json()
      notify(result.message || '邮件同步已开始，请稍后查看邮件历史', { type: 'success' })
      setDrawerOpen(false)
      refresh()
    } catch (error) {
      notify('同步邮件失败', { type: 'error' })
    } finally {
      setSyncing(false)
    }
  }

  const handleClick = (e: any) => {
    e.stopPropagation() // 阻止事件冒泡
    setDrawerOpen(true)
  }

  return (
    <>
      <RAButton
        label="同步邮件"
        onClick={handleClick}
        startIcon={<SyncIcon />}
        size="small"
      />
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 500, p: 3, height: '100vh', overflow: 'auto' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">配置邮件同步</Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  邮箱账户
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {record.account_name} ({record.email_address})
                </Typography>
              </CardContent>
            </Card>

            <MuiTextField
              label="同步数量"
              type="number"
              value={syncConfig.limit}
              onChange={(e) => setSyncConfig({ ...syncConfig, limit: parseInt(e.target.value) || 0 })}
              helperText="设为0则同步所有邮件（可能需要较长时间）"
              fullWidth
            />
            
            <MuiTextField
              label="从哪个日期开始同步"
              type="date"
              value={syncConfig.since_date}
              onChange={(e) => setSyncConfig({ ...syncConfig, since_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              helperText="留空则同步所有日期的邮件"
              fullWidth
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={syncConfig.only_unseen}
                  onChange={(e) => setSyncConfig({ ...syncConfig, only_unseen: e.target.checked })}
                />
              }
              label="只同步未读邮件（推荐）"
            />
            
            <Card variant="outlined" sx={{ bgcolor: '#f0f9ff' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  <strong>ℹ️ 提示：</strong>
                  <br />
                  • 邮件同步为后台任务，不会阻塞其他操作
                  <br />
                  • 同步期间您可以继续访问其他页面
                  <br />
                  • 同步完成后请刷新邮件历史页面
                  <br />
                  • <strong>首次同步会自动限制为最近30天</strong>
                  <br />
                  • 已同步的邮件会自动去重，不用担心重复
                </Typography>
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button onClick={() => setDrawerOpen(false)} fullWidth>
                取消
              </Button>
              <Button 
                onClick={handleSync} 
                variant="contained" 
                fullWidth
                disabled={syncing}
              >
                {syncing ? '同步中...' : '开始同步'}
              </Button>
            </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  )
}

// 测试IMAP连接按钮
const TestButton = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/email_accounts/${record.id}/test`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const result = await response.json()
      setTestResult(result)

      if (result.success) {
        notify(`IMAP连接成功！找到 ${result.mailbox_count} 个邮箱文件夹`, {
          type: 'success',
        })
      } else {
        notify('IMAP连接失败，请检查配置', { type: 'error' })
      }
    } catch (error) {
      notify('IMAP测试失败', { type: 'error' })
      setTestResult({ success: false, message: 'IMAP测试失败' })
    } finally {
      setTesting(false)
    }
  }

  const handleClick = (e: any) => {
    e.stopPropagation() // 阻止事件冒泡
    setDrawerOpen(true)
  }

  return (
    <>
      <RAButton
        label="测试连接"
        onClick={handleClick}
        startIcon={<CheckCircleIcon />}
        size="small"
      />
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 500, p: 3, height: '100vh', overflow: 'auto' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">测试邮箱连接</Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  邮箱账户信息
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>账户名称：</strong>{record.account_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>邮箱地址：</strong>{record.email_address}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>IMAP服务器：</strong>{record.imap_host}:{record.imap_port}
                </Typography>
              </CardContent>
            </Card>

            {testResult && (
              <Card variant="outlined" sx={{ bgcolor: testResult.success ? '#f0fdf4' : '#fef2f2' }}>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    {testResult.success ? '✅ 测试成功' : '❌ 测试失败'}
                  </Typography>
                  {testResult.success && (
                    <>
                      <Typography variant="body2" color="text.secondary">
                        {testResult.message || `找到 ${testResult.mailbox_count} 个邮箱文件夹`}
                      </Typography>
                      
                      {/* 显示测试步骤详情 */}
                      {testResult.details && testResult.details.length > 0 && (
                        <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(0,0,0,0.02)', borderRadius: 1 }}>
                          <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>测试步骤:</Typography>
                          {testResult.details.map((detail: string, idx: number) => (
                            <Typography key={idx} variant="caption" sx={{ display: 'block', color: '#666', lineHeight: 1.6 }}>
                              {detail}
                            </Typography>
                          ))}
                        </Box>
                      )}
                      
                      {testResult.mailboxes && testResult.mailboxes.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            可用文件夹（前10个）：
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {testResult.mailboxes.map((folder: string, idx: number) => (
                              <Chip key={idx} label={folder} size="small" />
                            ))}
                          </Box>
                        </Box>
                      )}
                    </>
                  )}
                  {!testResult.success && (
                    <Box>
                      <Typography variant="body2" color="error" sx={{ mb: 2 }}>
                        {testResult.message || '连接失败，请检查配置'}
                      </Typography>
                      
                      {/* 显示详细错误信息 */}
                      {testResult.details && testResult.details.length > 0 && (
                        <Box sx={{ 
                          mt: 2, 
                          p: 2, 
                          bgcolor: 'rgba(220,38,38,0.05)', 
                          borderRadius: 1,
                          border: '1px solid rgba(220,38,38,0.2)'
                        }}>
                          {testResult.details.map((detail: string, idx: number) => (
                            <Typography 
                              key={idx} 
                              variant="body2" 
                              sx={{ 
                                display: 'block', 
                                color: detail.startsWith('❌') || detail.startsWith('可能原因') || detail.startsWith('解决方案') ? '#991b1b' : '#666',
                                fontWeight: detail.startsWith('❌') || detail.startsWith('可能原因') || detail.startsWith('解决方案') ? 600 : 400,
                                lineHeight: 1.8,
                                fontFamily: detail.startsWith('  ') ? 'monospace' : 'inherit',
                                whiteSpace: 'pre-wrap'
                              }}
                            >
                              {detail}
                            </Typography>
                          ))}
                        </Box>
                      )}
                      
                      {/* 错误类型标签 */}
                      {testResult.error_type && (
                        <Box sx={{ mt: 2 }}>
                          <Chip 
                            label={`错误类型: ${testResult.error_type}`} 
                            size="small" 
                            color="error" 
                            variant="outlined"
                          />
                        </Box>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}

            <Card variant="outlined" sx={{ bgcolor: '#f0f9ff' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  <strong>ℹ️ 提示：</strong>
                  <br />
                  • 测试将验证IMAP服务器连接
                  <br />
                  • 检查用户名和密码是否正确
                  <br />
                  • 确保网络可以访问邮件服务器
                </Typography>
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button onClick={() => setDrawerOpen(false)} fullWidth>
                关闭
              </Button>
              <Button 
                onClick={handleTest} 
                variant="contained" 
                fullWidth
                disabled={testing}
              >
                {testing ? '测试中...' : '开始测试'}
              </Button>
            </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  )
}

// 测试SMTP连接按钮
const TestSMTPButton = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/email_accounts/${record.id}/test_smtp`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const result = await response.json()
      setTestResult(result)

      if (result.success) {
        notify('SMTP连接成功！', { type: 'success' })
      } else {
        notify('SMTP连接失败', { type: 'error' })
      }
    } catch (error) {
      notify('SMTP测试失败', { type: 'error' })
      setTestResult({ success: false, message: 'SMTP测试失败' })
    } finally {
      setTesting(false)
    }
  }

  const handleClick = (e: any) => {
    e.stopPropagation()
    setDrawerOpen(true)
  }

  return (
    <>
      <RAButton
        label="测试SMTP"
        onClick={handleClick}
        startIcon={<SendIcon />}
        size="small"
        color="warning"
      />
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 500, p: 3, height: '100vh', overflow: 'auto' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">测试SMTP连接</Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  SMTP配置信息
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>邮箱地址：</strong>{record.email_address}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>SMTP服务器：</strong>{record.smtp_host || '未配置'}:{record.smtp_port || 465}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>用户名：</strong>{record.smtp_username || record.email_address}
                </Typography>
              </CardContent>
            </Card>

            {testResult && (
              <Card variant="outlined" sx={{ bgcolor: testResult.success ? '#f0fdf4' : '#fef2f2' }}>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    {testResult.success ? '✅ 测试成功' : '❌ 测试失败'}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: testResult.success ? 'success.main' : 'error.main' }}>
                    {testResult.message}
                  </Typography>
                  {testResult.connection_type && (
                    <Box sx={{ mt: 2 }}>
                      <Chip label={`连接类型: ${testResult.connection_type}`} size="small" color="success" />
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}

            <Card variant="outlined" sx={{ bgcolor: '#fff8f0', border: '1px solid #ffe0b2' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  <strong>⚠️ 提示：</strong>
                  <br />
                  • 测试将验证SMTP服务器连接和认证
                  <br />
                  • 确保SMTP密码/授权码正确
                  <br />
                  • QQ/163邮箱需使用“授权码”
                  <br />
                  • Gmail需使用“应用专用密码”
                </Typography>
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button onClick={() => setDrawerOpen(false)} fullWidth>
                关闭
              </Button>
              <Button 
                onClick={handleTest} 
                variant="contained"
                color="warning"
                fullWidth
                disabled={testing || !record.smtp_host}
              >
                {testing ? '测试中...' : '开始测试'}
              </Button>
            </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  )
}

// 启用/禁用按钮
const ToggleButton = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const refresh = useRefresh()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [toggling, setToggling] = useState(false)

  const handleToggle = async () => {
    setToggling(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/email_accounts/${record.id}/toggle`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const result = await response.json()
      notify(result.message, { type: 'success' })
      setDrawerOpen(false)
      refresh()
    } catch (error) {
      notify('操作失败', { type: 'error' })
    } finally {
      setToggling(false)
    }
  }

  const handleClick = (e: any) => {
    e.stopPropagation() // 阻止事件冒泡
    setDrawerOpen(true)
  }

  return (
    <>
      <RAButton
        label={record.is_active ? '禁用' : '启用'}
        onClick={handleClick}
        startIcon={record.is_active ? <ToggleOffIcon /> : <ToggleOnIcon />}
        size="small"
      />
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 500, p: 3, height: '100vh', overflow: 'auto' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              {record.is_active ? '禁用邮箱账户' : '启用邮箱账户'}
            </Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  邮箱账户信息
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>账户名称：</strong>{record.account_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>邮箱地址：</strong>{record.email_address}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>当前状态：</strong>
                  <Chip 
                    label={record.is_active ? '已启用' : '已禁用'} 
                    color={record.is_active ? 'success' : 'default'} 
                    size="small" 
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </CardContent>
            </Card>

            <Card variant="outlined" sx={{ bgcolor: record.is_active ? '#fef2f2' : '#f0fdf4' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  {record.is_active ? '⚠️ 禁用后的影响' : '✅ 启用后的效果'}
                </Typography>
                {record.is_active ? (
                  <>
                    <Typography variant="body2" color="text.secondary">
                      • 停止自动同步邮件
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • 无法手动同步邮件
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • 已同步的邮件不会受影响
                    </Typography>
                  </>
                ) : (
                  <>
                    <Typography variant="body2" color="text.secondary">
                      • 恢复自动同步邮件功能
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • 可以手动同步邮件
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      • 开始接收新邮件
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button onClick={() => setDrawerOpen(false)} fullWidth>
                取消
              </Button>
              <Button 
                onClick={handleToggle} 
                variant="contained" 
                color={record.is_active ? 'error' : 'success'}
                fullWidth
                disabled={toggling}
              >
                {toggling ? '处理中...' : (record.is_active ? '确认禁用' : '确认启用')}
              </Button>
            </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  )
}

// 列表页面
const ListActions = () => {
  const [createOpen, setCreateOpen] = useState(false)
  
  return (
    <>
      <TopToolbar>
        <Button variant="contained" onClick={() => setCreateOpen(true)}>
          + 添加邮箱账户
        </Button>
        <ExportButton label="导出" />
      </TopToolbar>
      <CreateDrawer open={createOpen} onClose={() => setCreateOpen(false)} />
    </>
  )
}

export const EmailAccountList = () => (
  <List actions={<ListActions />} title="邮箱账户管理">
    <Datagrid rowClick={false} bulkActionButtons={false}>
      <TextField source="account_name" label="账户名称" />
      <TextField source="email_address" label="邮箱地址" />
      <FunctionField
        label="服务商"
        render={(record: any) => {
          const provider = providerChoices.find((p) => p.id === record.provider)
          return provider ? provider.name : record.provider
        }}
      />
      <BooleanField source="is_active" label="启用状态" />
      <SyncStatusField />
      <DateField source="last_sync_at" label="最后同步" showTime />
      <NumberField source="total_received" label="接收邮件数" />
      <FunctionField
        label="操作"
        render={() => (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <EditButton label="编辑" />
            <TestButton />
            <TestSMTPButton />
            <SyncButton />
            <ToggleButton />
          </Box>
        )}
      />
    </Datagrid>
  </List>
)

// 创建抽屉
const CreateDrawer = ({ open, onClose }: any) => {
  const notify = useNotify()
  const refresh = useRefresh()
  const [formData, setFormData] = useState<any>({
    imap_port: 993,
    smtp_port: 465,
    smtp_host: '',
    smtp_username: '',
    smtp_password: '',
    auto_sync: true,
    sync_interval: 5,
    sync_mode: 'unread_only',  // 默认只同步未读
    auto_match_customer: true,
    auto_create_followup: true
  })

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/email_accounts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        notify('邮箱账户创建成功', { type: 'success' })
        onClose()
        refresh()
        setFormData({
          imap_port: 993,
          smtp_port: 465,
          smtp_host: '',
          smtp_username: '',
          smtp_password: '',
          auto_sync: true,
          sync_interval: 5,
          sync_mode: 'unread_only',
          auto_match_customer: true,
          auto_create_followup: true
        })
      } else {
        const error = await response.json()
        notify(error.detail || '创建失败', { type: 'error' })
      }
    } catch (e) {
      notify('网络错误', { type: 'error' })
    }
  }

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 500, p: 3, height: '100vh', overflow: 'auto' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">添加邮箱账户</Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ mb: 2, color: 'info.main', display: 'flex', alignItems: 'center' }}>
              <EmailIcon sx={{ mr: 1 }} />
              <strong>配置说明：</strong>
            </Box>
            <Box sx={{ pl: 2, fontSize: '0.875rem', color: 'text.secondary' }}>
              • Gmail需要使用“应用专用密码”，在
              <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer">
                这里生成
              </a>
              <br />
              • QQ/163邮箱需要开启IMAP服务并使用“授权码”
              <br />
              • Outlook可直接使用账户密码
              <br />
              • 阿里云企业邮箱直接使用邮箱密码
            </Box>
          </CardContent>
        </Card>

        <MuiTextField
          fullWidth
          label="账户名称"
          value={formData.account_name || ''}
          onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
          helperText="例如：公司主邮箱、销售部邮箱"
          sx={{ mb: 2 }}
          required
        />

        <MuiTextField
          fullWidth
          label="邮箱地址"
          type="email"
          value={formData.email_address || ''}
          onChange={(e) => setFormData({ ...formData, email_address: e.target.value })}
          sx={{ mb: 2 }}
          required
        />

        <MuiTextField
          fullWidth
          select
          label="邮箱服务商"
          value={formData.provider || ''}
          onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
          sx={{ mb: 2 }}
          required
        >
          {providerChoices.map((choice) => (
            <MenuItem key={choice.id} value={choice.id}>
              {choice.name}
            </MenuItem>
          ))}
        </MuiTextField>

        <MuiTextField
          fullWidth
          label="IMAP密码/授权码"
          type="password"
          value={formData.imap_password || ''}
          onChange={(e) => setFormData({ ...formData, imap_password: e.target.value })}
          helperText="Gmail使用应用专用密码，QQ/163使用授权码"
          sx={{ mb: 2 }}
          required
        />

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 1.5, fontWeight: 600, color: '#1976d2' }}>
          IMAP配置（接收邮件）
        </Typography>

        <MuiTextField
          fullWidth
          label="IMAP服务器（可选）"
          value={formData.imap_host || ''}
          onChange={(e) => setFormData({ ...formData, imap_host: e.target.value })}
          helperText="选择服务商后会自动填充，自定义时才需要手动填写"
          sx={{ mb: 2 }}
        />

        <MuiTextField
          fullWidth
          label="IMAP端口"
          type="number"
          value={formData.imap_port || 993}
          onChange={(e) => setFormData({ ...formData, imap_port: parseInt(e.target.value) })}
          helperText="通常为993（SSL）或143（TLS）"
          sx={{ mb: 2 }}
        />

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 1.5, fontWeight: 600, color: '#d32f2f' }}>
          SMTP配置（发送邮件）
        </Typography>

        <Card sx={{ mb: 2, bgcolor: '#fff3e0' }}>
          <CardContent sx={{ py: 1.5 }}>
            <Typography variant="body2" color="text.secondary">
              ⚠️ <strong>重要：</strong>如果需要发送邮件，必须配置SMTP。如果只接收邮件，可以留空。
            </Typography>
          </CardContent>
        </Card>

        <MuiTextField
          fullWidth
          label="SMTP服务器"
          value={formData.smtp_host || ''}
          onChange={(e) => setFormData({ ...formData, smtp_host: e.target.value })}
          helperText="例如：smtp.gmail.com 或 smtp.exmail.qq.com"
          sx={{ mb: 2 }}
        />

        <MuiTextField
          fullWidth
          label="SMTP端口"
          type="number"
          value={formData.smtp_port || 465}
          onChange={(e) => setFormData({ ...formData, smtp_port: parseInt(e.target.value) })}
          helperText="通常为465（SSL）或587（TLS）"
          sx={{ mb: 2 }}
        />

        <MuiTextField
          fullWidth
          label="SMTP用户名（可选）"
          value={formData.smtp_username || ''}
          onChange={(e) => setFormData({ ...formData, smtp_username: e.target.value })}
          helperText="通常与邮箱地址相同，留空则自动使用邮箱地址"
          sx={{ mb: 2 }}
        />

        <MuiTextField
          fullWidth
          label="SMTP密码/授权码（可选）"
          type="password"
          value={formData.smtp_password || ''}
          onChange={(e) => setFormData({ ...formData, smtp_password: e.target.value })}
          helperText="通常与IMAP密码相同，留空则使用IMAP密码"
          sx={{ mb: 2 }}
        />

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 1.5, fontWeight: 600, color: '#1976d2' }}>
          同步设置
        </Typography>

        <MuiTextField
          fullWidth
          label="同步间隔（分钟）"
          type="number"
          value={formData.sync_interval || 5}
          onChange={(e) => setFormData({ ...formData, sync_interval: parseInt(e.target.value) })}
          sx={{ mb: 2 }}
        />

        <MuiTextField
          fullWidth
          select
          label="同步模式"
          value={formData.sync_mode || 'unread_only'}
          onChange={(e) => setFormData({ ...formData, sync_mode: e.target.value })}
          helperText="推荐使用“只同步未读”模式"
          sx={{ mb: 3 }}
        >
          <MenuItem value="unread_only">⚡ 只同步未读邮件（推荐）</MenuItem>
          <MenuItem value="recent_30days">📦 最近30天所有邮件</MenuItem>
          <MenuItem value="all">🗄️ 同步全部历史邮件</MenuItem>
        </MuiTextField>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
          <Button variant="outlined" onClick={onClose}>
            取消
          </Button>
          <Button variant="contained" onClick={handleSubmit}>
            创建
          </Button>
        </Box>
      </Box>
    </Drawer>
  )
}

// 保留空的Create组件以兼容路由
export const EmailAccountCreate = () => null

// 编辑页面 - 超紧凑单屏布局
export const EmailAccountEdit = () => (
  <Edit title="编辑邮箱账户">
    <SimpleForm sx={{ 
      '& .RaSimpleForm-content': { 
        maxWidth: '1200px',
        '& > div': { mb: '0 !important' },
        '& .MuiFormControl-root': { mb: '0 !important' },
        '& .MuiFormHelperText-root': { display: 'none' }
      } 
    }}>
      {/* 基本信息 - 单行3列 */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 1.5, mb: 1.5 }}>
        <TextInput source="account_name" label="账户名称" helperText={false} size="small" />
        <TextInput source="email_address" label="邮箱地址" disabled helperText={false} size="small" />
        <SelectInput
          source="provider"
          label="邮箱服务商"
          choices={providerChoices}
          helperText={false}
          size="small"
        />
      </Box>

      {/* IMAP和SMTP并排 */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5, mb: 1.5 }}>
        {/* IMAP配置 */}
        <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 1, fontWeight: 600, color: '#1976d2', fontSize: '0.875rem' }}>
            📥 IMAP（接收）
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <TextInput
              source="imap_host"
              label="服务器"
              helperText={false}
              placeholder="imap.gmail.com"
              size="small"
              fullWidth
            />
            <Box sx={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 1 }}>
              <TextInput
                source="imap_password"
                label="密码/授权码"
                type="password"
                helperText={false}
                placeholder="留空不修改"
                size="small"
              />
              <NumberInput source="imap_port" label="端口" helperText={false} size="small" />
            </Box>
          </Box>
        </Box>

        {/* SMTP配置 */}
        <Box sx={{ bgcolor: '#fff8f0', p: 1.5, borderRadius: 1, border: '1px solid #ffe0b2' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#d32f2f', fontSize: '0.875rem' }}>
              📤 SMTP（发送）
            </Typography>
            <Chip label="必填" size="small" color="warning" sx={{ height: '20px', fontSize: '0.7rem' }} />
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <TextInput source="smtp_host" label="服务器" helperText={false} placeholder="smtp.gmail.com" size="small" fullWidth />
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr', gap: 1 }}>
              <NumberInput source="smtp_port" label="端口" helperText={false} defaultValue={465} size="small" />
              <TextInput source="smtp_username" label="用户名" helperText={false} placeholder="可选" size="small" />
              <TextInput
                source="smtp_password"
                label="密码/授权码"
                type="password"
                helperText={false}
                placeholder="留空不修改"
                size="small"
              />
            </Box>
          </Box>
        </Box>
      </Box>

      {/* 同步设置、状态设置、高级选项 - 3列布局 */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 1.5 }}>
        {/* 同步设置 */}
        <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 1, fontWeight: 600, color: '#1976d2', fontSize: '0.875rem' }}>
            🔄 同步设置
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0, '& > div': { mb: '0 !important' } }}>
            <BooleanInput source="auto_sync" label="自动同步" sx={{ '& .MuiFormControlLabel-root': { mb: 0 } }} />
            <NumberInput
              source="sync_interval"
              label="间隔（分钟）"
              min={1}
              max={60}
              helperText={false}
              size="small"
              sx={{ width: '100%' }}
            />
            <SelectInput
              source="sync_mode"
              label="同步模式"
              choices={[
                { id: 'unread_only', name: '⚡ 只同步未读（推荐）' },
                { id: 'recent_30days', name: '📦 最近30天所有' },
                { id: 'all', name: '🗄️ 全部历史邮件' },
              ]}
              helperText={false}
              size="small"
              defaultValue="unread_only"
              sx={{ width: '100%' }}
            />
          </Box>
        </Box>

        {/* 高级选项 */}
        <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 1, fontWeight: 600, color: '#1976d2', fontSize: '0.875rem' }}>
            🔧 高级选项
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0, '& > div': { mb: '0 !important' } }}>
            <BooleanInput source="auto_match_customer" label="自动匹配客户" sx={{ '& .MuiFormControlLabel-root': { mb: 0 } }} />
            <BooleanInput source="auto_create_followup" label="自动创建跟进" sx={{ '& .MuiFormControlLabel-root': { mb: 0 } }} />
          </Box>
        </Box>

        {/* 状态设置 */}
        <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
          <Typography variant="body2" sx={{ mb: 1, fontWeight: 600, color: '#1976d2', fontSize: '0.875rem' }}>
            ⚙️ 状态
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0, '& > div': { mb: '0 !important' } }}>
            <BooleanInput source="is_active" label="启用" sx={{ '& .MuiFormControlLabel-root': { mb: 0 } }} />
            <BooleanInput source="is_default" label="默认账户" sx={{ '& .MuiFormControlLabel-root': { mb: 0 } }} />
          </Box>
        </Box>
      </Box>
    </SimpleForm>
  </Edit>
)

// 详情页面
export const EmailAccountShow = () => (
  <Show title="邮箱账户详情">
    <SimpleShowLayout>
      <TextField source="account_name" label="账户名称" />
      <TextField source="email_address" label="邮箱地址" />
      <FunctionField
        label="服务商"
        render={(record: any) => {
          const provider = providerChoices.find((p) => p.id === record.provider)
          return provider ? provider.name : record.provider
        }}
      />
      <TextField source="imap_host" label="IMAP服务器" />
      <NumberField source="imap_port" label="IMAP端口" />
      <BooleanField source="auto_sync" label="自动同步" />
      <NumberField source="sync_interval" label="同步间隔（分钟）" />
      <SyncStatusField />
      <DateField source="last_sync_at" label="最后同步时间" showTime />
      <BooleanField source="auto_match_customer" label="自动匹配客户" />
      <BooleanField source="auto_create_followup" label="自动创建跟进" />
      <NumberField source="total_received" label="接收邮件总数" />
      <NumberField source="total_sent" label="发送邮件总数" />
      <BooleanField source="is_active" label="启用状态" />
      <BooleanField source="is_default" label="默认账户" />
      <DateField source="created_at" label="创建时间" showTime />
      <DateField source="updated_at" label="更新时间" showTime />

      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <TestButton />
        <SyncButton />
        <ToggleButton />
      </Box>
    </SimpleShowLayout>
  </Show>
)
