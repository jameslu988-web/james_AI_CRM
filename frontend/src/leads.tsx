import { useState, useEffect } from 'react'
import { 
  List, 
  Datagrid, 
  TextField, 
  EmailField, 
  FunctionField,
  Create,
  Edit,
  SimpleForm,
  TextInput,
  SelectInput,
  NumberInput,
  DateTimeInput,
  Button as RAButton,
  useNotify,
  useRefresh,
  useRecordContext,
  BulkDeleteButton
} from 'react-admin'
import { 
  Box, 
  Chip, 
  Button, 
  IconButton,
  LinearProgress,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import StarIcon from '@mui/icons-material/Star'
import StarBorderIcon from '@mui/icons-material/StarBorder'
import StarHalfIcon from '@mui/icons-material/StarHalf'
import TransformIcon from '@mui/icons-material/Transform'
import EditIcon from '@mui/icons-material/Edit'

// 线索状态映射
const leadStatusMap: any = {
  new: { label: '新线索', color: '#3b82f6' },
  contacted: { label: '已联系', color: '#8b5cf6' },
  in_progress: { label: '跟进中', color: '#f59e0b' },
  qualified: { label: '合格', color: '#10b981' },
  unqualified: { label: '不合格', color: '#6b7280' },
  converted: { label: '已转化', color: '#059669' }
}

// 优先级映射
const priorityMap: any = {
  high: { label: '高', color: '#ef4444' },
  medium: { label: '中', color: '#f59e0b' },
  low: { label: '低', color: '#6b7280' }
}

// 线索来源选项
const leadSourceChoices = [
  { id: 'Google搜索', name: 'Google搜索' },
  { id: '展会', name: '展会' },
  { id: '推荐', name: '推荐' },
  { id: '官网询盘', name: '官网询盘' },
  { id: 'LinkedIn', name: 'LinkedIn' },
  { id: 'B2B平台', name: 'B2B平台' },
  { id: '其他', name: '其他' }
]

// 线索状态选项
const leadStatusChoices = [
  { id: 'new', name: '新线索' },
  { id: 'contacted', name: '已联系' },
  { id: 'in_progress', name: '跟进中' },
  { id: 'qualified', name: '合格' },
  { id: 'unqualified', name: '不合格' },
  { id: 'converted', name: '已转化' }
]

// 优先级选项
const priorityChoices = [
  { id: 'high', name: '高' },
  { id: 'medium', name: '中' },
  { id: 'low', name: '低' }
]

// 决策时间选项
const decisionTimeframeChoices = [
  { id: '立即', name: '立即' },
  { id: '1个月内', name: '1个月内' },
  { id: '3个月内', name: '3个月内' },
  { id: '6个月内', name: '6个月内' },
  { id: '待定', name: '待定' }
]

// 线索评分显示组件
const LeadScoreField = ({ record }: any) => {
  const score = record?.lead_score || 0
  
  // 根据分数显示不同颜色
  let color = '#6b7280' // 灰色
  let label = '冷线索'
  
  if (score >= 90) {
    color = '#ef4444' // 红色
    label = '热线索'
  } else if (score >= 70) {
    color = '#f59e0b' // 橙色
    label = '温线索'
  } else if (score >= 50) {
    color = '#eab308' // 黄色
    label = '一般'
  }
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: '120px' }}>
      <Box sx={{ flex: 1 }}>
        <LinearProgress 
          variant="determinate" 
          value={score} 
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: '#e5e7eb',
            '& .MuiLinearProgress-bar': {
              backgroundColor: color,
              borderRadius: 4
            }
          }}
        />
      </Box>
      <Typography variant="body2" sx={{ minWidth: '35px', color, fontWeight: 600 }}>
        {score}分
      </Typography>
    </Box>
  )
}

// 转化为客户按钮
const ConvertButton = ({ record }: any) => {
  const [open, setOpen] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()
  
  const handleConvert = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8002/api/leads/${record.id}/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        notify(`线索已成功转化为客户 #${result.customer_id}`, { type: 'success' })
        refresh()
        setOpen(false)
      } else {
        const error = await response.json()
        notify(error.detail || '转化失败', { type: 'error' })
      }
    } catch (error) {
      notify('转化失败', { type: 'error' })
    }
  }
  
  if (record?.converted) {
    return (
      <Chip 
        label="已转化" 
        size="small" 
        color="success"
        icon={<TransformIcon />}
      />
    )
  }
  
  return (
    <>
      <Button
        size="small"
        variant="outlined"
        startIcon={<TransformIcon />}
        onClick={(e) => {
          e.stopPropagation()
          setOpen(true)
        }}
        sx={{ textTransform: 'none' }}
      >
        转化客户
      </Button>
      
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>确认转化</DialogTitle>
        <DialogContent>
          <Typography>
            确定要将线索 <strong>{record?.company_name}</strong> 转化为正式客户吗？
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            转化后将在客户列表中创建新的客户记录。
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>取消</Button>
          <Button onClick={handleConvert} variant="contained" color="primary">
            确认转化
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

// 批量操作按钮
const BulkActionButtons = () => (
  <>
    <BulkDeleteButton />
  </>
)

// 线索列表
export const LeadList = (props: any) => {
  const [totalCount, setTotalCount] = useState(0)
  
  useEffect(() => {
    // 获取线索总数
    fetch('http://127.0.0.1:8002/api/leads?range=[0,0]', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
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
  
  return (
    <Box sx={{ pl: 3 }}>
      {/* 顶部栏 */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        px: 2, 
        py: 1.5,
        borderBottom: '1px solid #e0e0e0',
        backgroundColor: '#fff'
      }}>
        <Typography variant="body2" color="text.secondary">
          全部线索  <Typography component="span" variant="body2" sx={{ color: '#1976d2', fontWeight: 600 }}>{totalCount.toLocaleString()}</Typography> 条
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <RAButton 
            label="+ 新建线索"
            href="/#/leads/create"
            variant="contained"
          />
        </Box>
      </Box>
      
      <List {...props} perPage={20} actions={false}>
        <Datagrid
          rowClick="edit"
          bulkActionButtons={<BulkActionButtons />}
          sx={{
            '& .RaDatagrid-headerCell': { fontWeight: 600, backgroundColor: '#f9fafb' },
            '& .RaDatagrid-row': { '&:hover': { backgroundColor: '#f3f4f6' } }
          }}
        >
          <TextField source="company_name" label="公司名称" />
          <TextField source="contact_name" label="联系人" />
          <EmailField source="email" label="邮箱" />
          <TextField source="country" label="国家" />
          
          {/* 线索状态 */}
          <FunctionField 
            label="线索状态" 
            render={(record: any) => {
              const status = leadStatusMap[record?.lead_status]
              return (
                <Chip 
                  label={status?.label || record?.lead_status} 
                  size="small" 
                  sx={{ 
                    bgcolor: status?.color, 
                    color: '#fff', 
                    fontWeight: 500,
                    fontSize: '11px',
                    height: '20px'
                  }} 
                />
              )
            }}
          />
          
          {/* 线索评分 */}
          <FunctionField 
            label="线索评分" 
            render={(record: any) => <LeadScoreField record={record} />}
          />
          
          {/* 优先级 */}
          <FunctionField 
            label="优先级" 
            render={(record: any) => {
              const priority = priorityMap[record?.priority]
              return (
                <Chip 
                  label={priority?.label || record?.priority} 
                  size="small" 
                  sx={{ 
                    bgcolor: priority?.color, 
                    color: '#fff', 
                    fontWeight: 500,
                    fontSize: '11px',
                    height: '20px'
                  }} 
                />
              )
            }}
          />
          
          <TextField source="lead_source" label="线索来源" />
          
          {/* 转化操作 */}
          <FunctionField 
            label="操作" 
            render={(record: any) => <ConvertButton record={record} />}
          />
        </Datagrid>
      </List>
    </Box>
  )
}

// 线索创建
export const LeadCreate = (props: any) => (
  <Create {...props}>
    <SimpleForm sx={{ '& .MuiBox-root': { py: 0 } }}>
      <Box sx={{ width: '100%', px: 2, py: 1 }}>
        {/* 基本信息 - 两列布局 */}
        <Typography variant="subtitle1" sx={{ mb: 1, pb: 0.5, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>基本信息</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5, mb: 2 }}>
          <TextInput source="company_name" label="公司名称" required fullWidth size="small" />
          <TextInput source="contact_name" label="联系人" fullWidth size="small" />
          <TextInput source="email" label="邮箱" type="email" fullWidth size="small" />
          <TextInput source="phone" label="电话" fullWidth size="small" />
          <TextInput source="country" label="国家" fullWidth size="small" />
          <TextInput source="industry" label="行业" fullWidth size="small" />
        </Box>
        
        {/* 线索信息 - 四列布局 */}
        <Typography variant="subtitle1" sx={{ mb: 1, pb: 0.5, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>线索信息</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 1.5, mb: 2 }}>
          <SelectInput source="lead_source" label="线索来源" choices={leadSourceChoices} fullWidth size="small" />
          <SelectInput source="lead_status" label="线索状态" choices={leadStatusChoices} defaultValue="new" fullWidth size="small" />
          <SelectInput source="priority" label="优先级" choices={priorityChoices} defaultValue="medium" fullWidth size="small" />
          <NumberInput source="lead_score" label="评分" min={0} max={100} defaultValue={0} fullWidth size="small" />
          <NumberInput source="estimated_budget" label="预算(USD)" fullWidth size="small" />
          <SelectInput source="decision_timeframe" label="决策时间" choices={decisionTimeframeChoices} fullWidth size="small" />
          <TextInput source="product_interest" label="感兴趣产品" fullWidth size="small" />
          <TextInput source="competitor_info" label="竞争对手" fullWidth size="small" />
        </Box>
        
        {/* 需求分析 - 单行 */}
        <Typography variant="subtitle1" sx={{ mb: 1, pb: 0.5, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>需求分析</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 1.5 }}>
          <TextInput source="pain_points" label="痛点需求" fullWidth size="small" />
          <TextInput source="notes" label="备注" fullWidth size="small" />
        </Box>
      </Box>
    </SimpleForm>
  </Create>
)

// 线索编辑
export const LeadEdit = (props: any) => (
  <Edit {...props}>
    <SimpleForm sx={{ '& .MuiBox-root': { py: 0 } }}>
      <Box sx={{ width: '100%', px: 2, py: 1 }}>
        {/* 基本信息 - 两列布局 */}
        <Typography variant="subtitle1" sx={{ mb: 1, pb: 0.5, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>基本信息</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5, mb: 2 }}>
          <TextInput source="company_name" label="公司名称" required fullWidth size="small" />
          <TextInput source="contact_name" label="联系人" fullWidth size="small" />
          <TextInput source="email" label="邮箱" type="email" fullWidth size="small" />
          <TextInput source="phone" label="电话" fullWidth size="small" />
          <TextInput source="country" label="国家" fullWidth size="small" />
          <TextInput source="industry" label="行业" fullWidth size="small" />
        </Box>
        
        {/* 线索信息 - 四列布局 */}
        <Typography variant="subtitle1" sx={{ mb: 1, pb: 0.5, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>线索信息</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 1.5, mb: 2 }}>
          <SelectInput source="lead_source" label="线索来源" choices={leadSourceChoices} fullWidth size="small" />
          <SelectInput source="lead_status" label="线索状态" choices={leadStatusChoices} fullWidth size="small" />
          <SelectInput source="priority" label="优先级" choices={priorityChoices} fullWidth size="small" />
          <NumberInput source="lead_score" label="评分" min={0} max={100} fullWidth size="small" />
          <NumberInput source="estimated_budget" label="预算(USD)" fullWidth size="small" />
          <SelectInput source="decision_timeframe" label="决策时间" choices={decisionTimeframeChoices} fullWidth size="small" />
          <TextInput source="product_interest" label="感兴趣产品" fullWidth size="small" />
          <TextInput source="competitor_info" label="竞争对手" fullWidth size="small" />
        </Box>
        
        {/* 需求与跟进 - 合并 */}
        <Typography variant="subtitle1" sx={{ mb: 1, pb: 0.5, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>需求与跟进</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 1.5, mb: 1.5 }}>
          <TextInput source="pain_points" label="痛点需求" fullWidth size="small" />
          <TextInput source="notes" label="备注" fullWidth size="small" />
        </Box>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 1.5 }}>
          <DateTimeInput source="first_contact_date" label="首次联系" fullWidth size="small" />
          <DateTimeInput source="last_contact_date" label="最后联系" fullWidth size="small" />
          <DateTimeInput source="next_followup_date" label="下次跟进" fullWidth size="small" />
        </Box>
      </Box>
    </SimpleForm>
  </Edit>
)
