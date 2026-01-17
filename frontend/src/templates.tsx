import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, BooleanInput, NumberInput } from 'react-admin'

const templateFilters = [
  <TextInput key="search" label="搜索名称/主题" source="search" alwaysOn />, 
  <SelectInput key="category" label="分类" source="category" choices={[
    { id: 'Cold Email', name: 'Cold Email' },
    { id: 'Follow-up', name: 'Follow-up' },
    { id: 'Quotation', name: 'Quotation' },
    { id: 'Thank You', name: 'Thank You' },
  ]} />, 
  <SelectInput key="language" label="语言" source="language" choices={[
    { id: 'en', name: 'English' },
    { id: 'zh', name: '中文' },
    { id: 'es', name: 'Español' },
    { id: 'fr', name: 'Français' },
  ]} />
]

export const TemplateList = (props:any) => (
  <List {...props} perPage={20} filters={templateFilters}>
    <Datagrid rowClick="edit">
      <TextField source="name" label="名称" />
      <TextField source="category" label="分类" />
      <TextField source="language" label="语言" />
      <TextField source="usage_count" label="使用次数" />
      <TextField source="success_rate" label="成功率" />
      <TextField source="is_active" label="是否启用" />
    </Datagrid>
  </List>
)

export const TemplateCreate = (props:any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="name" label="名称" />
      <SelectInput source="category" label="分类" choices={[
        { id: 'Cold Email', name: 'Cold Email' },
        { id: 'Follow-up', name: 'Follow-up' },
        { id: 'Quotation', name: 'Quotation' },
        { id: 'Thank You', name: 'Thank You' },
      ]} />
      <SelectInput source="language" label="语言" choices={[
        { id: 'en', name: 'English' },
        { id: 'zh', name: '中文' },
        { id: 'es', name: 'Español' },
        { id: 'fr', name: 'Français' },
      ]} />
      <TextInput source="subject" label="主题" fullWidth />
      <TextInput source="body" label="正文" multiline fullWidth />
      <TextInput source="variables" label="变量（JSON）" fullWidth />
      <NumberInput source="usage_count" label="使用次数" />
      <TextInput source="success_rate" label="成功率" />
      <BooleanInput source="is_active" label="是否启用" />
    </SimpleForm>
  </Create>
)

export const TemplateEdit = (props:any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="name" label="名称" />
      <SelectInput source="category" label="分类" choices={[
        { id: 'Cold Email', name: 'Cold Email' },
        { id: 'Follow-up', name: 'Follow-up' },
        { id: 'Quotation', name: 'Quotation' },
        { id: 'Thank You', name: 'Thank You' },
      ]} />
      <SelectInput source="language" label="语言" choices={[
        { id: 'en', name: 'English' },
        { id: 'zh', name: '中文' },
        { id: 'es', name: 'Español' },
        { id: 'fr', name: 'Français' },
      ]} />
      <TextInput source="subject" label="主题" fullWidth />
      <TextInput source="body" label="正文" multiline fullWidth />
      <TextInput source="variables" label="变量（JSON）" fullWidth />
      <NumberInput source="usage_count" label="使用次数" />
      <TextInput source="success_rate" label="成功率" />
      <BooleanInput source="is_active" label="是否启用" />
    </SimpleForm>
  </Edit>
)
