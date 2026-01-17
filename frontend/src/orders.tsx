import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, NumberInput, FunctionField } from 'react-admin'
import Chip from '@mui/material/Chip'

const statusColorMap: any = {
  quotation: '#6b7280',
  confirmed: '#3b82f6',
  production: '#f59e0b',
  shipped: '#8b5cf6',
  delivered: '#10b981',
  completed: '#059669',
}

const orderFilters = [
  <TextInput key="search" label="搜索订单号/工厂" source="search" alwaysOn />, 
  <SelectInput key="status" label="状态" source="status" choices={[
    { id: 'quotation', name: '报价' },
    { id: 'confirmed', name: '确认' },
    { id: 'production', name: '生产' },
    { id: 'shipped', name: '发货' },
    { id: 'delivered', name: '交付' },
    { id: 'completed', name: '完成' },
  ]} />
]

export const OrderList = (props:any) => (
  <List {...props} perPage={20} filters={orderFilters}>
    <Datagrid
      rowClick="edit"
      bulkActionButtons={false}
      sx={{
        '& .RaDatagrid-headerCell': { fontWeight: 600, backgroundColor: '#f9fafb' },
        '& .RaDatagrid-row': { '&:hover': { backgroundColor: '#f3f4f6' } }
      }}
    >
      <TextField source="order_number" label="订单号" />
      <FunctionField label="状态" render={(record:any) => {
        const color = statusColorMap[record?.status] || '#6b7280'
        return <Chip label={record?.status || '-'} size="small" sx={{ bgcolor: color, color: '#fff', fontWeight: 500 }} />
      }} />
      <TextField source="customer_id" label="客户ID" />
      <TextField source="currency" label="币种" />
      <TextField source="total_amount" label="金额" />
    </Datagrid>
  </List>
)

export const OrderCreate = (props:any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="order_number" label="订单号" />
      <TextInput source="status" label="状态" />
      <TextInput source="customer_id" label="客户ID" />
      <TextInput source="currency" label="币种" />
      <NumberInput source="total_amount" label="金额" />
      <TextInput source="product_details" label="产品明细" fullWidth />
    </SimpleForm>
  </Create>
)

export const OrderEdit = (props:any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="order_number" label="订单号" />
      <TextInput source="status" label="状态" />
      <TextInput source="customer_id" label="客户ID" />
      <TextInput source="currency" label="币种" />
      <NumberInput source="total_amount" label="金额" />
      <TextInput source="product_details" label="产品明细" fullWidth />
    </SimpleForm>
  </Edit>
)
