import { useEffect, useState } from 'react'
import { List, Datagrid, TextField as RATextField, EmailField, TextInput, SelectInput, Edit, Create, SimpleForm, useRecordContext, FunctionField, TabbedForm, FormTab, EditButton, ReferenceManyField, Button as RAButton, useNotify, useRefresh, BulkDeleteButton, BulkExportButton, useListContext, TopToolbar, ListButton, Pagination, useListController } from 'react-admin'
import { getApiUrl } from './config/api'
import Box from '@mui/material/Box'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'
import Chip from '@mui/material/Chip'
import Button from '@mui/material/Button'
import Drawer from '@mui/material/Drawer'
import IconButton from '@mui/material/IconButton'
import TextField from '@mui/material/TextField'
import MenuItem from '@mui/material/MenuItem'
import CloseIcon from '@mui/icons-material/Close'
import EditIcon from '@mui/icons-material/Edit'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import LocalOfferIcon from '@mui/icons-material/LocalOffer'
import AddIcon from '@mui/icons-material/Add'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'
import MoreVertIcon from '@mui/icons-material/MoreVert'
import FilterListIcon from '@mui/icons-material/FilterList'
import SettingsIcon from '@mui/icons-material/Settings'
import GradeIcon from '@mui/icons-material/Grade'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import LinearProgress from '@mui/material/LinearProgress'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import DeleteIcon from '@mui/icons-material/Delete'
import Menu from '@mui/material/Menu'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
import Divider from '@mui/material/Divider'

const stageLabelMap: any = {
  cold: { label: '冷源客户', color: '#6b7280' },
  contacted: { label: '已联系', color: '#3b82f6' },
  replied: { label: '已回复', color: '#8b5cf6' },
  qualified: { label: '合格线索', color: '#f59e0b' },
  negotiating: { label: '谈判中', color: '#ef4444' },
  customer: { label: '成交客户', color: '#10b981' },
  lost: { label: '已流失', color: '#6b7280' },
}

// 客户阶段编辑组件
const EditableStageCell = ({ record, refresh }: any) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [isHovered, setIsHovered] = useState(false)
  const notify = useNotify()
  
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation() // 阻止事件冒泡，避免触发行点击
    setAnchorEl(event.currentTarget)
  }
  
  const handleClose = () => {
    setAnchorEl(null)
  }
  
  const handleStageChange = async (event: React.MouseEvent, newStage: string) => {
    event.stopPropagation() // 阻止事件冒泡
    
    try {
      const response = await fetch(getApiUrl('crm', `/customers/${record.id}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStage })
      })
      
      if (response.ok) {
        notify('客户阶段已更新', { type: 'success' })
        refresh()
      } else {
        notify('更新失败', { type: 'error' })
      }
    } catch (error) {
      notify('更新失败', { type: 'error' })
    }
    handleClose()
  }
  
  const stage = stageLabelMap[record?.status]
  
  return (
    <Box 
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={(e) => e.stopPropagation()} // 阻止整个单元格的点击事件
      sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 0.5,
        width: 'fit-content',
        maxWidth: '100px',
      }}
    >
      <Chip 
        label={stage?.label || record?.status || '-'} 
        size="small" 
        sx={{ 
          bgcolor: stage?.color, 
          color: '#fff', 
          fontWeight: 500,
          fontSize: '11px',
          height: '20px',
          '& .MuiChip-label': {
            px: 1
          }
        }} 
      />
      
      {/* 编辑按钮容器 - 固定宽度 */}
      <Box sx={{ width: '24px', height: '24px', flexShrink: 0 }}>
        {isHovered && (
          <IconButton 
            size="small" 
            onClick={handleClick}
            sx={{ 
              width: '24px',
              height: '24px',
              padding: 0,
              border: '1px solid #d0d0d0',
              '&:hover': {
                backgroundColor: '#f5f5f5'
              }
            }}
          >
            <EditIcon sx={{ fontSize: '14px' }} />
          </IconButton>
        )}
      </Box>
      
      <Menu 
        anchorEl={anchorEl} 
        open={Boolean(anchorEl)} 
        onClose={handleClose}
        onClick={(e) => e.stopPropagation()} // 阻止菜单点击事件冒泡
        PaperProps={{
          sx: {
            mt: 1,
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          }
        }}
      >
        {Object.entries(stageLabelMap).map(([key, value]: [string, any]) => (
          <MenuItem 
            key={key}
            onClick={(e) => handleStageChange(e, key)}
            sx={{
              display: 'flex',
              gap: 1,
              minWidth: '140px'
            }}
          >
            <Chip 
              label={value.label} 
              size="small" 
              sx={{ 
                bgcolor: value.color, 
                color: '#fff',
                fontWeight: 500,
                width: '100%'
              }} 
            />
          </MenuItem>
        ))}
      </Menu>
    </Box>
  )
}

// 标签管理 - 可用标签列表（使用 localStorage 存储）
const getAvailableTags = (): string[] => {
  const saved = localStorage.getItem('availableTags')
  if (saved) {
    try {
      return JSON.parse(saved)
    } catch (e) {
      return ['重要客户', '潜在客户', '长期合作', '新客户', 'VIP']
    }
  }
  return ['重要客户', '潜在客户', '长期合作', '新客户', 'VIP']
}

const saveAvailableTags = (tags: string[]) => {
  localStorage.setItem('availableTags', JSON.stringify(tags))
}

// 客户标签编辑组件
const EditableTagsCell = ({ record, refresh }: any) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [isHovered, setIsHovered] = useState(false)
  const [availableTags, setAvailableTags] = useState<string[]>(getAvailableTags())
  const [newTagName, setNewTagName] = useState('')
  const [showAddInput, setShowAddInput] = useState(false)
  const notify = useNotify()
  
  // 解析客户当前的标签
  const currentTags = record?.tags ? record.tags.split(',').map((t: string) => t.trim()).filter(Boolean) : []
  
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation()
    setAnchorEl(event.currentTarget)
  }
  
  const handleClose = () => {
    setAnchorEl(null)
    setShowAddInput(false)
    setNewTagName('')
  }
  
  const handleToggleTag = async (event: React.MouseEvent, tag: string) => {
    event.stopPropagation()
    
    let newTags: string[]
    if (currentTags.includes(tag)) {
      // 移除标签
      newTags = currentTags.filter((t: string) => t !== tag)
    } else {
      // 添加标签
      newTags = [...currentTags, tag]
    }
    
    try {
      const response = await fetch(getApiUrl('crm', `/customers/${record.id}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tags: newTags.join(', ') })
      })
      
      if (response.ok) {
        notify('标签已更新', { type: 'success' })
        refresh()
      } else {
        notify('更新失败', { type: 'error' })
      }
    } catch (error) {
      notify('更新失败', { type: 'error' })
    }
  }
  
  const handleAddNewTag = (event: React.MouseEvent) => {
    event.stopPropagation()
    if (!newTagName.trim()) {
      notify('请输入标签名称', { type: 'warning' })
      return
    }
    if (availableTags.includes(newTagName.trim())) {
      notify('标签已存在', { type: 'warning' })
      return
    }
    
    const updatedTags = [...availableTags, newTagName.trim()]
    setAvailableTags(updatedTags)
    saveAvailableTags(updatedTags)
    setNewTagName('')
    setShowAddInput(false)
    notify(`标签 "${newTagName.trim()}" 已添加`, { type: 'success' })
  }
  
  const handleRemoveTag = (event: React.MouseEvent, tag: string) => {
    event.stopPropagation()
    const updatedTags = availableTags.filter(t => t !== tag)
    setAvailableTags(updatedTags)
    saveAvailableTags(updatedTags)
    notify(`标签 "${tag}" 已删除`, { type: 'info' })
  }
  
  return (
    <Box 
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={(e) => e.stopPropagation()}
      sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'flex-start',
        gap: 0.5,
        width: 'fit-content',
        maxWidth: '120px',
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        gap: 0.5, 
        flexWrap: 'wrap', 
        flex: 1, 
        overflow: 'hidden',
        alignItems: 'center'
      }}>
        {currentTags.length === 0 ? (
          <Typography variant="body2" color="text.secondary">-</Typography>
        ) : (
          currentTags.map((tag: string) => (
            <Chip 
              key={tag}
              label={tag} 
              size="small" 
              icon={<LocalOfferIcon sx={{ fontSize: '12px' }} />}
              sx={{ 
                backgroundColor: '#e3f2fd',
                color: '#1976d2',
                fontWeight: 500,
                fontSize: '11px',
                height: '20px',
                '& .MuiChip-label': {
                  px: 0.5
                },
                '& .MuiChip-icon': {
                  ml: 0.5
                }
              }} 
            />
          ))
        )}
      </Box>
      
      {/* 编辑按钮容器 */}
      <Box sx={{ width: '24px', height: '24px', flexShrink: 0 }}>
        {isHovered && (
          <IconButton 
            size="small" 
            onClick={handleClick}
            sx={{ 
              width: '24px',
              height: '24px',
              padding: 0,
              border: '1px solid #d0d0d0',
              '&:hover': {
                backgroundColor: '#f5f5f5'
              }
            }}
          >
            <EditIcon sx={{ fontSize: '14px' }} />
          </IconButton>
        )}
      </Box>
      
      <Menu 
        anchorEl={anchorEl} 
        open={Boolean(anchorEl)} 
        onClose={handleClose}
        onClick={(e) => e.stopPropagation()}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: '280px',
            maxWidth: '400px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          }
        }}
      >
        <Box sx={{ px: 2, py: 1, borderBottom: '1px solid #e0e0e0' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>选择标签</Typography>
        </Box>
        
        {/* 标签列表 */}
        <Box sx={{ maxHeight: '300px', overflowY: 'auto' }}>
          {availableTags.map((tag) => (
            <MenuItem 
              key={tag}
              onClick={(e) => handleToggleTag(e, tag)}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                py: 1
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                <Checkbox 
                  checked={currentTags.includes(tag)}
                  size="small"
                  onClick={(e) => e.stopPropagation()}
                />
                <Chip 
                  label={tag} 
                  size="small"
                  icon={<LocalOfferIcon sx={{ fontSize: '14px' }} />}
                  sx={{ 
                    backgroundColor: currentTags.includes(tag) ? '#e3f2fd' : '#f5f5f5',
                    color: currentTags.includes(tag) ? '#1976d2' : '#666',
                    fontWeight: 500
                  }} 
                />
              </Box>
              <IconButton 
                size="small" 
                onClick={(e) => handleRemoveTag(e, tag)}
                sx={{ ml: 1 }}
              >
                <CloseIcon sx={{ fontSize: '16px', color: '#999' }} />
              </IconButton>
            </MenuItem>
          ))}
        </Box>
        
        <Divider />
        
        {/* 添加新标签 */}
        <Box sx={{ px: 2, py: 1.5 }}>
          {!showAddInput ? (
            <Button 
              size="small"
              startIcon={<AddIcon />}
              onClick={(e) => {
                e.stopPropagation()
                setShowAddInput(true)
              }}
              sx={{ textTransform: 'none' }}
            >
              添加新标签
            </Button>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }} onClick={(e) => e.stopPropagation()}>
              <TextField 
                size="small"
                placeholder="输入标签名称"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleAddNewTag(e as any)
                  }
                }}
                autoFocus
                sx={{ flex: 1 }}
              />
              <Button 
                size="small" 
                variant="contained"
                onClick={handleAddNewTag}
              >
                添加
              </Button>
              <IconButton 
                size="small"
                onClick={(e) => {
                  e.stopPropagation()
                  setShowAddInput(false)
                  setNewTagName('')
                }}
              >
                <CloseIcon sx={{ fontSize: '16px' }} />
              </IconButton>
            </Box>
          )}
        </Box>
      </Menu>
    </Box>
  )
}

const gradeLabelMap: any = {
  A: { label: 'A', color: '#10b981' },
  B: { label: 'B', color: '#3b82f6' },
  C: { label: 'C', color: '#f59e0b' },
  D: { label: 'D', color: '#6b7280' },
}
const countryFlag = (country?: string) => {
  const map: any = { USA: '🇺🇸', UK: '🇬🇧', Germany: '🇩🇪', France: '🇫🇷', China: '🇨🇳' }
  return map[country || ''] ? `${map[country!]} ${country}` : country || '-'
}

const RowActions = ({ record, onViewProfile }: any) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const notify = useNotify()
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation()
    setAnchorEl(event.currentTarget)
  }
  const handleClose = () => setAnchorEl(null)
  
  const handleEdit = () => {
    window.location.href = `#/customers/${record.id}`
    handleClose()
  }
  
  const handleViewProfile = () => {
    onViewProfile(record)
    handleClose()
  }
  
  const handleFollowup = () => {
    notify(`为客户 ${record?.company_name} 创建跟进`, { type: 'info' })
    handleClose()
  }
  
  const handleEmail = () => {
    notify(`向 ${record?.email} 发送邮件`, { type: 'info' })
    handleClose()
  }
  
  const handleDelete = async () => {
    if (window.confirm(`确定要删除客户 "${record?.company_name}" 吗？`)) {
      try {
        const res = await fetch(getApiUrl('crm', `/customers/${record.id}`), {
          method: 'DELETE'
        })
        if (res.ok) {
          notify('客户已删除', { type: 'success' })
          window.location.reload()  // 刷新页面
        } else {
          notify('删除失败', { type: 'error' })
        }
      } catch (e) {
        notify('网络错误', { type: 'error' })
      }
    }
    handleClose()
  }
  
  return (
    <>
      <IconButton size="small" onClick={handleClick}>
        <MoreVertIcon fontSize="small" />
      </IconButton>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        <MenuItem onClick={handleViewProfile}>
          <AnalyticsIcon fontSize="small" sx={{mr:1}} /> 查看画像
        </MenuItem>
        <MenuItem onClick={handleEdit}>
          <EditIcon fontSize="small" sx={{mr:1}} /> 编辑客户
        </MenuItem>
        <MenuItem onClick={handleFollowup}>
          <PhoneIcon fontSize="small" sx={{mr:1}} /> 跟进
        </MenuItem>
        <MenuItem onClick={handleEmail}>
          <EmailIcon fontSize="small" sx={{mr:1}} /> 发邮件
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDelete} sx={{ color: '#ef4444' }}>
          <DeleteIcon fontSize="small" sx={{mr:1}} /> 删除
        </MenuItem>
      </Menu>
    </>
  )
}

const customerFilters = [
  <TextInput key="search" label="搜索" source="search" alwaysOn />, 
  <SelectInput key="status" label="阶段" source="status" choices={[
    { id: 'cold', name: '冷源客户' },
    { id: 'contacted', name: '已联系' },
    { id: 'replied', name: '已回复' },
    { id: 'qualified', name: '合格线索' },
    { id: 'negotiating', name: '谈判中' },
    { id: 'customer', name: '成交客户' },
    { id: 'lost', name: '已流失' },
  ]} />,
  <TextInput key="country" label="国家地区" source="country" />,
  <SelectInput key="customer_grade" label="客户等级" source="customer_grade" choices={[
    { id: 'A', name: 'A' },
    { id: 'B', name: 'B' },
    { id: 'C', name: 'C' },
    { id: 'D', name: 'D' },
  ]} />
]

const CustomerListActions = ({ setFieldSettingsOpen, setFilterOpen, onGradeAll }: any) => (
  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
    <Button
      startIcon={<GradeIcon />}
      onClick={onGradeAll}
      variant="outlined"
      size="small"
      sx={{ textTransform: 'none' }}
    >
      批量分级
    </Button>
    
    <IconButton 
      onClick={() => setFilterOpen(true)} 
      sx={{ 
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
        width: '40px',
        height: '40px'
      }}
    >
      <FilterListIcon />
    </IconButton>
    
    <IconButton 
      onClick={() => setFieldSettingsOpen(true)} 
      sx={{ 
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
        width: '40px',
        height: '40px'
      }}
    >
      <SettingsIcon />
    </IconButton>
  </Box>
)

// 带固定顶部栏的客户列表包装组件
const CustomerListWithFixedHeader = (props: any) => {
  const { visibleFields, renderFieldColumn, totalCount, searchText, setSearchText, searchField, setSearchField, handleKeyPress, setFilterOpen, filterOpen, setFieldSettingsOpen, setCreateOpen, refresh, onGradeAll, onViewProfile } = props
  
  return (
    <Box sx={{
      position: 'fixed',
      top: 64,
      left: 240,
      right: 0,
      bottom: 0,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      backgroundColor: 'white'
    }}>
      {/* 固定的顶部栏：全部客户数量 + 搜索和操作按钮 */}
      <Box sx={{ 
        flexShrink: 0,
        backgroundColor: 'white',
        zIndex: 100,
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        px: 2, 
        py: 1.5,
        borderBottom: '1px solid #e0e0e0',
      }}>
        {/* 左侧：全部客户数量 */}
        <Typography variant="body2" color="text.secondary">
          全部客户  <Typography component="span" variant="body2" sx={{ color: '#1976d2', fontWeight: 600 }}>{totalCount.toLocaleString()}</Typography> 个客户
        </Typography>
        
        {/* 右侧：批量分级按钮 + 筛选下拉框 + 搜索框 + 按钮组 */}
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', height: '36px' }}>
          {/* 批量分级按钮 */}
          <Button
            startIcon={<GradeIcon />}
            onClick={onGradeAll}
            variant="outlined"
            size="small"
            sx={{ 
              height: '36px',
              textTransform: 'none',
              borderColor: '#d0d0d0'
            }}
          >
            批量分级
          </Button>
          {/* 筛选字段下拉框 */}
          <TextField
            select
            size="small"
            value={searchField}
            onChange={(e) => setSearchField(e.target.value)}
            sx={{ 
              minWidth: '120px',
              height: '36px',
              '& .MuiOutlinedInput-root': { 
                height: '36px',
                backgroundColor: 'transparent'
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#d0d0d0'
              },
              '& .MuiSelect-select': {
                paddingTop: '8px',
                paddingBottom: '8px',
                lineHeight: '20px',
                display: 'flex',
                alignItems: 'center',
                height: '36px',
                boxSizing: 'border-box'
              }
            }}
          >
            <MenuItem value="company_name">公司名称</MenuItem>
            <MenuItem value="contact_name">联系人</MenuItem>
            <MenuItem value="email">邮箱</MenuItem>
            <MenuItem value="country">国家地区</MenuItem>
          </TextField>
          
          {/* 搜索框 */}
          <TextField
            size="small"
            placeholder="请输入"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{ 
              minWidth: '200px',
              height: '36px',
              '& .MuiOutlinedInput-root': { 
                height: '36px',
                backgroundColor: 'transparent'
              },
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#d0d0d0'
              },
              '& .MuiInputBase-input': {
                paddingTop: '8px',
                paddingBottom: '8px',
                lineHeight: '20px',
                height: '36px',
                boxSizing: 'border-box'
              }
            }}
          />
          
          {/* 筛选按钮 */}
          <IconButton 
            onClick={() => setFilterOpen(!filterOpen)} 
            sx={{ 
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              width: '36px',
              height: '36px',
              padding: 0,
              backgroundColor: 'transparent',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              '&:hover': {
                backgroundColor: '#f5f5f5'
              }
            }}
          >
            <FilterListIcon fontSize="small" />
          </IconButton>
          
          {/* 自定义字段按钮 */}
          <IconButton 
            onClick={() => setFieldSettingsOpen(true)} 
            sx={{ 
              border: '1px solid #d0d0d0',
              borderRadius: '4px',
              width: '36px',
              height: '36px',
              padding: 0,
              backgroundColor: 'transparent',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              '&:hover': {
                backgroundColor: '#f5f5f5'
              }
            }}
          >
            <SettingsIcon fontSize="small" />
          </IconButton>
          
          {/* 新建客户按钮 */}
          <Button 
            variant="contained" 
            onClick={() => setCreateOpen(true)}
            sx={{ 
              height: '36px',
              minHeight: '36px',
              lineHeight: '36px',
              padding: '0 16px',
              textTransform: 'none',
              boxShadow: 'none',
              display: 'flex',
              alignItems: 'center',
              '&:hover': {
                boxShadow: 'none'
              }
            }}
          >
            + 新建客户
          </Button>
        </Box>
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
        },
        // 隐藏React Admin默认的翻页组件
        '& .RaList-content > .MuiToolbar-root': {
          display: 'none'
        }
      }}>
        <Datagrid
          rowClick={false}
          bulkActionButtons={<BulkActionButtons />}
          sx={{
            '& .RaDatagrid-headerCell': { fontWeight: 600, backgroundColor: '#f9fafb' },
            '& .RaDatagrid-row': { '&:hover': { backgroundColor: '#f3f4f6' } }
          }}
        >
          {visibleFields.map((fieldName: string) => renderFieldColumn(fieldName))}
          <FunctionField label="操作" render={(record:any) => <RowActions record={record} onViewProfile={onViewProfile} />} />
        </Datagrid>
      </Box>
      
      {/* 底部翻页区域 */}
      <Box sx={{ 
        flexShrink: 0,
        borderTop: '1px solid #e0e0e0',
        backgroundColor: 'white',
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        px: 2,
        py: 1
      }}>
        <Pagination rowsPerPageOptions={[10, 20, 50, 100]} />
      </Box>
    </Box>
  )
}

// 批量打标签对话框
const BatchTagDialog = ({ open, onClose, selectedIds, onSuccess }: any) => {
  const [allTags, setAllTags] = useState<any[]>([])
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  useEffect(() => {
    if (open) {
      // 获取所有标签
      fetch(getApiUrl('crm', '/tags?range=[0,999]'))
        .then(r => r.json())
        .then(tags => setAllTags(tags))
        .catch(() => notify('获取标签失败', { type: 'error' }))
    }
  }, [open])

  const handleToggleTag = (tagId: number) => {
    setSelectedTags(prev => 
      prev.includes(tagId) ? prev.filter(id => id !== tagId) : [...prev, tagId]
    )
  }

  const handleAddTags = async () => {
    if (selectedTags.length === 0) {
      notify('请选择至少一个标签', { type: 'warning' })
      return
    }

    setLoading(true)
    try {
      const response = await fetch(getApiUrl('crm', '/tags/batch'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_ids: selectedIds,
          tag_ids: selectedTags,
          action: 'add'
        })
      })

      if (response.ok) {
        const result = await response.json()
        notify(`批量打标签成功：已为 ${result.customers_count} 个客户添加 ${result.tags_count} 个标签`, { type: 'success' })
        refresh()
        onSuccess()
        onClose()
      } else {
        notify('批量打标签失败', { type: 'error' })
      }
    } catch (error) {
      notify('批量打标签失败', { type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveTags = async () => {
    if (selectedTags.length === 0) {
      notify('请选择至少一个标签', { type: 'warning' })
      return
    }

    setLoading(true)
    try {
      const response = await fetch(getApiUrl('crm', '/tags/batch'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_ids: selectedIds,
          tag_ids: selectedTags,
          action: 'remove'
        })
      })

      if (response.ok) {
        const result = await response.json()
        notify(`批量移除标签成功：已为 ${result.customers_count} 个客户移除 ${result.tags_count} 个标签`, { type: 'success' })
        refresh()
        onSuccess()
        onClose()
      } else {
        notify('批量移除标签失败', { type: 'error' })
      }
    } catch (error) {
      notify('批量移除标签失败', { type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>批量打标签（已选择 {selectedIds.length} 个客户）</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            选择要添加或移除的标签：
          </Typography>
          {allTags.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              暂无标签，请先在标签管理中创建标签
            </Typography>
          ) : (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {allTags.map(tag => (
                <Chip
                  key={tag.id}
                  label={tag.name}
                  onClick={() => handleToggleTag(tag.id)}
                  sx={{
                    backgroundColor: selectedTags.includes(tag.id) ? tag.color : '#f5f5f5',
                    color: selectedTags.includes(tag.id) ? '#fff' : '#333',
                    fontWeight: 600,
                    cursor: 'pointer',
                    '&:hover': {
                      opacity: 0.8
                    }
                  }}
                />
              ))}
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={handleRemoveTags} disabled={loading || selectedTags.length === 0} color="warning">
          移除标签
        </Button>
        <Button onClick={handleAddTags} disabled={loading || selectedTags.length === 0} variant="contained">
          添加标签
        </Button>
      </DialogActions>
    </Dialog>
  )
}

const BulkActionButtons = () => {
  const { selectedIds } = useListContext()
  const [batchTagOpen, setBatchTagOpen] = useState(false)

  return (
    <>
      <Button
        startIcon={<LocalOfferIcon />}
        onClick={() => setBatchTagOpen(true)}
        disabled={selectedIds.length === 0}
        sx={{ mr: 1 }}
      >
        批量打标签
      </Button>
      <BulkDeleteButton />
      
      <BatchTagDialog
        open={batchTagOpen}
        onClose={() => setBatchTagOpen(false)}
        selectedIds={selectedIds}
        onSuccess={() => {}}
      />
    </>
  )
}

export const CustomerList = (props:any) => {
  const [createOpen, setCreateOpen] = useState(false)
  const [allCustomFieldNames, setAllCustomFieldNames] = useState<string[]>([])
  const [fieldSettingsOpen, setFieldSettingsOpen] = useState(false)
  const [filterOpen, setFilterOpen] = useState(false)
  const [totalCount, setTotalCount] = useState(0)
  const [searchText, setSearchText] = useState('')
  const [searchField, setSearchField] = useState('company_name')
  const [filterParams, setFilterParams] = useState<any>({})
  const [profileOpen, setProfileOpen] = useState(false)
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null)
  const notify = useNotify()
  const refresh = useRefresh()
  
  // 处理批量分级
  const handleGradeAll = async () => {
    try {
      const response = await fetch(getApiUrl('crm', '/grade-all'), {
        method: 'POST'
      })
      if (response.ok) {
        const result = await response.json()
        notify(`批量分级完成：${result.upgraded}个升级，${result.downgraded}个降级，${result.unchanged}个不变`, { type: 'success' })
        refresh()
      } else {
        notify('批量分级失败', { type: 'error' })
      }
    } catch (error) {
      notify('批量分级失败', { type: 'error' })
    }
  }
  
  // 处理查看客户画像
  const handleViewProfile = (customer: any) => {
    setSelectedCustomer(customer)
    setProfileOpen(true)
  }
  
  // 处理搜索
  const handleSearch = () => {
    if (searchText.trim()) {
      setFilterParams({ [searchField]: searchText })
    } else {
      setFilterParams({})
    }
  }
  
  // 搜索框回车键搜索
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }
  
  // 搜索文本变化时实时搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch()
    }, 500) // 防抖动500ms
    
    return () => clearTimeout(timer)
  }, [searchText, searchField])
  
  // 默认固定字段
  const defaultFields = [
    { name: 'company_name', label: '公司名称', type: 'fixed' },
    { name: 'status', label: '客户阶段', type: 'fixed' },
    { name: 'customer_grade', label: '客户等级', type: 'fixed' },
    { name: 'engagement_score', label: '参与度评分', type: 'fixed' },
    { name: 'contact_name', label: '联系人', type: 'fixed' },
    { name: 'email', label: '邮箱', type: 'fixed' },
    { name: 'country', label: '国家地区', type: 'fixed' },
    { name: 'tags', label: '标签', type: 'fixed' },
    { name: 'phone', label: '电话', type: 'fixed' },
    { name: 'website', label: '网站', type: 'fixed' },
  ]
  
  // 显示的字段（默认显示前7个）
  const [visibleFields, setVisibleFields] = useState<string[]>([
    'company_name', 'status', 'customer_grade', 'engagement_score', 'contact_name', 'email', 'country', 'website'
  ])
  
  // 自定义字段列表
  const [customFieldsList, setCustomFieldsList] = useState<string[]>([])
  
  // 加载时从数据库获取自定义字段定义
  useEffect(() => {
    // 重置页码到第一页
    const currentUrl = new URL(window.location.href)
    const hash = currentUrl.hash
    if (hash.includes('/customers') && hash.includes('page=')) {
      // 如果 URL 中有 page 参数，移除它
      const newHash = hash.replace(/[?&]page=\d+/, '').replace(/\?&/, '?')
      window.location.hash = newHash
    }
    
    // 获取自定义字段
    fetch(getApiUrl('crm', '/custom_fields?range=[0,999]'))
      .then(r => r.json())
      .then((fields: any[]) => {
        const fieldNames = fields
          .sort((a, b) => a.display_order - b.display_order)
          .map(f => f.field_name)
        setAllCustomFieldNames(fieldNames)
        setCustomFieldsList(fieldNames)
        
        // 自动添加可见字段到显示列表
        const visibleCustomFields = fields
          .filter(f => f.is_visible)
          .map(f => f.field_name)
        const defaultVisibleFields = [
          'company_name', 'status', 'customer_grade', 'engagement_score', 'contact_name', 'email', 'country', 'website'
        ]
        const allVisible = [...new Set([...defaultVisibleFields, ...visibleCustomFields])]
        
        // 从 localStorage 加载已保存的顺序
        const savedOrder = localStorage.getItem('customerFieldsOrder')
        if (savedOrder) {
          try {
            const parsedOrder = JSON.parse(savedOrder)
            // 过滤掉不存在的字段
            const systemFieldNames = defaultFields.map((f: any) => f.name)
            const allAvailableFields = [...systemFieldNames, ...fieldNames]
            const validOrder = parsedOrder.filter((f: string) => allAvailableFields.includes(f))
            // 添加新字段（不在已保存顺序中的）
            const newFields = allVisible.filter((f: string) => !validOrder.includes(f))
            const finalOrder = [...validOrder, ...newFields]
            setVisibleFields(finalOrder)
          } catch (e) {
            // 解析失败，使用默认顺序
            setVisibleFields(allVisible)
          }
        } else {
          // 没有保存的顺序，使用默认顺序
          setVisibleFields(allVisible)
        }
      })
      .catch(() => {})
    
    // 获取客户总数
    fetch(getApiUrl('crm', '/customers?range=[0,0]'))
      .then(r => {
        const contentRange = r.headers.get('Content-Range')
        if (contentRange) {
          const total = parseInt(contentRange.split('/')[1])
          setTotalCount(total)
        }
        return r.json()
      })
      .catch(() => {})
  }, [])
  
  const renderFieldColumn = (fieldName: string) => {
    const field = defaultFields.find(f => f.name === fieldName)
    
    if (fieldName === 'company_name') {
      return <FunctionField key={fieldName} label="公司名称" render={(record:any) => (
        <Box sx={{ fontWeight: 500 }}>{record?.company_name || '-'}</Box>
      )} />
    }
    if (fieldName === 'status') {
      return <FunctionField key={fieldName} label="客户阶段" render={(record:any) => (
        <EditableStageCell record={record} refresh={refresh} />
      )} />
    }
    if (fieldName === 'customer_grade') {
      return <FunctionField key={fieldName} label="客户等级" render={(record:any) => {
        const grade = gradeLabelMap[record?.customer_grade]
        return <Chip label={grade?.label || record?.customer_grade || '-'} size="small" sx={{ bgcolor: grade?.color, color: '#fff', fontWeight: 500 }} />
      }} />
    }
    if (fieldName === 'engagement_score') {
      return <FunctionField key={fieldName} label="参与度评分" render={(record:any) => {
        const score = record?.engagement_score || 0
        const color = score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#6b7280'
        return (
          <Box sx={{ width: '100%', maxWidth: 100 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <TrendingUpIcon sx={{ fontSize: 14, color }} />
              <Typography variant="caption" sx={{ color, fontWeight: 600 }}>{score.toFixed(0)}</Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={score} 
              sx={{ 
                height: 4, 
                borderRadius: 2,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': { 
                  backgroundColor: color 
                }
              }} 
            />
          </Box>
        )
      }} />
    }
    if (fieldName === 'country') {
      return <FunctionField key={fieldName} label="国家地区" render={(record:any) => countryFlag(record?.country)} />
    }
    if (fieldName === 'email') {
      return <EmailField key={fieldName} source="email" label="邮箱" />
    }
    if (fieldName === 'tags') {
      return <FunctionField key={fieldName} label="标签" render={(record:any) => (
        <EditableTagsCell record={record} refresh={refresh} />
      )} />
    }
    if (fieldName === 'website') {
      return <FunctionField key={fieldName} label="官网" render={(record:any) => {
        const website = record?.website
        if (!website) return <span style={{ color: '#999' }}>-</span>
        
        // 确保 URL有协议
        const url = website.startsWith('http://') || website.startsWith('https://') 
          ? website 
          : `https://${website}`
        
        return (
          <Box 
            component="a" 
            href={url} 
            target="_blank" 
            rel="noopener noreferrer"
            sx={{ 
              color: '#1677ff',
              textDecoration: 'none',
              cursor: 'pointer',
              '&:hover': {
                textDecoration: 'underline'
              }
            }}
            onClick={(e: any) => e.stopPropagation()}
          >
            点击查看
          </Box>
        )
      }} />
    }
    if (field) {
      return <RATextField key={fieldName} source={fieldName} label={field.label} />
    }
    
    // 自定义字段
    return <FunctionField key={fieldName} label={fieldName} render={(record:any) => {
      if (!record?.custom_fields) return '-'
      try {
        const fields = JSON.parse(record.custom_fields)
        return fields[fieldName] || '-'
      } catch (e) {
        return '-'
      }
    }} />
  }
  
  return (
    <Box>
      <List 
        {...props} 
        perPage={20} 
        filters={[]} 
        actions={false}
        title={false}
        filterDefaultValues={filterParams}
        filter={filterParams}
        pagination={false}
        sort={{ field: 'id', order: 'DESC' }}
        disableSyncWithLocation
      >
        <CustomerListWithFixedHeader 
          visibleFields={visibleFields}
          renderFieldColumn={renderFieldColumn}
          totalCount={totalCount}
          searchText={searchText}
          setSearchText={setSearchText}
          searchField={searchField}
          setSearchField={setSearchField}
          handleKeyPress={handleKeyPress}
          setFilterOpen={setFilterOpen}
          filterOpen={filterOpen}
          setFieldSettingsOpen={setFieldSettingsOpen}
          setCreateOpen={setCreateOpen}
          refresh={refresh}
          onGradeAll={handleGradeAll}
          onViewProfile={handleViewProfile}
        />
      </List>
      <CreateDrawer open={createOpen} onClose={() => setCreateOpen(false)} />
      <CustomerProfileDrawer 
        open={profileOpen} 
        onClose={() => setProfileOpen(false)}
        customer={selectedCustomer}
      />
      <FieldSettingsDialog 
        open={fieldSettingsOpen} 
        onClose={() => setFieldSettingsOpen(false)}
        defaultFields={defaultFields}
        customFields={customFieldsList}
        visibleFields={visibleFields}
        setVisibleFields={setVisibleFields}
        setCustomFieldsList={setCustomFieldsList}
      />
    </Box>
  )
}

const FieldSettingsDialog = ({ open, onClose, defaultFields, customFields, visibleFields, setVisibleFields, setCustomFieldsList }: any) => {
  const [newFieldName, setNewFieldName] = useState('')
  const notify = useNotify()
  const refresh = useRefresh()
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [allFieldsOrder, setAllFieldsOrder] = useState<string[]>([])
  
  // 加载时从数据库获取自定义字段定义
  useEffect(() => {
    if (open) {
      fetch(getApiUrl('crm', '/custom_fields?range=[0,999]'))
        .then(r => r.json())
        .then((fields: any[]) => {
          const fieldNames = fields
            .sort((a, b) => a.display_order - b.display_order)
            .map(f => f.field_name)
          setCustomFieldsList(fieldNames)
          
          // 自动添加可见字段到显示列表
          const visibleCustomFields = fields
            .filter(f => f.is_visible)
            .map(f => f.field_name)
          const newVisibleFields = [...new Set([...visibleFields, ...visibleCustomFields])]
          setVisibleFields(newVisibleFields)
          
          // 从 localStorage 加载已保存的顺序
          const savedOrder = localStorage.getItem('customerFieldsOrder')
          if (savedOrder) {
            try {
              const parsedOrder = JSON.parse(savedOrder)
              // 过滤掉不存在的字段，添加新字段
              const systemFieldNames = defaultFields.map((f: any) => f.name)
              const allAvailableFields = [...systemFieldNames, ...fieldNames]
              const validOrder = parsedOrder.filter((f: string) => allAvailableFields.includes(f))
              // 添加新字段（不在已保存顺序中的）
              const newFields = newVisibleFields.filter((f: string) => !validOrder.includes(f))
              const finalOrder = [...validOrder, ...newFields]
              setAllFieldsOrder(finalOrder)
            } catch (e) {
              // 解析失败，使用默认顺序
              setAllFieldsOrder(newVisibleFields)
            }
          } else {
            // 没有保存的顺序，使用默认顺序
            setAllFieldsOrder(newVisibleFields)
          }
        })
        .catch(() => {})
    }
  }, [open])
  
  // 拖拽开始
  const handleDragStart = (index: number) => {
    setDraggedIndex(index)
  }
  
  // 拖拽结束
  const handleDragEnd = () => {
    setDraggedIndex(null)
    // 更新 visibleFields 为新顺序
    setVisibleFields([...allFieldsOrder])
    // 保存顺序到 localStorage
    localStorage.setItem('customerFieldsOrder', JSON.stringify(allFieldsOrder))
    notify('字段顺序已保存', { type: 'success' })
  }
  
  // 拖拽过程中
  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggedIndex === null || draggedIndex === index) return
    
    const newOrder = [...allFieldsOrder]
    const draggedItem = newOrder[draggedIndex]
    newOrder.splice(draggedIndex, 1)
    newOrder.splice(index, 0, draggedItem)
    
    setAllFieldsOrder(newOrder)
    setDraggedIndex(index)
  }
  
  const toggleField = (fieldName: string) => {
    if (visibleFields.includes(fieldName)) {
      // 取消选中：从 visibleFields 和 allFieldsOrder 中移除
      setVisibleFields(visibleFields.filter((f: string) => f !== fieldName))
      setAllFieldsOrder(allFieldsOrder.filter((f: string) => f !== fieldName))
      // 更新数据库中的可见性
      updateFieldVisibility(fieldName, false)
    } else {
      // 选中：添加到 visibleFields 和 allFieldsOrder 末尾
      setVisibleFields([...visibleFields, fieldName])
      setAllFieldsOrder([...allFieldsOrder, fieldName])
      // 更新数据库中的可见性
      updateFieldVisibility(fieldName, true)
    }
  }
  
  const updateFieldVisibility = async (fieldName: string, isVisible: boolean) => {
    // 只更新自定义字段，系统字段不存入数据库
    if (defaultFields.some((f: any) => f.name === fieldName)) return
    
    try {
      const res = await fetch(getApiUrl('crm', '/custom_fields?range=[0,999]'))
      const fields = await res.json()
      const field = fields.find((f: any) => f.field_name === fieldName)
      
      if (field) {
        await fetch(getApiUrl('crm', `/custom_fields/${field.id}`), {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_visible: isVisible })
        })
      }
    } catch (e) {}
  }
  
  const addNewCustomField = async () => {
    if (!newFieldName.trim()) {
      notify('请输入字段名称', { type: 'warning' })
      return
    }
    if (defaultFields.some((f: any) => f.name === newFieldName)) {
      notify('字段名已存在于系统字段中', { type: 'warning' })
      return
    }
    if (customFields.includes(newFieldName)) {
      notify('字段名已存在', { type: 'warning' })
      return
    }
    
    try {
      const res = await fetch(getApiUrl('crm', '/custom_fields'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_name: newFieldName,
          field_type: 'text',
          is_visible: true,
          display_order: customFields.length
        })
      })
      
      if (res.ok) {
        setCustomFieldsList([...customFields, newFieldName])
        setVisibleFields([...visibleFields, newFieldName])
        setNewFieldName('')
        notify(`自定义字段 "${newFieldName}" 已添加`, { type: 'success' })
        refresh()
      } else {
        const error = await res.json()
        notify(error.detail || '添加失败', { type: 'error' })
      }
    } catch (e) {
      notify('网络错误', { type: 'error' })
    }
  }
  
  const removeCustomField = async (fieldName: string) => {
    try {
      const res = await fetch(getApiUrl('crm', '/custom_fields?range=[0,999]'))
      const fields = await res.json()
      const field = fields.find((f: any) => f.field_name === fieldName)
      
      if (field) {
        const deleteRes = await fetch(getApiUrl('crm', `/custom_fields/${field.id}`), {
          method: 'DELETE'
        })
        
        if (deleteRes.ok) {
          setCustomFieldsList(customFields.filter((f: string) => f !== fieldName))
          setVisibleFields(visibleFields.filter((f: string) => f !== fieldName))
          notify(`字段 "${fieldName}" 已删除`, { type: 'info' })
          refresh()
        }
      }
    } catch (e) {
      notify('删除失败', { type: 'error' })
    }
  }
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">字段管理</Typography>
          <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ display: 'flex', gap: 3 }}>
          {/* 左侧：字段选择区 */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>系统字段</Typography>
            <Box sx={{ mb: 3 }}>
              {defaultFields.map((field: any) => (
                <FormControlLabel
                  key={field.name}
                  control={
                    <Checkbox 
                      checked={visibleFields.includes(field.name)}
                      onChange={() => toggleField(field.name)}
                    />
                  }
                  label={field.label}
                />
              ))}
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>自定义字段</Typography>
            <Box sx={{ mb: 2 }}>
              {customFields.length === 0 && (
                <Typography variant="body2" color="text.secondary">暂无自定义字段</Typography>
              )}
              {customFields.map((fieldName: string) => (
                <Box key={fieldName} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <FormControlLabel
                    control={
                      <Checkbox 
                        checked={visibleFields.includes(fieldName)}
                        onChange={() => toggleField(fieldName)}
                      />
                    }
                    label={fieldName}
                  />
                  <IconButton size="small" onClick={() => removeCustomField(fieldName)} color="error">
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Box>
              ))}
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>添加新字段</Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
              <TextField 
                size="small" 
                label="字段名称" 
                value={newFieldName} 
                onChange={(e:any) => setNewFieldName(e.target.value)}
                onKeyDown={(e:any) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addNewCustomField()
                  }
                }}
                placeholder="请输入字段名称"
                sx={{ flexGrow: 1 }}
              />
              <Button variant="contained" onClick={addNewCustomField} sx={{ minWidth: '80px', height: '40px' }}>+ 添加</Button>
            </Box>
          </Box>
          
          {/* 右侧：字段顺序调整区 */}
          <Box sx={{ flex: 1, borderLeft: '1px solid #e0e0e0', pl: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
              字段显示顺序
              <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                (拖动调整顺序)
              </Typography>
            </Typography>
            
            {allFieldsOrder.length === 0 ? (
              <Typography variant="body2" color="text.secondary">请先选择要显示的字段</Typography>
            ) : (
              <Box>
                {allFieldsOrder.map((fieldName, index) => {
                  const field = defaultFields.find((f: any) => f.name === fieldName)
                  const displayName = field ? field.label : fieldName
                  
                  return (
                    <Box
                      key={fieldName}
                      draggable
                      onDragStart={() => handleDragStart(index)}
                      onDragEnd={handleDragEnd}
                      onDragOver={(e) => handleDragOver(e, index)}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        p: 1.5,
                        mb: 1,
                        border: '1px solid #e0e0e0',
                        borderRadius: '4px',
                        backgroundColor: draggedIndex === index ? '#f0f0f0' : '#fff',
                        cursor: 'grab',
                        '&:active': {
                          cursor: 'grabbing'
                        },
                        '&:hover': {
                          backgroundColor: '#f9f9f9',
                          borderColor: '#1976d2'
                        },
                        transition: 'all 0.2s'
                      }}
                    >
                      <DragIndicatorIcon sx={{ color: '#999', fontSize: '20px' }} />
                      <Typography sx={{ flex: 1, fontWeight: 500 }}>
                        {index + 1}. {displayName}
                      </Typography>
                      <Chip 
                        label={field ? '系统' : '自定义'} 
                        size="small" 
                        sx={{ 
                          fontSize: '11px',
                          height: '20px',
                          backgroundColor: field ? '#e3f2fd' : '#fff3e0',
                          color: field ? '#1976d2' : '#f57c00'
                        }} 
                      />
                    </Box>
                  )
                })}
              </Box>
            )}
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">完成</Button>
      </DialogActions>
    </Dialog>
  )
}

const CreateDrawer = ({ open, onClose }: any) => {
  const notify = useNotify()
  const refresh = useRefresh()
  const [formData, setFormData] = useState<any>({})
  const [customFieldsValues, setCustomFieldsValues] = useState<any>({})
  const [availableCustomFields, setAvailableCustomFields] = useState<string[]>([])
  const [newFieldName, setNewFieldName] = useState('')
  
  // 加载时获取已有的自定义字段列表
  useEffect(() => {
    if (open) {
      fetch(getApiUrl('crm', '/customers?range=[0,999]'))
        .then(r => r.json())
        .then((customers: any[]) => {
          const fieldNamesSet = new Set<string>()
          customers.forEach(c => {
            if (c.custom_fields) {
              try {
                const fields = JSON.parse(c.custom_fields)
                Object.keys(fields).forEach(key => fieldNamesSet.add(key))
              } catch (e) {}
            }
          })
          setAvailableCustomFields(Array.from(fieldNamesSet))
        })
        .catch(() => {})
    }
  }, [open])
  
  const addCustomField = () => {
    if (newFieldName.trim()) {
      if (availableCustomFields.includes(newFieldName)) {
        notify('字段已存在，请直接填写值', { type: 'warning' })
        setNewFieldName('')
        return
      }
      setAvailableCustomFields([...availableCustomFields, newFieldName])
      setCustomFieldsValues({ ...customFieldsValues, [newFieldName]: '' })
      setNewFieldName('')
    }
  }
  
  const updateCustomFieldValue = (fieldName: string, value: string) => {
    setCustomFieldsValues({ ...customFieldsValues, [fieldName]: value })
  }
  
  const removeCustomField = (fieldName: string) => {
    const updated = { ...customFieldsValues }
    delete updated[fieldName]
    setCustomFieldsValues(updated)
  }
  
  const handleSubmit = async () => {
    // 验证必填字段
    if (!formData.company_name || !formData.company_name.trim()) {
      notify('请填写公司名称', { type: 'warning' })
      return
    }
    
    try {
      const customFieldsObj: any = {}
      Object.keys(customFieldsValues).forEach(key => {
        if (customFieldsValues[key]) {
          customFieldsObj[key] = customFieldsValues[key]
        }
      })
      const payload = {
        ...formData,
        custom_fields: Object.keys(customFieldsObj).length > 0 ? JSON.stringify(customFieldsObj) : null
      }
      
      console.log('发送客户数据:', payload)
      
      const res = await fetch(getApiUrl('crm', '/customers'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (res.ok) {
        notify('客户创建成功', { type: 'success' })
        onClose()
        refresh()
        setFormData({})
        setCustomFieldsValues({})
      } else {
        const errorData = await res.json().catch(() => ({}))
        console.error('API错误:', errorData)
        notify(errorData.detail || `创建失败 (${res.status})`, { type: 'error' })
      }
    } catch (e: any) {
      console.error('网络错误:', e)
      notify(`网络错误: ${e.message || '无法连接到服务器'}`, { type: 'error' })
    }
  }
  
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 500, p: 3, height: '100vh', overflow: 'auto' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">新建客户</Typography>
          <IconButton onClick={onClose}><CloseIcon /></IconButton>
        </Box>
        <Box sx={{ '& > *': { mb: 2 } }}>
          <TextField fullWidth label="公司名称" value={formData.company_name || ''} onChange={(e:any) => setFormData({...formData, company_name: e.target.value})} />
          <TextField fullWidth label="联系人" value={formData.contact_name || ''} onChange={(e:any) => setFormData({...formData, contact_name: e.target.value})} />
          <TextField fullWidth label="邮箱" value={formData.email || ''} onChange={(e:any) => setFormData({...formData, email: e.target.value})} />
          <TextField fullWidth label="电话" value={formData.phone || ''} onChange={(e:any) => setFormData({...formData, phone: e.target.value})} />
          <TextField fullWidth label="国家" value={formData.country || ''} onChange={(e:any) => setFormData({...formData, country: e.target.value})} />
          <TextField fullWidth label="官网" value={formData.website || ''} onChange={(e:any) => setFormData({...formData, website: e.target.value})} />
        </Box>
        
        <Box sx={{ mt: 3, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>自定义字段</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
            从已有字段中选择或添加新字段
          </Typography>
          
          {availableCustomFields.map((fieldName) => (
            <Box key={fieldName} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
              <TextField 
                size="small" 
                label={fieldName}
                value={customFieldsValues[fieldName] || ''} 
                onChange={(e:any) => updateCustomFieldValue(fieldName, e.target.value)} 
                sx={{ flex: 1 }} 
              />
              <IconButton size="small" onClick={() => removeCustomField(fieldName)} color="error">
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          ))}
          
          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
            <TextField size="small" label="新字段名" value={newFieldName} onChange={(e:any) => setNewFieldName(e.target.value)} sx={{ flex: 1 }} />
            <Button variant="outlined" size="small" onClick={addCustomField}>+ 添加</Button>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
          <Button variant="outlined" onClick={onClose} fullWidth>取消</Button>
          <Button variant="contained" onClick={handleSubmit} fullWidth>保存</Button>
        </Box>
      </Box>
    </Drawer>
  )
}

export const CustomerCreate = (props:any) => (
  <Create {...props}>
    <TabbedForm>
      <FormTab label="基本信息">
        <TextInput source="company_name" label="公司名称" fullWidth />
        <TextInput source="contact_name" label="联系人" />
        <TextInput source="email" label="邮箱" />
        <TextInput source="phone" label="电话" />
        <TextInput source="country" label="国家地区" />
        <SelectInput source="status" label="阶段" choices={[
          { id: 'cold', name: '冷源客户' },
          { id: 'contacted', name: '已联系' },
          { id: 'replied', name: '已回复' },
          { id: 'qualified', name: '合格线索' },
          { id: 'negotiating', name: '谈判中' },
          { id: 'customer', name: '成交客户' },
          { id: 'lost', name: '已流失' },
        ]} />
        <SelectInput source="customer_grade" label="客户等级" choices={[
          { id: 'A', name: 'A' },
          { id: 'B', name: 'B' },
          { id: 'C', name: 'C' },
          { id: 'D', name: 'D' },
        ]} />
      </FormTab>
      <FormTab label="社交">
        <TextInput source="website" label="网站" />
        <TextInput source="source" label="客户来源" />
        <TextInput source="linkedin_url" label="LinkedIn" />
        <TextInput source="facebook_url" label="Facebook" />
        <TextInput source="tags" label="客户标签（逗号分隔）" fullWidth />
      </FormTab>
      <FormTab label="备注">
        <TextInput source="last_followup_note" label="备注" multiline fullWidth />
      </FormTab>
    </TabbedForm>
  </Create>
)

const AnalyticsAside = () => {
  const record = useRecordContext();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    if (record?.id) {
      fetch(getApiUrl('crm', `/customers/${record.id}/analytics`))
        .then(r => r.json())
        .then(setData)
        .catch(() => setData(null));
    }
  }, [record]);
  return (
    <Box sx={{ width: 320, ml: 2 }}>
      <Card>
        <CardContent>
          <Typography variant="h6">客户分析</Typography>
          <Typography>CLV: {data?.clv ?? '-'}</Typography>
          <Typography>健康度: {data?.health_score ?? '-'}</Typography>
          <Typography>流失风险: {data?.churn_risk ?? '-'}</Typography>
          <Typography>建议行动: {data?.next_action ?? '-'}</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

// 客户编辑页面的顶部操作栏
const CustomerEditActions = () => (
  <TopToolbar>
    <Button
      startIcon={<ArrowBackIcon />}
      onClick={() => window.location.href = '#/customers'}
      variant="outlined"
      size="medium"
      sx={{ 
        textTransform: 'none',
        borderColor: '#1976d2',
        color: '#1976d2',
        '&:hover': {
          borderColor: '#1565c0',
          backgroundColor: '#e3f2fd'
        }
      }}
    >
      返回列表
    </Button>
  </TopToolbar>
)

export const CustomerEdit = (props:any) => (
  <Edit {...props} aside={<AnalyticsAside />} actions={false}>
    {/* 自定义标题栏，包含返回按钮 */}
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, px: 2, pt: 2 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => window.location.href = '#/customers'}
        variant="outlined"
        size="medium"
        sx={{ 
          textTransform: 'none',
          borderColor: '#1976d2',
          color: '#1976d2',
          '&:hover': {
            borderColor: '#1565c0',
            backgroundColor: '#e3f2fd'
          }
        }}
      >
        返回列表
      </Button>
      <Typography variant="h5" sx={{ fontWeight: 500 }}>编辑客户</Typography>
    </Box>
    
    <TabbedForm>
      <FormTab label="基本信息">
        <TextInput source="company_name" label="公司名称" fullWidth />
        <TextInput source="contact_name" label="联系人" />
        <TextInput source="email" label="邮箱" />
        <TextInput source="phone" label="电话" />
        <TextInput source="country" label="国家地区" />
        <SelectInput source="status" label="阶段" choices={[
          { id: 'cold', name: '冷源客户' },
          { id: 'contacted', name: '已联系' },
          { id: 'replied', name: '已回复' },
          { id: 'qualified', name: '合格线索' },
          { id: 'negotiating', name: '谈判中' },
          { id: 'customer', name: '成交客户' },
          { id: 'lost', name: '已流失' },
        ]} />
        <SelectInput source="customer_grade" label="客户等级" choices={[
          { id: 'A', name: 'A' },
          { id: 'B', name: 'B' },
          { id: 'C', name: 'C' },
          { id: 'D', name: 'D' },
        ]} />
      </FormTab>
      <FormTab label="社交">
        <TextInput source="website" label="网站" />
        <TextInput source="source" label="客户来源" />
        <TextInput source="linkedin_url" label="LinkedIn" />
        <TextInput source="facebook_url" label="Facebook" />
        <TextInput source="tags" label="客户标签（逗号分隔）" fullWidth />
      </FormTab>
      <FormTab label="备注">
        <TextInput source="last_followup_note" label="备注" multiline fullWidth />
      </FormTab>
      <FormTab label="关联">
        <ReferenceManyField label="订单" reference="orders" target="customer_id">
          <Datagrid>
            <RATextField source="order_number" label="订单号" />
            <RATextField source="status" label="状态" />
            <RATextField source="total_amount" label="金额" />
          </Datagrid>
        </ReferenceManyField>
        <ReferenceManyField label="邮件动态" reference="email_history" target="customer_id">
          <Datagrid>
            <RATextField source="direction" label="方向" />
            <RATextField source="subject" label="主题" />
            <RATextField source="sent_at" label="时间" />
          </Datagrid>
        </ReferenceManyField>
      </FormTab>
    </TabbedForm>
  </Edit>
)

// 客户画像抽屉组件
const CustomerProfileDrawer = ({ open, onClose, customer }: any) => {
  const [profileData, setProfileData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    if (open && customer?.id) {
      setLoading(true)
      console.log('Fetching customer profile for ID:', customer.id)
      fetch(getApiUrl('crm', `/${customer.id}/profile`))
        .then(r => {
          console.log('Profile API response status:', r.status)
          return r.json()
        })
        .then(data => {
          console.log('Profile data:', data)
          setProfileData(data)
          setLoading(false)
        })
        .catch(error => {
          console.error('Failed to fetch profile:', error)
          setLoading(false)
        })
    }
  }, [open, customer])
  
  if (!customer) return null
  
  const grade = gradeLabelMap[profileData?.grading?.grade || 'D']
  const score = profileData?.grading?.engagement_score || 0
  const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#6b7280'
  
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 500, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* 头部 */}
        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>客户画像</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        
        {/* 内容 */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <Typography>加载中...</Typography>
            </Box>
          ) : profileData ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* 基本信息 */}
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#666' }}>基本信息</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box><Typography variant="body2" color="text.secondary">公司名称：</Typography><Typography variant="body2" sx={{ fontWeight: 500 }}>{profileData.basic_info.company_name}</Typography></Box>
                    <Box><Typography variant="body2" color="text.secondary">联系人：</Typography><Typography variant="body2">{profileData.basic_info.contact_name || '-'}</Typography></Box>
                    <Box><Typography variant="body2" color="text.secondary">邮箱：</Typography><Typography variant="body2">{profileData.basic_info.email || '-'}</Typography></Box>
                    <Box><Typography variant="body2" color="text.secondary">国家：</Typography><Typography variant="body2">{profileData.basic_info.country || '-'}</Typography></Box>
                  </Box>
                </CardContent>
              </Card>
              
              {/* 分级情况 */}
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#666' }}>分级情况</Typography>
                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">客户等级</Typography>
                      <Chip label={grade?.label || '-'} size="medium" sx={{ bgcolor: grade?.color, color: '#fff', fontWeight: 600, mt: 0.5 }} />
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="caption" color="text.secondary">参与度评分</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Box sx={{ flex: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={score} 
                            sx={{ 
                              height: 8, 
                              borderRadius: 4,
                              backgroundColor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': { 
                                backgroundColor: scoreColor 
                              }
                            }} 
                          />
                        </Box>
                        <Typography variant="body2" sx={{ color: scoreColor, fontWeight: 600, minWidth: 35 }}>{score.toFixed(0)}</Typography>
                      </Box>
                    </Box>
                  </Box>
                  {profileData.grading.grading_reason && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      分级理由：{profileData.grading.grading_reason}
                    </Typography>
                  )}
                </CardContent>
              </Card>
              
              {/* 行为统计 */}
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#666' }}>行为统计</Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">发送邮件</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>{profileData.statistics.email_sent}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">接收邮件</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>{profileData.statistics.email_received}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">邮件回复</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>{profileData.statistics.email_reply}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">订单数量</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>{profileData.statistics.order_count}</Typography>
                    </Box>
                    <Box sx={{ gridColumn: 'span 2' }}>
                      <Typography variant="caption" color="text.secondary">总订单金额</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>${profileData.statistics.total_amount.toFixed(2)}</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
              
              {/* 活跃度 */}
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#666' }}>活跃度</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box><Typography variant="body2" color="text.secondary">最后活跃：</Typography><Typography variant="body2">{profileData.activity.last_active || '-'}</Typography></Box>
                    <Box><Typography variant="body2" color="text.secondary">距上次联系：</Typography><Typography variant="body2">{profileData.activity.days_since_contact}天</Typography></Box>
                    <Box><Typography variant="body2" color="text.secondary">成为客户：</Typography><Typography variant="body2">{profileData.activity.days_as_customer}天</Typography></Box>
                  </Box>
                </CardContent>
              </Card>
              
              {/* 价值评估 */}
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: '#666' }}>价值评估</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box><Typography variant="body2" color="text.secondary">年采购额：</Typography><Typography variant="body2" sx={{ fontWeight: 600 }}>${profileData.value.actual_annual_value?.toFixed(2) || '0.00'}</Typography></Box>
                    <Box><Typography variant="body2" color="text.secondary">生命周期价值：</Typography><Typography variant="body2" sx={{ fontWeight: 600 }}>${profileData.value.lifetime_value?.toFixed(2) || '0.00'}</Typography></Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <Typography color="text.secondary">无数据</Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  )
}
