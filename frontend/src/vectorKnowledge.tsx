import React, { useState } from 'react'
import {
  List,
  Datagrid,
  TextField,
  DateField,
  useNotify,
  useRefresh,
  FunctionField,
  TopToolbar,
  CreateButton,
  ExportButton,
  FilterButton,
  TextInput,
  SelectInput,
  useDataProvider,
  useRecordContext,
  Button as RaButton,
} from 'react-admin'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField as MuiTextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  IconButton,
  Chip,
  LinearProgress,
} from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DeleteIcon from '@mui/icons-material/Delete'
import SearchIcon from '@mui/icons-material/Search'
import DescriptionIcon from '@mui/icons-material/Description'
import EditIcon from '@mui/icons-material/Edit'

// 文件大小格式化
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 文档列表操作按钮
const DocumentActions = () => {
  const record = useRecordContext()
  const notify = useNotify()
  const refresh = useRefresh()
  const dataProvider = useDataProvider()
  const [editOpen, setEditOpen] = useState(false)

  const handleDelete = async () => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await dataProvider.delete('knowledge/documents', { id: record.id })
      notify('文档已删除', { type: 'success' })
      refresh()
    } catch (error) {
      console.error('删除失败:', error)
      notify('删除失败', { type: 'error' })
    }
  }

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <IconButton onClick={() => setEditOpen(true)} size="small" color="primary">
        <EditIcon />
      </IconButton>
      <IconButton onClick={handleDelete} size="small" color="error">
        <DeleteIcon />
      </IconButton>
      <EditDialog 
        open={editOpen} 
        onClose={() => setEditOpen(false)} 
        record={record}
      />
    </Box>
  )
}

// 列表顶部工具栏
const ListActions = () => {
  const [open, setOpen] = useState(false)

  return (
    <TopToolbar>
      <FilterButton />
      <Button
        startIcon={<UploadFileIcon />}
        onClick={() => setOpen(true)}
        variant="contained"
      >
        上传文档
      </Button>
      <ExportButton />
      <UploadDialog open={open} onClose={() => setOpen(false)} />
    </TopToolbar>
  )
}

// 上传文档对话框
const UploadDialog = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [category, setCategory] = useState('general')
  const [description, setDescription] = useState('')
  const [uploading, setUploading] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      
      // 自动填充标题
      if (!title) {
        const fileName = selectedFile.name.replace(/\.[^/.]+$/, '')
        setTitle(fileName)
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      notify('请选择文件', { type: 'warning' })
      return
    }

    if (!title.trim()) {
      notify('请输入文档标题', { type: 'warning' })
      return
    }

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', title)
      formData.append('category', category)
      if (description) {
        formData.append('description', description)
      }

      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/knowledge/upload', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        notify(`文档上传成功！共生成 ${result.document.chunk_count} 个知识片段`, {
          type: 'success',
        })
        refresh()
        handleClose()
      } else {
        const error = await response.json()
        notify(`上传失败: ${error.detail}`, { type: 'error' })
      }
    } catch (error) {
      console.error('上传失败:', error)
      notify('上传失败', { type: 'error' })
    } finally {
      setUploading(false)
    }
  }

  const handleClose = () => {
    setFile(null)
    setTitle('')
    setCategory('general')
    setDescription('')
    setUploading(false)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>上传文档到知识库</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {/* 文件选择 */}
          <Box>
            <input
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label htmlFor="file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<DescriptionIcon />}
                disabled={uploading}
                fullWidth
              >
                {file ? file.name : '选择文件 (PDF、Word、TXT)'}
              </Button>
            </label>
            {file && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                文件大小: {formatFileSize(file.size)}
              </Typography>
            )}
          </Box>

          {/* 文档标题 */}
          <MuiTextField
            label="文档标题"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
            required
            disabled={uploading}
          />

          {/* 分类 */}
          <FormControl fullWidth>
            <InputLabel>分类</InputLabel>
            <Select
              value={category}
              label="分类"
              onChange={(e) => setCategory(e.target.value)}
              disabled={uploading}
            >
              <MenuItem value="general">通用知识</MenuItem>
              <MenuItem value="product">产品信息</MenuItem>
              <MenuItem value="pricing">价格政策</MenuItem>
              <MenuItem value="faq">常见问题</MenuItem>
              <MenuItem value="case">案例模板</MenuItem>
              <MenuItem value="policy">公司政策</MenuItem>
            </Select>
          </FormControl>

          {/* 描述 */}
          <MuiTextField
            label="描述（可选）"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
            multiline
            rows={3}
            disabled={uploading}
          />

          {uploading && <LinearProgress />}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={uploading}>
          取消
        </Button>
        <Button onClick={handleUpload} variant="contained" disabled={uploading || !file}>
          {uploading ? '上传中...' : '上传'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// 编辑文档对话框
const EditDialog = ({ 
  open, 
  onClose, 
  record 
}: { 
  open: boolean
  onClose: () => void
  record: any 
}) => {
  const [title, setTitle] = useState('')
  const [category, setCategory] = useState('general')
  const [summary, setSummary] = useState('')
  const [content, setContent] = useState('')  // 新增：文档内容
  const [loading, setLoading] = useState(false)  // 加载状态
  const [updating, setUpdating] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  // 当对话框打开时加载文档详情
  React.useEffect(() => {
    if (open && record) {
      loadDocumentContent()
    }
  }, [open, record])
  
  // 加载文档完整内容
  const loadDocumentContent = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/knowledge/documents/${record.id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      
      if (response.ok) {
        const data = await response.json()
        console.log('加载文档详情:', data)
        setTitle(data.title || '')
        setCategory(data.category || 'general')
        setSummary(data.summary || '')
        setContent(data.content || '')  // 设置完整内容
      } else {
        notify('加载文档内容失败', { type: 'error' })
      }
    } catch (error) {
      console.error('加载失败:', error)
      notify('加载失败', { type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async () => {
    if (!title.trim()) {
      notify('请输入文档标题', { type: 'warning' })
      return
    }
    
    if (!content.trim()) {
      notify('请输入文档内容', { type: 'warning' })
      return
    }

    setUpdating(true)

    try {
      const formData = new FormData()
      formData.append('title', title)
      formData.append('category', category)
      if (summary) {
        formData.append('summary', summary)
      }
      formData.append('content', content)  // 添加内容

      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/knowledge/documents/${record.id}`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      )

      if (response.ok) {
        const result = await response.json()
        notify(
          result.message + (
            result.document.chunk_count 
              ? ` (已生成 ${result.document.chunk_count} 个知识片段)` 
              : ''
          ), 
          { type: 'success' }
        )
        refresh()
        handleClose()
      } else {
        const error = await response.json()
        notify(`更新失败: ${error.detail}`, { type: 'error' })
      }
    } catch (error) {
      console.error('更新失败:', error)
      notify('更新失败', { type: 'error' })
    } finally {
      setUpdating(false)
    }
  }

  const handleClose = () => {
    setUpdating(false)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>编辑文档</DialogTitle>
      <DialogContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
            <LinearProgress sx={{ width: '50%' }} />
            <Typography sx={{ ml: 2 }}>加载中...</Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {/* 调试信息 */}
            {record && (
              <Typography variant="caption" color="info.main" sx={{ mb: 1 }}>
                文件名: {record.filename} (ID: {record.id})
              </Typography>
            )}
            
            {/* 文档标题 */}
            <MuiTextField
              label="文档标题"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              fullWidth
              required
              disabled={updating}
              placeholder="请输入文档标题"
            />

            {/* 分类 */}
            <FormControl fullWidth disabled={updating}>
              <InputLabel>分类</InputLabel>
              <Select 
                value={category} 
                onChange={(e) => setCategory(e.target.value)} 
                label="分类"
              >
                <MenuItem value="general">通用知识</MenuItem>
                <MenuItem value="product">产品信息</MenuItem>
                <MenuItem value="pricing">价格政策</MenuItem>
                <MenuItem value="faq">常见问题</MenuItem>
                <MenuItem value="case">案例模板</MenuItem>
                <MenuItem value="policy">公司政策</MenuItem>
              </Select>
            </FormControl>

            {/* 描述 */}
            <MuiTextField
              label="文档描述（可选）"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              fullWidth
              multiline
              rows={2}
              disabled={updating}
              placeholder="请输入文档描述"
            />
            
            {/* 文档内容 */}
            <MuiTextField
              label="文档内容"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              fullWidth
              required
              multiline
              rows={15}
              disabled={updating}
              placeholder="请输入或编辑文档内容..."
              sx={{
                '& .MuiInputBase-root': {
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                }
              }}
            />

            {/* 提示信息 */}
            <Typography variant="caption" color="warning.main">
              ⚠️ 修改内容后将自动重新生成向量数据，这可能需要一些时间。
            </Typography>

            {updating && (
              <Box>
                <LinearProgress />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                  正在保存并重新生成向量，请稍候...
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={updating || loading}>
          取消
        </Button>
        <Button onClick={handleUpdate} variant="contained" disabled={updating || loading}>
          {updating ? '保存中...' : '保存'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// 过滤器
const documentFilters = [
  <TextInput label="搜索" source="q" alwaysOn />,
  <SelectInput
    label="分类"
    source="category"
    choices={[
      { id: 'general', name: '通用知识' },
      { id: 'product', name: '产品信息' },
      { id: 'pricing', name: '价格政策' },
      { id: 'faq', name: '常见问题' },
      { id: 'case', name: '案例模板' },
      { id: 'policy', name: '公司政策' },
    ]}
  />,
]

// 分类标签颜色
const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    general: 'default',
    product: 'primary',
    pricing: 'success',
    faq: 'info',
    case: 'warning',
    policy: 'error',
  }
  return colors[category] || 'default'
}

// 分类名称
const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    general: '通用知识',
    product: '产品信息',
    pricing: '价格政策',
    faq: '常见问题',
    case: '案例模板',
    policy: '公司政策',
  }
  return names[category] || category
}

// 文档列表
export const VectorKnowledgeList = () => (
  <List
    filters={documentFilters}
    actions={<ListActions />}
    sort={{ field: 'created_at', order: 'DESC' }}
    perPage={25}
  >
    <Datagrid bulkActionButtons={false}>
      <TextField source="title" label="文档标题" />
      <FunctionField
        label="分类"
        render={(record: any) => (
          <Chip
            label={getCategoryName(record.category)}
            color={getCategoryColor(record.category) as any}
            size="small"
          />
        )}
      />
      <TextField source="filename" label="文件名" />
      <FunctionField
        label="文件大小"
        render={(record: any) => formatFileSize(record.file_size || 0)}
      />
      <FunctionField
        label="知识片段"
        render={(record: any) => (
          <Chip label={`${record.chunk_count || 0} 个片段`} size="small" variant="outlined" />
        )}
      />
      <DateField source="created_at" label="上传时间" showTime />
      <FunctionField label="操作" render={() => <DocumentActions />} />
    </Datagrid>
  </List>
)

export default {
  list: VectorKnowledgeList,
}
