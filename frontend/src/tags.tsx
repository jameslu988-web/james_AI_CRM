import React, { useState } from 'react';
import {
  List,
  Datagrid,
  TextField,
  DateField,
  NumberField,
  Create,
  SimpleForm,
  TextInput,
  Edit,
  EditButton,
  DeleteButton,
  useNotify,
  useRefresh,
  FunctionField,
  TopToolbar,
  CreateButton,
  FilterButton,
  SelectColumnsButton,
  ExportButton,
} from 'react-admin';
import { Box, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField as MuiTextField } from '@mui/material';
import { HexColorPicker } from 'react-colorful';

// 颜色选择器组件
const ColorInput = (props: any) => {
  const [open, setOpen] = useState(false);
  const [color, setColor] = useState(props.record?.color || '#1677ff');

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);
  const handleSave = () => {
    props.onChange(color);
    setOpen(false);
  };

  return (
    <>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            backgroundColor: props.record?.color || color || '#1677ff',
            border: '1px solid #ddd',
            borderRadius: 1,
            cursor: 'pointer',
          }}
          onClick={handleOpen}
        />
        <TextInput {...props} value={props.record?.color || color} sx={{ flex: 1 }} />
      </Box>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>选择颜色</DialogTitle>
        <DialogContent>
          <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <HexColorPicker color={color} onChange={setColor} />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 60,
                  height: 60,
                  backgroundColor: color,
                  border: '1px solid #ddd',
                  borderRadius: 1,
                }}
              />
              <MuiTextField
                value={color}
                onChange={(e: any) => setColor(e.target.value)}
                sx={{ width: 120 }}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>取消</Button>
          <Button onClick={handleSave} variant="contained">
            确定
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

// 顶部操作栏
const ListActions = () => (
  <TopToolbar>
    <FilterButton />
    <SelectColumnsButton />
    <CreateButton label="新建标签" />
    <ExportButton />
  </TopToolbar>
);

// 标签列表
export const TagList = () => {
  return (
    <List actions={<ListActions />} perPage={25} sort={{ field: 'id', order: 'DESC' }}>
      <Datagrid>
        <TextField source="id" label="ID" />
        <FunctionField
          label="标签名称"
          render={(record: any) => (
            <Chip
              label={record.name}
              sx={{
                backgroundColor: record.color,
                color: '#fff',
                fontWeight: 600,
              }}
            />
          )}
        />
        <TextField source="description" label="描述" />
        <NumberField source="usage_count" label="使用次数" />
        <DateField source="created_at" label="创建时间" showTime />
        <DateField source="updated_at" label="更新时间" showTime />
        <EditButton label="编辑" />
        <DeleteButton label="删除" />
      </Datagrid>
    </List>
  );
};

// 创建标签
export const TagCreate = () => {
  const notify = useNotify();
  const refresh = useRefresh();

  const onSuccess = () => {
    notify('标签创建成功', { type: 'success' });
    refresh();
  };

  return (
    <Create mutationOptions={{ onSuccess }}>
      <SimpleForm>
        <TextInput source="name" label="标签名称" required fullWidth />
        <ColorInput source="color" label="标签颜色" defaultValue="#1677ff" fullWidth />
        <TextInput source="description" label="描述" multiline rows={3} fullWidth />
      </SimpleForm>
    </Create>
  );
};

// 编辑标签
export const TagEdit = () => {
  const notify = useNotify();
  const refresh = useRefresh();

  const onSuccess = () => {
    notify('标签更新成功', { type: 'success' });
    refresh();
  };

  return (
    <Edit mutationOptions={{ onSuccess }}>
      <SimpleForm>
        <TextInput source="name" label="标签名称" required fullWidth />
        <ColorInput source="color" label="标签颜色" fullWidth />
        <TextInput source="description" label="描述" multiline rows={3} fullWidth />
      </SimpleForm>
    </Edit>
  );
};
