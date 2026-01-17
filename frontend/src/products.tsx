import { List, Datagrid, TextField, TextInput, SelectInput, Edit, Create, SimpleForm, BooleanInput, NumberInput, NumberField, BooleanField } from 'react-admin'

const productFilters = [
  <TextInput key="search" label="搜索SKU/名称" source="search" alwaysOn />, 
  <SelectInput key="category" label="产品分类" source="category" choices={[
    { id: '平角内裤', name: '平角内裤' },
    { id: '三角内裤', name: '三角内裤' },
    { id: '运动内裤', name: '运动内裤' },
  ]} />
]

export const ProductList = (props: any) => (
  <List {...props} perPage={20} filters={productFilters}>
    <Datagrid rowClick="edit">
      <TextField source="sku" label="SKU" />
      <TextField source="name_en" label="英文名称" />
      <TextField source="name_zh" label="中文名称" />
      <TextField source="category" label="分类" />
      <NumberField source="moq" label="MOQ" />
      <NumberField source="base_price" label="基础价格" />
      <NumberField source="production_days" label="生产周期(天)" />
      <BooleanField source="is_active" label="启用" />
    </Datagrid>
  </List>
)

export const ProductCreate = (props: any) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="sku" label="SKU编码" required />
      <TextInput source="name_en" label="英文名称" required fullWidth />
      <TextInput source="name_zh" label="中文名称" fullWidth />
      <SelectInput source="category" label="产品分类" choices={[
        { id: '平角内裤', name: '平角内裤' },
        { id: '三角内裤', name: '三角内裤' },
        { id: '运动内裤', name: '运动内裤' },
      ]} />
      
      <TextInput source="description_en" label="英文描述" multiline fullWidth rows={4} />
      <TextInput source="description_zh" label="中文描述" multiline fullWidth rows={4} />
      <TextInput source="features" label="产品特点(JSON数组)" fullWidth placeholder='["高弹性", "透气舒适", "抗菌防臭"]' />
      
      <TextInput source="sizes" label="可用尺码(JSON数组)" fullWidth placeholder='["S", "M", "L", "XL", "XXL", "XXXL"]' />
      <TextInput source="colors" label="可用颜色(JSON数组)" fullWidth placeholder='["黑色", "白色", "灰色", "藏青"]' />
      <TextInput source="materials" label="材质选项(JSON)" multiline fullWidth rows={3} placeholder='[{"name": "精梳棉", "composition": "95%棉+5%氨纶", "price_multiplier": 1.2}]' />
      
      <NumberInput source="weight_gram" label="单件重量(克)" />
      <TextInput source="packaging_unit" label="包装单位" defaultValue="pcs/polybag" />
      
      <NumberInput source="moq" label="最小起订量(MOQ)" required defaultValue={1000} />
      <NumberInput source="base_price" label="基础价格(USD)" step={0.01} required />
      <NumberInput source="production_days" label="生产周期(天)" defaultValue={30} />
      <NumberInput source="sample_price" label="样品价格(USD)" step={0.01} />
      <NumberInput source="sample_days" label="样品周期(天)" defaultValue={7} />
      
      <TextInput source="main_image_url" label="主图URL" fullWidth />
      <TextInput source="images" label="图片列表(JSON数组)" multiline fullWidth placeholder='["url1", "url2", "url3"]' />
      
      <TextInput source="certifications" label="认证证书(JSON)" multiline fullWidth placeholder='["OEKO-TEX", "ISO9001"]' />
      <TextInput source="customization_options" label="定制选项(JSON)" multiline fullWidth rows={3} placeholder='{"印花": {"MOQ": 500, "price_add": 0.5}, "刺绣": {"MOQ": 1000, "price_add": 0.8}}' />
      
      <BooleanInput source="is_active" label="启用" />
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Create>
)

export const ProductEdit = (props: any) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="sku" label="SKU编码" disabled />
      <TextInput source="name_en" label="英文名称" required fullWidth />
      <TextInput source="name_zh" label="中文名称" fullWidth />
      <SelectInput source="category" label="产品分类" choices={[
        { id: '平角内裤', name: '平角内裤' },
        { id: '三角内裤', name: '三角内裤' },
        { id: '运动内裤', name: '运动内裤' },
      ]} />
      
      <TextInput source="description_en" label="英文描述" multiline fullWidth rows={4} />
      <TextInput source="description_zh" label="中文描述" multiline fullWidth rows={4} />
      <TextInput source="features" label="产品特点(JSON数组)" fullWidth />
      
      <TextInput source="sizes" label="可用尺码(JSON数组)" fullWidth />
      <TextInput source="colors" label="可用颜色(JSON数组)" fullWidth />
      <TextInput source="materials" label="材质选项(JSON)" multiline fullWidth rows={3} />
      
      <NumberInput source="weight_gram" label="单件重量(克)" />
      <TextInput source="packaging_unit" label="包装单位" />
      
      <NumberInput source="moq" label="最小起订量(MOQ)" required />
      <NumberInput source="base_price" label="基础价格(USD)" step={0.01} required />
      <NumberInput source="production_days" label="生产周期(天)" />
      <NumberInput source="sample_price" label="样品价格(USD)" step={0.01} />
      <NumberInput source="sample_days" label="样品周期(天)" />
      
      <TextInput source="main_image_url" label="主图URL" fullWidth />
      <TextInput source="images" label="图片列表(JSON数组)" multiline fullWidth />
      
      <TextInput source="certifications" label="认证证书(JSON)" multiline fullWidth />
      <TextInput source="customization_options" label="定制选项(JSON)" multiline fullWidth rows={3} />
      
      <BooleanInput source="is_active" label="启用" />
      <TextInput source="notes" label="内部备注" multiline fullWidth />
    </SimpleForm>
  </Edit>
)
