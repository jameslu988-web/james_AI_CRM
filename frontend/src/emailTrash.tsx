// 邮件回收站页面
import { List, Datagrid, TextField, FunctionField, useNotify, useRefresh, useListContext, useRecordContext } from 'react-admin'
import { Box, Button, Typography, Chip, Tooltip, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material'
import { useState } from 'react'
import RestoreIcon from '@mui/icons-material/Restore'
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep'
import AttachFileIcon from '@mui/icons-material/AttachFile'

// 提取纯文本内容（移除HTML标签）
const extractPlainText = (html: string): string => {
  if (!html) return ''
  if (!/<\/?[a-z][\s\S]*>/i.test(html)) return html
  
  return html
    .replace(/<style[^>]*>.*?<\/style>/gi, '')
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

// 相对时间显示组件
const RelativeTimeField = ({ source }: { source: string }) => {
  const record = useRecordContext()
  if (!record || !record[source]) return null
  
  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMinutes < 1) return '刚刚'
    if (diffMinutes < 60) return `${diffMinutes}分钟前`
    if (diffHours < 24) return `${diffHours}小时前`
    if (diffDays === 1) return '昨天'
    if (diffDays < 7) return `${diffDays}天前`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
    return `${Math.floor(diffDays / 30)}个月前`
  }
  
  const getFullTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }
  
  const relativeTime = getRelativeTime(record[source])
  const fullTime = getFullTime(record[source])
  
  return (
    <Tooltip title={fullTime} arrow>
      <span style={{ cursor: 'help' }}>{relativeTime}</span>
    </Tooltip>
  )
}

// 批量操作按钮
const TrashBulkActionButtons = () => {
  const { selectedIds, onUnselectItems } = useListContext()
  const notify = useNotify()
  const refresh = useRefresh()

  const handleBulkRestore = async () => {
    if (!selectedIds || selectedIds.length === 0) {
      notify('请先选择要恢复的邮件', { type: 'warning' })
      return
    }

    try {
      const token = localStorage.getItem('token')
      const restorePromises = selectedIds.map((id: any) =>
        fetch(`http://127.0.0.1:8001/api/email_history/${id}/restore`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      )

      await Promise.all(restorePromises)
      
      // 清空邮件列表页面的选中状态（React Admin 的 localStorage 缓存）
      // React Admin 使用 'RaStore.email_history.selectedIds' 存储选中状态
      try {
        localStorage.removeItem('RaStore.email_history.selectedIds')
      } catch (e) {
        console.warn('无法清除选中状态缓存', e)
      }
      
      notify(`已成功恢复 ${selectedIds.length} 封邮件`, { type: 'success' })
      // 清空当前回收站页面的选中状态
      onUnselectItems()
      refresh()
    } catch (error) {
      notify('恢复失败', { type: 'error' })
    }
  }

  const handleBulkPermanentDelete = async () => {
    if (!selectedIds || selectedIds.length === 0) {
      notify('请先选择要永久删除的邮件', { type: 'warning' })
      return
    }

    if (!window.confirm(`⚠️ 此操作不可恢复！确定要永久删除选中的 ${selectedIds.length} 封邮件吗？`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const deletePromises = selectedIds.map((id: any) =>
        fetch(`http://127.0.0.1:8001/api/email_history/${id}/permanent`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      )

      await Promise.all(deletePromises)
      notify(`已永久删除 ${selectedIds.length} 封邮件`, { type: 'success' })
      // 清空选中状态
      onUnselectItems()
      refresh()
    } catch (error) {
      notify('删除失败', { type: 'error' })
    }
  }

  return (
    <>
      <Button
        size="small"
        variant="outlined"
        startIcon={<RestoreIcon />}
        onClick={handleBulkRestore}
        sx={{ mr: 1 }}
      >
        恢复
      </Button>
      <Button
        size="small"
        variant="outlined"
        color="error"
        startIcon={<DeleteForeverIcon />}
        onClick={handleBulkPermanentDelete}
      >
        永久删除
      </Button>
    </>
  )
}

// 操作按钮列
const ActionsField = () => {
  const notify = useNotify()
  const refresh = useRefresh()

  const handleRestore = async (record: any, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${record.id}/restore`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        // 清空邮件列表页面的选中状态
        try {
          localStorage.removeItem('RaStore.email_history.selectedIds')
        } catch (err) {
          console.warn('无法清除选中状态缓存', err)
        }
        
        notify('邮件已恢复', { type: 'success' })
        refresh()
      }
    } catch (error) {
      notify('恢复失败', { type: 'error' })
    }
  }

  const handlePermanentDelete = async (record: any, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!window.confirm('⚠️ 此操作不可恢复！确定要永久删除这封邮件吗？')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${record.id}/permanent`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        notify('邮件已永久删除', { type: 'success' })
        refresh()
      }
    } catch (error) {
      notify('删除失败', { type: 'error' })
    }
  }

  return (
    <FunctionField
      label="操作"
      render={(record: any) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end', paddingRight: '8px' }}>
          <Tooltip title="恢复">
            <Button
              size="small"
              variant="outlined"
              startIcon={<RestoreIcon />}
              onClick={(e) => handleRestore(record, e)}
              sx={{ minWidth: '80px' }}
            >
              恢复
            </Button>
          </Tooltip>
          <Tooltip title="永久删除">
            <Button
              size="small"
              variant="outlined"
              color="error"
              startIcon={<DeleteForeverIcon />}
              onClick={(e) => handlePermanentDelete(record, e)}
              sx={{ minWidth: '100px' }}
            >
              永久删除
            </Button>
          </Tooltip>
        </Box>
      )}
      headerClassName="column-actions"
      cellClassName="column-actions"
    />
  )
}

// 顶部操作栏
const TrashActions = () => {
  const [dialogOpen, setDialogOpen] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  const handleEmptyTrash = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/email_history/empty_trash', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const result = await response.json()
        notify(result.message || '回收站已清空', { type: 'success' })
        setDialogOpen(false)
        refresh()
      }
    } catch (error) {
      notify('清空失败', { type: 'error' })
    }
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, p: 2, bgcolor: '#fff3cd', borderRadius: 1 }}>
      <Typography variant="body2" sx={{ flex: 1, color: '#856404' }}>
        ⚠️ 回收站中的邮件可以恢复。如需永久删除，请点击"清空回收站"按钮。
      </Typography>
      <Button
        variant="contained"
        color="error"
        startIcon={<DeleteSweepIcon />}
        onClick={() => setDialogOpen(true)}
      >
        清空回收站
      </Button>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>确认清空回收站</DialogTitle>
        <DialogContent>
          <Typography>
            ⚠️ 此操作将永久删除回收站中的所有邮件，无法恢复！
          </Typography>
          <Typography sx={{ mt: 2, color: 'error.main' }}>
            确定要继续吗？
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>取消</Button>
          <Button onClick={handleEmptyTrash} color="error" variant="contained">
            确认清空
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export const EmailTrashList = (props: any) => (
  <>
    <TrashActions />
    <List
      {...props}
      resource="email_history"
      filter={{ is_deleted: 'true' }}
      perPage={20}
      sort={{ field: 'deleted_at', order: 'DESC' }}
      actions={false}
      title="回收站"
    >
      <Datagrid
        bulkActionButtons={<TrashBulkActionButtons />}
        sx={{
          '& .RaDatagrid-headerCell': { 
            fontWeight: 600,
            backgroundColor: '#f9fafb',
            whiteSpace: 'nowrap',
          },
          '& .RaDatagrid-row': { 
            '&:hover': { backgroundColor: '#f3f4f6' },
            opacity: 0.7
          },
          '& .column-direction': { 
            width: '80px', 
            minWidth: '80px', 
            maxWidth: '80px',
            textAlign: 'center',
          },
          '& .column-from': { 
            width: '340px', 
            minWidth: '340px', 
            maxWidth: '340px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          },
          '& .column-subject': { 
            width: '480px', 
            minWidth: '480px', 
            maxWidth: '480px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          },
          '& .column-attachment': { 
            width: '60px', 
            minWidth: '60px', 
            maxWidth: '60px', 
            textAlign: 'center',
            '& .RaDatagrid-headerCell': {
              textAlign: 'right',
              paddingRight: '16px',
              '& span': {
                display: 'none',
              }
            }
          },
          '& .column-deleted-time': { 
            width: '120px', 
            minWidth: '120px', 
            maxWidth: '120px',
            '& .RaDatagrid-headerCell': {
              textAlign: 'right',
              paddingRight: '16px',
            }
          },
          '& .column-actions': { 
            width: '190px', 
            minWidth: '190px', 
            maxWidth: '190px',
            textAlign: 'right',
            '& .RaDatagrid-headerCell': {
              textAlign: 'right',
              paddingRight: '16px',
            }
          },
          '& table': {
            tableLayout: 'fixed',
            width: '100%'
          },
        }}
      >
        <FunctionField 
          label="方向" 
          render={(record: any) => (
            <Chip 
              label={record.direction === 'outbound' ? '出站' : '入站'} 
              size="small" 
              sx={{ 
                bgcolor: record.direction === 'outbound' ? '#3b82f6' : '#10b981', 
                color: '#fff', 
                fontWeight: 500 
              }} 
            />
          )}
          headerClassName="column-direction"
          cellClassName="column-direction"
        />
        
        <FunctionField
          label="发件人"
          render={(record: any) => {
            const name = record.from_name || record.from_email?.split('@')[0] || '未知'
            const email = record.from_email || ''
            return (
              <Box sx={{ 
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                <span style={{ fontWeight: 500 }}>{name}</span>
                {email && <span style={{ color: '#6b7280' }}> | {email}</span>}
              </Box>
            )
          }}
          headerClassName="column-from"
          cellClassName="column-from"
        />
        
        <FunctionField
          label="主题"
          render={(record: any) => (
            <Box sx={{ 
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              <Box sx={{ fontWeight: 500 }}>
                {record.subject || '(无主题)'}
              </Box>
            </Box>
          )}
          headerClassName="column-subject"
          cellClassName="column-subject"
        />
        
        <FunctionField
          label="附件"
          render={(record: any) => {
            if (!record.attachments) return null
            try {
              const attachments = JSON.parse(record.attachments)
              if (Array.isArray(attachments) && attachments.length > 0) {
                return (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, justifyContent: 'center' }}>
                    <AttachFileIcon sx={{ fontSize: 16 }} />
                    <span>{attachments.length}</span>
                  </Box>
                )
              }
            } catch (e) {}
            return null
          }}
          headerClassName="column-attachment"
          cellClassName="column-attachment"
        />
        
        <FunctionField 
          label="删除时间" 
          render={(record: any) => {
            if (!record.deleted_at) {
              return <Box sx={{ textAlign: 'right', paddingRight: '8px' }}><span style={{ color: '#9ca3af' }}>-</span></Box>
            }
            return <Box sx={{ textAlign: 'right', paddingRight: '8px' }}><RelativeTimeField source="deleted_at" /></Box>
          }}
          headerClassName="column-deleted-time"
          cellClassName="column-deleted-time"
        />
        
        <ActionsField />
      </Datagrid>
    </List>
  </>
)
