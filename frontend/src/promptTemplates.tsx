import React, { useState } from 'react'
import {
  List,
  Datagrid,
  TextField,
  DateField,
  BooleanField,
  FunctionField,
  TopToolbar,
  CreateButton,
  ExportButton,
  useNotify,
  useRefresh,
  useRecordContext,
  TextInput,
  SelectInput,
} from 'react-admin'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  TextField as MuiTextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Typography,
  LinearProgress,
  FormControlLabel,
  Checkbox,
  Alert,
} from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import StarIcon from '@mui/icons-material/Star'
import StarBorderIcon from '@mui/icons-material/StarBorder'
import VisibilityIcon from '@mui/icons-material/Visibility'
import AddIcon from '@mui/icons-material/Add'
import HelpIcon from '@mui/icons-material/Help'

// 可用的AI模型列表
const AI_MODELS = [
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini (快速)' },
  { value: 'gpt-4o', label: 'GPT-4o (标准)' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo (高级)' },
  { value: 'claude-3-haiku', label: 'Claude 3 Haiku' },
  { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
]

// 模板类型
const TEMPLATE_TYPES = [
  { value: 'reply', label: '邮件回复' },
  { value: 'analysis', label: '邮件分析' },
  { value: 'polish', label: '邮件润色' },
]

// 操作按钮
const TemplateActions = () => {
  const record = useRecordContext()
  const [editOpen, setEditOpen] = useState(false)
  const [previewOpen, setPreviewOpen] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  if (!record) return null

  const handleDelete = async () => {
    if (!window.confirm(`确定要删除模板"${record.name}"吗？`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:8001/api/prompt-templates/${record.id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        notify('模板已删除', { type: 'success' })
        refresh()
      } else {
        const error = await response.json()
        notify(`删除失败: ${error.detail}`, { type: 'error' })
      }
    } catch (error) {
      console.error('删除失败:', error)
      notify('删除失败', { type: 'error' })
    }
  }

  const handleSetDefault = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/prompt-templates/${record.id}/set-default`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        notify('已设置为默认模板', { type: 'success' })
        refresh()
      } else {
        const error = await response.json()
        notify(`设置失败: ${error.detail}`, { type: 'error' })
      }
    } catch (error) {
      console.error('设置失败:', error)
      notify('设置失败', { type: 'error' })
    }
  }

  return (
    <Box sx={{ display: 'flex', gap: 0.5 }}>
      <Tooltip title="预览">
        <IconButton size="small" onClick={() => setPreviewOpen(true)}>
          <VisibilityIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Tooltip title="编辑">
        <IconButton size="small" onClick={() => setEditOpen(true)}>
          <EditIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Tooltip title={record.is_default ? '已是默认' : '设为默认'}>
        <IconButton size="small" onClick={handleSetDefault} disabled={record.is_default}>
          {record.is_default ? (
            <StarIcon fontSize="small" sx={{ color: '#f59e0b' }} />
          ) : (
            <StarBorderIcon fontSize="small" />
          )}
        </IconButton>
      </Tooltip>
      <Tooltip title="删除">
        <IconButton size="small" onClick={handleDelete} disabled={record.is_default}>
          <DeleteIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <EditDialog open={editOpen} onClose={() => setEditOpen(false)} record={record} />
      <PreviewDialog open={previewOpen} onClose={() => setPreviewOpen(false)} record={record} />
    </Box>
  )
}

// 帮助对话框
const HelpDialog = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>📚 AI提示词模板使用说明</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
          {/* 概念说明 */}
          <Box>
            <Typography variant="h6" sx={{ mb: 1, color: '#1976d2' }}>
              🤔 什么是系统提示词和用户提示词？
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2" component="div">
                <strong>系统提示词</strong>：由<strong>你（管理员）</strong>来设置，告诉AI“你是谁”、“你的角色是什么”<br/>
                <strong>用户提示词</strong>：由<strong>系统自动</strong>生成，将实际的邮件内容填充进去
              </Typography>
            </Alert>
          </Box>

          {/* 完整示例 */}
          <Box>
            <Typography variant="h6" sx={{ mb: 1, color: '#2e7d32' }}>
              📝 完整示例
            </Typography>
            
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, color: '#1976d2' }}>
              1️⃣ 你在模板中设置：
            </Typography>
            <Box sx={{ bgcolor: '#e3f2fd', p: 2, borderRadius: 1, mb: 2 }}>
              <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                【系统提示词】
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                你是一个专业的外贸业务员，名叫张明。
你擅长处理国际客户询价，回复要专业、简洁、礼貌。
              </Typography>
              
              <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mt: 2, mb: 1 }}>
                【用户提示词模板】
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                {`客户发来的邮件：
主题: {subject}
正文: {body}

{knowledge_context}

请用{tone_desc}的语气回复。`}
              </Typography>
            </Box>
            
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, color: '#2e7d32' }}>
              2️⃣ 系统自动生成实际发给AI的内容：
            </Typography>
            <Box sx={{ bgcolor: '#f1f8e9', p: 2, borderRadius: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                【系统提示词】（你设置的）
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', mb: 2 }}>
                你是一个专业的外贸业务员，名叫张明。
你擅长处理国际客户询价，回复要专业、简洁、礼貌。
              </Typography>
              
              <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                【用户提示词】（系统自动填充）
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                {`客户发来的邮件：
主题: Inquiry about Men's Underwear MOQ
正文: Hi, I'm interested in your cotton underwear. What is the MOQ?

相关知识库信息：
1. 我们的MOQ是500件起订
2. 批量订购有优惠

请用专业、礼貌的语气回复。`}
              </Typography>
            </Box>
          </Box>

          {/* 变量说明 */}
          <Box>
            <Typography variant="h6" sx={{ mb: 1, color: '#ed6c02' }}>
              🔑 可用的变量占位符
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              <li><code>{'{subject}'}</code> - 邮件主题</li>
              <li><code>{'{body}'}</code> - 邮件正文</li>
              <li><code>{'{tone_desc}'}</code> - 语气描述（专业/友好/正式/热情）</li>
              <li><code>{'{knowledge_context}'}</code> - 从知识库检索到的相关信息</li>
              <li><code>{'{customer_context}'}</code> - 客户的历史信息和上下文</li>
            </Box>
          </Box>

          {/* 快速入门 */}
          <Box>
            <Typography variant="h6" sx={{ mb: 1, color: '#9c27b0' }}>
              🚀 快速入门
            </Typography>
            <Alert severity="success">
              <Typography variant="body2" component="div">
                1. 点击“新建模板”按钮<br/>
                2. 填写模板名称和描述<br/>
                3. 在“系统提示词”中定义AI的角色<br/>
                4. 在“用户提示词模板”中编写任务指令，使用 {'{subject}'}, {'{body}'} 等变量<br/>
                5. 保存后，在邮件编辑页面选择这个模板使用
              </Typography>
            </Alert>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">
          我知道了
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// 列表顶部操作
const ListActions = () => {
  const [open, setOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  return (
    <TopToolbar>
      <Button
        startIcon={<HelpIcon />}
        onClick={() => setHelpOpen(true)}
        variant="outlined"
        sx={{ mr: 1 }}
      >
        使用说明
      </Button>
      <Button
        startIcon={<AddIcon />}
        onClick={() => setOpen(true)}
        variant="contained"
        sx={{ bgcolor: '#1677ff' }}
      >
        新建模板
      </Button>
      <ExportButton />
      <CreateDialog open={open} onClose={() => setOpen(false)} />
      <HelpDialog open={helpOpen} onClose={() => setHelpOpen(false)} />
    </TopToolbar>
  )
}

// 创建模板对话框
const CreateDialog = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_type: 'reply',
    system_prompt: '',
    user_prompt_template: '',
    variables: '',
    recommended_model: 'gpt-4o-mini',
    is_active: true,
    is_default: false,
  })
  const [creating, setCreating] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  const handleCreate = async () => {
    if (!formData.name.trim()) {
      notify('请输入模板名称', { type: 'warning' })
      return
    }

    if (!formData.user_prompt_template.trim()) {
      notify('请输入用户提示词模板', { type: 'warning' })
      return
    }

    setCreating(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:8001/api/prompt-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        notify('模板创建成功', { type: 'success' })
        refresh()
        handleClose()
      } else {
        const error = await response.json()
        notify(`创建失败: ${error.detail}`, { type: 'error' })
      }
    } catch (error) {
      console.error('创建失败:', error)
      notify('创建失败', { type: 'error' })
    } finally {
      setCreating(false)
    }
  }

  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      template_type: 'reply',
      system_prompt: '',
      user_prompt_template: '',
      variables: '',
      recommended_model: 'gpt-4o-mini',
      is_active: true,
      is_default: false,
    })
    setCreating(false)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>新建提示词模板</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {/* 模板名称 */}
          <MuiTextField
            label="模板名称"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            fullWidth
            required
            disabled={creating}
            placeholder="例如：专业外贸回复模板"
          />

          {/* 模板描述 */}
          <MuiTextField
            label="模板描述"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            fullWidth
            multiline
            rows={2}
            disabled={creating}
            placeholder="简要描述这个模板的用途和特点"
          />

          {/* 模板类型和推荐模型 */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl fullWidth disabled={creating}>
              <InputLabel>模板类型</InputLabel>
              <Select
                value={formData.template_type}
                label="模板类型"
                onChange={(e) => setFormData({ ...formData, template_type: e.target.value })}
              >
                {TEMPLATE_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth disabled={creating}>
              <InputLabel>推荐模型</InputLabel>
              <Select
                value={formData.recommended_model}
                label="推荐模型"
                onChange={(e) => setFormData({ ...formData, recommended_model: e.target.value })}
              >
                {AI_MODELS.map((model) => (
                  <MenuItem key={model.value} value={model.value}>
                    {model.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* 系统提示词 */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="subtitle2" sx={{ color: '#1976d2' }}>
                🤖 系统提示词（可选）
              </Typography>
              <Tooltip title="系统提示词用于定义AI的角色和行为规范，由你来设置。例如：告诉AI它是一个专业的外贸业务员。">
                <IconButton size="small">
                  <HelpIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            <MuiTextField
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              fullWidth
              multiline
              rows={3}
              disabled={creating}
              placeholder="例如：你是一个专业的外贸业务员，名叫张明。你擅长处理国际客户询价，回复要专业、简洁、礼貌。"
              helperText="ℹ️ 这是告诉AI“你是谁”的地方，由你（管理员）来设置。可以为空，但建议填写以获得更好的效果。"
            />
          </Box>

          {/* 用户提示词模板 */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="subtitle2" sx={{ color: '#d32f2f' }}>
                ✨ 用户提示词模板（必填）
              </Typography>
              <Tooltip title="用户提示词模板是具体的任务指令，系统会自动将 {subject}, {body} 等变量替换为实际的邮件内容。">
                <IconButton size="small">
                  <HelpIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            <MuiTextField
              value={formData.user_prompt_template}
              onChange={(e) => setFormData({ ...formData, user_prompt_template: e.target.value })}
              fullWidth
              required
              multiline
              rows={12}
              disabled={creating}
              placeholder={`例如：
客户发来的邮件：
主题: {subject}
正文: {body}

{knowledge_context}

请用{tone_desc}的语气回复这封邮件。回复要求：
1. 简洁明了
2. 包含相关产品信息
3. 表达合作意愿`}
              sx={{
                '& .MuiInputBase-root': {
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                },
              }}
              helperText="ℹ️ 这是具体的任务指令。系统会自动将 {subject}, {body} 等变量替换为实际的邮件内容。"
            />
          </Box>

          {/* 变量说明 */}
          <MuiTextField
            label="变量说明（JSON格式，可选）"
            value={formData.variables}
            onChange={(e) => setFormData({ ...formData, variables: e.target.value })}
            fullWidth
            multiline
            rows={3}
            disabled={creating}
            placeholder='{"subject": "邮件主题", "body": "邮件正文", "tone_desc": "语气描述"}'
            sx={{
              '& .MuiInputBase-root': {
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              },
            }}
          />

          {/* 选项 */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  disabled={creating}
                />
              }
              label="启用此模板"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_default}
                  onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  disabled={creating}
                />
              }
              label="设为默认模板"
            />
          </Box>

          <Alert severity="info" sx={{ mt: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              💡 快速理解：
            </Typography>
            <Typography variant="body2" component="div">
              • <strong>系统提示词</strong>：由<strong>你</strong>来设置，告诉AI“你是谁”（例如：专业的外贸业务员）<br/>
              • <strong>用户提示词</strong>：由<strong>系统自动</strong>生成，将 {'{subject}'}, {'{body}'} 等变量替换为实际内容<br/>
              • <strong>变量占位符</strong>：使用 {'{subject}'}, {'{body}'}, {'{knowledge_context}'} 等，系统会自动替换
            </Typography>
          </Alert>

          {creating && <LinearProgress />}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={creating}>
          取消
        </Button>
        <Button onClick={handleCreate} variant="contained" disabled={creating}>
          {creating ? '创建中...' : '创建'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

// 编辑模板对话框
const EditDialog = ({
  open,
  onClose,
  record,
}: {
  open: boolean
  onClose: () => void
  record: any
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_type: 'reply',
    system_prompt: '',
    user_prompt_template: '',
    variables: '',
    recommended_model: 'gpt-4o-mini',
    is_active: true,
    is_default: false,
  })
  const [loading, setLoading] = useState(false)
  const [updating, setUpdating] = useState(false)
  const notify = useNotify()
  const refresh = useRefresh()

  // 加载模板数据
  React.useEffect(() => {
    if (open && record) {
      loadTemplateData()
    }
  }, [open, record])

  const loadTemplateData = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://127.0.0.1:8001/api/prompt-templates/${record.id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setFormData({
          name: data.name || '',
          description: data.description || '',
          template_type: data.template_type || 'reply',
          system_prompt: data.system_prompt || '',
          user_prompt_template: data.user_prompt_template || '',
          variables: data.variables || '',
          recommended_model: data.recommended_model || 'gpt-4o-mini',
          is_active: data.is_active ?? true,
          is_default: data.is_default ?? false,
        })
      } else {
        notify('加载模板失败', { type: 'error' })
      }
    } catch (error) {
      console.error('加载失败:', error)
      notify('加载失败', { type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async () => {
    if (!formData.name.trim()) {
      notify('请输入模板名称', { type: 'warning' })
      return
    }

    if (!formData.user_prompt_template.trim()) {
      notify('请输入用户提示词模板', { type: 'warning' })
      return
    }

    setUpdating(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:8001/api/prompt-templates/${record.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        notify('模板更新成功', { type: 'success' })
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
      <DialogTitle>编辑提示词模板</DialogTitle>
      <DialogContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
            <LinearProgress sx={{ width: '50%' }} />
            <Typography sx={{ ml: 2 }}>加载中...</Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Typography variant="caption" color="info.main">
              模板ID: {record?.id} | 使用次数: {record?.usage_count || 0} | 成功率:{' '}
              {((record?.success_rate || 0) * 100).toFixed(0)}%
            </Typography>

            {/* 模板名称 */}
            <MuiTextField
              label="模板名称"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
              disabled={updating}
            />

            {/* 模板描述 */}
            <MuiTextField
              label="模板描述"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
              disabled={updating}
            />

            {/* 模板类型和推荐模型 */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl fullWidth disabled={updating}>
                <InputLabel>模板类型</InputLabel>
                <Select
                  value={formData.template_type}
                  label="模板类型"
                  onChange={(e) => setFormData({ ...formData, template_type: e.target.value })}
                >
                  {TEMPLATE_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth disabled={updating}>
                <InputLabel>推荐模型</InputLabel>
                <Select
                  value={formData.recommended_model}
                  label="推荐模型"
                  onChange={(e) => setFormData({ ...formData, recommended_model: e.target.value })}
                >
                  {AI_MODELS.map((model) => (
                    <MenuItem key={model.value} value={model.value}>
                      {model.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {/* 系统提示词 */}
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="subtitle2" sx={{ color: '#1976d2' }}>
                  🤖 系统提示词（可选）
                </Typography>
                <Tooltip title="由你设置，告诉AI它的角色和行为规范">
                  <IconButton size="small">
                    <HelpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <MuiTextField
                value={formData.system_prompt}
                onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                fullWidth
                multiline
                rows={3}
                disabled={updating}
                helperText="ℹ️ 由你（管理员）来设置，告诉AI“你是谁”"
              />
            </Box>

            {/* 用户提示词模板 */}
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="subtitle2" sx={{ color: '#d32f2f' }}>
                  ✨ 用户提示词模板（必填）
                </Typography>
                <Tooltip title="系统会自动将变量替换为实际内容">
                  <IconButton size="small">
                    <HelpIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <MuiTextField
                value={formData.user_prompt_template}
                onChange={(e) => setFormData({ ...formData, user_prompt_template: e.target.value })}
                fullWidth
                required
                multiline
                rows={12}
                disabled={updating}
                sx={{
                  '& .MuiInputBase-root': {
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                  },
                }}
                helperText="ℹ️ 系统会自动将 {subject}, {body} 等变量替换为实际的邮件内容"
              />
            </Box>

            {/* 变量说明 */}
            <MuiTextField
              label="变量说明（JSON格式，可选）"
              value={formData.variables}
              onChange={(e) => setFormData({ ...formData, variables: e.target.value })}
              fullWidth
              multiline
              rows={3}
              disabled={updating}
              sx={{
                '& .MuiInputBase-root': {
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                },
              }}
            />

            {/* 选项 */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    disabled={updating}
                  />
                }
                label="启用此模板"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.is_default}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                    disabled={updating}
                  />
                }
                label="设为默认模板"
              />
            </Box>

            {updating && (
              <Box>
                <LinearProgress />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                  正在保存...
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

// 预览对话框
const PreviewDialog = ({
  open,
  onClose,
  record,
}: {
  open: boolean
  onClose: () => void
  record: any
}) => {
  const [previewData, setPreviewData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [testParams, setTestParams] = useState({
    subject: 'Inquiry about Men\'s Underwear',
    body: 'Hi, I\'m interested in your products. What is the MOQ?',
    tone: 'professional',
  })
  const notify = useNotify()

  const loadPreview = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const params = new URLSearchParams({
        subject: testParams.subject,
        body: testParams.body,
        tone: testParams.tone,
      })
      
      const response = await fetch(
        `http://127.0.0.1:8001/api/prompt-templates/${record.id}/preview?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setPreviewData(data)
      } else {
        notify('加载预览失败', { type: 'error' })
      }
    } catch (error) {
      console.error('加载失败:', error)
      notify('加载失败', { type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    if (open && record) {
      loadPreview()
    }
  }, [open, record])

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle sx={{ pb: 1.5 }}>预览提示词模板</DialogTitle>
      <DialogContent sx={{ pt: 1.5 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <LinearProgress sx={{ width: '50%' }} />
          </Box>
        ) : previewData ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* 测试参数 - 优化为横向紧凑布局 */}
            <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1, border: '1px solid #e0e0e0' }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontSize: '0.875rem', fontWeight: 600 }}>
                测试参数：
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
                <MuiTextField
                  size="small"
                  label="邮件主题"
                  value={testParams.subject}
                  onChange={(e) => setTestParams({ ...testParams, subject: e.target.value })}
                  sx={{ flex: 1 }}
                />
                <MuiTextField
                  size="small"
                  label="邮件正文"
                  value={testParams.body}
                  onChange={(e) => setTestParams({ ...testParams, body: e.target.value })}
                  sx={{ flex: 1.5 }}
                />
                <FormControl size="small" sx={{ minWidth: 100 }}>
                  <InputLabel>语气</InputLabel>
                  <Select
                    value={testParams.tone}
                    label="语气"
                    onChange={(e) => setTestParams({ ...testParams, tone: e.target.value })}
                  >
                    <MenuItem value="professional">专业</MenuItem>
                    <MenuItem value="friendly">友好</MenuItem>
                    <MenuItem value="formal">正式</MenuItem>
                    <MenuItem value="enthusiastic">热情</MenuItem>
                  </Select>
                </FormControl>
                <Button variant="outlined" onClick={loadPreview} size="small" sx={{ minWidth: 90 }}>
                  重新预览
                </Button>
              </Box>
            </Box>

            {/* 系统提示词 */}
            {previewData.system_prompt && (
              <Box>
                <Typography variant="subtitle2" sx={{ color: '#1976d2', mb: 0.5, fontSize: '0.875rem', fontWeight: 600 }}>
                  📋 系统提示词：
                </Typography>
                <Box
                  sx={{
                    bgcolor: '#e3f2fd',
                    p: 1.5,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.8125rem',
                    whiteSpace: 'pre-wrap',
                    border: '1px solid #bbdefb',
                  }}
                >
                  {previewData.system_prompt}
                </Box>
              </Box>
            )}

            {/* 渲染后的提示词 */}
            <Box>
              <Typography variant="subtitle2" sx={{ color: '#2e7d32', mb: 0.5, fontSize: '0.875rem', fontWeight: 600 }}>
                ✨ 渲染后的提示词：
              </Typography>
              <Box
                sx={{
                  bgcolor: '#f1f8e9',
                  p: 1.5,
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.8125rem',
                  whiteSpace: 'pre-wrap',
                  maxHeight: 400,
                  overflowY: 'auto',
                  border: '1px solid #c5e1a5',
                }}
              >
                {previewData.rendered_prompt}
              </Box>
            </Box>

            {/* 推荐模型 */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="subtitle2" sx={{ fontSize: '0.875rem' }}>
                🤖 推荐模型:
              </Typography>
              <Chip label={previewData.recommended_model} size="small" color="primary" variant="outlined" />
            </Box>
          </Box>
        ) : (
          <Typography color="text.secondary">无预览数据</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>关闭</Button>
      </DialogActions>
    </Dialog>
  )
}

// 过滤器
const templateFilters = [
  <TextInput label="搜索" source="q" alwaysOn />,
  <SelectInput
    label="模板类型"
    source="template_type"
    choices={TEMPLATE_TYPES}
  />,
  <SelectInput
    label="状态"
    source="is_active"
    choices={[
      { id: 'true', name: '启用' },
      { id: 'false', name: '禁用' },
    ]}
  />,
]

// 模板列表
export const PromptTemplateList = () => (
  <List
    filters={templateFilters}
    actions={<ListActions />}
    sort={{ field: 'created_at', order: 'DESC' }}
    perPage={25}
  >
    <Datagrid bulkActionButtons={false}>
      <FunctionField
        label="模板名称"
        render={(record: any) => (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {record.is_default && <StarIcon sx={{ fontSize: 18, color: '#f59e0b' }} />}
            {record.name}
          </Box>
        )}
      />
      <TextField source="description" label="描述" />
      <FunctionField
        label="类型"
        render={(record: any) => {
          const type = TEMPLATE_TYPES.find((t) => t.value === record.template_type)
          return <Chip label={type?.label || record.template_type} size="small" color="primary" />
        }}
      />
      <FunctionField
        label="推荐模型"
        render={(record: any) => {
          const model = AI_MODELS.find((m) => m.value === record.recommended_model)
          return <Chip label={model?.label || record.recommended_model} size="small" variant="outlined" />
        }}
      />
      <FunctionField
        label="使用统计"
        render={(record: any) => (
          <Box>
            <Typography variant="caption">
              {record.usage_count || 0} 次 | {((record.success_rate || 0) * 100).toFixed(0)}%
            </Typography>
          </Box>
        )}
      />
      <BooleanField source="is_active" label="启用" />
      <DateField source="created_at" label="创建时间" showTime />
      <FunctionField label="操作" render={() => <TemplateActions />} />
    </Datagrid>
  </List>
)

export default {
  list: PromptTemplateList,
}
