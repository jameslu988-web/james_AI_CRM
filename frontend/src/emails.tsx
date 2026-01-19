// Email History Module - Simplified but Complete Version
import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, FunctionField, TopToolbar, CreateButton, ExportButton, EditButton, ShowButton, DeleteButton, BulkDeleteButton, ReferenceField, Show, SimpleShowLayout, RichTextField, useRecordContext, useNotify, useRefresh, BooleanField, DateField, AutocompleteInput, required, Pagination, useListContext } from 'react-admin'
import Chip from '@mui/material/Chip'

import { getApiUrl } from './config/api'

import { Box, Tooltip, IconButton, Button, Divider, TextField as MuiTextField, Paper, Collapse, InputAdornment, IconButton as MuiIconButton, Tabs, Tab, Drawer, Select, MenuItem, Typography, Menu, ListItemIcon, ListItemText, CircularProgress } from '@mui/material'
import AttachFileIcon from '@mui/icons-material/AttachFile'
import ReplyIcon from '@mui/icons-material/Reply'
import ForwardIcon from '@mui/icons-material/Forward'
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead'
import MarkEmailUnreadIcon from '@mui/icons-material/MarkEmailUnread'
import DraftsIcon from '@mui/icons-material/Drafts'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SendIcon from '@mui/icons-material/Send'
import SaveIcon from '@mui/icons-material/Save'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import FormatBoldIcon from '@mui/icons-material/FormatBold'
import FormatItalicIcon from '@mui/icons-material/FormatItalic'
import FormatUnderlinedIcon from '@mui/icons-material/FormatUnderlined'
import InsertLinkIcon from '@mui/icons-material/InsertLink'
import InsertPhotoIcon from '@mui/icons-material/InsertPhoto'
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions'
import AttachFile from '@mui/icons-material/AttachFile'
import TemplateIcon from '@mui/icons-material/Description'
import CloseIcon from '@mui/icons-material/Close'
import UndoIcon from '@mui/icons-material/Undo'
import RedoIcon from '@mui/icons-material/Redo'
import RefreshIcon from '@mui/icons-material/Refresh'
import FormatColorTextIcon from '@mui/icons-material/FormatColorText'
import FormatColorFillIcon from '@mui/icons-material/FormatColorFill'
import FormatAlignLeftIcon from '@mui/icons-material/FormatAlignLeft'
import FormatAlignCenterIcon from '@mui/icons-material/FormatAlignCenter'
import FormatAlignRightIcon from '@mui/icons-material/FormatAlignRight'
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted'
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered'
import TableChartIcon from '@mui/icons-material/TableChart'
import CodeIcon from '@mui/icons-material/Code'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import BookmarkIcon from '@mui/icons-material/Bookmark'
import CommentIcon from '@mui/icons-material/Comment'
import FlagIcon from '@mui/icons-material/Flag'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Radio from '@mui/material/Radio'
import RadioGroup from '@mui/material/RadioGroup'
import AddIcon from '@mui/icons-material/Add'
import CreateIcon from '@mui/icons-material/Create'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import { useState, useEffect, useRef } from 'react'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import TranslateIcon from '@mui/icons-material/Translate'
import PsychologyIcon from '@mui/icons-material/Psychology'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import StarIcon from '@mui/icons-material/Star'
import LocalOfferIcon from '@mui/icons-material/LocalOffer'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import SpeedIcon from '@mui/icons-material/Speed'
import AssessmentIcon from '@mui/icons-material/Assessment'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import PushPinIcon from '@mui/icons-material/PushPin'
import DeleteIcon from '@mui/icons-material/Delete'
import FilterListIcon from '@mui/icons-material/FilterList'
import VisibilityIcon from '@mui/icons-material/Visibility'  // 🔥 预览模式图标
import ErrorIcon from '@mui/icons-material/Error'  // 🔥 错误图标
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'  // 🔥 未知图标
import WarningIcon from '@mui/icons-material/Warning'  // 🔥 警告图标
import DescriptionIcon from '@mui/icons-material/Description'  // 🔥 文件图标
import CloudDownloadIcon from '@mui/icons-material/CloudDownload'  // 🔥 下载图标

// AI分析按钮旋转动画
const spinKeyframes = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`
// 添加动画style
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style')
  styleSheet.textContent = spinKeyframes
  document.head.appendChild(styleSheet)
}

// 相对时间显示组件
const RelativeTimeField = ({ source }: { source: string }) => {
  const record = useRecordContext()
  if (!record) return null
  
  // 🔥 草稿使用 created_at（创建时间），已发送邮件使用 sent_at（发送时间）
  const timeField = record.status === 'draft' ? 'created_at' : source
  if (!record[timeField]) return <span style={{ color: '#9ca3af' }}>-</span>
  
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
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`
    return `${Math.floor(diffDays / 365)}年前`
  }
  
  const getFullTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  }
  
  const relativeTime = getRelativeTime(record[timeField])
  const fullTime = getFullTime(record[timeField])
  
  return (
    <Tooltip title={fullTime} arrow>
      <span style={{ cursor: 'help' }}>{relativeTime}</span>
    </Tooltip>
  )
}

// 🔥 投递状态图标组件
const DeliveryStatusIcon = ({ status }: { status?: string }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'delivered':
        return {
          icon: <CheckCircleIcon sx={{ fontSize: 16 }} />,
          color: '#10b981',
          tooltip: '已投递 - 邮件已成功投递到收件人邮箱'
        }
      case 'pending':
        return {
          icon: <AccessTimeIcon sx={{ fontSize: 16 }} />,
          color: '#f59e0b',
          tooltip: '发送中 - SMTP已接受，等待投递确认'
        }
      case 'bounced':
        return {
          icon: <ErrorIcon sx={{ fontSize: 16 }} />,
          color: '#ef4444',
          tooltip: '投递失败 - 邮件被退回（收件箱不存在或已满）'
        }
      case 'spam':
        return {
          icon: <WarningIcon sx={{ fontSize: 16 }} />,
          color: '#f97316',
          tooltip: '疑似垃圾邮件 - 可能被标记为垃圾邮件'
        }
      case 'failed':
        return {
          icon: <ErrorIcon sx={{ fontSize: 16 }} />,
          color: '#dc2626',
          tooltip: '发送失败 - SMTP发送失败'
        }
      case 'unknown':
      default:
        return {
          icon: <HelpOutlineIcon sx={{ fontSize: 16 }} />,
          color: '#9ca3af',
          tooltip: '未知状态 - 无法确认投递状态'
        }
    }
  }

  const config = getStatusConfig()
  
  return (
    <Tooltip title={config.tooltip} arrow>
      <Box sx={{ display: 'inline-flex', alignItems: 'center', color: config.color }}>
        {config.icon}
      </Box>
    </Tooltip>
  )
}

// AI分析结果徽章组件
const AIAnalysisChips = () => {
  const record = useRecordContext()
  if (!record) return null
  
  // 如果没有AI分析数据，不显示
  if (!record.ai_sentiment && !record.purchase_intent && !record.urgency_level && !record.business_stage) {
    return null
  }
  
  // 情感颜色映射和中文标签
  const sentimentColors: Record<string, { bg: string, text: string, icon: any, label: string }> = {
    'positive': { bg: '#d1fae5', text: '#065f46', icon: '😊', label: '积极' },
    'neutral': { bg: '#e5e7eb', text: '#374151', icon: '😐', label: '中性' },
    'negative': { bg: '#fee2e2', text: '#991b1b', icon: '😞', label: '消极' },
    'urgent': { bg: '#fef3c7', text: '#92400e', icon: '⚡', label: '紧急' },
    'complaint': { bg: '#fecaca', text: '#7f1d1d', icon: '⚠️', label: '投诉' }
  }
  
  // 购买意向颜色和中文标签
  const intentColors: Record<string, { bg: string, text: string, label: string }> = {
    'high': { bg: '#dcfce7', text: '#14532d', label: '高' },
    'medium': { bg: '#fef3c7', text: '#713f12', label: '中' },
    'low': { bg: '#f3f4f6', text: '#4b5563', label: '低' }
  }
  
  // 紧急度颜色和中文标签
  const urgencyColors: Record<string, { bg: string, text: string, label: string }> = {
    'high': { bg: '#fee2e2', text: '#991b1b', label: '高' },
    'medium': { bg: '#fed7aa', text: '#9a3412', label: '中' },
    'low': { bg: '#dbeafe', text: '#1e40af', label: '低' }
  }
  
  // 客户分级颜色
  const gradeColors: Record<string, { bg: string, text: string }> = {
    'A': { bg: '#fef3c7', text: '#78350f' },
    'B': { bg: '#dbeafe', text: '#1e3a8a' },
    'C': { bg: '#e0e7ff', text: '#3730a3' },
    'D': { bg: '#f3f4f6', text: '#374151' }
  }
  
  return (
    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
      {/* 业务阶段 */}
      {record.business_stage && (
        <Tooltip title={`业务阶段: ${record.business_stage}`} arrow>
          <Chip
            size="small"
            label={record.business_stage}
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: '#ede9fe',
              color: '#5b21b6',
              fontWeight: 500,
              '& .MuiChip-label': { px: 0.75, py: 0 }
            }}
          />
        </Tooltip>
      )}
      
      {/* 情感 */}
      {record.ai_sentiment && sentimentColors[record.ai_sentiment] && (
        <Tooltip title={`情感: ${sentimentColors[record.ai_sentiment].label}`} arrow>
          <Chip
            size="small"
            label={`${sentimentColors[record.ai_sentiment].icon} ${sentimentColors[record.ai_sentiment].label}`}
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: sentimentColors[record.ai_sentiment].bg,
              color: sentimentColors[record.ai_sentiment].text,
              fontWeight: 500,
              '& .MuiChip-label': { px: 0.75, py: 0 }
            }}
          />
        </Tooltip>
      )}
      
      {/* 购买意向 */}
      {record.purchase_intent && intentColors[record.purchase_intent] && (
        <Tooltip title={`购买意向: ${intentColors[record.purchase_intent].label}${record.purchase_intent_score ? ` (${record.purchase_intent_score}分)` : ''}`} arrow>
          <Chip
            icon={<TrendingUpIcon sx={{ fontSize: 14 }} />}
            size="small"
            label={intentColors[record.purchase_intent].label}
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: intentColors[record.purchase_intent].bg,
              color: intentColors[record.purchase_intent].text,
              fontWeight: 500,
              '& .MuiChip-label': { px: 0.5, py: 0 },
              '& .MuiChip-icon': { ml: 0.5 }
            }}
          />
        </Tooltip>
      )}
      
      {/* 紧急度 */}
      {record.urgency_level && urgencyColors[record.urgency_level] && (
        <Tooltip title={`紧急度: ${urgencyColors[record.urgency_level].label}${record.response_deadline ? ` - 建议${record.response_deadline}回复` : ''}`} arrow>
          <Chip
            icon={<SpeedIcon sx={{ fontSize: 14 }} />}
            size="small"
            label={urgencyColors[record.urgency_level].label}
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: urgencyColors[record.urgency_level].bg,
              color: urgencyColors[record.urgency_level].text,
              fontWeight: 500,
              '& .MuiChip-label': { px: 0.5, py: 0 },
              '& .MuiChip-icon': { ml: 0.5 }
            }}
          />
        </Tooltip>
      )}
      
      {/* 客户分级建议 */}
      {record.customer_grade_suggestion && (
        <Tooltip title={`客户分级: ${record.customer_grade_suggestion}`} arrow>
          <Chip
            size="small"
            label={record.customer_grade_suggestion.substring(0, 2)}
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: gradeColors[record.customer_grade_suggestion[0]]?.bg || '#f3f4f6',
              color: gradeColors[record.customer_grade_suggestion[0]]?.text || '#374151',
              fontWeight: 600,
              '& .MuiChip-label': { px: 0.75, py: 0 }
            }}
          />
        </Tooltip>
      )}
      
      {/* 机会评分 */}
      {record.opportunity_score && record.opportunity_score > 0 && (
        <Tooltip title={`机会评分: ${record.opportunity_score}/100 | 转化概率: ${record.conversion_probability || 0}%`} arrow>
          <Chip
            icon={<AssessmentIcon sx={{ fontSize: 14 }} />}
            size="small"
            label={`${record.opportunity_score}`}
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: record.opportunity_score >= 70 ? '#dcfce7' : record.opportunity_score >= 40 ? '#fef3c7' : '#fee2e2',
              color: record.opportunity_score >= 70 ? '#14532d' : record.opportunity_score >= 40 ? '#713f12' : '#991b1b',
              fontWeight: 500,
              '& .MuiChip-label': { px: 0.5, py: 0 },
              '& .MuiChip-icon': { ml: 0.5 }
            }}
          />
        </Tooltip>
      )}
      
      {/* 需要人工审核 */}
      {record.requires_human_review && (
        <Tooltip title={`需要人工审核: ${record.human_review_reason || '重要邮件'}`} arrow>
          <Chip
            size="small"
            label="\ud83d\udc41️ 人工审核"
            sx={{
              height: 20,
              fontSize: '0.7rem',
              bgcolor: '#fef3c7',
              color: '#78350f',
              fontWeight: 600,
              border: '1px solid #fbbf24',
              '& .MuiChip-label': { px: 0.75, py: 0 }
            }}
          />
        </Tooltip>
      )}
    </Box>
  )
}

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

// 检测是否为HTML内容
const isHtmlContent = (content: string): boolean => {
  if (!content) return false
  return /<\/?[a-z][\s\S]*>/i.test(content)
}

// 安全的HTML渲染组件
const HtmlContent = ({ content, maxHeight }: { content: string, maxHeight?: string | number }) => {
  if (!content) return <Box sx={{ color: '#9ca3af', fontStyle: 'italic' }}>（无内容）</Box>
  
  if (isHtmlContent(content)) {
    // ✅ 后端已经处理了所有图片（内嵌图片和外部图片），前端直接渲染即可
    // 不再需要手动处理 cid: 或添加 onerror，避免破坏 HTML 结构
    
    return (
      <Box 
        sx={{ 
          '& img': { 
            maxWidth: '100%', 
            height: 'auto',
            borderRadius: '4px',
            margin: '8px 0'
          },
          '& a': { color: '#3b82f6', textDecoration: 'underline' },
          '& table': { borderCollapse: 'collapse', width: '100%' },
          '& td, & th': { border: '1px solid #e5e7eb', padding: '8px' },
          maxHeight: maxHeight || 'none',
          overflowY: maxHeight ? 'auto' : 'visible',
          wordBreak: 'break-word'
        }}
        dangerouslySetInnerHTML={{ __html: content }}
      />
    )
  }
  
  return (
    <Box sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', maxHeight: maxHeight || 'none', overflowY: maxHeight ? 'auto' : 'visible' }}>
      {content}
    </Box>
  )
}

// 自定义简洁翻页组件（包含批量操作按钮）
const CustomPagination = ({ previewMode, setPreviewMode }: { previewMode?: boolean, setPreviewMode?: (mode: boolean) => void }) => {
  const { total, page, perPage, setPage, selectedIds, onUnselectItems, filterValues, setFilters } = useListContext()
  const totalPages = Math.ceil(total / perPage) || 1
  const [inputPage, setInputPage] = useState(page)
  const notify = useNotify()
  const refresh = useRefresh()
  const [typeAnchorEl, setTypeAnchorEl] = useState<null | HTMLElement>(null)
  const typeMenuOpen = Boolean(typeAnchorEl)

  useEffect(() => {
    setInputPage(page)
  }, [page])

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage)
      setInputPage(newPage)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    if (value === '' || /^\d+$/.test(value)) {
      setInputPage(value === '' ? 1 : parseInt(value))
    }
  }

  const handleInputBlur = () => {
    if (inputPage >= 1 && inputPage <= totalPages) {
      setPage(inputPage)
    } else {
      setInputPage(page)
    }
  }

  const handleInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleInputBlur()
    }
  }

  const handleBulkDelete = async () => {
    if (!selectedIds || selectedIds.length === 0) {
      notify('请先选择要删除的邮件', { type: 'warning' })
      return
    }
    
    if (!window.confirm(`确定要删除选中的 ${selectedIds.length} 封邮件吗？`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const deletePromises = selectedIds.map((id: any) =>
        fetch(`http://127.0.0.1:8001/api/email_history/${id}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      )

      await Promise.all(deletePromises)
      notify(`已成功删除 ${selectedIds.length} 封邮件`, { type: 'success' })
      // 清空选中状态
      onUnselectItems()
      refresh()
    } catch (error) {
      notify('删除失败', { type: 'error' })
    }
  }

  const handleMarkAsRead = async () => {
    if (!selectedIds || selectedIds.length === 0) {
      notify('请先选择要标记的邮件', { type: 'warning' })
      return
    }
    
    try {
      const token = localStorage.getItem('token')
      const updatePromises = selectedIds.map((id: any) =>
        fetch(`http://127.0.0.1:8001/api/email_history/${id}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ opened: true }),
        })
      )

      await Promise.all(updatePromises)
      notify(`已标记 ${selectedIds.length} 封邮件为已读`, { type: 'success' })
      // 清空选中状态
      onUnselectItems()
      refresh()
    } catch (error) {
      notify('操作失败', { type: 'error' })
    }
  }

  const handleMarkAsUnread = async () => {
    if (!selectedIds || selectedIds.length === 0) {
      notify('请先选择要标记的邮件', { type: 'warning' })
      return
    }
    
    try {
      const token = localStorage.getItem('token')
      const updatePromises = selectedIds.map((id: any) =>
        fetch(`http://127.0.0.1:8001/api/email_history/${id}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ opened: false }),
        })
      )

      await Promise.all(updatePromises)
      notify(`已标记 ${selectedIds.length} 封邮件为未读`, { type: 'success' })
      // 清空选中状态
      onUnselectItems()
      refresh()
    } catch (error) {
      notify('操作失败', { type: 'error' })
    }
  }

  // 🔥 类型筛选按钮处理
  const handleTypeFilterClick = (e: React.MouseEvent<HTMLElement>) => {
    setTypeAnchorEl(e.currentTarget)
  }

  const handleTypeFilterClose = () => {
    setTypeAnchorEl(null)
  }

  const handleTypeFilterSelect = (type: string | null) => {
    console.log('🔥 =================筛选开始=================')  
    console.log('🔥 选择筛选类型:', type)
    console.log('🔥 当前 filterValues:', JSON.stringify(filterValues, null, 2))
    
    if (type === null) {
      // 清除类型筛选
      const newFilters = { ...filterValues }
      delete newFilters.business_stage
      delete newFilters.ai_category
      console.log('🔥 清除筛选，新的 filters:', JSON.stringify(newFilters, null, 2))
      setFilters(newFilters, {})
    } else {
      // 设置类型筛选
      const newFilters = { ...filterValues, business_stage: type }
      console.log('🔥 设置筛选，新的 filters:', JSON.stringify(newFilters, null, 2))
      console.log('🔥 调用 setFilters 函数...')
      setFilters(newFilters, {})
      console.log('🔥 setFilters 调用完成')
    }
    handleTypeFilterClose()
    console.log('🔥 =================筛选结束=================') 
  }

  const hasSelection = selectedIds && selectedIds.length > 0

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        py: 1,
        px: 2,
      }}
    >
      {/* 左侧：批量操作按钮（始终显示） */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {hasSelection && (
          <Typography sx={{ fontSize: '13px', color: '#666', mr: 1 }}>
            已选中 {selectedIds.length} 项
          </Typography>
        )}
        <Button
          size="small"
          variant="outlined"
          color="error"
          onClick={handleBulkDelete}
          disabled={!hasSelection}
          sx={{ minWidth: '60px', height: '28px', fontSize: '12px' }}
        >
          删除
        </Button>
        <Button
          size="small"
          variant="outlined"
          onClick={handleMarkAsRead}
          disabled={!hasSelection}
          sx={{ minWidth: '80px', height: '28px', fontSize: '12px' }}
        >
          标记已读
        </Button>
        <Button
          size="small"
          variant="outlined"
          onClick={handleMarkAsUnread}
          disabled={!hasSelection}
          sx={{ minWidth: '80px', height: '28px', fontSize: '12px' }}
        >
          标记未读
        </Button>
      </Box>

      {/* 🔥 中间：类型筛选区域 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1, justifyContent: 'center' }}>
        <Button
          size="small"
          variant={filterValues?.business_stage ? 'contained' : 'outlined'}
          startIcon={<FilterListIcon />}
          onClick={handleTypeFilterClick}
          sx={{ 
            minWidth: '100px', 
            height: '28px', 
            fontSize: '12px',
            bgcolor: filterValues?.business_stage ? '#1677ff' : 'transparent',
            '&:hover': {
              bgcolor: filterValues?.business_stage ? '#4096ff' : 'rgba(0, 0, 0, 0.04)'
            }
          }}
        >
          {filterValues?.business_stage || '按类型筛选'}
        </Button>
        
        {/* 类型筛选菜单 */}
        <Menu
          anchorEl={typeAnchorEl}
          open={typeMenuOpen}
          onClose={handleTypeFilterClose}
          transformOrigin={{ horizontal: 'center', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'center', vertical: 'bottom' }}
          PaperProps={{
            sx: {
              minWidth: 120,
              maxHeight: 400,
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              '& .MuiMenuItem-root': {
                fontSize: '0.875rem',
                py: 1,
                px: 2,
                '&:hover': {
                  bgcolor: '#f3f4f6'
                }
              }
            }
          }}
        >
          <MenuItem onClick={() => handleTypeFilterSelect(null)}>
            <Typography sx={{ fontWeight: !filterValues?.business_stage ? 600 : 400 }}>
              全部类型
            </Typography>
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('新客询盘')}>
            <Chip
              size="small"
              label="新客询盘"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#dbeafe',
                color: '#1e40af',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('报价跟进')}>
            <Chip
              size="small"
              label="报价跟进"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#fef3c7',
                color: '#92400e',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('样品阶段')}>
            <Chip
              size="small"
              label="样品阶段"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#fce7f3',
                color: '#9f1239',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('谈判议价')}>
            <Chip
              size="small"
              label="谈判议价"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#fed7aa',
                color: '#9a3412',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('订单确认')}>
            <Chip
              size="small"
              label="订单确认"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#dcfce7',
                color: '#14532d',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('生产跟踪')}>
            <Chip
              size="small"
              label="生产跟踪"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#e0e7ff',
                color: '#3730a3',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('售后服务')}>
            <Chip
              size="small"
              label="售后服务"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#fee2e2',
                color: '#991b1b',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('老客维护')}>
            <Chip
              size="small"
              label="老客维护"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#d1fae5',
                color: '#065f46',
                fontWeight: 500
              }}
            />
          </MenuItem>
          <MenuItem onClick={() => handleTypeFilterSelect('垃圾营销')}>
            <Chip
              size="small"
              label="垃圾营销"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                bgcolor: '#f3f4f6',
                color: '#6b7280',
                fontWeight: 500
              }}
            />
          </MenuItem>
        </Menu>
      </Box>

      {/* 右侧：翻页控件和导出按钮 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography sx={{ fontSize: '13px', color: '#666', lineHeight: '28px' }}>
          共 {total} 封
        </Typography>

        <MuiTextField
          value={inputPage}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          onKeyPress={handleInputKeyPress}
          size="small"
          variant="outlined"
          sx={{
            width: '50px',
            '& .MuiOutlinedInput-root': {
              height: '28px',
              fontSize: '13px',
              bgcolor: 'white',
              borderRadius: '2px',
              display: 'flex',
              alignItems: 'center',
              '& fieldset': {
                borderColor: '#d9d9d9',
              },
              '&:hover fieldset': {
                borderColor: '#40a9ff',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1677ff',
                borderWidth: '1px',
              },
            },
            '& input': {
              textAlign: 'center',
              padding: '0',
              fontSize: '13px',
              lineHeight: '28px',
              height: '28px',
              boxSizing: 'border-box',
            },
          }}
        />

        <Typography sx={{ fontSize: '13px', color: '#666', lineHeight: '28px' }}>
          / {totalPages} 页
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0, ml: 0.5 }}>
          <IconButton
            size="small"
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
            sx={{
              width: 28,
              height: 28,
              padding: 0,
              minHeight: 28,
              borderRadius: 0,
              color: '#666',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              '&:hover': { bgcolor: '#f5f5f5' },
              '&.Mui-disabled': { opacity: 0.25, color: '#d9d9d9' },
            }}
          >
            <ChevronLeftIcon sx={{ fontSize: 20 }} />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= totalPages}
            sx={{
              width: 28,
              height: 28,
              padding: 0,
              minHeight: 28,
              borderRadius: 0,
              color: '#666',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              '&:hover': { bgcolor: '#f5f5f5' },
              '&.Mui-disabled': { opacity: 0.25, color: '#d9d9d9' },
            }}
          >
            <ChevronRightIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </Box>

        {/* 导出按钮 - 与翻页按钮在同一组 */}
        <Box sx={{ ml: 2, display: 'flex', gap: 1 }}>
          <ExportButton label="导出" />
          
          {/* 🔥 预览模式按钮 */}
          {setPreviewMode && (
            <Button
              size="small"
              variant={previewMode ? 'contained' : 'outlined'}
              startIcon={<VisibilityIcon />}
              onClick={() => setPreviewMode(!previewMode)}
              sx={{
                minWidth: '90px',
                height: '28px',
                fontSize: '12px',
                bgcolor: previewMode ? '#1677ff' : 'transparent',
                '&:hover': {
                  bgcolor: previewMode ? '#4096ff' : 'rgba(0, 0, 0, 0.04)'
                }
              }}
            >
              预览模式
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  )
}

// 🔥 简化版分页器（不带筛选按钮，用于已发送和草稿箱）
const SimplePagination = () => {
  const { page, perPage, total, setPage } = useListContext()
  const { selectedIds, onUnselectItems } = useListContext()
  const notify = useNotify()
  const refresh = useRefresh()
  const totalPages = Math.ceil(total / perPage)
  const [inputPage, setInputPage] = useState(page)

  useEffect(() => {
    setInputPage(page)
  }, [page])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    if (value === '') {
      setInputPage(1)
    } else if (/^\d+$/.test(value)) {
      setInputPage(parseInt(value))
    }
  }

  const handleInputBlur = () => {
    if (inputPage >= 1 && inputPage <= totalPages) {
      setPage(inputPage)
    } else {
      setInputPage(page)
    }
  }

  const handleInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleInputBlur()
    }
  }

  const handleBulkDelete = async () => {
    if (!selectedIds || selectedIds.length === 0) {
      notify('请先选择要删除的邮件', { type: 'warning' })
      return
    }
    
    if (!window.confirm(`确定要删除选中的 ${selectedIds.length} 封邮件吗？`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const deletePromises = selectedIds.map((id: any) =>
        fetch(`http://127.0.0.1:8001/api/email_history/${id}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      )

      await Promise.all(deletePromises)
      notify(`已成功删除 ${selectedIds.length} 封邮件`, { type: 'success' })
      onUnselectItems()
      refresh()
    } catch (error) {
      notify('删除失败', { type: 'error' })
    }
  }

  const hasSelection = selectedIds && selectedIds.length > 0

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        py: 1,
        px: 2,
        borderBottom: '1px solid #e5e7eb',
      }}
    >
      {/* 左侧：批量操作按钮 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {hasSelection && (
          <Typography sx={{ fontSize: '13px', color: '#666', mr: 1 }}>
            已选中 {selectedIds.length} 项
          </Typography>
        )}
        <Button
          size="small"
          variant="outlined"
          color="error"
          onClick={handleBulkDelete}
          disabled={!hasSelection}
          sx={{ minWidth: '60px', height: '28px', fontSize: '12px' }}
        >
          删除
        </Button>
      </Box>

      {/* 右侧：翻页控件和导出按钮 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography sx={{ fontSize: '13px', color: '#666', lineHeight: '28px' }}>
          共 {total} 封
        </Typography>

        <MuiTextField
          value={inputPage}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          onKeyPress={handleInputKeyPress}
          size="small"
          variant="outlined"
          sx={{
            width: '50px',
            '& .MuiOutlinedInput-root': {
              height: '28px',
              fontSize: '13px',
              bgcolor: 'white',
              borderRadius: '2px',
              display: 'flex',
              alignItems: 'center',
              '& fieldset': {
                borderColor: '#d9d9d9',
              },
              '&:hover fieldset': {
                borderColor: '#40a9ff',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1677ff',
                borderWidth: '1px',
              },
            },
            '& input': {
              textAlign: 'center',
              p: 0,
            }
          }}
        />
        
        <Typography sx={{ fontSize: '13px', color: '#666', lineHeight: '28px' }}>
          / {totalPages} 页
        </Typography>

        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <IconButton
            size="small"
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
            sx={{
              width: '28px',
              height: '28px',
              border: '1px solid #d9d9d9',
              borderRadius: '2px',
              '&:hover': {
                borderColor: '#40a9ff',
                bgcolor: 'transparent'
              },
              '&.Mui-disabled': {
                borderColor: '#f0f0f0',
              }
            }}
          >
            <ChevronLeftIcon sx={{ fontSize: 20 }} />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages}
            sx={{
              width: '28px',
              height: '28px',
              border: '1px solid #d9d9d9',
              borderRadius: '2px',
              '&:hover': {
                borderColor: '#40a9ff',
                bgcolor: 'transparent'
              },
              '&.Mui-disabled': {
                borderColor: '#f0f0f0',
              }
            }}
          >
            <ChevronRightIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </Box>

        <Box sx={{ ml: 2 }}>
          <ExportButton label="导出" />
        </Box>
      </Box>
    </Box>
  )
}

const emailFilters = [
  <SelectInput key="direction" label="方向" source="direction" choices={[
    { id: 'outbound', name: '出站' },
    { id: 'inbound', name: '入站' },
  ]} />,
  <SelectInput key="opened" label="状态" source="opened" choices={[
    { id: 'true', name: '已读' },
    { id: 'false', name: '未读' },
  ]} />,
  <SelectInput key="replied" label="是否已回复" source="replied" choices={[
    { id: 'true', name: '已回复' },
    { id: 'false', name: '未回复' },
  ]} />
]

// 快速操作按钮组件（收件箱专用 - 完整功能）
const QuickActionsField = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const refresh = useRefresh()
  const navigate = useNavigate()
  const [analyzing, setAnalyzing] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const open = Boolean(anchorEl)
  const [isPinned, setIsPinned] = useState(record.is_starred || false)  // 使用is_starred字段标记是否置顶
  
  // 🔥 同步 record.is_starred 的变化
  useEffect(() => {
    setIsPinned(record.is_starred || false)
  }, [record.is_starred])
  
  if (!record) return null
  
  const handleMenuClick = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation()
    setAnchorEl(e.currentTarget)
  }
  
  const handleMenuClose = () => {
    setAnchorEl(null)
  }
  
  const handleReply = (e: React.MouseEvent) => {
    e.stopPropagation()
    handleMenuClose()
    navigate('/email_history/create', { 
      state: { 
        customer_id: record.customer_id,
        direction: 'outbound',
        subject: `Re: ${record.subject}`,
        to_email: record.from_email,
        from_email: record.from_email,
        originalBody: record.body,
        originalEmailId: record.id  // 🔥 传递原邮件ID，用于回复后更新replied状态
      } 
    })
  }
  
  const handleForward = (e: React.MouseEvent) => {
    e.stopPropagation()
    handleMenuClose()
    navigate('/email_history/create', { 
      state: { 
        direction: 'outbound',
        subject: `Fwd: ${record.subject}`,
        body: `\n\n---------- Forwarded message ---------\n${record.body}`,
        from_email: record.from_email,
        originalBody: record.body
      } 
    })
  }
  
  const handleToggleRead = async (e: React.MouseEvent) => {
    e.stopPropagation()
    handleMenuClose()
    
    try {
      const token = localStorage.getItem('token')
      console.log(`🔄 标记邮件 ID=${record.id} 为 ${record.opened ? '未读' : '已读'}`)
      
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${record.id}`, {
        method: 'PATCH',  // 🔥 改用PATCH方法
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          opened: !record.opened  // 🔥 只发送opened字段
        })
      })
      
      console.log(`🔄 响应状态: ${response.status}`)
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ 更新成功:', data)
        notify(record.opened ? '已标记为未读' : '已标记为已读', { type: 'success' })
        refresh()
      } else {
        const error = await response.json()
        console.error('❌ 更新失败:', error)
        notify('操作失败', { type: 'error' })
      }
    } catch (error) {
      console.error('❌ 请求异常:', error)
      notify('操作失败', { type: 'error' })
    }
  }
  
  // 🔥 新增：触发AI分析
  const handleAIAnalysis = async (e: React.MouseEvent) => {
    e.stopPropagation()
    handleMenuClose()
    
    if (analyzing) return
    
    try {
      setAnalyzing(true)
      const token = localStorage.getItem('token')
      
      // 调用AI分析任务API
      const response = await fetch(`http://127.0.0.1:8001/api/ai/analyze-email/${record.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        }
      })
      
      if (response.ok) {
        notify('AI分析已提交，正在处理中...', { type: 'info' })
        // 3秒后刷新页面以显示分析结果
        setTimeout(() => {
          refresh()
          notify('AI分析完成！', { type: 'success' })
        }, 3000)
      } else {
        notify('AI分析失败', { type: 'error' })
      }
    } catch (error) {
      notify('AI分析失败', { type: 'error' })
    } finally {
      setAnalyzing(false)
    }
  }
  
  // 🔥 新增：切换置顶状态
  const handleTogglePin = async (e: React.MouseEvent) => {
    e.stopPropagation()
    
    try {
      const token = localStorage.getItem('token')
      const newPinState = !isPinned
      
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${record.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          is_starred: newPinState
        })
      })
      
      if (response.ok) {
        setIsPinned(newPinState)
        notify(newPinState ? '已置顶' : '已取消置顶', { type: 'success' })
        refresh()
      } else {
        notify('操作失败', { type: 'error' })
      }
    } catch (error) {
      notify('操作失败', { type: 'error' })
    }
  }
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
      <Tooltip title="更多操作">
        <IconButton 
          size="small" 
          onClick={handleMenuClick}
          sx={{ 
            color: '#6b7280',
            padding: '4px'
          }}
        >
          <MoreVertIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      
      {/* 🔥 置顶按钮 */}
      <Tooltip title={isPinned ? "取消置顶" : "置顶邮件"}>
        <IconButton 
          size="small" 
          onClick={handleTogglePin}
          sx={{ 
            color: isPinned ? '#f59e0b' : '#9ca3af',
            padding: '4px'
          }}
        >
          <PushPinIcon fontSize="small" sx={{
            transform: isPinned ? 'rotate(0deg)' : 'rotate(45deg)',
            transition: 'transform 0.2s'
          }} />
        </IconButton>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        onClick={(e) => e.stopPropagation()}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: {
            minWidth: 160,
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            '& .MuiMenuItem-root': {
              fontSize: '0.875rem',
              py: 1,
              '&:hover': {
                bgcolor: '#f3f4f6'
              }
            }
          }
        }}
      >
        <MenuItem onClick={handleReply}>
          <ListItemIcon>
            <ReplyIcon fontSize="small" sx={{ color: '#3b82f6' }} />
          </ListItemIcon>
          <ListItemText>回复</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleForward}>
          <ListItemIcon>
            <ForwardIcon fontSize="small" sx={{ color: '#8b5cf6' }} />
          </ListItemIcon>
          <ListItemText>转发</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleToggleRead}>
          <ListItemIcon>
            {record.opened ? (
              <MarkEmailUnreadIcon fontSize="small" sx={{ color: '#f59e0b' }} />
            ) : (
              <MarkEmailReadIcon fontSize="small" sx={{ color: '#10b981' }} />
            )}
          </ListItemIcon>
          <ListItemText>{record.opened ? '标记为未读' : '标记为已读'}</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleAIAnalysis} disabled={analyzing}>
          <ListItemIcon>
            {analyzing ? (
              <AutoFixHighIcon fontSize="small" sx={{ color: '#9ca3af', animation: 'spin 1s linear infinite' }} />
            ) : (
              <AutoFixHighIcon fontSize="small" sx={{ color: '#8b5cf6' }} />
            )}
          </ListItemIcon>
          <ListItemText>{analyzing ? 'AI分析中...' : 'AI智能分析'}</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  )
}

// 简化操作按钮组件（已发送/草稿箱专用 - 只有置顶按钮）
const SimpleQuickActionsField = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const refresh = useRefresh()
  const [isPinned, setIsPinned] = useState(record.is_starred || false)
  
  // 🔥 同步 record.is_starred 的变化
  useEffect(() => {
    setIsPinned(record.is_starred || false)
  }, [record.is_starred])
  
  if (!record) return null
  
  // 🔥 切换置顶状态
  const handleTogglePin = async (e: React.MouseEvent) => {
    e.stopPropagation()
    
    try {
      const token = localStorage.getItem('token')
      const newPinState = !isPinned
      
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${record.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          is_starred: newPinState
        })
      })
      
      if (response.ok) {
        setIsPinned(newPinState)
        notify(newPinState ? '已置顶' : '已取消置顶', { type: 'success' })
        refresh()
      } else {
        notify('操作失败', { type: 'error' })
      }
    } catch (error) {
      notify('操作失败', { type: 'error' })
    }
  }
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {/* 🔥 只保留置顶按钮 */}
      <Tooltip title={isPinned ? "取消置顶" : "置顶邮件"}>
        <IconButton 
          size="small" 
          onClick={handleTogglePin}
          sx={{ 
            color: isPinned ? '#f59e0b' : '#9ca3af',
            padding: '4px'
          }}
        >
          <PushPinIcon fontSize="small" sx={{
            transform: isPinned ? 'rotate(0deg)' : 'rotate(45deg)',
            transition: 'transform 0.2s'
          }} />
        </IconButton>
      </Tooltip>
    </Box>
  )
}

const EmailBulkActionButtons = () => (
  <>
    <BulkDeleteButton label="删除" />
  </>
)

const EmailListActions = () => (
  <TopToolbar>
    {/* 导出按钮已移到翻页器那一行 */}
  </TopToolbar>
)

// 带固定头部的邮件列表包装组件
const EmailListWithFixedHeader = (props: any) => {
  const navigate = useNavigate()
  const notify = useNotify()
  const refresh = useRefresh()
  
  // 预览模式状态
  const [previewMode, setPreviewMode] = useState(false)
  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null)
  const [selectedEmailData, setSelectedEmailData] = useState<any>(null)
  const [translating, setTranslating] = useState(false)
  const [translatedContent, setTranslatedContent] = useState<string | null>(null)
  const [showTranslation, setShowTranslation] = useState(false)
  
  // 处理邮件点击
  const handleEmailClick = (record: any) => {
    if (previewMode) {
      // 预览模式：更新右侧详情
      setSelectedEmailId(record.id)
      setSelectedEmailData(null)
      setTranslatedContent(null)
      setShowTranslation(false)
      
      // 获取邮件详情并标记为已读
      const token = localStorage.getItem('token')
      if (token) {
        fetch(`http://127.0.0.1:8001/api/email_history/${record.id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          }
        })
        .then(response => response.json())
        .then(data => {
          setSelectedEmailData(data)
          
          // 标记为已读
          if (!data.opened) {
            fetch(`http://127.0.0.1:8001/api/email_history/${record.id}`, {
              method: 'PATCH',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({ opened: true })
            })
            .then(() => refresh())
          }
        })
        .catch(error => {
          console.error('获取邮件详情失败:', error)
          notify('获取邮件详情失败', { type: 'error' })
        })
      }
    } else {
      // 普通模式：跳转到详情页
      if (record.status === 'draft') {
        const isDraftsPage = window.location.hash.includes('status":"draft')
        navigate('/email_history/create', {
          state: {
            ...record,
            fromDrafts: isDraftsPage
          }
        })
      } else {
        navigate(`/email_history/${record.id}/show`)
      }
    }
  }
  
  // 处理翻译
  const handleTranslate = async () => {
    if (!selectedEmailData) {
      notify('邮件数据还未加载', { type: 'warning' })
      return
    }
    
    if (translatedContent) {
      setShowTranslation(!showTranslation)
      return
    }
    
    setTranslating(true)
    try {
      const token = localStorage.getItem('token')
      const content = selectedEmailData.html_body || selectedEmailData.body
      
      const response = await fetch('http://127.0.0.1:8001/api/ai/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          content: content,
          target_lang: 'zh'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setTranslatedContent(data.translated)
        setShowTranslation(true)
        notify('翻译完成', { type: 'success' })
      } else {
        notify('翻译失败', { type: 'error' })
      }
    } catch (error) {
      console.error('翻译异常:', error)
      notify('翻译失败', { type: 'error' })
    } finally {
      setTranslating(false)
    }
  }
  
  // 处理回复
  const handleReply = () => {
    if (!selectedEmailData) {
      notify('请先选择邮件', { type: 'warning' })
      return
    }
    
    navigate('/email_history/create', { 
      state: { 
        customer_id: selectedEmailData.customer_id,
        direction: 'outbound',
        subject: `Re: ${selectedEmailData.subject}`,
        to_email: selectedEmailData.from_email,
        from_email: selectedEmailData.to_email,
        originalBody: selectedEmailData.body || selectedEmailData.html_body,
        originalEmailId: selectedEmailData.id
      } 
    })
  }
  
  // 处理删除
  const handleDelete = async () => {
    if (!selectedEmailData) {
      notify('请先选择邮件', { type: 'warning' })
      return
    }
    
    if (!window.confirm('确定要删除这封邮件吗？')) {
      return
    }
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${selectedEmailData.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_deleted: true })
      })
      
      if (response.ok) {
        notify('邮件已移至回收站', { type: 'success' })
        setSelectedEmailId(null)
        setSelectedEmailData(null)
        refresh()
      } else {
        notify('删除失败', { type: 'error' })
      }
    } catch (error) {
      console.error('删除邮件异常:', error)
      notify('删除失败', { type: 'error' })
    }
  }
  
  return (
    <Box sx={{
      marginTop: '-61px',
      height: 'calc(100vh - 64px)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* 固定的翻页器区域 */}
      <Box sx={{ 
        flexShrink: 0,
        backgroundColor: 'white',
        zIndex: 100,
      }}>
        <CustomPagination previewMode={previewMode} setPreviewMode={setPreviewMode} />
      </Box>

      {/* 内容区域 - 根据预览模式变化布局 */}
      <Box sx={{ 
        flex: 1,
        display: 'flex',
        overflow: 'hidden',
      }}>
        {/* 左侧：邮件列表 */}
        <Box sx={{ 
          width: previewMode ? '40%' : '100%',
          minWidth: previewMode ? '400px' : 'auto',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderRight: previewMode ? '1px solid #e5e7eb' : 'none',
          transition: 'width 0.3s',
          bgcolor: 'white',
        }}>
          {/* 表格区域 */}
          <Box sx={{ 
            flex: 1,
            overflow: 'auto',
            '&::-webkit-scrollbar': previewMode ? {
              width: '6px',
            } : {},
            '&::-webkit-scrollbar-thumb': previewMode ? {
              backgroundColor: '#d1d5db',
              borderRadius: '3px',
            } : {},
            '& .MuiTableContainer-root': {
              overflow: 'visible !important',
            },
            '& table': {
              '& thead': {
                position: 'sticky',
                top: 0,
                zIndex: 10,
                '& th': {
                  backgroundColor: '#f9fafb !important',
                  height: '48px',
                  padding: previewMode ? '8px 12px' : '12px 16px',
                  fontSize: previewMode ? '12px' : '14px',
                }
              }
            }
          }}>
        <Datagrid
          rowClick={(id, resource, record) => {
            handleEmailClick(record)
            return false
          }}
          bulkActionButtons={<EmailBulkActionButtons />}
          sx={{
            '& .RaDatagrid-headerCell': { 
              fontWeight: 600, 
              backgroundColor: '#f9fafb',
              fontSize: previewMode ? '12px' : '14px',
            },
            '& .RaDatagrid-row': { 
              cursor: 'pointer',
              '&:hover': { 
                backgroundColor: '#f3f4f6'
              },
            },
            '& .RaDatagrid-rowCell': {
              padding: previewMode ? '8px 12px !important' : '12px 16px !important',
              fontSize: previewMode ? '12px' : '14px',
            },
            '& .column-status': { 
              width: previewMode ? '25px' : '35px',
              minWidth: previewMode ? '25px' : '35px',
              maxWidth: previewMode ? '25px' : '35px',
              textAlign: 'left',
              paddingLeft: '8px !important'
            },
            '& .column-direction': { 
              width: '35px',
              minWidth: '35px',
              maxWidth: '35px',
              textAlign: 'left',
              paddingLeft: '8px !important',
              display: previewMode ? 'none' : 'table-cell',
            },
            '& .column-type': { 
              width: previewMode ? '70px' : '110px',
              minWidth: previewMode ? '70px' : '110px',
              maxWidth: previewMode ? '70px' : '110px',
              textAlign: 'center',
              display: previewMode ? 'none' : 'table-cell',
            },
            '& .column-from': { 
              width: previewMode ? '120px' : '200px',
              minWidth: previewMode ? '120px' : '200px',
              maxWidth: previewMode ? '120px' : '200px',
            },
            '& .column-subject': { 
              width: previewMode ? '200px' : '350px',
              minWidth: previewMode ? '200px' : '350px',
              maxWidth: previewMode ? '200px' : '350px',
              overflow: 'hidden'
            },
            '& .column-reply-status': { 
              width: '80px',
              minWidth: '80px',
              maxWidth: '80px',
              textAlign: 'center',
              display: previewMode ? 'none' : 'table-cell',
            },
            '& .column-attachment': { 
              width: '50px',
              minWidth: '50px',
              maxWidth: '50px',
              display: previewMode ? 'none' : 'table-cell',
            },
            '& .column-time': { 
              width: previewMode ? '80px' : '90px',
              minWidth: previewMode ? '80px' : '90px',
              maxWidth: previewMode ? '80px' : '90px',
            },
            '& .column-actions': { 
              width: '80px',
              minWidth: '80px',
              maxWidth: '80px',
              textAlign: 'center !important',
              display: previewMode ? 'none' : 'table-cell',
              '& .RaDatagrid-headerCell': {
                textAlign: 'center !important'
              }
            },
            '& table': {
              tableLayout: 'fixed',
              width: '100%'
            },
          }}
          rowStyle={(record) => {
            const isSelected = previewMode && selectedEmailId === record.id
            return {
              backgroundColor: isSelected ? '#dbeafe' : (!record.opened && !isSelected && !previewMode ? '#f0f9ff' : undefined),
              borderLeft: isSelected ? '4px solid #2563eb' : undefined,
              fontWeight: !record.opened ? 600 : 400,
            }
          }}
        >
          <FunctionField label="" render={(record:any) => (
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start', gap: 0 }}>
              {/* 未读蓝色圆点 */}
              {!record.opened && record.status !== 'draft' && (
                <Tooltip title="未读">
                  <Box sx={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: '#3b82f6',
                    flexShrink: 0
                  }} />
                </Tooltip>
              )}
              {/* 草稿图标 */}
              {record.status === 'draft' && (
                <Tooltip title="草稿">
                  <DraftsIcon sx={{ fontSize: 14, color: '#f59e0b' }} />
                </Tooltip>
              )}
              {/* 已回复图标 */}
              {record.replied && (
                <Tooltip title="已回复">
                  <CheckCircleIcon sx={{ fontSize: 14, color: '#10b981' }} />
                </Tooltip>
              )}
            </Box>
          )} headerClassName="column-status" cellClassName="column-status" />
          
          {/* 🔥 邮件类型列 */}
          <FunctionField label="类型" render={(record:any) => {
            if (!record.business_stage && !record.ai_category) return <Box sx={{ textAlign: 'center', color: '#9ca3af' }}>-</Box>
            
            // 英文到中文的映射
            const categoryMap: Record<string, string> = {
              'inquiry': '新客询盘',
              'quotation': '报价跟进',
              'sample': '样品阶段',
              'negotiation': '谈判议价',
              'order': '订单确认',
              'production': '生产跟踪',
              'support': '售后服务',
              'maintenance': '老客维护',
              'spam': '垃圾营销',
              'other': '垃圾营销',  // 兼容旧数据，将other映射为垃圾营销
              'general': '垃圾营销',  // 兼容旧数据
              'complaint': '售后服务',
              'follow_up': '老客维护'
            }
            
            // 业务阶段颜色映射
            const stageColors: Record<string, { bg: string, text: string }> = {
              '新客询盘': { bg: '#dbeafe', text: '#1e40af' },
              '报价跟进': { bg: '#fef3c7', text: '#92400e' },
              '样品阶段': { bg: '#fce7f3', text: '#9f1239' },
              '谈判议价': { bg: '#fed7aa', text: '#9a3412' },
              '订单确认': { bg: '#dcfce7', text: '#14532d' },
              '生产跟踪': { bg: '#e0e7ff', text: '#3730a3' },
              '售后服务': { bg: '#fee2e2', text: '#991b1b' },
              '老客维护': { bg: '#d1fae5', text: '#065f46' },
              '垃圾营销': { bg: '#f3f4f6', text: '#6b7280' },
              // 英文分类的颜色
              '询盘': { bg: '#dbeafe', text: '#1e40af' },
              '样品': { bg: '#fce7f3', text: '#9f1239' },
              '订单': { bg: '#dcfce7', text: '#14532d' },
              '投诉': { bg: '#fee2e2', text: '#991b1b' },
              '其他': { bg: '#f3f4f6', text: '#6b7280' },
              '报价': { bg: '#fef3c7', text: '#92400e' },
              '付款': { bg: '#d1fae5', text: '#065f46' },
              '出货': { bg: '#e0e7ff', text: '#3730a3' },
              '支持': { bg: '#fee2e2', text: '#991b1b' }
            }
            
            const stage = record.business_stage || ''
            // 将英文分类转为中文
            const category = record.ai_category ? categoryMap[record.ai_category] || record.ai_category : ''
            const displayLabel = stage || category || '未分类'
            const colors = stageColors[displayLabel] || { bg: '#f3f4f6', text: '#6b7280' }
            
            return (
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Chip
                  size="small"
                  label={displayLabel}
                  sx={{
                    height: 22,
                    fontSize: '0.75rem',
                    bgcolor: colors.bg,
                    color: colors.text,
                    fontWeight: 500,
                    '& .MuiChip-label': { px: 1, py: 0 }
                  }}
                />
              </Box>
            )
          }} headerClassName="column-type" cellClassName="column-type" />
          
          <FunctionField label="发件人" render={(record:any) => {
            const email = record.from_email || ''
            
            // 优先使用数据库中存储的发件人名称（从邮件头部解析）
            let displayName = record.from_name || ''
            
            // 如果数据库中没有名称，则从邮箱地址推测
            if (!displayName && email) {
              const namePart = email.split('@')[0] || ''
              const parts: string[] = namePart.split(/[._-]/)  // 按点、下划线、连字符分割
              displayName = parts
                .map((part: string) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
                .join(' ')
            }
            
            return (
              <Box sx={{ 
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                display: 'block'
              }}>
                {displayName && (
                  <>
                    <span style={{ fontWeight: 500 }}>{displayName}</span>
                    <span style={{ color: '#9ca3af', margin: '0 6px' }}>|</span>
                  </>
                )}
                <span style={{ color: '#6b7280', fontSize: '0.85em' }}>{email}</span>
              </Box>
            )
          }} headerClassName="column-from" cellClassName="column-from" />
          
          <FunctionField label="主题" render={(record:any) => {
            // 🔥 检查是否有附件
            const hasAttachments = record.attachments && record.attachments !== 'null' && record.attachments !== 'None'
            
            return (
              <Box sx={{ 
                width: '100%',
                maxWidth: '100%',
                overflow: 'hidden',
                padding: '4px 0'
              }}>
                <Tooltip 
                  title={
                    <Box sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', maxWidth: '400px' }}>
                      <Box sx={{ fontWeight: 600, mb: 1 }}>主题：</Box>
                      <Box sx={{ mb: 2 }}>{record.subject || '(无主题)'}</Box>
                      {record.body && (
                        <>  
                          <Box sx={{ fontWeight: 600, mb: 1 }}>正文预览：</Box>
                          <Box>{extractPlainText(record.body).substring(0, 300)}</Box>
                        </>
                      )}
                      {/* AI摘要 */}
                      {record.ai_summary && (
                        <>
                          <Box sx={{ fontWeight: 600, mb: 1, mt: 2, color: '#3b82f6' }}>AI摘要：</Box>
                          <Box sx={{ color: '#3b82f6' }}>{record.ai_summary}</Box>
                        </>
                      )}
                    </Box>
                  } 
                  arrow
                  placement="bottom-start"
                  disableHoverListener={previewMode}  // 🔥 预览模式下禁用悬停提示
                >
                  <Box>
                    <Box sx={{ 
                      fontWeight: record.opened ? 400 : 600, 
                      mb: 0.3,
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis', 
                      whiteSpace: 'nowrap',
                      width: '100%',
                      fontSize: '0.875rem',
                      lineHeight: 1.3,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5
                    }}>
                      <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {record.subject || '(无主题)'}
                      </span>
                      {/* 🔥 附件图标 */}
                      {hasAttachments && (
                        <AttachFileIcon sx={{ 
                          fontSize: 16, 
                          color: '#6b7280',
                          flexShrink: 0
                        }} />
                      )}
                    </Box>
                    <Box sx={{ 
                      fontSize: '0.7rem', 
                      color: 'text.secondary', 
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis', 
                      whiteSpace: 'nowrap',
                      width: '100%',
                      lineHeight: 1.2
                    }}>
                      {record.body ? extractPlainText(record.body).substring(0, 50) + '...' : ''}
                    </Box>
                    {/* AI分析徽章 */}
                    <AIAnalysisChips />
                  </Box>
                </Tooltip>
              </Box>
            )
          }} headerClassName="column-subject" cellClassName="column-subject" />
          
          {/* 🔥 回复状态列 */}
          <FunctionField label="状态" render={(record:any) => (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              {record.replied ? (
                <Chip
                  size="small"
                  label="已回复"
                  sx={{
                    height: 22,
                    fontSize: '0.75rem',
                    bgcolor: '#dcfce7',
                    color: '#14532d',
                    fontWeight: 500,
                    '& .MuiChip-label': { px: 0.75, py: 0 }
                  }}
                />
              ) : (
                <Chip
                  size="small"
                  label="未回复"
                  sx={{
                    height: 22,
                    fontSize: '0.75rem',
                    bgcolor: '#f3f4f6',
                    color: '#6b7280',
                    fontWeight: 500,
                    '& .MuiChip-label': { px: 0.75, py: 0 }
                  }}
                />
              )}
            </Box>
          )} headerClassName="column-reply-status" cellClassName="column-reply-status" />
          
          <FunctionField label="时间" render={() => <RelativeTimeField source="sent_at" />} headerClassName="column-time" cellClassName="column-time" />
          
          <FunctionField label="操作" render={() => <QuickActionsField />} headerClassName="column-actions" cellClassName="column-actions" />
        </Datagrid>
          </Box>
        </Box>
        
        {/* 右侧：邮件详情（仅在预览模式下显示） */}
        {previewMode && (
          <Box sx={{ 
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            bgcolor: '#f9fafb',
          }}>
            {!selectedEmailId ? (
              // 未选择邮件
              <Box sx={{ 
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#9ca3af'
              }}>
                <Typography variant="body1">请选择邮件查看详情</Typography>
              </Box>
            ) : !selectedEmailData ? (
              // 加载中
              <Box sx={{ 
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                gap: 2
              }}>
                <CircularProgress />
                <Typography sx={{ color: '#6b7280' }}>加载邮件详情中...</Typography>
              </Box>
            ) : (
              // 邮件详情
              <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', bgcolor: 'white', overflow: 'hidden' }}>
                {/* 顶部操作栏 */}
                <Box sx={{ px: 3, py: 2, flexShrink: 0 }}>
                  <Box sx={{ display: 'flex', gap: 1, pb: 2, borderBottom: '1px solid #e5e7eb' }}>
                  <Button 
                    startIcon={<ReplyIcon />} 
                    onClick={handleReply} 
                    variant="contained" 
                    size="small"
                    sx={{ 
                      bgcolor: '#1677ff', 
                      '&:hover': { bgcolor: '#4096ff' },
                      fontSize: '12px'
                    }}
                  >
                    回复
                  </Button>
                  
                  <Button 
                    startIcon={<DeleteIcon />} 
                    onClick={handleDelete} 
                    variant="outlined" 
                    size="small"
                    color="error"
                    sx={{ fontSize: '12px' }}
                  >
                    删除
                  </Button>
                  </Box>
                </Box>
                
                {/* 邮件内容区域 */}
                <Box sx={{ 
                  flex: 1,
                  overflow: 'auto',
                  p: 3,
                  '&::-webkit-scrollbar': {
                    width: '6px',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    backgroundColor: '#d1d5db',
                    borderRadius: '3px',
                  },
                }}>
                  {/* 主题 */}
                  <Typography variant="h6" sx={{ mb: 2, fontSize: '18px', fontWeight: 600 }}>
                    {selectedEmailData.subject || '(无主题)'}
                  </Typography>
                  
                  {/* 发件人信息 */}
                  <Box sx={{ 
                    mb: 2,
                    pb: 2,
                    borderBottom: '1px solid #e5e7eb',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    fontSize: '13px'
                  }}>
                    <Box sx={{ 
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      bgcolor: '#ef4444',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '14px',
                      fontWeight: 600
                    }}>
                      {selectedEmailData.from_name?.charAt(0) || selectedEmailData.from_email?.charAt(0)?.toUpperCase() || 'U'}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ fontWeight: 600 }}>
                        {selectedEmailData.from_name || selectedEmailData.from_email?.split('@')[0] || '未知发件人'}
                      </Box>
                      <Box sx={{ fontSize: '12px', color: '#6b7280' }}>
                        {selectedEmailData.from_email}
                      </Box>
                    </Box>
                    <Box sx={{ fontSize: '12px', color: '#9ca3af' }}>
                      {selectedEmailData.sent_at ? new Date(selectedEmailData.sent_at).toLocaleString('zh-CN', {
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      }) : '-'}
                    </Box>
                  </Box>
                  
                  {/* 翻译提示条 */}
                  <Box sx={{ 
                    mb: 2,
                    p: 1.5,
                    bgcolor: '#f0f9ff',
                    borderRadius: '4px',
                    border: '1px solid #bae6fd',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <TranslateIcon sx={{ fontSize: 18, color: '#0284c7' }} />
                      <Typography sx={{ fontSize: '13px', color: '#0c4a6e' }}>
                        {showTranslation ? '正在查看中文翻译' : '邮件可翻译为中文'}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {translatedContent && (
                        <Button
                          size="small"
                          onClick={() => setShowTranslation(!showTranslation)}
                          sx={{ fontSize: '12px', textTransform: 'none', color: '#0284c7' }}
                        >
                          {showTranslation ? '查看原文' : '查看翻译'}
                        </Button>
                      )}
                      
                      {!translatedContent && (
                        <Button
                          size="small"
                          onClick={handleTranslate}
                          disabled={translating}
                          startIcon={translating ? <CircularProgress size={14} /> : null}
                          sx={{ fontSize: '12px', textTransform: 'none', color: '#0284c7', fontWeight: 500 }}
                        >
                          {translating ? '翻译中...' : '全文翻译'}
                        </Button>
                      )}
                      
                      <IconButton 
                        size="small" 
                        onClick={() => {
                          setShowTranslation(false)
                          setTranslatedContent(null)
                        }}
                        sx={{ ml: 1 }}
                      >
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                    </Box>
                  </Box>
                  
                  {/* 邮件正文 */}
                  <Box sx={{ 
                    p: 2,
                    bgcolor: '#ffffff',
                    borderRadius: '4px',
                    border: '1px solid #e5e7eb',
                    minHeight: '300px'
                  }}>
                    {showTranslation && translatedContent ? (
                      <HtmlContent content={translatedContent} />
                    ) : (
                      <HtmlContent content={selectedEmailData.html_body || selectedEmailData.body} />
                    )}
                  </Box>
                  
                  {/* 🔥 附件区域 */}
                  {selectedEmailData?.attachments && selectedEmailData.attachments !== 'null' && selectedEmailData.attachments !== 'None' && (() => {
                    try {
                      // 处理Python风格的单引号JSON（将单引号替换为双引号）
                      let attachmentsStr = selectedEmailData.attachments
                      if (typeof attachmentsStr === 'string') {
                        // Python的字典字符串转换为JSON
                        attachmentsStr = attachmentsStr.replace(/'/g, '"')
                      }
                      
                      const attachments = JSON.parse(attachmentsStr)
                      console.log('📎 预览模式-附件数据:', attachments)
                      
                      if (Array.isArray(attachments) && attachments.length > 0) {
                        // 计算总大小
                        const totalSize = attachments.reduce((sum, file) => sum + (file.size || 0), 0)
                        const totalSizeKB = (totalSize / 1024).toFixed(1)
                        
                        return (
                          <Box sx={{ mt: 2 }}>
                            {/* 附件标题 */}
                            <Box sx={{ 
                              fontSize: '13px',
                              color: '#6b7280',
                              mb: 1.5,
                              fontWeight: 500
                            }}>
                              {totalSizeKB} KB · {attachments.length}个附件
                            </Box>
                            
                            {/* 附件列表 - 横向排列 */}
                            <Box sx={{ 
                              display: 'flex', 
                              flexWrap: 'wrap',
                              gap: 1.5
                            }}>
                              {attachments.map((file: any, index: number) => {
                                const fileName = typeof file === 'string' ? file : (file.filename || file.name || '未知文件')
                                const fileSize = file.size ? `${(file.size / 1024).toFixed(0)} KB` : '未知大小'
                                
                                // 🔥 下载附件函数
                                const handleDownload = async () => {
                                  try {
                                    const response = await fetch(
                                      getApiUrl('email', `/email_history/${selectedEmailData.id}/attachments/${index}`),
                                      {
                                        method: 'GET',
                                        headers: {
                                          'Accept': '*/*'
                                        }
                                      }
                                    )
                                    
                                    if (!response.ok) {
                                      throw new Error('下载失败')
                                    }
                                    
                                    // 获取文件blob
                                    const blob = await response.blob()
                                    
                                    // 创建下载链接
                                    const url = window.URL.createObjectURL(blob)
                                    const a = document.createElement('a')
                                    a.href = url
                                    a.download = fileName
                                    document.body.appendChild(a)
                                    a.click()
                                    
                                    // 清理
                                    window.URL.revokeObjectURL(url)
                                    document.body.removeChild(a)
                                    
                                    console.log('✅ 附件下载成功:', fileName)
                                  } catch (error) {
                                    console.error('❌ 下载附件失败:', error)
                                    alert('下载失败，请重试')
                                  }
                                }
                                
                                return (
                                  <Box 
                                    key={index} 
                                    sx={{ 
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      gap: 1,
                                      px: 1.5,
                                      py: 1,
                                      bgcolor: '#f9fafb',
                                      borderRadius: '6px',
                                      border: '1px solid #e5e7eb',
                                      cursor: 'pointer',
                                      '&:hover': { 
                                        bgcolor: '#f3f4f6',
                                        borderColor: '#d1d5db'
                                      },
                                      maxWidth: '280px'
                                    }}
                                    onClick={handleDownload}
                                    title="点击下载附件"
                                  >
                                    <AttachFileIcon sx={{ fontSize: 18, color: '#6b7280', flexShrink: 0 }} />
                                    <Box sx={{ 
                                      fontSize: '13px', 
                                      color: '#374151',
                                      overflow: 'hidden',
                                      textOverflow: 'ellipsis',
                                      whiteSpace: 'nowrap',
                                      flex: 1,
                                      minWidth: 0
                                    }}>
                                      {fileName}
                                    </Box>
                                    <Box sx={{ 
                                      fontSize: '12px', 
                                      color: '#9ca3af',
                                      flexShrink: 0,
                                      ml: 0.5
                                    }}>
                                      {fileSize}
                                    </Box>
                                    <IconButton 
                                      size="small" 
                                      sx={{ 
                                        p: 0.5,
                                        ml: 0.5,
                                        color: '#3b82f6',
                                        '&:hover': { bgcolor: '#eff6ff' }
                                      }}
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        handleDownload()
                                      }}
                                    >
                                      <CloudDownloadIcon sx={{ fontSize: 16 }} />
                                    </IconButton>
                                  </Box>
                                )
                              })}
                            </Box>
                          </Box>
                        )
                      }
                    } catch (e) {
                      console.error('🐞 预览模式-解析附件数据失败:', e, selectedEmailData.attachments)
                    }
                    return null
                  })()}
                </Box>
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Box>
  )
}

// 🔥 已发送邮件列表（使用简化分页器）
const SentListWithFixedHeader = (props: any) => {
  const navigate = useNavigate()
  
  return (
    <Box sx={{
      marginTop: '0px',
      height: 'calc(100vh - 64px)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* 固定的翻页器区域（简化版） */}
      <Box sx={{ 
        flexShrink: 0,
        backgroundColor: 'white',
        zIndex: 100,
      }}>
        <SimplePagination />
      </Box>

      {/* 可滚动的表格区域 */}
      <Box sx={{ 
        flex: 1,
        overflow: 'auto',
        '& .MuiTableContainer-root': {
          overflow: 'visible !important',
        },
        '& table': {
          '& thead': {
            position: 'sticky',
            top: 0,
            zIndex: 10,
            '& th': {
              backgroundColor: '#f9fafb !important',
              height: '48px',
              padding: '12px 16px',
            }
          }
        }
      }}>
        <Datagrid
          rowClick={(id, resource, record) => {
            // 🔥 跳转到 email_history 资源的详情页
            navigate(`/email_history/${record.id}/show`)
            return false  // 阻止默认导航
          }}
          bulkActionButtons={<EmailBulkActionButtons />}
          sx={{
            '& .RaDatagrid-headerCell': { 
              fontWeight: 600, 
              backgroundColor: '#f9fafb'
            },
            '& .RaDatagrid-row': { 
              '&:hover': { backgroundColor: '#f3f4f6' } 
            },
            // 🔥 操作列居中对齐
            '& .column-actions': {
              textAlign: 'center !important',
              '& .RaDatagrid-headerCell': {
                textAlign: 'center !important'
              }
            }
          }}
        >
          <FunctionField label="收件人" render={(record:any) => (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {/* 🔥 投递状态图标 */}
              <DeliveryStatusIcon status={record.delivery_status} />
              <span>{record.to_email || '-'}</span>
            </Box>
          )} />
          <FunctionField label="主题" render={(record:any) => (
            <Box>{record.subject || '(无主题)'}</Box>
          )} />
          <FunctionField label="时间" render={() => <RelativeTimeField source="sent_at" />} />
          <FunctionField 
            label="操作" 
            render={() => <SimpleQuickActionsField />} 
            headerClassName="column-actions" 
            cellClassName="column-actions" 
          />
        </Datagrid>
      </Box>
    </Box>
  )
}

// 🔥 草稿箱邮件列表（使用简化分页器）
const DraftsListWithFixedHeader = (props: any) => {
  const navigate = useNavigate()
  
  return (
    <Box sx={{
      marginTop: '0px',
      height: 'calc(100vh - 64px)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* 固定的翻页器区域（简化版） */}
      <Box sx={{ 
        flexShrink: 0,
        backgroundColor: 'white',
        zIndex: 100,
      }}>
        <SimplePagination />
      </Box>

      {/* 可滚动的表格区域 */}
      <Box sx={{ 
        flex: 1,
        overflow: 'auto',
        '& .MuiTableContainer-root': {
          overflow: 'visible !important',
        },
        '& table': {
          '& thead': {
            position: 'sticky',
            top: 0,
            zIndex: 10,
            '& th': {
              backgroundColor: '#f9fafb !important',
              height: '48px',
              padding: '12px 16px',
            }
          }
        }
      }}>
        <Datagrid
          rowClick={(id, resource, record) => {
            navigate('/email_history/create', {
              state: { ...record, fromDrafts: true }
            })
            return false
          }}
          bulkActionButtons={<EmailBulkActionButtons />}
          sx={{
            '& .RaDatagrid-headerCell': { 
              fontWeight: 600, 
              backgroundColor: '#f9fafb'
            },
            '& .RaDatagrid-row': { 
              '&:hover': { backgroundColor: '#f3f4f6' } 
            },
            // 🔥 操作列居中对齐
            '& .column-actions': {
              textAlign: 'center !important',
              '& .RaDatagrid-headerCell': {
                textAlign: 'center !important'
              }
            }
          }}
        >
          <FunctionField label="收件人" render={(record:any) => (
            <Box>{record.to_email || '(未填写)'}</Box>
          )} />
          <FunctionField label="主题" render={(record:any) => (
            <Box>{record.subject || '(无主题)'}</Box>
          )} />
          <FunctionField label="创建时间" render={(record:any) => (
            <Box>{record.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-'}</Box>
          )} />
          <FunctionField 
            label="操作" 
            render={() => <SimpleQuickActionsField />} 
            headerClassName="column-actions" 
            cellClassName="column-actions" 
          />
        </Datagrid>
      </Box>
    </Box>
  )
}

export const EmailList = (props:any) => {
  // 🔥 支持筛选功能
  const permanentFilter = props.filter || {}
  
  return (
    <List 
      {...props}
      filter={permanentFilter}
      perPage={20} 
      filters={[
        // 🔥 定义筛选字段，但不显示在UI上（我们使用自定义按钮）
        <TextInput source="business_stage" alwaysOn style={{ display: 'none' }} />,
      ]}
      actions={false} 
      title={false}
      sort={{ field: 'sent_at', order: 'DESC' }}
      disableSyncWithLocation={false}
      storeKey={false}
      pagination={false}
    >
      <EmailListWithFixedHeader />
    </List>
  )
}

export const EmailCreate = (props:any) => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotify()
  const [showOriginal, setShowOriginal] = useState(true)
  const [attachments, setAttachments] = useState<File[]>([])
  const [emailHistory, setEmailHistory] = useState<any[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [currentEmail, setCurrentEmail] = useState<string>('')
  const [selectedTab, setSelectedTab] = useState(0)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedEmail, setSelectedEmail] = useState<any>(null)
  const [quickReplies, setQuickReplies] = useState<any[]>([])
  const [signatures, setSignatures] = useState<any[]>([])
  const [selectedSignatureId, setSelectedSignatureId] = useState<number | null>(null)
  const [showCreateSignature, setShowCreateSignature] = useState(false)
  const [newSignature, setNewSignature] = useState({ name: '', content: '' })
  const signatureEditorRef = useRef<HTMLDivElement>(null)
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([])
  const [aiAnalysis, setAiAnalysis] = useState<any>(null)
  const [loadingAI, setLoadingAI] = useState(false)
  // 🔥 新增：知识库相关状态
  const [useKnowledgeBase, setUseKnowledgeBase] = useState(true)  // 默认开启知识库
  const [knowledgeUsed, setKnowledgeUsed] = useState<any[]>([])  // 使用的知识片段
  const [generatingReply, setGeneratingReply] = useState(false)  // 生成回复中
  const [lastGeneratedReply, setLastGeneratedReply] = useState('')  // 🔥 保存上次生成的回复
  const [generatingStep, setGeneratingStep] = useState('')  // 🔥 当前生成步骤
  const [replyTone, setReplyTone] = useState('professional')  // 🔥 回复语气
  const [selectedModel, setSelectedModel] = useState('gpt-4o-mini')  // 🔥 选择的AI模型
  const [selectedPromptTemplate, setSelectedPromptTemplate] = useState<number | null>(null)  // 🔥 选择的提示词模板
  const [promptTemplates, setPromptTemplates] = useState<any[]>([])  // 🔥 提示词模板列表
  const [fromDrafts, setFromDrafts] = useState(false)  // 🔥 记录是否从草稿箱进入
  const [originalEmailTranslated, setOriginalEmailTranslated] = useState('')  // 🔥 原邮件翻译内容
  const [showOriginalTranslation, setShowOriginalTranslation] = useState(false)  // 🔥 显示原邮件翻译
  const [translatingOriginal, setTranslatingOriginal] = useState(false)  // 🔥 翻译中状态
  const editorRef = useRef<HTMLDivElement>(null)
  const isInitializedRef = useRef(false)
  const [emailOptions, setEmailOptions] = useState({
    signature: '不使用',
    isUrgent: false,
    needReceipt: false,
    trackEmail: true,
    scheduledSend: false,
    markPending: false,
    addNote: false,
    priority: 'normal' as 'high' | 'normal' | 'low'
  })
  const [signatureDialogOpen, setSignatureDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    from_email: '',
    from_name: '',
    to_email: '',
    cc_email: '',
    bcc_email: '',
    subject: '',
    body: ''
  })
  const [emailAccounts, setEmailAccounts] = useState<any[]>([])
  const [showCc, setShowCc] = useState(false)
  const [showBcc, setShowBcc] = useState(false)
  const [emailSuggestions, setEmailSuggestions] = useState<any[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [sending, setSending] = useState(false)  // 🔥 发送中状态
  // 🔥 已移除 autoSaveTimer 状态（不再需要自动保存）
  
  // 组件挂载后立即初始化编辑器
  useEffect(() => {
    if (editorRef.current && !isInitializedRef.current) {
      const editor = editorRef.current;
      // 设置文本方向
      editor.setAttribute('dir', 'ltr');
      editor.style.direction = 'ltr';
      editor.style.textAlign = 'left';
      
      // 如果有初始内容（回复/转发），则设置内容
      if (formData.body) {
        editor.innerHTML = formData.body;
      } else {
        // 没有初始内容，创建空行
        editor.innerHTML = '';
        const initialDiv = document.createElement('div');
        initialDiv.setAttribute('dir', 'ltr');
        initialDiv.style.direction = 'ltr';
        initialDiv.innerHTML = '<br>';
        editor.appendChild(initialDiv);
      }
      
      // 设置光标到末尾
      setTimeout(() => {
        const range = document.createRange();
        const sel = window.getSelection();
        range.selectNodeContents(editor);
        range.collapse(false);
        sel?.removeAllRanges();
        sel?.addRange(range);
      }, 0);
      
      isInitializedRef.current = true;
    }
  }, [])
  
  // 单独处理formData.body的变化（应用AI建议或快捷回复）
  useEffect(() => {
    if (editorRef.current && isInitializedRef.current && formData.body !== editorRef.current.innerHTML) {
      const editor = editorRef.current;
      // 保存当前光标位置
      const sel = window.getSelection();
      const currentRange = sel && sel.rangeCount > 0 ? sel.getRangeAt(0) : null;
      
      // 更新内容
      editor.innerHTML = formData.body;
      
      // 尝试恢复光标位置，如果失败则移到末尾
      try {
        if (currentRange && editor.contains(currentRange.startContainer)) {
          sel?.removeAllRanges();
          sel?.addRange(currentRange);
        } else {
          throw new Error('Range invalid');
        }
      } catch {
        // 光标位置无效，移到末尾
        const range = document.createRange();
        range.selectNodeContents(editor);
        range.collapse(false);
        sel?.removeAllRanges();
        sel?.addRange(range);
      }
    }
  }, [formData.body])
  
  useEffect(() => {
    // 🔥 检查是否从草稿箱进入：通过 location.state 传递的标记
    if (location.state?.fromDrafts) {
      setFromDrafts(true)
    }
    
    if (location.state) {
      const emailAddress = location.state.from_email || location.state.to_email || ''
      setCurrentEmail(emailAddress)
      
      // 🔥 如果是草稿，加载完整的草稿数据
      if (location.state.status === 'draft') {
        setFormData({
          from_email: location.state.from_email || '',
          from_name: location.state.from_name || '',
          to_email: location.state.to_email || '',
          cc_email: location.state.cc_email || '',
          bcc_email: location.state.bcc_email || '',
          subject: location.state.subject || '',
          body: location.state.html_body || location.state.body || ''
        })
        // 显示CC和BCC如果有值
        if (location.state.cc_email) setShowCc(true)
        if (location.state.bcc_email) setShowBcc(true)
      } else {
        // 普通邮件回复/转发
        setFormData({
          from_email: '',
          from_name: '',
          to_email: location.state.to_email || '',
          cc_email: '',
          bcc_email: '',
          subject: location.state.subject || '',
          body: location.state.body || ''
        })
      }
      
      // 加载客户邮件历史
      if (location.state.customer_id) {
        loadEmailHistoryByCustomerId(location.state.customer_id)
      } else if (emailAddress) {
        loadEmailHistoryByEmail(emailAddress)
      }
      
      // 如果是回复邮件，加载AI分析
      if (location.state.originalBody) {
        loadAISuggestions({
          subject: location.state.subject?.replace(/^(Re: |Fwd: )/, '') || '',
          body: location.state.originalBody
        })
      }
    }
    
    // 加载快捷回复模板
    loadQuickReplies()
    // 加载签名列表
    loadSignatures()
    // 加载邮箱账户
    loadEmailAccounts()
    // 🔥 加载提示词模板
    loadPromptTemplates()
  }, [location.state])
  
  const handleSend = async () => {
    // 🔥 防止重复发送
    if (sending) {
      return
    }
    
    // P0: 发送前验证
    if (!formData.to_email) {
      notify('请输入收件人', { type: 'warning' })
      return
    }
    if (!formData.subject) {
      notify('请输入主题', { type: 'warning' })
      return
    }
    if (!formData.from_email) {
      notify('请选择发件人账户', { type: 'warning' })
      return
    }
    
    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const toEmails = formData.to_email.split(/[,;；，]/).map(e => e.trim()).filter(Boolean)
    const invalidEmails = toEmails.filter(email => !emailRegex.test(email))
    if (invalidEmails.length > 0) {
      notify(`无效的邮箱地址: ${invalidEmails.join(', ')}`, { type: 'error' })
      return
    }
    
    // 检查附件总大小 (P1)
    const totalSize = attachments.reduce((sum, file) => sum + file.size, 0)
    const maxSize = 25 * 1024 * 1024 // 25MB
    if (totalSize > maxSize) {
      notify(`附件总大小超过 25MB，请减少附件或使用网盘分享`, { type: 'error' })
      return
    }
    
    // 检查是否提到附件但未添加
    if ((formData.body.includes('附件') || formData.body.includes('attach')) && attachments.length === 0) {
      if (!window.confirm('您在邮件中提到了附件，但没有添加任何附件。是否继续发送？')) {
        return
      }
    }
    
    // 群发提醒
    if (toEmails.length > 50) {
      if (!window.confirm(`您即将群发邮件给 ${toEmails.length} 个收件人，建议使用“群发单显”功能。是否继续？`)) {
        return
      }
    }
    
    try {
      setSending(true)  // 🔥 设置发送中状态
      console.log('🚀 开始发送邮件...')
      console.log('发件人:', formData.from_email)
      console.log('收件人:', formData.to_email)
      console.log('主题:', formData.subject)
      
      const token = localStorage.getItem('token')
      const apiUrl = 'http://127.0.0.1:8001/api/email_history'
      
      console.log('API地址:', apiUrl)
      
      const requestBody = {
        direction: 'outbound',
        subject: formData.subject,
        body: formData.body,
        html_body: formData.body,
        from_email: formData.from_email,
        to_email: formData.to_email,
        cc_email: formData.cc_email || null,
        bcc_email: formData.bcc_email || null,
        customer_id: location.state?.customer_id,
        need_receipt: emailOptions.needReceipt,
        priority: emailOptions.priority
      }
      
      console.log('请求体:', JSON.stringify(requestBody, null, 2))
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody)
      })
      
      console.log('响应状态:', response.status, response.statusText)
      
      if (response.ok) {
        notify('邮件发送成功！', { type: 'success' })
        
        // 🔥 如果是回复邮件，更新原邮件的replied状态
        if (location.state?.originalEmailId) {
          try {
            await fetch(`http://127.0.0.1:8001/api/email_history/${location.state.originalEmailId}`, {
              method: 'PATCH',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({ replied: true })
            })
            console.log('✅ 已更新原邮件replied状态')
          } catch (error) {
            console.error('⚠️ 更新replied状态失败:', error)
          }
        }
        
        // 🔥 根据来源跳转到不同的页面
        if (location.state?.originalEmailId) {
          // 如果是回复邮件，返回上一页（保持筛选状态）
          navigate(-1)
        } else {
          // 其他情况跳转到所有邮件
          navigate('/email_history')
        }
      } else {
        // 获取详细错误信息
        const errorData = await response.json().catch(() => ({ detail: '服务器返回错误但无法解析响应' }))
        console.error('服务器错误:', errorData)
        
        // 显示详细错误信息
        const errorMsg = errorData.detail || `服务器错误 (${response.status})`
        notify(errorMsg, { type: 'error' })
      }
    } catch (error: any) {
      console.error('❌ 发送邮件异常:', error)
      
      // 提供更详细的错误信息
      let errorMessage = '发送失败'
      
      if (error.message === 'Failed to fetch') {
        errorMessage = '❌ 无法连接到后端服务！\n\n可能原因：\n1. 后端服务未启动（请运行: python main.py）\n2. 后端地址错误（当前: http://127.0.0.1:8001）\n3. 防火墙阻止连接\n\n请检查后端服务是否正常运行。'
      } else if (error.name === 'TypeError') {
        errorMessage = `网络错误: ${error.message}`
      } else {
        errorMessage = error.message || '未知错误'
      }
      
      notify(errorMessage, { type: 'error' })
    } finally {
      setSending(false)  // 🔥 恢复按钮状态
    }
  }
  
  const handleSaveDraft = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        notify('请先登录', { type: 'warning' })
        return
      }
      
      // 获取编辑器内容
      const bodyContent = editorRef.current?.innerText?.trim() || ''
      const htmlContent = editorRef.current?.innerHTML || ''
      
      // 🔥 核心限制：如果文本框内没有内容，不保存草稿
      if (!formData.to_email?.trim() && !formData.subject?.trim() && !bodyContent) {
        notify('⚠️ 请至少填写收件人、主题或正文内容', { type: 'warning' })
        return
      }
      
      const apiUrl = 'http://127.0.0.1:8001/api/email_history'
      
      const requestBody = {
        from_email: formData.from_email,
        from_name: formData.from_name,
        to_email: formData.to_email || '',
        cc_email: formData.cc_email || null,
        bcc_email: formData.bcc_email || null,
        subject: formData.subject || '(无主题)',
        body: bodyContent,
        html_body: htmlContent,
        direction: 'outbound',
        status: 'draft',  // 关键：设置为草稿状态
        customer_id: null,
        ai_generated: false,
        attachments: attachments.length > 0 ? JSON.stringify(attachments.map(f => f.name)) : null,
        priority: emailOptions.priority
      }
      
      console.log('💾 保存草稿:', requestBody)
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody)
      })
      
      if (response.ok) {
        const savedDraft = await response.json()
        notify(`✅ 草稿已保存（ID: ${savedDraft.id}）`, { type: 'success' })
        
        // 可选：跳转到草稿列表
        // navigate('/email_history?filter={"status":"draft"}')
      } else {
        const errorData = await response.json().catch(() => ({ detail: '保存失败' }))
        notify(errorData.detail || '保存草稿失败', { type: 'error' })
      }
    } catch (error: any) {
      console.error('❌ 保存草稿异常:', error)
      notify('保存草稿失败', { type: 'error' })
    }
  }
  
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments([...attachments, ...Array.from(e.target.files)])
    }
  }
  
  const removeAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index))
  }
  
  const loadEmailHistoryByCustomerId = async (customerId: number) => {
    try {
      setLoadingHistory(true)
      const token = localStorage.getItem('token')
      const filterParams = JSON.stringify({ customer_id: customerId })
      const sortParams = JSON.stringify(["sent_at", "DESC"])
      const url = `http://127.0.0.1:8001/api/email_history?filter=${encodeURIComponent(filterParams)}&sort=${encodeURIComponent(sortParams)}`
      
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setEmailHistory(data || [])
      }
    } catch (error) {
      console.error('Failed to load email history:', error)
    } finally {
      setLoadingHistory(false)
    }
  }
  
  const loadEmailHistoryByEmail = async (emailAddress: string) => {
    try {
      setLoadingHistory(true)
      const token = localStorage.getItem('token')
      const sortParams = JSON.stringify(["sent_at", "DESC"])
      const url = `http://127.0.0.1:8001/api/email_history?range=[0,99]&sort=${encodeURIComponent(sortParams)}`
      
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        const filtered = data.filter((email: any) => 
          email.from_email === emailAddress || email.to_email === emailAddress
        )
        setEmailHistory(filtered || [])
      }
    } catch (error) {
      console.error('Failed to load email history:', error)
    } finally {
      setLoadingHistory(false)
    }
  }
  
  const loadQuickReplies = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/quick-replies', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setQuickReplies(data)
      }
    } catch (error) {
      console.error('Failed to load quick replies:', error)
    }
  }
  
  const loadSignatures = async () => {
    try {
      const token = localStorage.getItem('token')
      console.log('🔑 加载签名列表...')
      const response = await fetch('http://127.0.0.1:8001/api/signatures', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      console.log('签名 API 响应:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ 签名数据加载成功:', data)
        setSignatures(data)
        
        // 自动选择默认签名
        const defaultSig = data.find((s: any) => s.is_default)
        if (defaultSig) {
          console.log('✅ 找到默认签名:', defaultSig.name)
          setSelectedSignatureId(defaultSig.id)
          setEmailOptions({ ...emailOptions, signature: defaultSig.name })
        } else if (data.length > 0) {
          // 如果没有默认签名，选择第一个
          console.log('✅ 使用第一个签名:', data[0].name)
          setSelectedSignatureId(data[0].id)
          setEmailOptions({ ...emailOptions, signature: data[0].name })
        } else {
          console.log('⚠️ 没有签名数据')
        }
      } else {
        const errorText = await response.text()
        console.error('❌ 签名 API 错误:', response.status, errorText)
      }
    } catch (error) {
      console.error('❌ Failed to load signatures:', error)
    }
  }
  
  // 加载邮箱账户列表
  const loadEmailAccounts = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/email_accounts', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setEmailAccounts(data)
        
        // 自动选择默认发件账户
        const defaultAccount = data.find((acc: any) => acc.is_default)
        if (defaultAccount) {
          setFormData(prev => ({
            ...prev,
            from_email: defaultAccount.email_address,
            from_name: defaultAccount.account_name
          }))
        } else if (data.length > 0) {
          setFormData(prev => ({
            ...prev,
            from_email: data[0].email_address,
            from_name: data[0].account_name
          }))
        }
      }
    } catch (error) {
      console.error('Failed to load email accounts:', error)
    }
  }
  
  // 🔥 翻译原邮件
  const translateOriginalEmail = async () => {
    if (!location.state?.originalBody) {
      notify('没有原邮件内容', { type: 'warning' })
      return
    }
    
    if (originalEmailTranslated) {
      setShowOriginalTranslation(!showOriginalTranslation)
      return
    }
    
    setTranslatingOriginal(true)
    try {
      const token = localStorage.getItem('token')
      const content = location.state.originalBody
      
      const response = await fetch('http://127.0.0.1:8001/api/ai/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          content: content,
          target_lang: 'zh'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setOriginalEmailTranslated(data.translated)
        setShowOriginalTranslation(true)
        notify('翻译完成', { type: 'success' })
      } else {
        notify('翻译失败', { type: 'error' })
      }
    } catch (error) {
      console.error('翻译异常:', error)
      notify('翻译失败', { type: 'error' })
    } finally {
      setTranslatingOriginal(false)
    }
  }
  
  // 🔥 加载提示词模板列表
  const loadPromptTemplates = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/prompt-templates?template_type=reply&is_active=true', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setPromptTemplates(data)
        
        // 自动选择默认模板
        const defaultTemplate = data.find((t: any) => t.is_default)
        if (defaultTemplate) {
          setSelectedPromptTemplate(defaultTemplate.id)
          // 如果模板有推荐模型，使用推荐模型
          if (defaultTemplate.recommended_model) {
            setSelectedModel(defaultTemplate.recommended_model)
          }
        }
      }
    } catch (error) {
      console.error('Failed to load prompt templates:', error)
    }
  }
  
  // 搜索邮箱建议
  const searchEmailSuggestions = async (query: string) => {
    if (!query || query.length < 2) {
      setEmailSuggestions([])
      setShowSuggestions(false)
      return
    }
    
    try {
      const token = localStorage.getItem('token')
      // 从客户表和邮件历史中搜索
      const [customersRes, emailsRes] = await Promise.all([
        fetch(`http://127.0.0.1:8001/api/customers?filter=${encodeURIComponent(JSON.stringify({ email: query }))}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`http://127.0.0.1:8001/api/email_history?range=[0,10]`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ])
      
      const suggestions: any[] = []
      
      if (customersRes.ok) {
        const customers = await customersRes.json()
        customers.forEach((c: any) => {
          if (c.email && c.email.toLowerCase().includes(query.toLowerCase())) {
            suggestions.push({
              email: c.email,
              name: c.contact_name || c.company_name,
              type: 'customer'
            })
          }
        })
      }
      
      if (emailsRes.ok) {
        const emails = await emailsRes.json()
        const uniqueEmails = new Set<string>()
        emails.forEach((e: any) => {
          if (e.from_email && e.from_email.toLowerCase().includes(query.toLowerCase())) {
            if (!uniqueEmails.has(e.from_email)) {
              uniqueEmails.add(e.from_email)
              suggestions.push({
                email: e.from_email,
                name: '',
                type: 'recent'
              })
            }
          }
          if (e.to_email && e.to_email.toLowerCase().includes(query.toLowerCase())) {
            if (!uniqueEmails.has(e.to_email)) {
              uniqueEmails.add(e.to_email)
              suggestions.push({
                email: e.to_email,
                name: '',
                type: 'recent'
              })
            }
          }
        })
      }
      
      setEmailSuggestions(suggestions.slice(0, 5))
      setShowSuggestions(suggestions.length > 0)
    } catch (error) {
      console.error('Failed to search email suggestions:', error)
    }
  }
  
  // 🔥 已移除自动保存草稿功能
  // useEffect 中的自动保存逻辑已删除
  
  const createSignature = async () => {
    if (!newSignature.name.trim()) {
      notify('请输入签名名称', { type: 'warning' })
      return
    }
    
    console.log('Creating signature:', newSignature)
    
    try {
      const token = localStorage.getItem('token')
      console.log('Token:', token ? 'exists' : 'missing')
      
      const requestBody = {
        name: newSignature.name,
        content: newSignature.content || '',
        is_default: false
      }
      console.log('Request body:', requestBody)
      
      const response = await fetch('http://127.0.0.1:8001/api/signatures', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      })
      
      console.log('Response status:', response.status)
      const responseText = await response.text()
      console.log('Response text:', responseText)
      
      if (response.ok) {
        notify('签名创建成功', { type: 'success' })
        setNewSignature({ name: '', content: '' })
        setShowCreateSignature(false)
        loadSignatures() // 重新加载签名列表
      } else {
        let errorData
        try {
          errorData = JSON.parse(responseText)
        } catch {
          errorData = { detail: responseText || '未知错误' }
        }
        console.error('Create signature error:', errorData)
        notify(`创建失败: ${errorData.detail || response.statusText}`, { type: 'error' })
      }
    } catch (error) {
      console.error('Failed to create signature:', error)
      notify(`创建失败: ${error}`, { type: 'error' })
    }
  }
  
  // 插入图片到签名编辑器
  const insertImageToSignature = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = (e: any) => {
      const file = e.target.files[0]
      if (!file) return
      
      // 检查文件大小（500KB）
      if (file.size > 500 * 1024) {
        notify('图片大小不能超过500KB', { type: 'warning' })
        return
      }
      
      // 读取文件为Base64
      const reader = new FileReader()
      reader.onload = (event: any) => {
        const img = document.createElement('img')
        img.src = event.target.result
        img.style.maxWidth = '100%'
        img.style.height = 'auto'
        
        // 插入图片到编辑器
        if (signatureEditorRef.current) {
          signatureEditorRef.current.focus()
          const selection = window.getSelection()
          if (selection && selection.rangeCount > 0) {
            const range = selection.getRangeAt(0)
            range.deleteContents()
            range.insertNode(img)
            range.collapse(false)
          } else {
            signatureEditorRef.current.appendChild(img)
          }
          
          // 更新签名内容
          setNewSignature({ ...newSignature, content: signatureEditorRef.current.innerHTML })
        }
      }
      reader.readAsDataURL(file)
    }
    input.click()
  }
  
  // 富文本编辑器命令
  const execSignatureCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value)
    if (signatureEditorRef.current) {
      setNewSignature({ ...newSignature, content: signatureEditorRef.current.innerHTML })
    }
  }
  
  // 插入链接
  const insertLink = () => {
    const url = prompt('请输入链接地址:', 'https://')
    if (url) {
      execSignatureCommand('createLink', url)
    }
  }
  
  // 改变字体
  const changeFontFamily = (font: string) => {
    execSignatureCommand('fontName', font)
  }
  
  // 改变字号
  const changeFontSize = (size: string) => {
    // execCommand的fontSize使用1-7，我们需要转换
    const sizeMap: { [key: string]: string } = {
      '12px': '2',
      '14px': '3',
      '16px': '4',
      '18px': '5',
      '20px': '6',
      '24px': '7'
    }
    execSignatureCommand('fontSize', sizeMap[size] || '3')
  }
  
  const loadAISuggestions = async (emailContent: { subject: string, body: string }) => {
    try {
      setLoadingAI(true)
      const token = localStorage.getItem('token')
      
      const analysisResponse = await fetch('http://127.0.0.1:8001/api/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(emailContent)
      })
      
      if (analysisResponse.ok) {
        const analysis = await analysisResponse.json()
        setAiAnalysis(analysis)
      }
      
      const suggestionsResponse = await fetch('http://127.0.0.1:8001/api/ai/suggest-replies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(emailContent)
      })
      
      if (suggestionsResponse.ok) {
        const suggestions = await suggestionsResponse.json()
        setAiSuggestions(suggestions)
      }
    } catch (error) {
      console.error('Failed to load AI suggestions:', error)
    } finally {
      setLoadingAI(false)
    }
  }
  
  // 🔥 新增：生成AI回复（支持知识库）
  const generateAIReply = async () => {
    if (!location.state?.originalBody) {
      notify('没有原始邮件内容', { type: 'warning' })
      return
    }
    
    try {
      setGeneratingReply(true)
      setGeneratingStep('🔍 检索知识库...')  // 🔥 步骤1
      
      const token = localStorage.getItem('token')
      
      // 模拟检索延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      setGeneratingStep('🤖 AI生成中...')  // 🔥 步骤2
      
      const response = await fetch('http://127.0.0.1:8001/api/ai/generate-reply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          subject: location.state.subject?.replace(/^(Re: |Fwd: )/, '') || '',
          body: location.state.originalBody,
          use_knowledge_base: useKnowledgeBase,
          tone: replyTone,  // 🔥 传递语气参数
          model: selectedModel,  // 🔥 传递模型参数
          prompt_template_id: selectedPromptTemplate  // 🔥 传递提示词模板 ID
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        
        if (result.success) {
          setGeneratingStep('✅ 应用回复...')  // 🔥 步骤3
          
          // 🔥 保存生成的回复
          setLastGeneratedReply(result.reply)
          
          // 应用AI生成的回复
          if (editorRef.current) {
            editorRef.current.innerHTML = result.reply
            setFormData({ ...formData, body: result.reply })
          }
          
          // 保存使用的知识库信息
          if (result.knowledge_used && result.knowledge_context) {
            setKnowledgeUsed(result.knowledge_context)
          }
          
          notify(`✅ AI回复已生成${result.knowledge_used ? '（已引用知识库）' : ''}`, { type: 'success' })
        } else {
          // 🔥 优化错误提示
          const errorMsg = result.error || '未知错误'
          notify(`❌ 生成失败: ${errorMsg}`, { type: 'error' })
          console.error('生成失败详情:', result)
        }
      } else {
        // 🔥 根据状态码给出不同提示
        let errorMsg = '生成回复失败'
        if (response.status === 401) {
          errorMsg = '身份验证失效，请重新登录'
        } else if (response.status === 429) {
          errorMsg = 'AI请求过于频繁，请稍后再试'
        } else if (response.status >= 500) {
          errorMsg = '服务器错误，请稍后重试'
        }
        notify(`❌ ${errorMsg}`, { type: 'error' })
        console.error('请求失败，状态码:', response.status)
      }
    } catch (error: any) {
      console.error('Failed to generate AI reply:', error)
      // 🔥 优化网络错误提示
      let errorMsg = '生成回复失败'
      if (error.message?.includes('Failed to fetch')) {
        errorMsg = '网络连接失败，请检查网络或后端服务'
      } else if (error.message?.includes('timeout')) {
        errorMsg = '请求超时，请稍后重试'
      }
      notify(`❌ ${errorMsg}`, { type: 'error' })
    } finally {
      setGeneratingReply(false)
      setGeneratingStep('')  // 🔥 清空步骤
    }
  }
  
  const useAISuggestion = (suggestion: any) => {
    setFormData({
      ...formData,
      body: suggestion.content
    })
    notify('已应用AI建议', { type: 'success' })
  }
  
  const useQuickReply = async (template: any) => {
    let content = template.body
    content = content.replace('{contact_name}', 'Customer')
    content = content.replace('{sender_name}', 'Your Name')
    
    setFormData({
      ...formData,
      subject: template.subject,
      body: content
    })
    
    try {
      const token = localStorage.getItem('token')
      await fetch(`http://127.0.0.1:8001/api/quick-replies/${template.id}/use`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })
    } catch (error) {
      console.error('Failed to update template usage:', error)
    }
    
    notify('已应用模板', { type: 'success' })
  }
  
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

  return (
    <Box sx={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column', bgcolor: '#fafafa' }}>
      {/* 主体内容区 - 左右分栏 */}
      <Box sx={{ flex: 1, overflow: 'hidden', display: 'grid', gridTemplateColumns: '1fr 400px', gap: 0 }}>
        {/* 左侧 - 邮件编辑区 */}
        <Box sx={{ overflow: 'hidden', bgcolor: '#fff', display: 'flex', flexDirection: 'column' }}>
          {/* 顶部操作按钮栏 - 仅在左侧编辑区 */}
          <Box sx={{ p: 2, display: 'flex', gap: 1.5, alignItems: 'center' }}>
            <Button 
              variant="contained" 
              startIcon={sending ? <CircularProgress size={16} sx={{ color: 'white' }} /> : <SendIcon />} 
              onClick={handleSend} 
              disabled={sending}
              sx={{ 
                bgcolor: '#1677ff', 
                '&:hover': { bgcolor: '#4096ff' }, 
                '&.Mui-disabled': { bgcolor: '#b3d9ff', color: 'white' },
                borderRadius: '6px', 
                textTransform: 'none', 
                px: 3 
              }}
            >
              {sending ? '发送中...' : '发送'}
            </Button>
            <Button variant="outlined" onClick={handleSaveDraft} sx={{ borderColor: '#d9d9d9', color: '#000000d9', '&:hover': { borderColor: '#40a9ff', color: '#40a9ff' }, borderRadius: '6px', textTransform: 'none' }}>
              存草稿
            </Button>
            <Button variant="outlined" sx={{ borderColor: '#d9d9d9', color: '#000000d9', '&:hover': { borderColor: '#40a9ff', color: '#40a9ff' }, borderRadius: '6px', textTransform: 'none' }}>
              预览
            </Button>
            <Button variant="outlined" onClick={() => {
              // 🔥 根据来源跳转到不同的页面
              if (fromDrafts) {
                navigate('/email_history?filter={"status":"draft"}')
              } else {
                navigate('/email_history')
              }
            }} sx={{ borderColor: '#d9d9d9', color: '#000000d9', '&:hover': { borderColor: '#ff4d4f', color: '#ff4d4f' }, borderRadius: '6px', textTransform: 'none' }}>
              取消
            </Button>
          </Box>
          
          {/* 可滚动内容区域 */}
          <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 2, pb: 0, flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* 发件人 - P0: 下拉选择器 */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5, pb: 0.5, borderBottom: '1px solid #f0f0f0' }}>
          <Box sx={{ width: 60, fontSize: '13px', color: '#000000d9', fontWeight: 500 }}>发件人</Box>
          <Box sx={{ flex: 1 }}>
            <Select
              fullWidth
              value={formData.from_email}
              onChange={(e) => {
                const selected = emailAccounts.find(acc => acc.email_address === e.target.value)
                setFormData({ 
                  ...formData, 
                  from_email: e.target.value,
                  from_name: selected?.account_name || ''
                })
              }}
              variant="standard"
              disableUnderline
              sx={{ fontSize: '13px' }}
              displayEmpty
            >
              {emailAccounts.length === 0 && (
                <MenuItem value="" disabled>没有可用的发件账户</MenuItem>
              )}
              {emailAccounts.map((account: any) => (
                <MenuItem key={account.id} value={account.email_address}>
                  {account.account_name} &lt;{account.email_address}&gt;
                  {account.is_default && <Chip label="默认" size="small" sx={{ ml: 1, height: 18 }} />}
                </MenuItem>
              ))}
            </Select>
          </Box>
        </Box>
        
        {/* 收件人 - P0: 智能提示, P1: 验证 */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5, pb: 0.5, borderBottom: '1px solid #f0f0f0', position: 'relative' }}>
          <Box sx={{ width: 60, fontSize: '13px', color: '#000000d9', fontWeight: 500 }}>收件人</Box>
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ flex: 1, position: 'relative' }}>
              <MuiTextField 
                fullWidth 
                placeholder="请选择收件人或输入收件人邮箱（多个邮箱用逗号分隔）" 
                value={formData.to_email} 
                onChange={(e) => {
                  setFormData({ ...formData, to_email: e.target.value })
                  searchEmailSuggestions(e.target.value)
                }} 
                onFocus={() => formData.to_email && searchEmailSuggestions(formData.to_email)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                variant="standard" 
                InputProps={{ disableUnderline: true, sx: { fontSize: '13px' } }} 
              />
              {/* P1: 智能提示下拉框 */}
              {showSuggestions && emailSuggestions.length > 0 && (
                <Box sx={{ 
                  position: 'absolute', 
                  top: '100%', 
                  left: 0, 
                  right: 0, 
                  bgcolor: 'white', 
                  border: '1px solid #e0e0e0', 
                  borderRadius: 1, 
                  boxShadow: 2, 
                  zIndex: 1000,
                  maxHeight: 200,
                  overflowY: 'auto'
                }}>
                  {emailSuggestions.map((suggestion, index) => (
                    <Box
                      key={index}
                      onClick={() => {
                        setFormData({ ...formData, to_email: suggestion.email })
                        setShowSuggestions(false)
                      }}
                      sx={{
                        p: 1,
                        cursor: 'pointer',
                        '&:hover': { bgcolor: '#f5f5f5' },
                        borderBottom: index < emailSuggestions.length - 1 ? '1px solid #f0f0f0' : 'none'
                      }}
                    >
                      <Typography sx={{ fontSize: '13px', fontWeight: 500 }}>{suggestion.email}</Typography>
                      {suggestion.name && (
                        <Typography sx={{ fontSize: '11px', color: '#999' }}>{suggestion.name}</Typography>
                      )}
                      <Chip 
                        label={suggestion.type === 'customer' ? '客户' : '最近联系'} 
                        size="small" 
                        sx={{ height: 16, fontSize: '10px', mt: 0.5 }} 
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 1, whiteSpace: 'nowrap' }}>
              <Button 
                size="small" 
                onClick={() => setShowCc(!showCc)}
                sx={{ 
                  fontSize: '11px', 
                  color: showCc ? '#1677ff' : '#999', 
                  textTransform: 'none', 
                  minWidth: 'auto', 
                  p: 0,
                  fontWeight: showCc ? 600 : 400
                }}
              >
                抄送
              </Button>
              <Button 
                size="small" 
                onClick={() => setShowBcc(!showBcc)}
                sx={{ 
                  fontSize: '11px', 
                  color: showBcc ? '#1677ff' : '#999', 
                  textTransform: 'none', 
                  minWidth: 'auto', 
                  p: 0,
                  fontWeight: showBcc ? 600 : 400
                }}
              >
                密送
              </Button>
              <Button size="small" sx={{ fontSize: '11px', color: '#999', textTransform: 'none', minWidth: 'auto', p: 0 }}>群发单显</Button>
            </Box>
          </Box>
        </Box>
        
        {/* P0: 抄送 CC */}
        {showCc && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5, pb: 0.5, borderBottom: '1px solid #f0f0f0' }}>
            <Box sx={{ width: 60, fontSize: '13px', color: '#000000d9', fontWeight: 500 }}>抄送</Box>
            <Box sx={{ flex: 1 }}>
              <MuiTextField 
                fullWidth 
                placeholder="输入抄送邮箱（多个邮箱用逗号分隔）" 
                value={formData.cc_email} 
                onChange={(e) => setFormData({ ...formData, cc_email: e.target.value })} 
                variant="standard" 
                InputProps={{ disableUnderline: true, sx: { fontSize: '13px' } }} 
              />
            </Box>
          </Box>
        )}
        
        {/* P0: 密送 BCC */}
        {showBcc && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5, pb: 0.5, borderBottom: '1px solid #f0f0f0' }}>
            <Box sx={{ width: 60, fontSize: '13px', color: '#000000d9', fontWeight: 500 }}>密送</Box>
            <Box sx={{ flex: 1 }}>
              <MuiTextField 
                fullWidth 
                placeholder="输入密送邮箱（多个邮箱用逗号分隔）" 
                value={formData.bcc_email} 
                onChange={(e) => setFormData({ ...formData, bcc_email: e.target.value })} 
                variant="standard" 
                InputProps={{ disableUnderline: true, sx: { fontSize: '13px' } }} 
              />
            </Box>
          </Box>
        )}
        
        {/* 主题 */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, pb: 0.5, borderBottom: '1px solid #f0f0f0' }}>
          <Box sx={{ width: 60, fontSize: '13px', color: '#000000d9', fontWeight: 500 }}>主题</Box>
          <Box sx={{ flex: 1 }}>
            <MuiTextField fullWidth placeholder="请输入邮件主题" value={formData.subject} onChange={(e) => setFormData({ ...formData, subject: e.target.value })} variant="standard" InputProps={{ disableUnderline: true, sx: { fontSize: '13px' } }} />
          </Box>
        </Box>
        
        {/* 邮件编辑器区域 - 三层结构 */}
        <Box sx={{ mb: 1, border: '1px solid #e0e0e0', borderRadius: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
          {/* 第一层：富文本编辑器工具栏 */}
          <Box sx={{ 
            borderBottom: '1px solid #e0e0e0', 
            bgcolor: '#fafafa', 
            p: 1,
            display: 'flex',
            gap: 0.5,
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
            {/* 撤销/重做 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('undo')}>
              <UndoIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('redo')}>
              <RedoIcon sx={{ fontSize: 18 }} />
            </IconButton>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 字体选择 */}
            <Select
              size="small"
              defaultValue="系统字体"
              onChange={(e) => document.execCommand('fontName', false, e.target.value)}
              sx={{ 
                minWidth: 100, 
                height: 28,
                fontSize: '13px',
                '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
                bgcolor: '#fff'
              }}
            >
              <MenuItem value="系统字体">系统字体</MenuItem>
              <MenuItem value="SimSun">宋体</MenuItem>
              <MenuItem value="Microsoft YaHei">微软雅黑</MenuItem>
              <MenuItem value="Arial">Arial</MenuItem>
            </Select>
            
            {/* 字号选择 */}
            <Select
              size="small"
              defaultValue="3"
              onChange={(e) => document.execCommand('fontSize', false, e.target.value)}
              sx={{ 
                width: 80, 
                height: 28,
                fontSize: '13px',
                '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
                bgcolor: '#fff'
              }}
            >
              <MenuItem value="1">小</MenuItem>
              <MenuItem value="2">较小</MenuItem>
              <MenuItem value="3">正常</MenuItem>
              <MenuItem value="4">较大</MenuItem>
              <MenuItem value="5">大</MenuItem>
              <MenuItem value="6">特大</MenuItem>
            </Select>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 粗体/斜体/下划线 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('bold')}>
              <FormatBoldIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('italic')}>
              <FormatItalicIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('underline')}>
              <FormatUnderlinedIcon sx={{ fontSize: 18 }} />
            </IconButton>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 文本颜色/背景色 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => {
              const color = prompt('请输入颜色代码（例如：#ff0000）');
              if (color) document.execCommand('foreColor', false, color);
            }}>
              <FormatColorTextIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => {
              const color = prompt('请输入背景颜色代码（例如：#ffff00）');
              if (color) document.execCommand('backColor', false, color);
            }}>
              <FormatColorFillIcon sx={{ fontSize: 18 }} />
            </IconButton>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 对齐方式 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('justifyLeft')}>
              <FormatAlignLeftIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('justifyCenter')}>
              <FormatAlignCenterIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('justifyRight')}>
              <FormatAlignRightIcon sx={{ fontSize: 18 }} />
            </IconButton>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 列表 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('insertUnorderedList')}>
              <FormatListBulletedIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => document.execCommand('insertOrderedList')}>
              <FormatListNumberedIcon sx={{ fontSize: 18 }} />
            </IconButton>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 插入链接/图片 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => {
              const url = prompt('请输入链接地址：');
              if (url) document.execCommand('createLink', false, url);
            }}>
              <InsertLinkIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => {
              const url = prompt('请输入图片地址：');
              if (url) document.execCommand('insertImage', false, url);
            }}>
              <InsertPhotoIcon sx={{ fontSize: 18 }} />
            </IconButton>
            
            <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
            
            {/* 表情/表格 */}
            <IconButton size="small" sx={{ width: 28, height: 28 }}>
              <EmojiEmotionsIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => {
              const rows = prompt('请输入表格行数：', '3');
              const cols = prompt('请输入表格列数：', '3');
              if (rows && cols) {
                let table = '<table border="1" style="border-collapse: collapse; width: 100%;">';
                for (let i = 0; i < parseInt(rows); i++) {
                  table += '<tr>';
                  for (let j = 0; j < parseInt(cols); j++) {
                    table += '<td style="padding: 8px; border: 1px solid #ddd;">&nbsp;</td>';
                  }
                  table += '</tr>';
                }
                table += '</table>';
                document.execCommand('insertHTML', false, table);
              }
            }}>
              <TableChartIcon sx={{ fontSize: 18 }} />
            </IconButton>
            <IconButton size="small" sx={{ width: 28, height: 28 }} onClick={() => {
              const code = prompt('请输入代码：');
              if (code) document.execCommand('insertHTML', false, `<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;"><code>${code}</code></pre>`);
            }}>
              <CodeIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Box>
          
          {/* 第二层：邮件编写文本框 */}
          <Box 
            ref={editorRef}
            contentEditable
            suppressContentEditableWarning
            onInput={(e: any) => {
              setFormData({ ...formData, body: e.currentTarget.innerHTML });
            }}
            dir="ltr"
            sx={{ 
              bgcolor: '#fff',
              p: 2,
              flex: 1,
              minHeight: 0,
              overflowY: 'auto',
              fontSize: '14px',
              lineHeight: 1.8,
              outline: 'none',
              direction: 'ltr !important',
              textAlign: 'left !important',
              '&:empty:before': {
                content: '"输入邮件内容..."',
                color: '#999',
                fontStyle: 'italic'
              },
              '& *': {
                direction: 'ltr !important'
              },
              '& p, & div': { 
                margin: 0, 
                marginBottom: '0.5em',
                direction: 'ltr !important'
              },
              '& ul, & ol': { paddingLeft: '20px' },
              '& table': { borderCollapse: 'collapse', width: '100%' },
              '& td, & th': { border: '1px solid #ddd', padding: '8px' }
            }}
          />
          
          {/* 第三层：附件区域 */}
          <Box sx={{ 
            borderTop: '1px solid #e0e0e0', 
            bgcolor: '#fafafa', 
            px: 1.5,
            py: 0.5,
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            minHeight: 'auto'
          }}>
            <Button 
              component="label" 
              startIcon={<AttachFile sx={{ fontSize: 18 }} />} 
              sx={{ 
                fontSize: '13px', 
                color: '#666', 
                textTransform: 'none',
                '&:hover': { color: '#1677ff' }
              }}
            >
              附件
              <input type="file" hidden multiple onChange={handleFileSelect} />
            </Button>
            
            <Box sx={{ flex: 1 }} />
            
            {/* P1: 附件大小显示 */}
            <Box sx={{ fontSize: '12px', color: attachments.length > 0 ? '#333' : '#999' }}>
              附件大小: {(() => {
                const totalBytes = attachments.reduce((sum, file) => sum + file.size, 0)
                if (totalBytes === 0) return '0 B'
                if (totalBytes < 1024) return `${totalBytes} B`
                if (totalBytes < 1024 * 1024) return `${(totalBytes / 1024).toFixed(1)} KB`
                return `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`
              })()}
              {attachments.length > 0 && (
                <span style={{ color: attachments.reduce((sum, f) => sum + f.size, 0) > 25 * 1024 * 1024 ? '#ff4d4f' : '#52c41a' }}>
                  {' '}/ 25 MB
                </span>
              )}
            </Box>
          </Box>
        </Box>
        
        {/* 附件列表 - P1: 显示文件大小 */}
        {attachments.length > 0 && (
          <Box sx={{ mb: 1 }}>
            <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1, color: '#374151' }}>
              附件 ({attachments.length}) - 总大小: {(() => {
                const totalBytes = attachments.reduce((sum, file) => sum + file.size, 0)
                if (totalBytes < 1024) return `${totalBytes} B`
                if (totalBytes < 1024 * 1024) return `${(totalBytes / 1024).toFixed(1)} KB`
                return `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`
              })()}
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {attachments.map((file, index) => {
                const sizeStr = file.size < 1024 ? `${file.size} B` : 
                                file.size < 1024 * 1024 ? `${(file.size / 1024).toFixed(1)} KB` :
                                `${(file.size / (1024 * 1024)).toFixed(1)} MB`
                return (
                  <Chip 
                    key={index} 
                    label={`${file.name} (${sizeStr})`} 
                    onDelete={() => removeAttachment(index)} 
                    deleteIcon={<CloseIcon />} 
                    sx={{ maxWidth: 300 }} 
                  />
                )
              })}
            </Box>
          </Box>
        )}
        
        {/* 原邮件引用 */}
        {location.state?.subject && (
          <Paper variant="outlined" sx={{ mt: 1 }}>
            <Box sx={{ p: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: '#f9fafb' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ fontSize: '0.875rem', fontWeight: 600, color: '#6b7280', cursor: 'pointer' }} onClick={() => setShowOriginal(!showOriginal)}>
                  原邮件
                </Box>
                {/* 🔥 翻译按钮 */}
                <Button
                  size="small"
                  startIcon={translatingOriginal ? <CircularProgress size={14} /> : <TranslateIcon sx={{ fontSize: 16 }} />}
                  onClick={translateOriginalEmail}
                  disabled={translatingOriginal}
                  sx={{ 
                    fontSize: '12px',
                    textTransform: 'none',
                    color: showOriginalTranslation ? '#1677ff' : '#666',
                    minWidth: 'auto',
                    px: 1,
                    py: 0.5,
                    '&:hover': {
                      bgcolor: 'rgba(22, 119, 255, 0.08)'
                    }
                  }}
                >
                  {originalEmailTranslated ? (showOriginalTranslation ? '查看原文' : '查看翻译') : '翻译'}
                </Button>
              </Box>
              <MuiIconButton size="small" onClick={() => setShowOriginal(!showOriginal)}>
                {showOriginal ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </MuiIconButton>
            </Box>
            <Collapse in={showOriginal}>
              <Box sx={{ p: 2, borderTop: '1px solid #e5e7eb' }}>
                <Box sx={{ mb: 1, display: 'grid', gridTemplateColumns: '80px 1fr', gap: 1, fontSize: '0.813rem' }}>
                  <Box sx={{ color: '#6b7280' }}>发件人：</Box>
                  <Box>{location.state.from_email || location.state.to_email}</Box>
                  <Box sx={{ color: '#6b7280' }}>时间：</Box>
                  <Box>{new Date().toLocaleString()}</Box>
                  <Box sx={{ color: '#6b7280' }}>主题：</Box>
                  <Box>{location.state.subject?.replace(/^(Re: |Fwd: )/, '')}</Box>
                </Box>
                <Divider sx={{ my: 1.5 }} />
                <Box sx={{ fontSize: '0.813rem', color: '#374151' }}>
                  <HtmlContent content={showOriginalTranslation ? originalEmailTranslated : (location.state.originalBody || '')} maxHeight={300} />
                </Box>
              </Box>
            </Collapse>
          </Paper>
        )}
          </Box>
          </Box>
          
          {/* 邮件选项功能区 - 固定在底部 */}
          <Box sx={{ 
            p: 1.5, 
            bgcolor: '#fafafa', 
            borderTop: '1px solid #e0e0e0',
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            flexWrap: 'wrap'
          }}>
            {/* 签名按钮 */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ fontSize: '13px', color: '#666', whiteSpace: 'nowrap' }}>签名：</Box>
              <Button
                size="small"
                onClick={() => setSignatureDialogOpen(true)}
                sx={{ 
                  minWidth: 120,
                  height: 32,
                  fontSize: '13px',
                  bgcolor: '#fff',
                  color: '#333',
                  textTransform: 'none',
                  border: '1px solid #d0d0d0',
                  justifyContent: 'flex-start',
                  '&:hover': {
                    bgcolor: '#f5f5f5',
                    borderColor: '#1677ff'
                  }
                }}
              >
                {emailOptions.signature}
              </Button>
            </Box>
            
            {/* P1: 邮件优先级 */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ fontSize: '13px', color: '#666', whiteSpace: 'nowrap' }}>优先级：</Box>
              <Select
                size="small"
                value={emailOptions.priority}
                onChange={(e) => setEmailOptions({ ...emailOptions, priority: e.target.value as 'high' | 'normal' | 'low' })}
                sx={{ 
                  minWidth: 100,
                  height: 32,
                  fontSize: '13px',
                  bgcolor: '#fff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#d0d0d0' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#1677ff' }
                }}
              >
                <MenuItem value="high">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <FlagIcon sx={{ fontSize: 16, color: '#ff4d4f' }} />
                    高优先级
                  </Box>
                </MenuItem>
                <MenuItem value="normal">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <FlagIcon sx={{ fontSize: 16, color: '#999' }} />
                    普通
                  </Box>
                </MenuItem>
                <MenuItem value="low">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <FlagIcon sx={{ fontSize: 16, color: '#52c41a' }} />
                    低优先级
                  </Box>
                </MenuItem>
              </Select>
            </Box>
            
            {/* 紧急 */}
            <FormControlLabel
              control={
                <Checkbox 
                  size="small"
                  checked={emailOptions.isUrgent}
                  onChange={(e) => setEmailOptions({ ...emailOptions, isUrgent: e.target.checked })}
                  icon={<FlagIcon sx={{ fontSize: 18 }} />}
                  checkedIcon={<FlagIcon sx={{ fontSize: 18, color: '#ff4d4f' }} />}
                />
              }
              label={<Box sx={{ fontSize: '13px', color: '#666' }}>紧急</Box>}
              sx={{ m: 0 }}
            />
            
            {/* P1: 已读回执 */}
            <FormControlLabel
              control={
                <Checkbox 
                  size="small"
                  checked={emailOptions.needReceipt}
                  onChange={(e) => setEmailOptions({ ...emailOptions, needReceipt: e.target.checked })}
                />
              }
              label={<Box sx={{ fontSize: '13px', color: '#666' }}>已读回执</Box>}
              sx={{ m: 0 }}
            />
            
            {/* 追踪邮件 */}
            <FormControlLabel
              control={
                <Checkbox 
                  size="small"
                  checked={emailOptions.trackEmail}
                  onChange={(e) => setEmailOptions({ ...emailOptions, trackEmail: e.target.checked })}
                />
              }
              label={<Box sx={{ fontSize: '13px', color: '#666' }}>追踪邮件</Box>}
              sx={{ m: 0 }}
            />
            
            {/* 定时发送 */}
            <Button
              size="small"
              startIcon={<AccessTimeIcon sx={{ fontSize: 16 }} />}
              onClick={() => setEmailOptions({ ...emailOptions, scheduledSend: !emailOptions.scheduledSend })}
              sx={{ 
                fontSize: '13px',
                color: emailOptions.scheduledSend ? '#1677ff' : '#666',
                textTransform: 'none',
                borderColor: '#d0d0d0',
                '&:hover': {
                  borderColor: '#1677ff',
                  bgcolor: 'transparent'
                }
              }}
              variant="outlined"
            >
              定时发送
            </Button>
            
            {/* 标记为待处理 */}
            <Button
              size="small"
              startIcon={<BookmarkIcon sx={{ fontSize: 16 }} />}
              onClick={() => setEmailOptions({ ...emailOptions, markPending: !emailOptions.markPending })}
              sx={{ 
                fontSize: '13px',
                color: emailOptions.markPending ? '#1677ff' : '#666',
                textTransform: 'none',
                borderColor: '#d0d0d0',
                '&:hover': {
                  borderColor: '#1677ff',
                  bgcolor: 'transparent'
                }
              }}
              variant="outlined"
            >
              标记为待处理
            </Button>
            
            {/* 设置备注 */}
            <Button
              size="small"
              startIcon={<CommentIcon sx={{ fontSize: 16 }} />}
              onClick={() => setEmailOptions({ ...emailOptions, addNote: !emailOptions.addNote })}
              sx={{ 
                fontSize: '13px',
                color: emailOptions.addNote ? '#1677ff' : '#666',
                textTransform: 'none',
                borderColor: '#d0d0d0',
                '&:hover': {
                  borderColor: '#1677ff',
                  bgcolor: 'transparent'
                }
              }}
              variant="outlined"
            >
              设置备注
            </Button>
          </Box>
        </Box>
        
        {/* 右侧 - 往来邮件和AI助手 */}
        <Box sx={{ bgcolor: '#fafafa', overflow: 'auto', display: 'flex', flexDirection: 'column', borderLeft: '1px solid #e5e7eb' }}>
          {/* 标签页 */}
          <Box sx={{ borderBottom: '1px solid #e5e7eb', bgcolor: '#fff' }}>
            <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)} sx={{ minHeight: 48 }}>
              <Tab label="往来邮件" sx={{ minHeight: 48, fontSize: '0.813rem' }} />
              <Tab label="AI助手" icon={<PsychologyIcon sx={{ fontSize: 18 }} />} iconPosition="start" sx={{ minHeight: 48, fontSize: '0.813rem' }} />
              <Tab label="快捷回复" sx={{ minHeight: 48, fontSize: '0.813rem' }} />
            </Tabs>
          </Box>
          
          {/* 内容区域 */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
            {/* Tab 0: 往来邮件 */}
            {selectedTab === 0 && (
              <Box>
                {currentEmail && (
                  <Box sx={{ mb: 2, p: 1.5, bgcolor: '#f0f9ff', borderRadius: 1 }}>
                    <Box sx={{ fontSize: '0.75rem', color: '#6b7280', mb: 0.5 }}>当前客户</Box>
                    <Box sx={{ fontSize: '0.813rem', fontWeight: 500, color: '#374151' }}>{currentEmail}</Box>
                  </Box>
                )}
                
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#374151', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 4, height: 16, bgcolor: '#3b82f6', borderRadius: 1 }} />
                    往来邮件 ({emailHistory.length})
                  </Box>
                  
                  {loadingHistory ? (
                    <Box sx={{ textAlign: 'center', py: 4, color: '#9ca3af', fontSize: '0.813rem' }}>加载中...</Box>
                  ) : emailHistory.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4, color: '#9ca3af', fontSize: '0.813rem' }}>暂无历史邮件</Box>
                  ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {emailHistory.slice(0, 10).map((email: any) => (
                        <Paper key={email.id} variant="outlined" sx={{ p: 1.5, cursor: 'pointer', transition: 'all 0.2s', '&:hover': { bgcolor: '#f0f9ff', borderColor: '#3b82f6' } }} onClick={() => { setSelectedEmail(email); setDrawerOpen(true); }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Chip label={email.direction === 'outbound' ? '出站' : '入站'} size="small" sx={{ height: 18, fontSize: '0.65rem', bgcolor: email.direction === 'outbound' ? '#3b82f6' : '#10b981', color: '#fff' }} />
                            <Box sx={{ fontSize: '0.7rem', color: '#9ca3af' }}>{getRelativeTime(email.sent_at)}</Box>
                            {!email.opened && <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: '#3b82f6' }} />}
                          </Box>
                          <Box sx={{ fontSize: '0.813rem', fontWeight: email.opened ? 400 : 600, mb: 0.5, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{email.subject || '(无主题)'}</Box>
                          <Box sx={{ fontSize: '0.75rem', color: '#6b7280', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{email.body ? extractPlainText(email.body).substring(0, 60) : ''}</Box>
                        </Paper>
                      ))}
                    </Box>
                  )}
                </Box>
              </Box>
            )}
            
            {/* Tab 1: AI智能助手 */}
            {selectedTab === 1 && (
              <Box>
                {/* 🔥 知识库控制区 */}
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    mb: 2, 
                    bgcolor: '#f0f9ff', 
                    borderColor: '#93c5fd',  // 🔥 柔和的蓝色边框
                    borderWidth: '1.5px',  // 🔥 稍粗边框
                    boxShadow: '0 2px 8px rgba(59, 130, 246, 0.08)',  // 🔥 添加阴影
                    transition: 'box-shadow 0.2s ease',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(59, 130, 246, 0.12)'  // 🔥 hover加强阴影
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ 
                        width: 4, 
                        height: 18,  // 🔥 增加高度
                        bgcolor: '#3b82f6', 
                        borderRadius: 1,
                        boxShadow: '0 2px 4px rgba(59, 130, 246, 0.3)'  // 🔥 添加阴影
                      }} />
                      <Box sx={{ fontSize: '0.875rem', fontWeight: 600, color: '#1e40af' }}>📚 知识库增强</Box>
                    </Box>
                    <FormControlLabel
                      control={
                        <Checkbox 
                          checked={useKnowledgeBase}
                          onChange={(e) => setUseKnowledgeBase(e.target.checked)}
                          size="small"
                          sx={{ color: '#3b82f6', '&.Mui-checked': { color: '#3b82f6' } }}
                        />
                      }
                      label={<Box sx={{ fontSize: '0.813rem', color: '#1e40af' }}>启用知识库</Box>}
                      sx={{ m: 0 }}
                    />
                  </Box>
                  <Box sx={{ fontSize: '0.75rem', color: '#6b7280', mb: 1.5 }}>
                    开启后，AI将从向量知识库中检索相关信息，生成更专业的回复内容。
                  </Box>
                  
                  {/* 🔥 新增：语气选择 */}
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ fontSize: '0.75rem', color: '#1e40af', mb: 0.5, fontWeight: 500 }}>回复语气</Box>
                    <Select
                      fullWidth
                      size="small"
                      value={replyTone}
                      onChange={(e) => setReplyTone(e.target.value)}
                      sx={{ 
                        fontSize: '0.813rem',
                        bgcolor: '#fff',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#bfdbfe'
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#3b82f6'
                        }
                      }}
                    >
                      <MenuItem value="professional">💼 专业型 - 适合商务洽谈</MenuItem>
                      <MenuItem value="friendly">😊 友好型 - 适合熟络客户</MenuItem>
                      <MenuItem value="formal">🎯 正式型 - 适合大客户</MenuItem>
                      <MenuItem value="enthusiastic">✨ 热情型 - 适合新客户</MenuItem>
                    </Select>
                  </Box>
                  
                  {/* 🔥 新增：AI模型选择 */}
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ fontSize: '0.75rem', color: '#1e40af', mb: 0.5, fontWeight: 500 }}>AI模型</Box>
                    <Select
                      fullWidth
                      size="small"
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      sx={{ 
                        fontSize: '0.813rem',
                        bgcolor: '#fff',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#bfdbfe'
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#3b82f6'
                        }
                      }}
                    >
                      <MenuItem value="gpt-4o-mini">🚀 GPT-4o Mini (快速)</MenuItem>
                      <MenuItem value="gpt-4o">🎯 GPT-4o (标准)</MenuItem>
                      <MenuItem value="gpt-4-turbo">💡 GPT-4 Turbo (高级)</MenuItem>
                      <MenuItem value="claude-3-haiku">🌿 Claude 3 Haiku</MenuItem>
                      <MenuItem value="claude-3-sonnet">🎵 Claude 3 Sonnet</MenuItem>
                    </Select>
                  </Box>
                  
                  {/* 🔥 新增：提示词模板选择 */}
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ fontSize: '0.75rem', color: '#1e40af', mb: 0.5, fontWeight: 500 }}>提示词模板</Box>
                    <Select
                      fullWidth
                      size="small"
                      value={selectedPromptTemplate || ''}
                      onChange={(e) => {
                        const templateId = e.target.value ? parseInt(String(e.target.value)) : null
                        setSelectedPromptTemplate(templateId)
                        // 如果选择了模板，并且模板有推荐模型，自动切换模型
                        if (templateId) {
                          const template = promptTemplates.find(t => t.id === templateId)
                          if (template?.recommended_model) {
                            setSelectedModel(template.recommended_model)
                          }
                        }
                      }}
                      sx={{ 
                        fontSize: '0.813rem',
                        bgcolor: '#fff',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#bfdbfe'
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#3b82f6'
                        }
                      }}
                    >
                      <MenuItem value="">🛠️ 使用默认提示词</MenuItem>
                      {promptTemplates.map((template: any) => (
                        <MenuItem key={template.id} value={template.id}>
                          {template.is_default ? '⭐ ' : '📝 '}{template.name}
                        </MenuItem>
                      ))}
                    </Select>
                    {selectedPromptTemplate && (
                      <Box sx={{ fontSize: '0.7rem', color: '#6b7280', mt: 0.5 }}>
                        {promptTemplates.find(t => t.id === selectedPromptTemplate)?.description}
                      </Box>
                    )}
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={generatingReply ? <AutoFixHighIcon sx={{ animation: 'spin 1s linear infinite' }} /> : <AutoFixHighIcon />}
                      onClick={generateAIReply}
                      disabled={generatingReply || !location.state?.originalBody}
                      sx={{ 
                        bgcolor: '#3b82f6', 
                        '&:hover': { bgcolor: '#2563eb' },
                        textTransform: 'none',
                        fontWeight: 600,
                        height: '40px',  // 🔥 固定高度
                        fontSize: '0.875rem'  // 🔥 稍微减小字体
                      }}
                    >
                      {/* 🔥 显示当前步骤 */}
                      {generatingReply ? (generatingStep || 'AI生成中...') : '🤖 生成AI回复'}
                    </Button>
                    {/* 🔥 新增：重新生成按钮 */}
                    {lastGeneratedReply && (
                      <Button
                        variant="outlined"
                        startIcon={<RefreshIcon sx={{ fontSize: '1.1rem' }} />}
                        onClick={generateAIReply}
                        disabled={generatingReply || !location.state?.originalBody}
                        sx={{ 
                          minWidth: '110px',  // 🔥 缩小宽度
                          height: '40px',
                          borderColor: '#3b82f6',
                          color: '#3b82f6',
                          '&:hover': { 
                            borderColor: '#2563eb',
                            bgcolor: '#eff6ff'
                          },
                          textTransform: 'none',
                          fontWeight: 600,
                          fontSize: '0.875rem',  // 🔥 稍微减小字体
                          px: 1.5  // 🔥 减小左右内边距
                        }}
                      >
                        重新生成
                      </Button>
                    )}
                  </Box>
                </Paper>
                
                {/* 🔥 显示使用的知识片段 */}
                {knowledgeUsed.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ 
                      fontSize: '0.875rem', 
                      fontWeight: 600, 
                      mb: 1.5, 
                      color: '#047857',  // 🔥 使用知识库主题色
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: 1 
                    }}>
                      <Box sx={{ 
                        width: 4, 
                        height: 18,  // 🔥 增加高度 
                        bgcolor: '#10b981', 
                        borderRadius: 1,
                        boxShadow: '0 2px 4px rgba(16, 185, 129, 0.3)'  // 🔥 添加阴影
                      }} />
                      📚 已引用知识 ({knowledgeUsed.length})
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {knowledgeUsed.map((knowledge: any, i: number) => (
                        <Paper 
                          key={i} 
                          variant="outlined" 
                          sx={{ 
                            p: 1.5, 
                            bgcolor: '#f0fdf4',  // 🔥 浅绿色背景
                            borderColor: '#bbf7d0',  // 🔥 绿色边框
                            transition: 'all 0.2s ease',  // 🔥 添加过渡效果
                            '&:hover': {
                              bgcolor: '#dcfce7',  // 🔥 hover加深
                              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.15)',  // 🔥 hover阴影
                              transform: 'translateY(-2px)'  // 🔥 hover微幅上移
                            }
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 0.5 }}>
                            <Box sx={{ 
                              fontSize: '0.75rem', 
                              fontWeight: 600, 
                              color: '#047857',
                              display: 'flex',
                              alignItems: 'center',
                              gap: 0.5
                            }}>
                              📄 {knowledge.document_title || '文档'}
                            </Box>
                            <Chip 
                              label={`相似度: ${(knowledge.similarity * 100).toFixed(0)}%`}
                              size="small" 
                              sx={{ 
                                height: 20,  // 🔥 统一高度
                                fontSize: '0.7rem',  // 🔥 稍大字体
                                bgcolor: '#dcfce7', 
                                color: '#047857',
                                fontWeight: 600,
                                border: '1px solid #bbf7d0'  // 🔥 添加边框
                              }}
                            />
                          </Box>
                          <Box sx={{ 
                            fontSize: '0.7rem', 
                            color: '#6b7280', 
                            bgcolor: '#fefefe', 
                            p: 1.5,  // 🔥 增加内边距 
                            borderRadius: 1,  // 🔥 增加圆角
                            maxHeight: 100, 
                            overflowY: 'auto', 
                            whiteSpace: 'pre-wrap', 
                            border: '1px solid #e5e7eb',
                            lineHeight: 1.6,  // 🔥 增加行高
                            '&::-webkit-scrollbar': {  // 🔥 美化滚动条
                              width: '6px'
                            },
                            '&::-webkit-scrollbar-thumb': {
                              bgcolor: '#d1d5db',
                              borderRadius: '3px'
                            }
                          }}>
                            {knowledge.content.substring(0, 200)}{knowledge.content.length > 200 ? '...' : ''}
                          </Box>
                        </Paper>
                      ))}
                    </Box>
                  </Box>
                )}
                
                {loadingAI ? (
                  <Box sx={{ textAlign: 'center', py: 4, color: '#9ca3af' }}>
                    <PsychologyIcon sx={{ fontSize: 48, mb: 1 }} />
                    <Box>AI分析中...</Box>
                  </Box>
                ) : (
                  <>
                    {aiAnalysis && (
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#374151', display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{ width: 4, height: 16, bgcolor: '#8b5cf6', borderRadius: 1 }} />
                          📊 邮件分析
                        </Box>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5, fontSize: '0.75rem' }}>
                            <Box>
                              <Box sx={{ color: '#6b7280', mb: 0.5 }}>类型</Box>
                              <Chip label={aiAnalysis.category} size="small" sx={{ height: 20, fontSize: '0.7rem' }} />
                            </Box>
                            <Box>
                              <Box sx={{ color: '#6b7280', mb: 0.5 }}>紧急度</Box>
                              <Chip label={aiAnalysis.urgency_level} size="small" color={aiAnalysis.urgency_level === 'high' ? 'error' : 'default'} sx={{ height: 20, fontSize: '0.7rem' }} />
                            </Box>
                          </Box>
                        </Paper>
                      </Box>
                    )}
                    
                    {aiSuggestions.length > 0 && (
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#374151', display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{ width: 4, height: 16, bgcolor: '#10b981', borderRadius: 1 }} />
                          🤖 AI回复建议
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                          {aiSuggestions.map((suggestion: any, i: number) => (
                            <Paper key={i} variant="outlined" sx={{ p: 2 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                                <Box sx={{ fontSize: '0.813rem', fontWeight: 600, color: '#374151' }}>{suggestion.title}</Box>
                                <Button size="small" variant="outlined" startIcon={<LightbulbIcon />} onClick={() => useAISuggestion(suggestion)} sx={{ fontSize: '0.7rem', minWidth: 'auto', px: 1 }}>应用</Button>
                              </Box>
                              <Box sx={{ fontSize: '0.7rem', color: '#6b7280', bgcolor: '#f9fafb', p: 1, borderRadius: 0.5, maxHeight: 120, overflowY: 'auto', whiteSpace: 'pre-wrap' }}>{suggestion.content.substring(0, 200)}{suggestion.content.length > 200 ? '...' : ''}</Box>
                            </Paper>
                          ))}
                        </Box>
                      </Box>
                    )}
                    
                    {!aiAnalysis && !aiSuggestions.length && (
                      <Box sx={{ textAlign: 'center', py: 6, color: '#9ca3af' }}>
                        <PsychologyIcon sx={{ fontSize: 48, mb: 1, opacity: 0.3 }} />
                        <Box sx={{ fontSize: '0.813rem' }}>回复邮件时将自动生成AI分析</Box>
                      </Box>
                    )}
                  </>
                )}
              </Box>
            )}
            
            {/* Tab 2: 快捷回复 */}
            {selectedTab === 2 && (
              <Box>
                <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#374151', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 4, height: 16, bgcolor: '#10b981', borderRadius: 1 }} />
                  快捷回复模板 ({quickReplies.length})
                </Box>
                
                {quickReplies.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4, color: '#9ca3af', fontSize: '0.813rem' }}>暂无模板</Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    {quickReplies.map((template: any) => (
                      <Paper key={template.id} variant="outlined" sx={{ p: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                          <Box sx={{ flex: 1 }}>
                            <Box sx={{ fontSize: '0.813rem', fontWeight: 600, color: '#374151', mb: 0.5 }}>{template.name}</Box>
                            <Box sx={{ display: 'flex', gap: 0.5, mb: 1 }}>
                              <Chip label={template.category} size="small" sx={{ height: 18, fontSize: '0.65rem' }} />
                              {template.usage_count > 0 && (
                                <Chip label={`使用${template.usage_count}次`} size="small" sx={{ height: 18, fontSize: '0.65rem', bgcolor: '#e0f2fe', color: '#0369a1' }} />
                              )}
                            </Box>
                          </Box>
                          <Button size="small" variant="outlined" onClick={() => useQuickReply(template)} sx={{ fontSize: '0.7rem', minWidth: 'auto', px: 1 }}>应用</Button>
                        </Box>
                        <Box sx={{ fontSize: '0.75rem', color: '#6b7280', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{template.subject}</Box>
                      </Paper>
                    ))}
                  </Box>
                )}
              </Box>
            )}
          </Box>
        </Box>
      </Box>
      
      {/* 往来邮件抽屉弹窗 */}
      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)} sx={{ '& .MuiDrawer-paper': { width: '50%', maxWidth: '800px', minWidth: '600px', p: 3 } }}>
        {selectedEmail && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, pb: 2, borderBottom: '2px solid #e5e7eb' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Chip label={selectedEmail.direction === 'outbound' ? '出站' : '入站'} size="small" sx={{ bgcolor: selectedEmail.direction === 'outbound' ? '#3b82f6' : '#10b981', color: '#fff', fontWeight: 500 }} />
                <Box sx={{ fontSize: '1.25rem', fontWeight: 600, color: '#374151' }}>邮件详情</Box>
              </Box>
              <IconButton onClick={() => setDrawerOpen(false)} size="small"><CloseIcon /></IconButton>
            </Box>
            
            <Box sx={{ overflowY: 'auto', maxHeight: 'calc(100vh - 150px)' }}>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#6b7280' }}>基本信息</Box>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  <Box>
                    <Box sx={{ fontSize: '0.75rem', color: '#9ca3af', mb: 0.5 }}>发件人</Box>
                    <Box sx={{ fontSize: '0.875rem', color: '#374151' }}>{selectedEmail.from_email}</Box>
                  </Box>
                  <Box>
                    <Box sx={{ fontSize: '0.75rem', color: '#9ca3af', mb: 0.5 }}>收件人</Box>
                    <Box sx={{ fontSize: '0.875rem', color: '#374151' }}>{selectedEmail.to_email}</Box>
                  </Box>
                  <Box>
                    <Box sx={{ fontSize: '0.75rem', color: '#9ca3af', mb: 0.5 }}>时间</Box>
                    <Box sx={{ fontSize: '0.875rem', color: '#374151' }}>{getRelativeTime(selectedEmail.sent_at)}</Box>
                  </Box>
                </Box>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#6b7280' }}>主题</Box>
                <Box sx={{ fontSize: '1rem', fontWeight: 500, color: '#374151', p: 2, bgcolor: '#f9fafb', borderRadius: 1, border: '1px solid #e5e7eb' }}>{selectedEmail.subject || '(无主题)'}</Box>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ fontSize: '0.875rem', fontWeight: 600, mb: 1.5, color: '#6b7280' }}>邮件正文</Box>
                <Paper variant="outlined" sx={{ p: 2.5, bgcolor: '#fff', minHeight: '200px', maxHeight: '500px', overflowY: 'auto' }}>
                  <Box sx={{ fontSize: '0.875rem', color: '#374151' }}>
                    <HtmlContent content={selectedEmail.body || ''} />
                  </Box>
                </Paper>
              </Box>
            </Box>
          </Box>
        )}
      </Drawer>
      
      {/* 签名选择对话框 */}
      <Dialog 
        open={signatureDialogOpen} 
        onClose={() => setSignatureDialogOpen(false)}
        maxWidth={showCreateSignature ? 'md' : 'xs'}
        fullWidth
        PaperProps={{
          sx: {
            minHeight: showCreateSignature ? 520 : 'auto'
          }
        }}
      >
        <DialogTitle sx={{ pb: 1, fontSize: '15px', fontWeight: 500 }}>
          {showCreateSignature ? '新建个性签名' : '选择签名'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {!showCreateSignature ? (
            <>
              <RadioGroup
                value={selectedSignatureId?.toString() || ''}
                onChange={(e) => {
                  const sigId = parseInt(e.target.value)
                  setSelectedSignatureId(sigId)
                  const sig = signatures.find(s => s.id === sigId)
                  if (sig) {
                    setEmailOptions({ ...emailOptions, signature: sig.name })
                  }
                }}
              >
                {signatures.map((sig) => (
                  <FormControlLabel 
                    key={sig.id}
                    value={sig.id.toString()}
                    control={<Radio size="small" />} 
                    label={
                      <Box>
                        <Box sx={{ fontSize: '14px', fontWeight: sig.is_default ? 600 : 400 }}>
                          {sig.name}
                          {sig.is_default && (
                            <Chip 
                              label="默认" 
                              size="small" 
                              sx={{ ml: 1, height: 18, fontSize: '11px', bgcolor: '#fef3c7', color: '#92400e' }}
                            />
                          )}
                        </Box>
                        {sig.content && (
                          <Box 
                            sx={{ 
                              fontSize: '12px', 
                              color: '#999',
                              mt: 0.5,
                              maxWidth: 300,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {sig.content.replace(/<[^>]*>/g, '').substring(0, 50)}
                          </Box>
                        )}
                      </Box>
                    }
                    sx={{ mb: 1, alignItems: 'flex-start' }}
                  />
                ))}
              </RadioGroup>
                      
              <Divider sx={{ my: 2 }} />
                      
              {/* 新增签名按钮 */}
              <Button
                fullWidth
                startIcon={<CreateIcon sx={{ fontSize: 16 }} />}
                onClick={() => setShowCreateSignature(true)}
                sx={{ 
                  fontSize: '13px',
                  color: '#1677ff',
                  textTransform: 'none',
                  justifyContent: 'flex-start',
                  '&:hover': {
                    bgcolor: '#f0f9ff'
                  }
                }}
              >
                新建个性签名
              </Button>
            </>
          ) : (
            <Box>
              {/* 签名名称 */}
              <Box sx={{ mb: 3 }}>
                <Typography sx={{ fontSize: '14px', color: '#333', mb: 1.5, fontWeight: 500 }}>名称</Typography>
                <MuiTextField
                  fullWidth
                  placeholder="Please enter"
                  value={newSignature.name}
                  onChange={(e) => setNewSignature({ ...newSignature, name: e.target.value })}
                  sx={{ 
                    '& .MuiOutlinedInput-root': {
                      fontSize: '14px',
                      bgcolor: '#fafafa'
                    }
                  }}
                />
              </Box>
              
              {/* 签名内容 */}
              <Box sx={{ mb: 2 }}>
                <Typography sx={{ fontSize: '14px', color: '#333', mb: 1.5, fontWeight: 500 }}>内容</Typography>
                <Box sx={{ border: '1px solid #d9d9d9', borderRadius: 1, overflow: 'hidden' }}>
                  {/* 富文本工具栏 */}
                  <Box sx={{ 
                    borderBottom: '1px solid #e0e0e0',
                    bgcolor: '#fafafa',
                    p: 1,
                    display: 'flex',
                    gap: 0.5,
                    alignItems: 'center',
                    flexWrap: 'wrap'
                  }}>
                    {/* 撤销/重做 */}
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('undo')}
                      sx={{ width: 32, height: 32 }}
                      title="撤销"
                    >
                      <UndoIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('redo')}
                      sx={{ width: 32, height: 32 }}
                      title="重做"
                    >
                      <RedoIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 字体选择 */}
                    <Select
                      size="small"
                      defaultValue="Arial"
                      onChange={(e) => changeFontFamily(e.target.value)}
                      sx={{ minWidth: 120, height: 32, fontSize: '13px', bgcolor: 'white' }}
                    >
                      <MenuItem value="Arial">Arial</MenuItem>
                      <MenuItem value="SimSun">宋体</MenuItem>
                      <MenuItem value="Microsoft YaHei">微软雅黑</MenuItem>
                      <MenuItem value="SimHei">黑体</MenuItem>
                      <MenuItem value="KaiTi">楷体</MenuItem>
                      <MenuItem value="Courier New">Courier New</MenuItem>
                      <MenuItem value="Times New Roman">Times New Roman</MenuItem>
                    </Select>
                    
                    {/* 字号选择 */}
                    <Select
                      size="small"
                      defaultValue="14px"
                      onChange={(e) => changeFontSize(e.target.value)}
                      sx={{ width: 90, height: 32, fontSize: '13px', bgcolor: 'white' }}
                    >
                      <MenuItem value="12px">12px</MenuItem>
                      <MenuItem value="14px">14px</MenuItem>
                      <MenuItem value="16px">16px</MenuItem>
                      <MenuItem value="18px">18px</MenuItem>
                      <MenuItem value="20px">20px</MenuItem>
                      <MenuItem value="24px">24px</MenuItem>
                    </Select>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 文字格式 */}
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('bold')}
                      sx={{ width: 32, height: 32 }}
                      title="加粗"
                    >
                      <FormatBoldIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('italic')}
                      sx={{ width: 32, height: 32 }}
                      title="斜体"
                    >
                      <FormatItalicIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('underline')}
                      sx={{ width: 32, height: 32 }}
                      title="下划线"
                    >
                      <FormatUnderlinedIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('strikeThrough')}
                      sx={{ width: 32, height: 32 }}
                      title="删除线"
                    >
                      <Box component="span" sx={{ fontSize: 18, fontWeight: 'bold', textDecoration: 'line-through' }}>S</Box>
                    </IconButton>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 文字颜色 */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <IconButton 
                        size="small" 
                        sx={{ width: 32, height: 32 }}
                        title="文字颜色"
                      >
                        <FormatColorTextIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                      <input 
                        type="color" 
                        onChange={(e) => execSignatureCommand('foreColor', e.target.value)}
                        style={{ width: 24, height: 24, border: 'none', cursor: 'pointer' }}
                      />
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <IconButton 
                        size="small" 
                        sx={{ width: 32, height: 32 }}
                        title="背景颜色"
                      >
                        <FormatColorFillIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                      <input 
                        type="color" 
                        onChange={(e) => execSignatureCommand('backColor', e.target.value)}
                        style={{ width: 24, height: 24, border: 'none', cursor: 'pointer' }}
                      />
                    </Box>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 对齐方式 */}
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('justifyLeft')}
                      sx={{ width: 32, height: 32 }}
                      title="左对齐"
                    >
                      <FormatAlignLeftIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('justifyCenter')}
                      sx={{ width: 32, height: 32 }}
                      title="居中对齐"
                    >
                      <FormatAlignCenterIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('justifyRight')}
                      sx={{ width: 32, height: 32 }}
                      title="右对齐"
                    >
                      <FormatAlignRightIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 列表 */}
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('insertUnorderedList')}
                      sx={{ width: 32, height: 32 }}
                      title="无序列表"
                    >
                      <FormatListBulletedIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('insertOrderedList')}
                      sx={{ width: 32, height: 32 }}
                      title="有序列表"
                    >
                      <FormatListNumberedIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 插入链接 */}
                    <IconButton 
                      size="small" 
                      onClick={insertLink}
                      sx={{ width: 32, height: 32 }}
                      title="插入链接"
                    >
                      <InsertLinkIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    
                    {/* 插入图片 */}
                    <IconButton 
                      size="small" 
                      onClick={insertImageToSignature}
                      sx={{ width: 32, height: 32 }}
                      title="插入图片"
                    >
                      <InsertPhotoIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                    
                    <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                    
                    {/* 清除格式 */}
                    <IconButton 
                      size="small" 
                      onClick={() => execSignatureCommand('removeFormat')}
                      sx={{ width: 32, height: 32 }}
                      title="清除格式"
                    >
                      <CloseIcon sx={{ fontSize: 18 }} />
                    </IconButton>
                  </Box>
                  
                  {/* 编辑器 */}
                  <Box
                    ref={signatureEditorRef}
                    contentEditable
                    suppressContentEditableWarning
                    onInput={(e: any) => {
                      setNewSignature({ ...newSignature, content: e.currentTarget.innerHTML })
                    }}
                    onKeyDown={(e) => {
                      // 处理Tab键
                      if (e.key === 'Tab') {
                        e.preventDefault()
                        execSignatureCommand('insertHTML', '&nbsp;&nbsp;&nbsp;&nbsp;')
                      }
                    }}
                    sx={{
                      minHeight: 280,
                      maxHeight: 400,
                      overflowY: 'auto',
                      p: 2.5,
                      fontSize: '14px',
                      lineHeight: 1.6,
                      bgcolor: 'white',
                      outline: 'none',
                      cursor: 'text',
                      '&:empty:before': {
                        content: '"请输入签名内容..."',
                        color: '#bfbfbf'
                      },
                      '& img': {
                        maxWidth: '100%',
                        height: 'auto',
                        display: 'block',
                        margin: '10px 0'
                      },
                      '& a': {
                        color: '#1677ff',
                        textDecoration: 'underline'
                      },
                      '& ul, & ol': {
                        paddingLeft: '30px',
                        margin: '10px 0'
                      },
                      '& p': {
                        margin: '5px 0'
                      }
                    }}
                  />
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2.5, pt: 2, bgcolor: '#fafafa', borderTop: '1px solid #e8e8e8' }}>
          {showCreateSignature ? (
            <>
              <Button 
                onClick={() => {
                  setShowCreateSignature(false)
                  setNewSignature({ name: '', content: '' })
                }}
                sx={{ 
                  fontSize: '14px',
                  color: '#666',
                  textTransform: 'none',
                  px: 3,
                  py: 0.75
                }}
              >
                取消
              </Button>
              <Button 
                onClick={createSignature}
                variant="contained"
                sx={{ 
                  fontSize: '14px',
                  bgcolor: '#1677ff',
                  textTransform: 'none',
                  px: 3,
                  py: 0.75,
                  '&:hover': {
                    bgcolor: '#0958d9'
                  }
                }}
              >
                保存
              </Button>
            </>
          ) : (
            <>
              <Button 
                onClick={() => setSignatureDialogOpen(false)} 
                sx={{ 
                  fontSize: '13px',
                  color: '#666',
                  textTransform: 'none'
                }}
              >
                取消
              </Button>
              <Button 
                onClick={() => {
                  // 应用签名到邮件内容
                  if (selectedSignatureId && editorRef.current) {
                    const signature = signatures.find(s => s.id === selectedSignatureId)
                    if (signature && signature.content) {
                      const currentBody = editorRef.current.innerHTML
                      // 移除之前的签名（如果有）
                      let newBody = currentBody
                      // 添加新签名
                      if (newBody && !newBody.endsWith('<br>')) {
                        newBody += '<br><br>'
                      }
                      newBody += signature.content
                      editorRef.current.innerHTML = newBody
                      setFormData({ ...formData, body: newBody })
                    }
                  }
                  setSignatureDialogOpen(false)
                }}
                variant="contained"
                sx={{ 
                  fontSize: '13px',
                  bgcolor: '#1677ff',
                  textTransform: 'none',
                  '&:hover': {
                    bgcolor: '#4096ff'
                  }
                }}
              >
                确定
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export const EmailShow = (props:any) => {
  const navigate = useNavigate()
  const notify = useNotify()
  const refresh = useRefresh()
  const { id: recordId } = useParams() // 🔥 从 URL 获取 ID
  const record = useRecordContext() // 🔥 获取记录上下文
  const [emailData, setEmailData] = useState<any>(null) // 🔥 存储邮件数据
  const [translating, setTranslating] = useState(false) // 🔥 翻译状态
  const [translatedContent, setTranslatedContent] = useState<string | null>(null) // 🔥 翻译后的内容
  const [showTranslation, setShowTranslation] = useState(false) // 🔥 是否显示翻译
  
  // 🔥 组件加载时获取邮件数据并标记为已读
  useEffect(() => {
    const emailId = recordId || record?.id
    
    console.log('🔍 EmailShow useEffect 触发:', {
      recordId,
      'record?.id': record?.id,
      emailId
    })
    
    // 🔥 只要有 ID 就获取邮件数据
    if (emailId) {
      console.log('📖 EmailShow 加载，获取邮件数据, ID:', emailId)
      const token = localStorage.getItem('token')
      if (token) {
        // 🔥 先获取邮件数据
        fetch(`http://127.0.0.1:8001/api/email_history/${emailId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          }
        })
        .then(response => {
          if (response.ok) {
            return response.json()
          } else {
            throw new Error(`获取邮件数据失败: ${response.status}`)
          }
        })
        .then(data => {
          console.log('✅ 邮件数据已加载:', data)
          setEmailData(data)
          
          // 🔥 然后标记为已读
          return fetch(`http://127.0.0.1:8001/api/email_history/${emailId}`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ opened: true })
          })
        })
        .then(response => {
          if (response?.ok) {
            console.log('✅ 已标记为已读')
          }
        })
        .catch(error => {
          console.error('❌ 请求异常:', error)
          notify(`加载邮件失败: ${error.message}`, { type: 'error' })
        })
      } else {
        console.error('❌ 没有token')
      }
    } else {
      console.warn('⚠️ 没有获取到emailId')
    }
  }, [recordId, record])
  
  // 使用浏览器历史返回，保持列表的筛选状态
  const handleBack = () => {
    console.log('🔙 返回列表')
    // 🔥 使用 navigate(-1) 返回上一页，保持筛选状态
    navigate(-1)
  }
  
  // 🔥 处理回复按钮
  const handleReply = () => {
    const currentEmail = emailData || record
    
    if (!currentEmail) {
      notify('邮件数据还未加载，请稍后', { type: 'warning' })
      return
    }
    
    console.log('📧 回复邮件:', currentEmail)
    
    // 跳转到邮件创建页，带上回复所需的信息
    navigate('/email_history/create', { 
      state: { 
        customer_id: currentEmail.customer_id,
        direction: 'outbound',
        subject: `Re: ${currentEmail.subject}`,
        to_email: currentEmail.from_email,
        from_email: currentEmail.to_email,
        originalBody: currentEmail.body || currentEmail.html_body,
        originalEmailId: currentEmail.id  // 🔥 传递原邮件ID
      } 
    })
  }
  
  // 🔥 处理删除按钮
  const handleDelete = async () => {
    const currentEmail = emailData || record
    const emailId = recordId || currentEmail?.id
    
    if (!emailId) {
      notify('邮件数据还未加载，请稍后', { type: 'warning' })
      return
    }
    
    if (!window.confirm('确定要删除这封邮件吗？')) {
      return
    }
    
    console.log('🗑️ 删除邮件 ID:', emailId)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:8001/api/email_history/${emailId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_deleted: true })
      })
      
      if (response.ok) {
        notify('邮件已移至回收站', { type: 'success' })
        // 返回列表
        navigate(-1)
      } else {
        const errorText = await response.text()
        console.error('删除失败:', errorText)
        notify('删除失败', { type: 'error' })
      }
    } catch (error) {
      console.error('删除邮件异常:', error)
      notify('删除失败', { type: 'error' })
    }
  }
  
  // 🔥 处理翻译按钮
  const handleTranslate = async () => {
    const currentEmail = emailData || record
    if (!currentEmail) {
      notify('邮件数据还未加载，请稍后', { type: 'warning' })
      return
    }
    
    // 如果已经有翻译内容，直接切换显示
    if (translatedContent) {
      setShowTranslation(!showTranslation)
      return
    }
    
    // 开始翻译
    setTranslating(true)
    try {
      const token = localStorage.getItem('token')
      const content = currentEmail.html_body || currentEmail.body
      
      const response = await fetch('http://127.0.0.1:8001/api/ai/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          content: content,  // 🔥 后端参数名是 content
          target_lang: 'zh'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setTranslatedContent(data.translated)  // 🔥 后端返回的字段名是 translated
        setShowTranslation(true)
        notify('翻译完成', { type: 'success' })
      } else {
        notify('翻译失败', { type: 'error' })
      }
    } catch (error) {
      console.error('翻译异常:', error)
      notify('翻译失败', { type: 'error' })
    } finally {
      setTranslating(false)
    }
  }
  
  const currentEmail = emailData || record
  
  return (
    <Show {...props} title="邮件详情">
      <Box sx={{ p: 3 }}>
        {/* 🔥 顶部操作按钮 */}
        <Box sx={{ mb: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button 
            startIcon={<ArrowBackIcon />} 
            onClick={handleBack} 
            variant="outlined" 
            size="small"
            sx={{ fontSize: '13px' }}
          >
            返回列表
          </Button>
          
          <Button 
            startIcon={<ReplyIcon />} 
            onClick={handleReply} 
            variant="contained" 
            size="small"
            disabled={!currentEmail}
            sx={{ 
              bgcolor: '#1677ff', 
              '&:hover': { bgcolor: '#4096ff' },
              fontSize: '13px'
            }}
          >
            回复
          </Button>
          
          <Button 
            startIcon={<DeleteIcon />} 
            onClick={handleDelete} 
            variant="outlined" 
            size="small"
            color="error"
            disabled={!currentEmail}
            sx={{ fontSize: '13px' }}
          >
            删除
          </Button>
        </Box>
        
        {/* 🔥 邮件详情内容 */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          {!currentEmail ? (
            // 🔥 加载中状态
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              flexDirection: 'column',
              gap: 2
            }}>
              <CircularProgress />
              <Typography sx={{ color: '#6b7280' }}>加载邮件详情中...</Typography>
            </Box>
          ) : (
            <>
              {/* 邮件主题 */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
                  {currentEmail?.subject || '(无主题)'}
                </Typography>
              </Box>
              
              {/* 发件人和收件人信息 */}
              <Box sx={{ 
                mb: 2, 
                pb: 2,
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                fontSize: '13px',
                color: '#6b7280'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ 
                    width: 32, 
                    height: 32, 
                    borderRadius: '50%', 
                    bgcolor: '#ef4444',
                    color: '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: 600,
                    flexShrink: 0
                  }}>
                    {currentEmail?.from_name?.charAt(0) || currentEmail?.from_email?.charAt(0)?.toUpperCase() || 'U'}
                  </Box>
                  <Box>
                    <Box sx={{ fontWeight: 600, color: '#1f2937', fontSize: '14px' }}>
                      {currentEmail?.from_name || currentEmail?.from_email?.split('@')[0] || '未知发件人'}
                    </Box>
                    <Box sx={{ fontSize: '12px', color: '#9ca3af' }}>
                      收件人：{currentEmail?.to_email || '-'}
                    </Box>
                  </Box>
                </Box>
                
                <Box sx={{ ml: 'auto', fontSize: '12px', color: '#9ca3af' }}>
                  {currentEmail?.sent_at ? new Date(currentEmail.sent_at).toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  }) : '-'}
                </Box>
              </Box>
              
              {/* 翻译提示条 */}
              <Box sx={{ 
                mb: 2,
                p: 1.5,
                bgcolor: '#f0f9ff',
                borderRadius: '4px',
                border: '1px solid #bae6fd',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TranslateIcon sx={{ fontSize: 18, color: '#0284c7' }} />
                  <Typography sx={{ fontSize: '13px', color: '#0c4a6e' }}>
                    {showTranslation ? '正在查看中文翻译' : '邮件可翻译为中文'}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {translatedContent && (
                    <Button
                      size="small"
                      onClick={() => setShowTranslation(!showTranslation)}
                      sx={{ 
                        fontSize: '12px',
                        textTransform: 'none',
                        color: '#0284c7',
                        minWidth: 'auto'
                      }}
                    >
                      {showTranslation ? '查看原文' : '查看翻译'}
                    </Button>
                  )}
                  
                  {!translatedContent && (
                    <Button
                      size="small"
                      onClick={handleTranslate}
                      disabled={translating}
                      startIcon={translating ? <CircularProgress size={14} /> : null}
                      sx={{ 
                        fontSize: '12px',
                        textTransform: 'none',
                        color: '#0284c7',
                        fontWeight: 500
                      }}
                    >
                      {translating ? '翻译中...' : '全文翻译'}
                    </Button>
                  )}
                  
                  <IconButton 
                    size="small" 
                    onClick={() => {
                      setShowTranslation(false)
                      setTranslatedContent(null)
                    }}
                    sx={{ ml: 1 }}
                  >
                    <CloseIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </Box>
              </Box>
              
              {/* 邮件正文 */}
              <Box sx={{ 
                p: 2,
                bgcolor: '#ffffff',
                borderRadius: '4px',
                border: '1px solid #e5e7eb',
                minHeight: '300px'
              }}>
                {showTranslation && translatedContent ? (
                  <HtmlContent content={translatedContent} />
                ) : (
                  <HtmlContent content={currentEmail?.html_body || currentEmail?.body} />
                )}
              </Box>
              
              {/* 🔥 附件区域 */}
              {currentEmail?.attachments && currentEmail.attachments !== 'null' && currentEmail.attachments !== 'None' && (() => {
                try {
                  // 处理Python风格的单引号JSON（将单引号替换为双引号）
                  let attachmentsStr = currentEmail.attachments
                  if (typeof attachmentsStr === 'string') {
                    // Python的字典字符串转换为JSON
                    attachmentsStr = attachmentsStr.replace(/'/g, '"')
                  }
                  
                  const attachments = JSON.parse(attachmentsStr)
                  console.log('📎 附件数据:', attachments)
                  
                  if (Array.isArray(attachments) && attachments.length > 0) {
                    // 计算总大小
                    const totalSize = attachments.reduce((sum, file) => sum + (file.size || 0), 0)
                    const totalSizeKB = (totalSize / 1024).toFixed(1)
                    
                    return (
                      <Box sx={{ mt: 2 }}>
                        {/* 附件标题 */}
                        <Box sx={{ 
                          fontSize: '13px',
                          color: '#6b7280',
                          mb: 1.5,
                          fontWeight: 500
                        }}>
                          {totalSizeKB} KB · {attachments.length}个附件
                        </Box>
                        
                        {/* 附件列表 - 横向排列 */}
                        <Box sx={{ 
                          display: 'flex', 
                          flexWrap: 'wrap',
                          gap: 1.5
                        }}>
                          {attachments.map((file: any, index: number) => {
                            const fileName = typeof file === 'string' ? file : (file.filename || file.name || '未知文件')
                            const fileSize = file.size ? `${(file.size / 1024).toFixed(0)} KB` : '未知大小'
                            
                            // 🔥 下载附件函数
                            const handleDownload = async () => {
                              try {
                                const response = await fetch(
                                  getApiUrl('email', `/email_history/${currentEmail.id}/attachments/${index}`),
                                  {
                                    method: 'GET',
                                    headers: {
                                      'Accept': '*/*'
                                    }
                                  }
                                )
                                
                                if (!response.ok) {
                                  throw new Error('下载失败')
                                }
                                
                                // 获取文件blob
                                const blob = await response.blob()
                                
                                // 创建下载链接
                                const url = window.URL.createObjectURL(blob)
                                const a = document.createElement('a')
                                a.href = url
                                a.download = fileName
                                document.body.appendChild(a)
                                a.click()
                                
                                // 清理
                                window.URL.revokeObjectURL(url)
                                document.body.removeChild(a)
                                
                                console.log('✅ 附件下载成功:', fileName)
                              } catch (error) {
                                console.error('❌ 下载附件失败:', error)
                                alert('下载失败，请重试')
                              }
                            }
                            
                            return (
                              <Box 
                                key={index} 
                                sx={{ 
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: 1,
                                  px: 1.5,
                                  py: 1,
                                  bgcolor: '#f9fafb',
                                  borderRadius: '6px',
                                  border: '1px solid #e5e7eb',
                                  cursor: 'pointer',
                                  '&:hover': { 
                                    bgcolor: '#f3f4f6',
                                    borderColor: '#d1d5db'
                                  },
                                  maxWidth: '280px'
                                }}
                                onClick={handleDownload}
                                title="点击下载附件"
                              >
                                <AttachFileIcon sx={{ fontSize: 18, color: '#6b7280', flexShrink: 0 }} />
                                <Box sx={{ 
                                  fontSize: '13px', 
                                  color: '#374151',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                  flex: 1,
                                  minWidth: 0
                                }}>
                                  {fileName}
                                </Box>
                                <Box sx={{ 
                                  fontSize: '12px', 
                                  color: '#9ca3af',
                                  flexShrink: 0,
                                  ml: 0.5
                                }}>
                                  {fileSize}
                                </Box>
                                <IconButton 
                                  size="small" 
                                  sx={{ 
                                    p: 0.5,
                                    ml: 0.5,
                                    color: '#3b82f6',
                                    '&:hover': { bgcolor: '#eff6ff' }
                                  }}
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleDownload()
                                  }}
                                >
                                  <CloudDownloadIcon sx={{ fontSize: 16 }} />
                                </IconButton>
                              </Box>
                            )
                          })}
                        </Box>
                      </Box>
                    )
                  }
                } catch (e) {
                  console.error('🐞 解析附件数据失败:', e, currentEmail.attachments)
                }
                return null
              })()}
            </>
          )}
        </Box>
      </Box>
    </Show>
  )
}

// ==================== 收件箱独立组件 ====================
export const InboxList = (props: any) => {
  return (
    <List
      {...props}
      filter={{ direction: 'inbound' }}
      perPage={20}
      filters={[
        <TextInput source="business_stage" alwaysOn style={{ display: 'none' }} />,
      ]}
      actions={false}
      title="收件箱"
      sort={{ field: 'sent_at', order: 'DESC' }}
      disableSyncWithLocation={false}
      storeKey={false}
      pagination={false}
    >
      <EmailListWithFixedHeader />
    </List>
  )
}

// ==================== 已发送独立组件 ====================
export const SentList = (props: any) => {
  return (
    <List
      {...props}
      filter={{ direction: 'outbound' }}
      perPage={20}
      actions={false}
      title="已发送"
      sort={{ field: 'sent_at', order: 'DESC' }}
      disableSyncWithLocation={false}
      storeKey={false}
      pagination={false}
    >
      <SentListWithFixedHeader />
    </List>
  )
}

// ==================== 草稿箱独立组件 ====================
export const DraftsList = (props: any) => {
  return (
    <List
      {...props}
      filter={{ status: 'draft' }}
      perPage={20}
      actions={false}
      title="草稿箱"
      sort={{ field: 'created_at', order: 'DESC' }}
      disableSyncWithLocation={false}
      storeKey={false}
      pagination={false}
    >
      <DraftsListWithFixedHeader />
    </List>
  )
}
