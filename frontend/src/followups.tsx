import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm } from 'react-admin'

const followupFilters = [
  <TextInput key="search" label="搜索主题/内容" source="search" alwaysOn />, 
  <TextInput key="customer_id" label="客户ID" source="customer_id" />, 
  <SelectInput key="followup_type" label="类型" source="followup_type" choices={[
    { id: 'Email', name: 'Email' },
    { id: 'Phone', name: 'Phone' },
    { id: 'Meeting', name: 'Meeting' },
    { id: 'WhatsApp', name: 'WhatsApp' },
    { id: 'LinkedIn', name: 'LinkedIn' },
  ]} />
]

export const FollowupList = (props:any) => (
  <List {...props} perPage={20} filters={followupFilters}>
    <Datagrid rowClick="edit">
      <TextField source="customer_id" label="客户ID" />
      <TextField source="followup_type" label="类型" />
      <TextField source="subject" label="主题" />
      <TextField source="created_by" label="跟进人" />
      <TextField source="created_at" label="时间" />
    </Datagrid>
  </List>
)

export const FollowupCreate = (props:any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="customer_id" label="客户ID" />
      <SelectInput source="followup_type" label="类型" choices={[
        { id: 'Email', name: 'Email' },
        { id: 'Phone', name: 'Phone' },
        { id: 'Meeting', name: 'Meeting' },
        { id: 'WhatsApp', name: 'WhatsApp' },
        { id: 'LinkedIn', name: 'LinkedIn' },
      ]} />
      <TextInput source="subject" label="主题" fullWidth />
      <TextInput source="content" label="内容" multiline fullWidth />
      <TextInput source="result" label="结果" />
      <TextInput source="next_action" label="下一步行动" />
      <TextInput source="created_by" label="跟进人" />
    </SimpleForm>
  </Create>
)

export const FollowupEdit = (props:any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="customer_id" label="客户ID" />
      <SelectInput source="followup_type" label="类型" choices={[
        { id: 'Email', name: 'Email' },
        { id: 'Phone', name: 'Phone' },
        { id: 'Meeting', name: 'Meeting' },
        { id: 'WhatsApp', name: 'WhatsApp' },
        { id: 'LinkedIn', name: 'LinkedIn' },
      ]} />
      <TextInput source="subject" label="主题" fullWidth />
      <TextInput source="content" label="内容" multiline fullWidth />
      <TextInput source="result" label="结果" />
      <TextInput source="next_action" label="下一步行动" />
      <TextInput source="created_by" label="跟进人" />
    </SimpleForm>
  </Edit>
)
