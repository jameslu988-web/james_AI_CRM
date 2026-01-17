import { 
  List, 
  Datagrid, 
  TextField, 
  BooleanField, 
  Edit, 
  Create, 
  SimpleForm, 
  TextInput, 
  BooleanInput, 
  DeleteButton,
  TopToolbar,
  CreateButton,
  useNotify,
  useRefresh,
  useRecordContext,
  useInput,
  SaveButton,
  Toolbar,
  useDataProvider,
  useRedirect
} from 'react-admin'
import { Box, Chip, Typography, IconButton, Select, MenuItem, Divider } from '@mui/material'
import StarIcon from '@mui/icons-material/Star'
import StarBorderIcon from '@mui/icons-material/StarBorder'
import { useRef, useState, useEffect } from 'react'
import UndoIcon from '@mui/icons-material/Undo'
import RedoIcon from '@mui/icons-material/Redo'
import FormatBoldIcon from '@mui/icons-material/FormatBold'
import FormatItalicIcon from '@mui/icons-material/FormatItalic'
import FormatUnderlinedIcon from '@mui/icons-material/FormatUnderlined'
import FormatColorTextIcon from '@mui/icons-material/FormatColorText'
import FormatColorFillIcon from '@mui/icons-material/FormatColorFill'
import FormatAlignLeftIcon from '@mui/icons-material/FormatAlignLeft'
import FormatAlignCenterIcon from '@mui/icons-material/FormatAlignCenter'
import FormatAlignRightIcon from '@mui/icons-material/FormatAlignRight'
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted'
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered'
import InsertLinkIcon from '@mui/icons-material/InsertLink'
import InsertPhotoIcon from '@mui/icons-material/InsertPhoto'
import CloseIcon from '@mui/icons-material/Close'

// 富文本输入组件（与表单集成）- 使用隐藏input存储数据
const RichTextInput = ({ source, onContentChange }: { 
  source: string, 
  onContentChange?: (content: string, domRef: HTMLDivElement | null) => void 
}) => {
  const { field } = useInput({ source })
  const editorRef = useRef<HTMLDivElement>(null)
  const record = useRecordContext()
  const [initialized, setInitialized] = useState(false)
  
  // 初始化编辑器内容
  useEffect(() => {
    if (record && record[source] !== undefined && !initialized) {
      console.log('Initializing editor with content length:', record[source]?.length || 0)
      const initialContent = record[source] || ''
      if (editorRef.current) {
        editorRef.current.innerHTML = initialContent
      }
      setInitialized(true)
    }
  }, [record, source, initialized])
  
  // 更新内容
  const updateContent = (newContent: string) => {
    console.log('updateContent called, length:', newContent.length)
    // 直接调用field.onChange，并等待一个微小的延迟确保更新
    setTimeout(() => {
      field.onChange(newContent)
      console.log('Field updated')
    }, 0)
    
    if (onContentChange) {
      onContentChange(newContent, editorRef.current)
    }
  }
  
  // 富文本编辑器命令
  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value)
    if (editorRef.current) {
      const newContent = editorRef.current.innerHTML
      updateContent(newContent)
    }
  }
  
  // 插入链接
  const insertLink = () => {
    const url = prompt('请输入链接地址:', 'https://')
    if (url) execCommand('createLink', url)
  }
  
  // 改变字体
  const changeFontFamily = (font: string) => execCommand('fontName', font)
  
  // 改变字号
  const changeFontSize = (size: string) => {
    const sizeMap: { [key: string]: string } = {
      '12px': '2', '14px': '3', '16px': '4', '18px': '5', '20px': '6', '24px': '7'
    }
    execCommand('fontSize', sizeMap[size] || '3')
  }
  
  // 插入图片
  const insertImage = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = (e: any) => {
      const file = e.target.files[0]
      if (!file) return
      
      if (file.size > 500 * 1024) {
        alert('图片大小不能超过500KB')
        return
      }
      
      const reader = new FileReader()
      reader.onload = (event: any) => {
        const img = document.createElement('img')
        img.src = event.target.result
        img.style.maxWidth = '100%'
        img.style.height = 'auto'
        
        if (editorRef.current) {
          editorRef.current.focus()
          const selection = window.getSelection()
          if (selection && selection.rangeCount > 0) {
            const range = selection.getRangeAt(0)
            range.deleteContents()
            range.insertNode(img)
            range.collapse(false)
          } else {
            editorRef.current.appendChild(img)
          }
          
          const newContent = editorRef.current.innerHTML
          updateContent(newContent)
        }
      }
      reader.readAsDataURL(file)
    }
    input.click()
  }
  
  if (!initialized) {
    return (
      <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1, textAlign: 'center', color: '#999' }}>
        加载中...
      </Box>
    )
  }
  
  return (
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
        <IconButton size="small" onClick={() => execCommand('undo')} sx={{ width: 32, height: 32 }} title="撤销">
          <UndoIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('redo')} sx={{ width: 32, height: 32 }} title="重做">
          <RedoIcon sx={{ fontSize: 18 }} />
        </IconButton>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 字体选择 */}
        <Select size="small" defaultValue="Arial" onChange={(e) => changeFontFamily(e.target.value)}
          sx={{ minWidth: 120, height: 32, fontSize: '13px', bgcolor: 'white' }}>
          <MenuItem value="Arial">Arial</MenuItem>
          <MenuItem value="SimSun">宋体</MenuItem>
          <MenuItem value="Microsoft YaHei">微软雅黑</MenuItem>
          <MenuItem value="SimHei">黑体</MenuItem>
          <MenuItem value="KaiTi">楷体</MenuItem>
          <MenuItem value="Courier New">Courier New</MenuItem>
          <MenuItem value="Times New Roman">Times New Roman</MenuItem>
        </Select>
        
        {/* 字号选择 */}
        <Select size="small" defaultValue="14px" onChange={(e) => changeFontSize(e.target.value)}
          sx={{ width: 90, height: 32, fontSize: '13px', bgcolor: 'white' }}>
          <MenuItem value="12px">12px</MenuItem>
          <MenuItem value="14px">14px</MenuItem>
          <MenuItem value="16px">16px</MenuItem>
          <MenuItem value="18px">18px</MenuItem>
          <MenuItem value="20px">20px</MenuItem>
          <MenuItem value="24px">24px</MenuItem>
        </Select>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 文字格式 */}
        <IconButton size="small" onClick={() => execCommand('bold')} sx={{ width: 32, height: 32 }} title="加粗">
          <FormatBoldIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('italic')} sx={{ width: 32, height: 32 }} title="斜体">
          <FormatItalicIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('underline')} sx={{ width: 32, height: 32 }} title="下划线">
          <FormatUnderlinedIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('strikeThrough')} sx={{ width: 32, height: 32 }} title="删除线">
          <Box component="span" sx={{ fontSize: 18, fontWeight: 'bold', textDecoration: 'line-through' }}>S</Box>
        </IconButton>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 文字颜色 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <IconButton size="small" sx={{ width: 32, height: 32 }} title="文字颜色">
            <FormatColorTextIcon sx={{ fontSize: 18 }} />
          </IconButton>
          <input type="color" onChange={(e) => execCommand('foreColor', e.target.value)}
            style={{ width: 24, height: 24, border: 'none', cursor: 'pointer' }} />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <IconButton size="small" sx={{ width: 32, height: 32 }} title="背景颜色">
            <FormatColorFillIcon sx={{ fontSize: 18 }} />
          </IconButton>
          <input type="color" onChange={(e) => execCommand('backColor', e.target.value)}
            style={{ width: 24, height: 24, border: 'none', cursor: 'pointer' }} />
        </Box>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 对齐方式 */}
        <IconButton size="small" onClick={() => execCommand('justifyLeft')} sx={{ width: 32, height: 32 }} title="左对齐">
          <FormatAlignLeftIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('justifyCenter')} sx={{ width: 32, height: 32 }} title="居中对齐">
          <FormatAlignCenterIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('justifyRight')} sx={{ width: 32, height: 32 }} title="右对齐">
          <FormatAlignRightIcon sx={{ fontSize: 18 }} />
        </IconButton>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 列表 */}
        <IconButton size="small" onClick={() => execCommand('insertUnorderedList')} sx={{ width: 32, height: 32 }} title="无序列表">
          <FormatListBulletedIcon sx={{ fontSize: 18 }} />
        </IconButton>
        <IconButton size="small" onClick={() => execCommand('insertOrderedList')} sx={{ width: 32, height: 32 }} title="有序列表">
          <FormatListNumberedIcon sx={{ fontSize: 18 }} />
        </IconButton>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 插入链接 */}
        <IconButton size="small" onClick={insertLink} sx={{ width: 32, height: 32 }} title="插入链接">
          <InsertLinkIcon sx={{ fontSize: 18 }} />
        </IconButton>
        
        {/* 插入图片 */}
        <IconButton size="small" onClick={insertImage} sx={{ width: 32, height: 32 }} title="插入图片">
          <InsertPhotoIcon sx={{ fontSize: 18 }} />
        </IconButton>
        
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        
        {/* 清除格式 */}
        <IconButton size="small" onClick={() => execCommand('removeFormat')} sx={{ width: 32, height: 32 }} title="清除格式">
          <CloseIcon sx={{ fontSize: 18 }} />
        </IconButton>
      </Box>
      
      {/* 编辑器 */}
      <Box
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning
        onInput={(e: any) => {
          const newContent = e.currentTarget.innerHTML
          updateContent(newContent)
        }}
        onKeyDown={(e) => {
          if (e.key === 'Tab') {
            e.preventDefault()
            execCommand('insertHTML', '&nbsp;&nbsp;&nbsp;&nbsp;')
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
  )
}

// 自定义富文本输入组件
const HtmlEditor = (props: any) => {
  return (
    <Box>
      <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
        {props.label}
      </Typography>
      <Box
        component="textarea"
        {...props}
        rows={10}
        style={{
          width: '100%',
          padding: '12px',
          fontSize: '14px',
          fontFamily: 'monospace',
          border: '1px solid #d0d0d0',
          borderRadius: '4px',
          resize: 'vertical'
        }}
      />
    </Box>
  )
}

// 列表操作栏
const ListActions = () => (
  <TopToolbar>
    <CreateButton label="新增签名" />
  </TopToolbar>
)

// 默认签名标记
const DefaultBadge = () => {
  const record = useRecordContext()
  if (!record) return null
  
  return record.is_default ? (
    <Chip 
      icon={<StarIcon sx={{ fontSize: 16 }} />}
      label="默认" 
      size="small" 
      sx={{ 
        bgcolor: '#fef3c7', 
        color: '#92400e',
        height: 22,
        fontSize: '11px',
        fontWeight: 500
      }} 
    />
  ) : (
    <StarBorderIcon sx={{ fontSize: 18, color: '#d0d0d0' }} />
  )
}

// 签名内容预览
const SignaturePreview = () => {
  const record = useRecordContext()
  if (!record) return null
  
  const previewText = record.content
    ? record.content.replace(/<[^>]*>/g, '').substring(0, 50)
    : '(无内容)'
  
  return (
    <Typography 
      variant="body2" 
      sx={{ 
        color: '#666',
        fontSize: '13px',
        maxWidth: 300,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }}
    >
      {previewText}
    </Typography>
  )
}

// 签名列表
export const SignatureList = () => (
  <List
    actions={<ListActions />}
    sx={{
      '& .RaList-content': {
        boxShadow: 'none',
        border: '1px solid #e5e7eb'
      }
    }}
  >
    <Datagrid 
      rowClick="edit"
      sx={{
        '& .RaDatagrid-headerCell': {
          bgcolor: '#fafafa',
          fontWeight: 600,
          fontSize: '13px'
        },
        '& .RaDatagrid-rowCell': {
          fontSize: '13px'
        }
      }}
    >
      <DefaultBadge />
      <TextField source="name" label="签名名称" />
      <SignaturePreview />
      <TextField source="created_at" label="创建时间" />
      <DeleteButton 
        label="" 
        confirmTitle="删除签名"
        confirmContent="确定要删除这个签名吗？"
      />
    </Datagrid>
  </List>
)

// 自定义工具栏，使用自定义保存逻辑
const CustomToolbar = ({ contentRef, editorDomRef }: { 
  contentRef: React.RefObject<string>,
  editorDomRef: React.RefObject<HTMLDivElement | null>
}) => {
  const notify = useNotify()
  const redirect = useRedirect()
  const refresh = useRefresh()
  const dataProvider = useDataProvider()
  const record = useRecordContext()
  const [saving, setSaving] = useState(false)
  
  const handleSave = async () => {
    setSaving(true)
    try {
      // 从 DOM 获取最新内容
      const latestContent = editorDomRef.current?.innerHTML || contentRef.current || ''
      
      // 获取表单中的其他字段值
      const nameInput = document.querySelector('input[name="name"]') as HTMLInputElement
      const isDefaultInput = document.querySelector('input[name="is_default"]') as HTMLInputElement
      
      const dataToSave = {
        name: nameInput?.value || record.name,
        content: latestContent,
        is_default: isDefaultInput?.checked || record.is_default
      }
      
      console.log('=== Saving with custom handler ===')
      console.log('Content length:', latestContent.length)
      console.log('Content preview:', latestContent.substring(0, 100))
      console.log('Data:', { name: dataToSave.name, is_default: dataToSave.is_default, content_length: dataToSave.content.length })
      
      await dataProvider.update('signatures', {
        id: record.id,
        data: dataToSave,
        previousData: record
      })
      
      notify('签名已更新', { type: 'success' })
      refresh()
      redirect('list', 'signatures')
    } catch (error: any) {
      console.error('Save error:', error)
      notify(error.message || '保存失败', { type: 'error' })
    } finally {
      setSaving(false)
    }
  }
  
  return (
    <Toolbar>
      <SaveButton 
        label="保存"
        onClick={handleSave}
        disabled={saving}
        type="button"
      />
    </Toolbar>
  )
}

// 签名编辑
export const SignatureEdit = () => {
  const notify = useNotify()
  const refresh = useRefresh()
  const record = useRecordContext()
  const [previewContent, setPreviewContent] = useState('')
  const contentRef = useRef<string>('')  // 保存最新内容
  const editorDomRef = useRef<HTMLDivElement | null>(null)  // 保存编辑器DOM引用
  
  // 初始化预览内容
  useEffect(() => {
    if (record?.content) {
      setPreviewContent(record.content)
      contentRef.current = record.content
    }
  }, [record])
  
  const onSuccess = () => {
    notify('签名已更新', { type: 'success' })
    refresh()
  }
  
  // 添加 transform 函数来查看提交的数据
  const transform = (data: any) => {
    // 直接从编辑器DOM获取最新内容
    const latestContent = editorDomRef.current?.innerHTML || contentRef.current
    const finalData = {
      ...data,
      content: latestContent
    }
    console.log('=== Transform data before submit ===')
    console.log('Latest content length:', latestContent.length)
    console.log('Content preview:', latestContent.substring(0, 100))
    return finalData
  }
  
  // 内容变化回调
  const handleContentChange = (newContent: string, domRef: HTMLDivElement | null) => {
    contentRef.current = newContent
    editorDomRef.current = domRef
    setPreviewContent(newContent)
  }
  
  return (
    <Edit mutationOptions={{ onSuccess }}>
      <SimpleForm toolbar={<CustomToolbar contentRef={contentRef} editorDomRef={editorDomRef} />}>
        <Box sx={{ width: '100%', maxWidth: 900 }}>
          {/* 签名名称 */}
          <Box sx={{ mb: 3 }}>
            <Typography sx={{ fontSize: '14px', color: '#333', mb: 1.5, fontWeight: 500 }}>名称</Typography>
            <TextInput 
              source="name" 
              label="" 
              fullWidth 
              required 
              sx={{ 
                '& .MuiOutlinedInput-root': {
                  fontSize: '14px',
                  bgcolor: '#fafafa'
                }
              }}
            />
          </Box>
          
          {/* 签名内容 */}
          <Box sx={{ mb: 3 }}>
            <Typography sx={{ fontSize: '14px', color: '#333', mb: 1.5, fontWeight: 500 }}>内容</Typography>
            <RichTextInput 
              source="content" 
              onContentChange={handleContentChange}
            />
          </Box>
          
          {/* 预览区域 */}
          <Box sx={{ 
            p: 2.5, 
            bgcolor: '#f9fafb', 
            borderRadius: 1,
            border: '1px solid #e5e7eb',
            mb: 3
          }}>
            <Typography variant="caption" sx={{ mb: 1.5, display: 'block', color: '#666', fontWeight: 500 }}>
              预览效果
            </Typography>
            <Box 
              dangerouslySetInnerHTML={{ __html: previewContent || '<p style="color: #999;">（暂无内容）</p>' }}
              sx={{ 
                minHeight: 60,
                fontSize: '14px',
                color: '#333',
                '& img': {
                  maxWidth: '100%',
                  height: 'auto'
                },
                '& a': {
                  color: '#1677ff'
                }
              }}
            />
          </Box>
          
          {/* 默认签名选项 */}
          <BooleanInput 
            source="is_default" 
            label="设为默认签名" 
            helperText="设为默认后,发送邮件时会自动使用此签名"
          />
        </Box>
      </SimpleForm>
    </Edit>
  )
}

// 签名创建
export const SignatureCreate = () => {
  const notify = useNotify()
  const refresh = useRefresh()
  
  const onSuccess = () => {
    notify('签名已创建', { type: 'success' })
    refresh()
  }
  
  const defaultValues = {
    name: '',
    content: '<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">\n  <p>Best regards,</p>\n  <p><strong>Your Name</strong></p>\n  <p>Your Title</p>\n  <p>Company Name</p>\n  <p>Email: your@email.com | Tel: +86 xxx xxxx</p>\n</div>',
    is_default: false
  }
  
  return (
    <Create mutationOptions={{ onSuccess }}>
      <SimpleForm defaultValues={defaultValues}>
        <Box sx={{ width: '100%', maxWidth: 800 }}>
          <TextInput 
            source="name" 
            label="签名名称" 
            fullWidth 
            required 
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ mb: 2 }}>
            <HtmlEditor 
              source="content" 
              label="签名内容（HTML格式）"
            />
          </Box>
          
          <Box sx={{ 
            p: 2, 
            bgcolor: '#f0f9ff', 
            borderRadius: 1,
            border: '1px solid #bae6fd',
            mb: 2
          }}>
            <Typography variant="caption" sx={{ mb: 1, display: 'block', color: '#0369a1', fontWeight: 500 }}>
              💡 提示
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '13px', color: '#0c4a6e' }}>
              • 支持HTML格式，可以设置字体、颜色、链接等<br />
              • 建议保持签名简洁专业<br />
              • 可以包含公司Logo图片链接
            </Typography>
          </Box>
          
          <BooleanInput 
            source="is_default" 
            label="设为默认签名" 
            helperText="设为默认后，发送邮件时会自动使用此签名"
          />
        </Box>
      </SimpleForm>
    </Create>
  )
}
