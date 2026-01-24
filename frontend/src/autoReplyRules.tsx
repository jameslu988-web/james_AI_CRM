/**
 * 自动回复规则管理页面
 * 用户可以配置哪些邮件类型需要自动回复
 */
import {
  List,
  Datagrid,
  TextField,
  BooleanField,
  NumberField,
  DateField,
  EditButton,
  DeleteButton,
  Create,
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
  CreateButton,
  ExportButton,
  ListButton,
} from 'react-admin'
import { Chip, Box } from '@mui/material'

// 邮件类型选项
const categoryChoices = [
  { id: 'inquiry', name: '新客询盘' },
  { id: 'quotation', name: '报价跟进' },
  { id: 'sample', name: '样品阶段' },
  { id: 'order', name: '订单确认' },
  { id: 'complaint', name: '售后服务' },
  { id: 'follow_up', name: '老客维护' },
  { id: 'spam', name: '垃圾营销' },
]

// 审核方式选项
const approvalMethodChoices = [
  { id: 'system', name: '系统内审核' },
  { id: 'wechat', name: '企业微信' },
  { id: 'email', name: '邮件通知' },
]

// 自定义列表顶部操作栏
const ListActions = () => (
  <TopToolbar>
    <CreateButton label="新建规则" />
    <ExportButton label="导出" />
  </TopToolbar>
)

// 编辑/创建页面的顶部操作栏
const EditActions = () => (
  <TopToolbar>
    <ListButton label="返回列表" />
  </TopToolbar>
)

// 编辑页面使用默认工具栏（包含保存按钮）
const CreateActions = () => (
  <TopToolbar>
    <ListButton label="返回列表" />
  </TopToolbar>
)

// 邮件类型显示
const CategoryField = () => {
  const record = useRecordContext()
  if (!record) return null
  
  const category = categoryChoices.find(c => c.id === record.email_category)
  const colors: Record<string, string> = {
    inquiry: '#52c41a',
    quotation: '#1677ff',
    sample: '#fa8c16',
    order: '#f5222d',
    complaint: '#722ed1',
    follow_up: '#13c2c2',
    spam: '#8c8c8c',
  }
  
  return (
    <Chip 
      label={category?.name || record.email_category} 
      size="small"
      sx={{ 
        bgcolor: colors[record.email_category] || '#d9d9d9',
        color: 'white'
      }}
    />
  )
}

// 列表组件
export const AutoReplyRuleList = () => (
  <List
    actions={<ListActions />}
    sort={{ field: 'priority', order: 'DESC' }}
    perPage={25}
  >
    <Datagrid rowClick="edit">
      <TextField source="id" label="ID" />
      <TextField source="rule_name" label="规则名称" />
      <FunctionField
        label="邮件类型"
        render={(record: any) => {
          const category = categoryChoices.find(c => c.id === record.email_category)
          const colors: Record<string, string> = {
            inquiry: '#52c41a',
            quotation: '#1677ff',
            sample: '#fa8c16',
            order: '#f5222d',
            complaint: '#722ed1',
            follow_up: '#13c2c2',
            spam: '#8c8c8c',
          }
          return (
            <Chip 
              label={category?.name || record.email_category} 
              size="small"
              sx={{ 
                bgcolor: colors[record.email_category] || '#d9d9d9',
                color: 'white'
              }}
            />
          )
        }}
      />
      <BooleanField source="is_enabled" label="启用" />
      <BooleanField source="auto_generate_reply" label="自动生成回复" />
      <BooleanField source="require_approval" label="需要审核" />
      <NumberField source="priority" label="优先级" />
      <NumberField source="triggered_count" label="触发次数" />
      <NumberField source="approved_count" label="通过次数" />
      <NumberField source="rejected_count" label="拒绝次数" />
      <FunctionField
        label="通过率"
        render={(record: any) => {
          const total = record.approved_count + record.rejected_count
          if (total === 0) return '-'
          const rate = ((record.approved_count / total) * 100).toFixed(1)
          return `${rate}%`
        }}
      />
      <DateField source="created_at" label="创建时间" showTime />
      <EditButton label="编辑" />
      <DeleteButton label="删除" />
    </Datagrid>
  </List>
)

// 创建组件
export const AutoReplyRuleCreate = () => (
  <Create redirect="list">
    <SimpleForm toolbar={undefined}> {/* 使用默认工具栏 */}
      <TextInput 
        source="rule_name" 
        label="规则名称" 
        validate={required()}
        fullWidth
      />
      
      <SelectInput 
        source="email_category" 
        label="邮件类型" 
        choices={categoryChoices}
        validate={required()}
      />
      
      <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
        <BooleanInput 
          source="is_enabled" 
          label="启用规则" 
        />
        <BooleanInput 
          source="auto_generate_reply" 
          label="自动生成回复" 
        />
        <BooleanInput 
          source="require_approval" 
          label="需要人工审核" 
        />
      </Box>
      
      <SelectInput 
        source="approval_method" 
        label="审核方式" 
        choices={approvalMethodChoices}
        defaultValue="system"
      />
      
      <NumberInput 
        source="approval_timeout_hours" 
        label="审核超时时间（小时）" 
        defaultValue={24}
        min={1}
        max={168}
      />
      
      <NumberInput 
        source="priority" 
        label="优先级（数字越大越优先）" 
        defaultValue={0}
        helperText="当多个规则匹配时，优先级高的规则生效"
      />
      
      <TextInput 
        source="conditions" 
        label="额外触发条件（JSON）" 
        multiline
        rows={3}
        fullWidth
        helperText='例如：{"purchase_intent_min": 50}'
      />
    </SimpleForm>
  </Create>
)

// 编辑组件
export const AutoReplyRuleEdit = () => (
  <Edit>
    <SimpleForm toolbar={undefined}> {/* 使用默认工具栏，包含保存按钮 */}
      <TextInput 
        source="rule_name" 
        label="规则名称" 
        validate={required()}
        fullWidth
      />
      
      <SelectInput 
        source="email_category" 
        label="邮件类型" 
        choices={categoryChoices}
        validate={required()}
      />
      
      <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
        <BooleanInput 
          source="is_enabled" 
          label="启用规则"
        />
        <BooleanInput 
          source="auto_generate_reply" 
          label="自动生成回复"
        />
        <BooleanInput 
          source="require_approval" 
          label="需要人工审核"
        />
      </Box>
      
      <SelectInput 
        source="approval_method" 
        label="审核方式" 
        choices={approvalMethodChoices}
      />
      
      <NumberInput 
        source="approval_timeout_hours" 
        label="审核超时时间（小时）" 
        min={1}
        max={168}
      />
      
      <NumberInput 
        source="priority" 
        label="优先级（数字越大越优先）"
        helperText="当多个规则匹配时，优先级高的规则生效"
      />
      
      <TextInput 
        source="conditions" 
        label="额外触发条件（JSON）" 
        multiline
        rows={3}
        fullWidth
        helperText='例如：{"purchase_intent_min": 50}'
      />
      
      <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <h4>统计信息</h4>
        <p>触发次数：<TextField source="triggered_count" /></p>
        <p>通过次数：<TextField source="approved_count" /></p>
        <p>拒绝次数：<TextField source="rejected_count" /></p>
      </Box>
    </SimpleForm>
  </Edit>
)
