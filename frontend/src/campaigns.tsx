import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, NumberInput } from 'react-admin'

const campaignFilters = [
  <TextInput key="search" label="搜索名称" source="search" alwaysOn />, 
  <SelectInput key="status" label="状态" source="status" choices={[
    { id: 'Draft', name: '草稿' },
    { id: 'Scheduled', name: '已排期' },
    { id: 'Running', name: '进行中' },
    { id: 'Completed', name: '已完成' },
    { id: 'Paused', name: '暂停' },
  ]} />
]

export const CampaignList = (props:any) => (
  <List {...props} perPage={20} filters={campaignFilters}>
    <Datagrid rowClick="edit">
      <TextField source="name" label="活动名称" />
      <TextField source="status" label="状态" />
      <TextField source="template_id" label="模板ID" />
      <TextField source="target_segment" label="目标群体" />
      <TextField source="total_sent" label="发送数" />
      <TextField source="total_opened" label="打开数" />
    </Datagrid>
  </List>
)

export const CampaignCreate = (props:any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="name" label="活动名称" />
      <SelectInput source="status" label="状态" choices={[
        { id: 'Draft', name: '草稿' },
        { id: 'Scheduled', name: '已排期' },
        { id: 'Running', name: '进行中' },
        { id: 'Completed', name: '已完成' },
        { id: 'Paused', name: '暂停' },
      ]} />
      <TextInput source="template_id" label="模板ID" />
      <TextInput source="target_segment" label="目标群体" />
      <NumberInput source="total_sent" label="发送数" />
      <NumberInput source="total_opened" label="打开数" />
      <NumberInput source="total_clicked" label="点击数" />
      <NumberInput source="total_replied" label="回复数" />
      <NumberInput source="total_bounced" label="退信数" />
    </SimpleForm>
  </Create>
)

export const CampaignEdit = (props:any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="name" label="活动名称" />
      <SelectInput source="status" label="状态" choices={[
        { id: 'Draft', name: '草稿' },
        { id: 'Scheduled', name: '已排期' },
        { id: 'Running', name: '进行中' },
        { id: 'Completed', name: '已完成' },
        { id: 'Paused', name: '暂停' },
      ]} />
      <TextInput source="template_id" label="模板ID" />
      <TextInput source="target_segment" label="目标群体" />
      <NumberInput source="total_sent" label="发送数" />
      <NumberInput source="total_opened" label="打开数" />
      <NumberInput source="total_clicked" label="点击数" />
      <NumberInput source="total_replied" label="回复数" />
      <NumberInput source="total_bounced" label="退信数" />
    </SimpleForm>
  </Edit>
)
