/**
 * 审核中心 - 人工审核AI生成的邮件回复
 */
import {
  List,
  Datagrid,
  TextField,
  DateField,
  FunctionField,
  Show,
  SimpleShowLayout,
  useRecordContext,
  useRefresh,
  useNotify,
  Button,
  TopToolbar,
  FilterButton,
  SelectInput,
  useGetOne,
  useDataProvider,
} from 'react-admin'
import {
  Chip,
  Box,
  Typography,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button as MuiButton,
  TextField as MuiTextField,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material'
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import EditIcon from '@mui/icons-material/Edit'
import SaveIcon from '@mui/icons-material/Save'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import CloseIcon from '@mui/icons-material/Close'
import TranslateIcon from '@mui/icons-material/Translate'

// 状态选项
const statusChoices = [
  { id: 'pending', name: '待审核' },
  { id: 'approved', name: '已通过' },
  { id: 'rejected', name: '已拒绝' },
  { id: 'revised', name: '已修改' },
  { id: 'expired', name: '已超时' },
]

// 状态显示
const StatusField = () => {
  const record = useRecordContext()
  if (!record) return null
  
  const statusMap: Record<string, { label: string; color: string }> = {
    pending: { label: '待审核', color: '#fa8c16' },
    approved: { label: '已通过', color: '#52c41a' },
    rejected: { label: '已拒绝', color: '#f5222d' },
    revised: { label: '已修改', color: '#1677ff' },
    expired: { label: '已超时', color: '#8c8c8c' },
  }
  
  const status = statusMap[record.status] || { label: record.status, color: '#d9d9d9' }
  
  return (
    <Chip 
      label={status.label} 
      size="small"
      sx={{ bgcolor: status.color, color: 'white' }}
    />
  )
}

// AI回复卡片组件
const AIReplyCard = ({ 
  record, 
  editing, 
  setEditing, 
  editedSubject, 
  setEditedSubject, 
  editedBody, 
  setEditedBody 
}: { 
  record: any
  editing: boolean
  setEditing: (v: boolean) => void
  editedSubject: string
  setEditedSubject: (v: string) => void
  editedBody: string
  setEditedBody: (v: string) => void
}) => {
  const refresh = useRefresh()
  const notify = useNotify()
  const dataProvider = useDataProvider()
  const [openAIDialog, setOpenAIDialog] = useState(false)
  const [aiInstruction, setAiInstruction] = useState('')
  const [regenerating, setRegenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [translating, setTranslating] = useState(false)
  const [translatedContent, setTranslatedContent] = useState('')
  const [showTranslation, setShowTranslation] = useState(false)
  const editableRef = useRef<HTMLDivElement>(null)

  const handleEdit = () => {
    setEditedSubject(record.draft_subject || '')
    setEditedBody(record.draft_html || record.draft_body || '')
    setEditing(true)
  }

  // 编辑模式下，设置初始内容
  useEffect(() => {
    if (editing && editableRef.current && editedBody) {
      editableRef.current.innerHTML = editedBody
    }
  }, [editing, editedBody])

  const handleCancelEdit = () => {
    setEditing(false)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      // 获取富文本编辑器的HTML内容
      const htmlContent = editableRef.current?.innerHTML || editedBody
      
      // 🔥 使用当前主机名，自动适配localhost和局域网IP
      const response = await fetch(`http://${window.location.hostname}:8001/api/approval_tasks/${record.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          draft_subject: editedSubject,
          draft_body: htmlContent,
          draft_html: htmlContent,
        })
      })

      if (response.ok) {
        notify('保存成功！', { type: 'success' })
        setEditing(false)
        refresh()
      } else {
        notify('保存失败', { type: 'error' })
      }
    } catch (error) {
      notify('网络错误', { type: 'error' })
    } finally {
      setSaving(false)
    }
  }

  const handleAIRegenerate = async () => {
    setRegenerating(true)
    try {
      // 🔥 使用当前主机名
      const response = await fetch(`http://${window.location.hostname}:8001/api/approval_tasks/${record.id}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instruction: aiInstruction || '请重新生成更专业的回复'
        })
      })

      if (response.ok) {
        notify('AI重新生成成功！', { type: 'success' })
        setOpenAIDialog(false)
        setAiInstruction('')
        
        // 如果当前在编辑模式，退出编辑模式
        if (editing) {
          setEditing(false)
        }
        
        // 延迟300ms后强制重新获取数据，绕过缓存
        setTimeout(async () => {
          try {
            // 直接从后端重新获取数据
            await dataProvider.getOne('approval_tasks', { id: record.id })
            // 然后再调用refresh刷新页面
            refresh()
          } catch (error) {
            console.error('刷新数据失败:', error)
            refresh()
          }
        }, 300)
      } else {
        notify('AI重新生成失败', { type: 'error' })
      }
    } catch (error) {
      notify('网络错误', { type: 'error' })
    } finally {
      setRegenerating(false)
    }
  }

  const handleTranslate = async () => {
    if (showTranslation) {
      // 如果已经显示翻译，切换回原文
      setShowTranslation(false)
      return
    }

    if (translatedContent) {
      // 如果已经翻译过，直接显示
      setShowTranslation(true)
      return
    }

    // 否则调用API翻译
    setTranslating(true)
    try {
      const content = record.draft_html || record.draft_body || ''
      // 🔥 使用当前主机名
      const response = await fetch(`http://${window.location.hostname}:8001/api/ai/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          target_lang: 'zh'
        })
      })

      if (response.ok) {
        const result = await response.json()
        setTranslatedContent(result.translated || '')
        setShowTranslation(true)
        notify('翻译成功！', { type: 'success' })
      } else {
        notify('翻译失败', { type: 'error' })
      }
    } catch (error) {
      notify('网络错误', { type: 'error' })
    } finally {
      setTranslating(false)
    }
  }

  return (
    <Card sx={{ 
      height: { xs: 'auto', md: '100%' },  // 📱 手机端自适应高度
      display: 'flex', 
      flexDirection: 'column' 
    }}>
      <CardContent sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        overflow: 'hidden',
        p: { xs: 1.5, md: 2 },  // 📱 手机端减小内边距
        '&:last-child': { pb: { xs: 1.5, md: 2 } }
      }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 2,
          flexWrap: 'wrap',  // 📱 手机端允许换行
          gap: 1
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" sx={{ fontSize: { xs: '1rem', md: '1.1rem' } }}>AI生成的回复</Typography>
            <Tooltip title={showTranslation ? '显示原文' : (translating ? '翻译中...' : '翻译成中文')}>
              <span>
                <IconButton 
                  color={showTranslation ? 'primary' : 'default'} 
                  size="small" 
                  onClick={handleTranslate}
                  disabled={translating}
                >
                  {translating ? <CircularProgress size={20} /> : <TranslateIcon />}
                </IconButton>
              </span>
            </Tooltip>
          </Box>
          {record.status === 'pending' && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {editing ? (
                <>
                  <Tooltip title="保存修改">
                    <IconButton color="primary" size="small" onClick={handleSave} disabled={saving}>
                      <SaveIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="取消编辑">
                    <IconButton color="default" size="small" onClick={handleCancelEdit}>
                      <CloseIcon />
                    </IconButton>
                  </Tooltip>
                </>
              ) : (
                <>
                  <Tooltip title="手动编辑">
                    <IconButton color="primary" size="small" onClick={handleEdit}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="AI重新生成">
                    <IconButton color="secondary" size="small" onClick={() => setOpenAIDialog(true)}>
                      <AutoFixHighIcon />
                    </IconButton>
                  </Tooltip>
                </>
              )}
            </Box>
          )}
        </Box>

        {/* 主题 */}
        {editing ? (
          <MuiTextField
            label="回复主题"
            fullWidth
            size="small"
            value={editedSubject}
            onChange={(e) => setEditedSubject(e.target.value)}
            sx={{ mb: 1.5, flexShrink: 0 }}
          />
        ) : (
          <Box sx={{ mb: 1.5, p: { xs: 1, md: 1.5 }, bgcolor: '#f5f5f5', borderRadius: 1, flexShrink: 0 }}>
            <Typography variant="body2" sx={{ fontSize: { xs: '0.85rem', md: '0.9rem' }, wordBreak: 'break-word' }}><strong>主题：</strong>{record?.draft_subject}</Typography>
          </Box>
        )}

        {/* 正文 */}
        {editing ? (
          <Box 
            ref={editableRef}
            contentEditable
            suppressContentEditableWarning
            sx={{ 
              flex: 1,
              p: { xs: 1, md: 1.5 },  // 📱 手机端减小内边距
              bgcolor: '#fff', 
              border: '2px solid #1976d2',
              borderRadius: 1,
              overflowY: 'auto',
              overflowX: 'hidden',
              minHeight: { xs: '200px', md: 0 },  // 📱 手机端最小高度
              outline: 'none',
              '& p': { margin: '8px 0' },
              '& ul, & ol': { paddingLeft: '20px', margin: '8px 0' },
              lineHeight: 1.6,
              wordBreak: 'break-word',
              fontSize: { xs: '0.85rem', md: '0.9rem' },  // 📱 手机端字体稍小
              '&:focus': {
                border: '2px solid #1976d2',
                boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.1)'
              }
            }}
          />
        ) : (
          <Box 
            sx={{ 
              flex: 1,
              p: { xs: 1, md: 1.5 },  // 📱 手机端减小内边距
              bgcolor: '#fff', 
              border: '1px solid #d9d9d9', 
              borderRadius: 1,
              overflowY: 'auto',
              overflowX: 'hidden',
              minHeight: { xs: '200px', md: 0 },  // 📱 手机端最小高度
              '& p': { margin: '8px 0' },
              '& ul, & ol': { paddingLeft: '20px', margin: '8px 0' },
              lineHeight: 1.6,
              wordBreak: 'break-word',
              fontSize: { xs: '0.85rem', md: '0.9rem' }  // 📱 手机端字体稍小
            }}
          >
            {record?.draft_html || record?.draft_body ? (
              <div dangerouslySetInnerHTML={{ __html: showTranslation ? translatedContent : (record.draft_html || record.draft_body) }} />
            ) : (
              <Typography variant="body2" color="textSecondary" sx={{ fontSize: { xs: '0.85rem', md: '0.9rem' } }}>
                回复内容为空
              </Typography>
            )}
          </Box>
        )}
      </CardContent>

      {/* AI重新生成对话框 */}
      <Dialog open={openAIDialog} onClose={() => setOpenAIDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>AI重新生成回复</DialogTitle>
        <DialogContent>
          <MuiTextField
            label="调整指令（可选）"
            placeholder="例如：请使用更正式的语气，增加产品优势介绍"
            multiline
            rows={4}
            fullWidth
            value={aiInstruction}
            onChange={(e) => setAiInstruction(e.target.value)}
            sx={{ mt: 2 }}
            helperText="告诉AI如何改进回复内容，留空则使用默认提示"
          />
        </DialogContent>
        <DialogActions>
          <MuiButton onClick={() => setOpenAIDialog(false)}>取消</MuiButton>
          <MuiButton 
            onClick={handleAIRegenerate} 
            variant="contained" 
            color="primary"
            disabled={regenerating}
          >
            {regenerating ? '生成中...' : '重新生成'}
          </MuiButton>
        </DialogActions>
      </Dialog>
    </Card>
  )
}

// 审核操作按钮
const ApprovalActions = () => {
  const record = useRecordContext()
  const refresh = useRefresh()
  const notify = useNotify()
  const navigate = useNavigate()
  const [openReject, setOpenReject] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [approving, setApproving] = useState(false)
  
  if (!record || record.status !== 'pending') return null
  
  const handleApprove = async () => {
    setApproving(true)
    try {
      // 🔥 使用当前主机名
      const response = await fetch(`http://${window.location.hostname}:8001/api/approval_tasks/${record.id}/approve?approved_by=Admin`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        const result = await response.json()
        
        // 根据返回结果显示不同的消息
        if (result.sent_email_id) {
          notify('✅ 审核通过，邮件已自动发送！', { type: 'success' })
        } else if (result.warning === 'NO_SMTP_CONFIG') {
          notify('⚠️ 审核通过，但未配置SMTP，请手动发送', { type: 'warning' })
        } else if (result.warning === 'SEND_FAILED') {
          notify(`⚠️ ${result.message}`, { type: 'warning' })
        } else {
          notify('审核通过！', { type: 'success' })
        }
        
        // 审核成功后，延迟一点再跳转，让用户看到提示消息
        setTimeout(() => {
          navigate('/approval_tasks?filter=%7B%22status%22%3A%22pending%22%7D')
        }, 800)
      } else {
        const errorData = await response.json().catch(() => ({}))
        notify(`操作失败: ${errorData.detail || '未知错误'}`, { type: 'error' })
      }
    } catch (error) {
      console.error('审核通过失败:', error)
      notify('网络错误', { type: 'error' })
    } finally {
      setApproving(false)
    }
  }
  
  const handleReject = async () => {
    try {
      // 🔥 使用当前主机名
      const url = new URL(`http://${window.location.hostname}:8001/api/approval_tasks/${record.id}/reject`)
      url.searchParams.append('rejected_by', 'Admin')
      if (rejectReason) {
        url.searchParams.append('reason', rejectReason)
      }
      
      const response = await fetch(url.toString(), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        notify('已拒绝', { type: 'success' })
        setOpenReject(false)
        
        // 拒绝后也跳转到列表页
        setTimeout(() => {
          navigate('/approval_tasks?filter=%7B%22status%22%3A%22pending%22%7D')
        }, 800)
      } else {
        const errorData = await response.json().catch(() => ({}))
        notify(`操作失败: ${errorData.detail || '未知错误'}`, { type: 'error' })
      }
    } catch (error) {
      console.error('拒绝审核失败:', error)
      notify('网络错误', { type: 'error' })
    }
  }
  
  return (
    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>  {/* 📱 允许按钮换行 */}
      <MuiButton
        variant="contained"
        color="success"
        size="small"
        startIcon={<CheckCircleIcon />}
        onClick={handleApprove}
        disabled={approving}
        sx={{ minWidth: { xs: '100px', md: 'auto' } }}  // 📱 手机端最小宽度
      >
        {approving ? '发送中...' : '通过'}
      </MuiButton>
      
      <MuiButton
        variant="outlined"
        color="error"
        size="small"
        startIcon={<CancelIcon />}
        onClick={() => setOpenReject(true)}
        sx={{ minWidth: { xs: '100px', md: 'auto' } }}  // 📱 手机端最小宽度
      >
        拒绝
      </MuiButton>
      
      <Dialog open={openReject} onClose={() => setOpenReject(false)} fullWidth maxWidth="sm">
        <DialogTitle>拒绝审核</DialogTitle>
        <DialogContent>
          <MuiTextField
            label="拒绝原因（可选）"
            multiline
            rows={3}
            fullWidth
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <MuiButton onClick={() => setOpenReject(false)}>取消</MuiButton>
          <MuiButton onClick={handleReject} color="error">确认拒绝</MuiButton>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

// 自定义列表操作栏
const ListActions = () => (
  <TopToolbar>
    <FilterButton />
  </TopToolbar>
)

// 筛选器
const filters = [
  <SelectInput 
    source="status" 
    label="状态" 
    choices={statusChoices} 
    alwaysOn 
  />,
]

// 列表组件
export const ApprovalTaskList = () => (
  <List
    actions={<ListActions />}
    filters={filters}
    sort={{ field: 'created_at', order: 'DESC' }}
    perPage={25}
    filterDefaultValues={{ status: 'pending' }}
  >
    <Datagrid rowClick="show" bulkActionButtons={false}>
      <TextField source="id" label="ID" />
      <StatusField />
      <FunctionField
        label="原始邮件"
        render={(record: any) => (
          <Box>
            <Typography variant="body2" fontWeight="bold">
              {record.original_email?.from_name || record.original_email?.from_email}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {record.original_email?.subject}
            </Typography>
          </Box>
        )}
      />
      <TextField source="draft_subject" label="回复主题" />
      <FunctionField
        label="邮件类型"
        render={(record: any) => {
          const categoryMap: Record<string, string> = {
            inquiry: '新客询盘',
            quotation: '报价跟进',
            sample: '样品阶段',
          }
          return categoryMap[record.original_email?.ai_category] || '-'
        }}
      />
      <DateField source="created_at" label="创建时间" showTime />
      <FunctionField
        label="操作"
        render={(record: any) => <ApprovalActions />}
      />
    </Datagrid>
  </List>
)

// 详情展示组件
export const ApprovalTaskShow = () => {
  return (
    <Show sx={{ 
      '& .RaShow-main': { 
        height: { xs: 'auto', md: 'calc(100vh - 100px)' },  // 📱 手机端自适应高度
        overflow: { xs: 'visible', md: 'hidden' }  // 📱 手机端允许滚动
      } 
    }}>
      <ApprovalTaskDetail />
    </Show>
  )
}

// 内部详情组件
const ApprovalTaskDetail = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const [editing, setEditing] = useState(false)
  const [editedSubject, setEditedSubject] = useState('')
  const [editedBody, setEditedBody] = useState('')
  const [translatingOriginal, setTranslatingOriginal] = useState(false)
  const [translatedOriginal, setTranslatedOriginal] = useState('')
  const [showOriginalTranslation, setShowOriginalTranslation] = useState(false)
  
  if (!record) {
    return <Box sx={{ p: 3 }}><Typography>加载中...</Typography></Box>
  }

  const handleTranslateOriginal = async () => {
    if (showOriginalTranslation) {
      // 如果已经显示翻译，切换回原文
      setShowOriginalTranslation(false)
      return
    }

    if (translatedOriginal) {
      // 如果已经翻译过，直接显示
      setShowOriginalTranslation(true)
      return
    }

    // 否则调用API翻译
    setTranslatingOriginal(true)
    try {
      const content = record.original_email?.html_body || record.original_email?.body || ''
      // 🔥 使用当前主机名
      const response = await fetch(`http://${window.location.hostname}:8001/api/ai/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          target_lang: 'zh'
        })
      })

      if (response.ok) {
        const result = await response.json()
        setTranslatedOriginal(result.translated || '')
        setShowOriginalTranslation(true)
        notify('翻译成功！', { type: 'success' })
      } else {
        notify('翻译失败', { type: 'error' })
      }
    } catch (error) {
      notify('网络错误', { type: 'error' })
    } finally {
      setTranslatingOriginal(false)
    }
  }
  
  return (
    <Box sx={{ 
      height: { xs: 'auto', md: '100%' },  // 📱 手机端自适应高度
      display: 'flex', 
      flexDirection: 'column', 
      overflow: { xs: 'visible', md: 'hidden' },  // 📱 手机端允许滚动
      pb: { xs: 2, md: 0 }  // 📱 手机端底部留出空间
    }}>
      {/* 状态卡片 */}
      <Card sx={{ mb: 2, flexShrink: 0 }}>
        <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 1
          }}>
            <Box>
              <Typography variant="h6" sx={{ fontSize: '1.1rem' }}>审核状态</Typography>
              <StatusField />
            </Box>
            <ApprovalActions />
          </Box>
        </CardContent>
      </Card>
      
      {/* 响应式布局：电脑端左右，手机端上下 */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', md: 'row' },  // 📱 手机上下，💻 电脑左右
        gap: 2, 
        flex: 1, 
        minHeight: 0,
        overflowY: { xs: 'auto', md: 'hidden' }  // 📱 手机允许整体滚动
      }}>
        {/* 原始邮件（电脑端左侧，手机端上方） */}
        <Box sx={{ 
          flex: 1, 
          minWidth: 0, 
          display: 'flex', 
          flexDirection: 'column',
          minHeight: { xs: '400px', md: 0 }  // 📱 手机端最小高度
        }}>
          <Card sx={{ 
            height: { xs: 'auto', md: '100%' },  // 📱 手机端自适应高度
            display: 'flex', 
            flexDirection: 'column' 
          }}>
            <CardContent sx={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              p: { xs: 1.5, md: 2 },  // 📱 手机端减小内边距
              '&:last-child': { pb: { xs: 1.5, md: 2 } }, 
              overflow: 'hidden' 
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0, mb: 1 }}>
                <Typography variant="h6" sx={{ fontSize: { xs: '1rem', md: '1.1rem' } }}>原始邮件</Typography>
                <Tooltip title={showOriginalTranslation ? '显示原文' : (translatingOriginal ? '翻译中...' : '翻译成中文')}>
                  <span>
                    <IconButton 
                      color={showOriginalTranslation ? 'primary' : 'default'} 
                      size="small" 
                      onClick={handleTranslateOriginal}
                      disabled={translatingOriginal}
                    >
                      {translatingOriginal ? <CircularProgress size={20} /> : <TranslateIcon />}
                    </IconButton>
                  </span>
                </Tooltip>
              </Box>
              
              {/* 邮件基本信息 */}
              <Box sx={{ 
                p: { xs: 1, md: 1.5 },  // 📱 手机端减小内边距
                bgcolor: '#f5f5f5', 
                borderRadius: 1, 
                flexShrink: 0, 
                mb: 1.5 
              }}>
                <Typography variant="body2" sx={{ mb: 0.5, fontSize: { xs: '0.85rem', md: '0.9rem' }, wordBreak: 'break-all' }}>
                  <strong>发件人：</strong>
                  {record?.original_email?.from_name && `${record.original_email.from_name} `}
                  &lt;{record?.original_email?.from_email}&gt;
                </Typography>
                <Typography variant="body2" sx={{ mb: 0.5, fontSize: { xs: '0.85rem', md: '0.9rem' }, wordBreak: 'break-word' }}>
                  <strong>主题：</strong>{record?.original_email?.subject}
                </Typography>
                <Typography variant="body2" sx={{ mb: 0.5, fontSize: { xs: '0.85rem', md: '0.9rem' } }}>
                  <strong>时间：</strong>{record?.original_email?.sent_at}
                </Typography>
                <Typography variant="body2" sx={{ mb: 0, fontSize: { xs: '0.85rem', md: '0.9rem' } }}>
                  <strong>类型：</strong>
                  <Chip 
                    label={record?.original_email?.ai_category || '未分类'} 
                    size="small" 
                    sx={{ ml: 1, height: '22px' }}
                  />
                </Typography>
              </Box>
              
              {/* 邮件正文 - 带内部滚动条 */}
              <Box sx={{ 
                flex: 1,
                p: { xs: 1, md: 1.5 },  // 📱 手机端减小内边距
                bgcolor: 'white', 
                borderRadius: 1, 
                border: '1px solid #d9d9d9',
                overflowY: 'auto',
                overflowX: 'hidden',
                minHeight: { xs: '200px', md: 0 }  // 📱 手机端最小高度
              }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1, fontSize: { xs: '0.85rem', md: '0.9rem' } }}>正文：</Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: 1.6, 
                    wordBreak: 'break-word',
                    fontSize: { xs: '0.85rem', md: '0.9rem' }  // 📱 手机端字体稍小
                  }}
                  dangerouslySetInnerHTML={{ 
                    __html: showOriginalTranslation 
                      ? translatedOriginal 
                      : (record?.original_email?.html_body || record?.original_email?.body?.replace(/\n/g, '<br/>')) 
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Box>
        
        {/* AI生成的回复（电脑端右侧，手机端下方） */}
        <Box sx={{ 
          flex: 1, 
          minWidth: 0,
          minHeight: { xs: '400px', md: 0 }  // 📱 手机端最小高度
        }}>
          <AIReplyCard record={record} editing={editing} setEditing={setEditing} editedSubject={editedSubject} setEditedSubject={setEditedSubject} editedBody={editedBody} setEditedBody={setEditedBody} />
        </Box>
      </Box>
    </Box>
  )
}
