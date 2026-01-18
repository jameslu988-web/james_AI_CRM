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
  DialogActions,
  TextField as MuiTextField,
  Alert,
  CircularProgress,
  Drawer,
  MenuItem
} from '@mui/material'
import StarIcon from '@mui/icons-material/Star'
import StarBorderIcon from '@mui/icons-material/StarBorder'
import StarHalfIcon from '@mui/icons-material/StarHalf'
import TransformIcon from '@mui/icons-material/Transform'
import EditIcon from '@mui/icons-material/Edit'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import CloseIcon from '@mui/icons-material/Close'
import { getApiUrl } from './config/api'

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
      const response = await fetch(getApiUrl('crm', `/leads/${record.id}/convert`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
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
  const [createOpen, setCreateOpen] = useState(false)
  const [prospectingOpen, setProspectingOpen] = useState(false)
  const [prospectConfig, setProspectConfig] = useState({
    keywords: '',
    limit: 50,
    use_proxy: true,
    proxy_url: 'socks5://127.0.0.1:10808'
  })
  const [starting, setStarting] = useState(false)
  const [taskRunning, setTaskRunning] = useState(false)
  const [taskStatus, setTaskStatus] = useState<any>(null)
  const [startResult, setStartResult] = useState<any>(null)
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([])
  const notify = useNotify()
  const refresh = useRefresh()
  
  // 智能关键词推荐
  const recommendedKeywords = [
    // DTC品牌 + 产品
    { label: '男士内裤DTC品牌（美国）', value: 'men\'s underwear DTC brand USA', category: 'DTC品牌' },
    { label: '男士内裤电商品牌', value: 'men\'s underwear ecommerce brand', category: 'DTC品牌' },
    { label: '在线内裤品牌', value: 'online men\'s underwear brand', category: 'DTC品牌' },
    { label: '直销内裤公司', value: 'direct to consumer underwear company', category: 'DTC品牌' },
    
    // 采购需求
    { label: '寻找内裤制造商', value: 'looking for underwear manufacturer', category: '采购需求' },
    { label: '内裤ODM服务', value: 'men\'s underwear ODM service', category: '采购需求' },
    { label: '定制内裤供应商', value: 'custom underwear supplier', category: '采购需求' },
    { label: '私人标签内裤', value: 'private label men\'s underwear', category: '采购需求' },
    
    // 批发/零售
    { label: '内裤批发商（美国）', value: 'men\'s underwear wholesale USA', category: '批发零售' },
    { label: '内裤零售商', value: 'men\'s underwear retailer contact', category: '批发零售' },
    { label: '内裤分销商', value: 'men\'s underwear distributor', category: '批发零售' },
    
    // 地区定向
    { label: '内裤品牌（欧洲）', value: 'men\'s underwear brand Europe', category: '地区定向' },
    { label: '内裤品牌（澳洲）', value: 'men\'s underwear brand Australia', category: '地区定向' },
    { label: '内裤品牌（加拿大）', value: 'men\'s underwear brand Canada', category: '地区定向' },
    
    // 细分市场
    { label: '高端内裤品牌', value: 'premium men\'s underwear brand', category: '细分市场' },
    { label: '运动内裤品牌', value: 'athletic men\'s underwear brand', category: '细分市场' },
    { label: '环保内裤品牌', value: 'sustainable men\'s underwear brand', category: '细分市场' },
  ]
  
  useEffect(() => {
    // 获取线索总数
    fetch(getApiUrl('crm', '/leads?range=[0,0]'))
      .then(r => {
        const contentRange = r.headers.get('Content-Range')
        if (contentRange) {
          const total = parseInt(contentRange.split('/')[1])
          setTotalCount(total)
        }
        return r.json()
      })
      .catch(() => {})
    
    // 获取代理配置
    fetch(getApiUrl('crm', '/prospecting/proxy-config'))
      .then(r => r.json())
      .then(data => {
        if (data.proxy_url) {
          setProspectConfig(prev => ({
            ...prev,
            proxy_url: data.proxy_url,
            use_proxy: data.enabled
          }))
        }
      })
      .catch(() => {})
  }, [])
  
  // 轮询任务状态
  useEffect(() => {
    if (!taskRunning) return
    
    const interval = setInterval(async () => {
      try {
        const response = await fetch(getApiUrl('crm', '/prospecting/status'))
        const status = await response.json()
        
        setTaskStatus(status)
        
        if (!status.running) {
          setTaskRunning(false)
          clearInterval(interval)
          
          if (status.error) {
            notify(`任务失败: ${status.error}`, { type: 'error' })
          } else {
            notify(`任务完成！创建了 ${status.leads_created || 0} 条线索，跳过 ${status.leads_skipped || 0} 条重复`, { type: 'success' })
            refresh() // 刷新列表
            
            // 更新总数
            fetch(getApiUrl('crm', '/leads?range=[0,0]'))
              .then(r => {
                const contentRange = r.headers.get('Content-Range')
                if (contentRange) {
                  const total = parseInt(contentRange.split('/')[1])
                  setTotalCount(total)
                }
              })
          }
        }
      } catch (error) {
        console.error('获取任务状态失败:', error)
      }
    }, 2000) // 每2秒轮询一次
    
    return () => clearInterval(interval)
  }, [taskRunning, notify, refresh])
  
  const handleKeywordToggle = (keyword: string) => {
    setSelectedKeywords(prev => {
      if (prev.includes(keyword)) {
        return prev.filter(k => k !== keyword)
      } else {
        return [...prev, keyword]
      }
    })
  }
  
  const handleStartProspecting = async () => {
    setStarting(true)
    setStartResult(null)
    
    // 合并自定义关键词和选中的推荐关键词
    const customKeywords = prospectConfig.keywords.split(',').map((k: string) => k.trim()).filter(k => k)
    const allKeywords = [...customKeywords, ...selectedKeywords]
    
    if (allKeywords.length === 0) {
      setStartResult({ success: false, message: '请至少输入或选择一个关键词' })
      setStarting(false)
      return
    }
    
    try {
      const response = await fetch(getApiUrl('crm', '/prospecting/start'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords: allKeywords,
          limit: prospectConfig.limit,
          use_proxy: prospectConfig.use_proxy,
          proxy_url: prospectConfig.proxy_url
        })
      })
      
      const result = await response.json()
      
      if (response.ok) {
        setStartResult({ success: true, message: result.message })
        notify('流量获取任务已启动，正在后台运行...', { type: 'info' })
        setTaskRunning(true)
        setTaskStatus({ running: true, progress: 0, total: prospectConfig.limit })
        
        // 3秒后关闭对话框
        setTimeout(() => {
          setProspectingOpen(false)
        }, 3000)
      } else {
        setStartResult({ success: false, message: result.detail || '启动失败' })
      }
    } catch (error: any) {
      setStartResult({ success: false, message: `启动失败: ${error.message}` })
    } finally {
      setStarting(false)
    }
  }
  
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
          {taskRunning && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2, px: 2, py: 0.5, bgcolor: 'info.light', borderRadius: 1 }}>
              <CircularProgress size={16} />
              <Typography variant="body2" sx={{ color: 'info.dark' }}>
                正在获取流量... {taskStatus?.progress || 0}/{taskStatus?.total || 0}
              </Typography>
            </Box>
          )}
          <Button
            variant="contained"
            color="success"
            startIcon={<RocketLaunchIcon />}
            onClick={() => setProspectingOpen(true)}
            disabled={taskRunning}
            sx={{ textTransform: 'none' }}
          >
            🚀 获取流量
          </Button>
          <RAButton 
            label="+ 新建线索"
            onClick={() => setCreateOpen(true)}
            variant="contained"
          />
        </Box>
      </Box>
      
      {/* 🔥 流量获取对话框 */}
      <Dialog open={prospectingOpen} onClose={() => !starting && setProspectingOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>🚀 启动流量获取 - 专注海外DTC品牌</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            通过 Google 搜索自动查找海外男士内裤DTC品牌，提取联系方式（邮箱、电话、社交媒体）并导入线索库。
          </Typography>
          
          <Alert severity="info" icon={false} sx={{ mb: 3 }}>
            <Typography variant="caption" sx={{ display: 'block', fontWeight: 600 }}>
              💡 我们的目标客户：
            </Typography>
            <Typography variant="caption">
              • 海外DTC品牌（Direct-to-Consumer）<br/>
              • 需要ODM/OEM定制服务的内裤品牌<br/>
              • 主要市场：美国、欧洲、澳洲<br/>
              • 提取信息：公司名、网站、邮箱、电话、社交媒体
            </Typography>
          </Alert>
          
          {taskRunning && taskStatus && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>任务正在运行中...</Typography>
              <Typography variant="caption">进度: {taskStatus.progress}/{taskStatus.total}</Typography>
              {taskStatus.leads_created !== undefined && (
                <Typography variant="caption" sx={{ display: 'block' }}>
                  已创建: {taskStatus.leads_created} 条 | 跳过: {taskStatus.leads_skipped || 0} 条
                </Typography>
              )}
            </Alert>
          )}
          
          {/* 智能关键词推荐 */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              🎯 智能关键词推荐（点击选择）
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              已选择 {selectedKeywords.length} 个关键词
            </Typography>
            
            {['DTC品牌', '采购需求', '批发零售', '地区定向', '细分市场'].map(category => (
              <Box key={category} sx={{ mb: 2 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: 'primary.main', display: 'block', mb: 0.5 }}>
                  {category}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {recommendedKeywords
                    .filter(k => k.category === category)
                    .map(keyword => (
                      <Chip
                        key={keyword.value}
                        label={keyword.label}
                        onClick={() => handleKeywordToggle(keyword.value)}
                        color={selectedKeywords.includes(keyword.value) ? 'primary' : 'default'}
                        variant={selectedKeywords.includes(keyword.value) ? 'filled' : 'outlined'}
                        size="small"
                        disabled={taskRunning}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))
                  }
                </Box>
              </Box>
            ))}
          </Box>
          
          <MuiTextField
            fullWidth
            label="自定义关键词（可选）"
            value={prospectConfig.keywords}
            onChange={(e) => setProspectConfig({...prospectConfig, keywords: e.target.value})}
            placeholder="输入自定义关键词，用逗号分隔"
            helperText="如：luxury men's underwear brand, organic underwear company"
            disabled={taskRunning}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <MuiTextField
              type="number"
              label="目标数量"
              value={prospectConfig.limit}
              onChange={(e) => setProspectConfig({...prospectConfig, limit: parseInt(e.target.value)})}
              disabled={taskRunning}
              sx={{ flex: 1 }}
              helperText="建议20-100条"
            />
            
            <MuiTextField
              label="代理地址"
              value={prospectConfig.proxy_url}
              onChange={(e) => setProspectConfig({...prospectConfig, proxy_url: e.target.value})}
              placeholder="socks5://127.0.0.1:10808"
              disabled={taskRunning}
              sx={{ flex: 2 }}
              helperText="访问Google必需"
            />
          </Box>
          
          {startResult && (
            <Alert severity={startResult.success ? 'success' : 'error'} sx={{ mt: 2 }}>
              {startResult.message}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProspectingOpen(false)} disabled={starting}>
            {taskRunning ? '关闭' : '取消'}
          </Button>
          {!taskRunning && (
            <Button 
              onClick={handleStartProspecting} 
              variant="contained" 
              disabled={starting}
              startIcon={starting ? <CircularProgress size={20} /> : <RocketLaunchIcon />}
            >
              {starting ? '正在启动...' : '开始获取'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
      
      <List {...props} perPage={20} actions={false}>
        <Datagrid
          rowClick="edit"
          bulkActionButtons={<BulkActionButtons />}
          sx={{
            '& .RaDatagrid-headerCell': { 
              fontWeight: 600, 
              backgroundColor: '#f9fafb',
              whiteSpace: 'nowrap',  // 列头不换行
              padding: '12px 8px'  // 减少列头内边距
            },
            '& .RaDatagrid-row': { 
              '&:hover': { backgroundColor: '#f3f4f6' } 
            },
            // 公司名称列宽度控制
            '& .column-company_name': {
              maxWidth: '280px',
              width: '280px'
            },
            // 品牌官网列宽度
            '& .column-undefined:nth-of-type(3)': {  // 品牌官网列
              maxWidth: '200px',
              width: '200px'
            },
            // 其他列的宽度优化
            '& .column-contact_name': {
              width: '100px'
            },
            '& .column-email': {
              width: '180px'
            },
            '& .column-country': {
              width: '90px'
            },
            '& .column-lead_source': {
              width: '120px'
            }
          }}
        >
          <TextField source="company_name" label="公司名称" />
          
          {/* 🔥 品牌官网（可直达） */}
          <FunctionField 
            label="品牌官网" 
            render={(record: any) => {
              if (!record?.website) return <span style={{ color: '#999' }}>未知</span>
              
              return (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <a 
                    href={record.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ 
                      color: '#1976d2', 
                      textDecoration: 'none',
                      maxWidth: '250px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      display: 'inline-block'
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {record.website.replace(/^https?:\/\//, '').replace(/\/$/, '')}
                  </a>
                  <IconButton 
                    size="small" 
                    href={record.website} 
                    target="_blank"
                    onClick={(e) => e.stopPropagation()}
                    sx={{ p: 0.5 }}
                  >
                    <OpenInNewIcon sx={{ fontSize: 16, color: '#1976d2' }} />
                  </IconButton>
                </Box>
              )
            }}
          />
          
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
      
      {/* 新建线索抽屉 */}
      <CreateLeadDrawer 
        open={createOpen} 
        onClose={() => setCreateOpen(false)} 
        onSuccess={() => {
          setCreateOpen(false)
          refresh()
          // 更新总数
          fetch(getApiUrl('crm', '/leads?range=[0,0]'))
            .then(r => {
              const contentRange = r.headers.get('Content-Range')
              if (contentRange) {
                const total = parseInt(contentRange.split('/')[1])
                setTotalCount(total)
              }
            })
        }}
      />
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

// 新建线索抽屉组件
const CreateLeadDrawer = ({ open, onClose, onSuccess }: { open: boolean, onClose: () => void, onSuccess: () => void }) => {
  const [formData, setFormData] = useState<any>({
    company_name: '',
    contact_name: '',
    email: '',
    phone: '',
    country: '',
    industry: '',
    website: '',
    lead_source: 'Google搜索',
    lead_status: 'new',
    priority: 'medium',
    lead_score: 50,
    estimated_budget: null,
    decision_timeframe: '待定',
    product_interest: '',
    competitor_info: '',
    pain_points: '',
    notes: ''
  })
  const notify = useNotify()
  
  // 重置表单
  const resetForm = () => {
    setFormData({
      company_name: '',
      contact_name: '',
      email: '',
      phone: '',
      country: '',
      industry: '',
      website: '',
      lead_source: 'Google搜索',
      lead_status: 'new',
      priority: 'medium',
      lead_score: 50,
      estimated_budget: null,
      decision_timeframe: '待定',
      product_interest: '',
      competitor_info: '',
      pain_points: '',
      notes: ''
    })
  }
  
  const handleClose = () => {
    resetForm()
    onClose()
  }
  
  const handleSubmit = async () => {
    if (!formData.company_name) {
      notify('公司名称不能为空', { type: 'warning' })
      return
    }
    
    try {
      const response = await fetch(getApiUrl('crm', '/leads'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        notify('线索创建成功', { type: 'success' })
        resetForm()
        onSuccess()
      } else {
        const error = await response.json()
        notify(error.detail || '创建失败', { type: 'error' })
      }
    } catch (error) {
      notify('网络错误', { type: 'error' })
    }
  }
  
  return (
    <Drawer anchor="right" open={open} onClose={handleClose}>
      <Box sx={{ width: 600, p: 3, height: '100vh', overflow: 'auto' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">新建线索</Typography>
          <IconButton onClick={handleClose}><CloseIcon /></IconButton>
        </Box>
        
        {/* 基本信息 */}
        <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600, color: 'primary.main' }}>基本信息</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
          <MuiTextField 
            fullWidth 
            label="公司名称" 
            required
            value={formData.company_name || ''} 
            onChange={(e) => setFormData({...formData, company_name: e.target.value})} 
          />
          <MuiTextField 
            fullWidth 
            label="联系人" 
            value={formData.contact_name || ''} 
            onChange={(e) => setFormData({...formData, contact_name: e.target.value})} 
          />
          <MuiTextField 
            fullWidth 
            label="邮箱" 
            type="email"
            value={formData.email || ''} 
            onChange={(e) => setFormData({...formData, email: e.target.value})} 
          />
          <MuiTextField 
            fullWidth 
            label="电话" 
            value={formData.phone || ''} 
            onChange={(e) => setFormData({...formData, phone: e.target.value})} 
          />
          <MuiTextField 
            fullWidth 
            label="国家" 
            value={formData.country || ''} 
            onChange={(e) => setFormData({...formData, country: e.target.value})} 
          />
          <MuiTextField 
            fullWidth 
            label="行业" 
            value={formData.industry || ''} 
            onChange={(e) => setFormData({...formData, industry: e.target.value})} 
          />
        </Box>
        
        <MuiTextField 
          fullWidth 
          label="网站" 
          value={formData.website || ''} 
          onChange={(e) => setFormData({...formData, website: e.target.value})} 
          sx={{ mb: 3 }}
        />
        
        {/* 线索信息 */}
        <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600, color: 'primary.main' }}>线索信息</Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
          <MuiTextField 
            select
            fullWidth 
            label="线索来源" 
            value={formData.lead_source} 
            onChange={(e) => setFormData({...formData, lead_source: e.target.value})}
          >
            {leadSourceChoices.map(choice => (
              <MenuItem key={choice.id} value={choice.id}>{choice.name}</MenuItem>
            ))}
          </MuiTextField>
          
          <MuiTextField 
            select
            fullWidth 
            label="线索状态" 
            value={formData.lead_status} 
            onChange={(e) => setFormData({...formData, lead_status: e.target.value})}
          >
            {leadStatusChoices.map(choice => (
              <MenuItem key={choice.id} value={choice.id}>{choice.name}</MenuItem>
            ))}
          </MuiTextField>
          
          <MuiTextField 
            select
            fullWidth 
            label="优先级" 
            value={formData.priority} 
            onChange={(e) => setFormData({...formData, priority: e.target.value})}
          >
            {priorityChoices.map(choice => (
              <MenuItem key={choice.id} value={choice.id}>{choice.name}</MenuItem>
            ))}
          </MuiTextField>
          
          <MuiTextField 
            type="number"
            fullWidth 
            label="线索评分" 
            value={formData.lead_score} 
            onChange={(e) => setFormData({...formData, lead_score: parseInt(e.target.value)})}
            InputProps={{ inputProps: { min: 0, max: 100 } }}
          />
          
          <MuiTextField 
            type="number"
            fullWidth 
            label="预算 (USD)" 
            value={formData.estimated_budget || ''} 
            onChange={(e) => setFormData({...formData, estimated_budget: e.target.value ? parseFloat(e.target.value) : null})}
          />
          
          <MuiTextField 
            select
            fullWidth 
            label="决策时间" 
            value={formData.decision_timeframe} 
            onChange={(e) => setFormData({...formData, decision_timeframe: e.target.value})}
          >
            {decisionTimeframeChoices.map(choice => (
              <MenuItem key={choice.id} value={choice.id}>{choice.name}</MenuItem>
            ))}
          </MuiTextField>
          
          <MuiTextField 
            fullWidth 
            label="感兴趣产品" 
            value={formData.product_interest || ''} 
            onChange={(e) => setFormData({...formData, product_interest: e.target.value})} 
          />
          
          <MuiTextField 
            fullWidth 
            label="竞争对手" 
            value={formData.competitor_info || ''} 
            onChange={(e) => setFormData({...formData, competitor_info: e.target.value})} 
          />
        </Box>
        
        {/* 需求分析 */}
        <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600, color: 'primary.main' }}>需求分析</Typography>
        <MuiTextField 
          fullWidth 
          multiline
          rows={3}
          label="痛点需求" 
          value={formData.pain_points || ''} 
          onChange={(e) => setFormData({...formData, pain_points: e.target.value})} 
          sx={{ mb: 2 }}
        />
        
        <MuiTextField 
          fullWidth 
          multiline
          rows={3}
          label="备注" 
          value={formData.notes || ''} 
          onChange={(e) => setFormData({...formData, notes: e.target.value})} 
          sx={{ mb: 3 }}
        />
        
        <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
          <Button variant="outlined" onClick={handleClose} fullWidth>取消</Button>
          <Button variant="contained" onClick={handleSubmit} fullWidth>保存</Button>
        </Box>
      </Box>
    </Drawer>
  )
}
