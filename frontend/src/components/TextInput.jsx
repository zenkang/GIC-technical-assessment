/**
 * TextInput — reusable form field component.
 *
 * Wraps Antd's Form.Item + Input (or TextArea for multiline fields).
 * Used by both AddEditCafePage and AddEditEmployeePage for every text field.
 *
 * Props:
 *   label      {string}   - visible label above the input
 *   name       {string}   - Antd Form field name (must match the form's field keys)
 *   rules      {Array}    - Antd validation rules array
 *   multiline  {boolean}  - render a TextArea instead of a single-line Input
 *   rows       {number}   - number of rows for TextArea (default 3)
 *   ...rest               - any other props are forwarded to Input/TextArea
 */
import React from "react";
import { Form, Input } from "antd";

const { TextArea } = Input;

export default function TextInput({ label, name, rules = [], multiline = false, rows = 3, ...rest }) {
  return (
    <Form.Item label={label} name={name} rules={rules}>
      {multiline ? (
        <TextArea rows={rows} {...rest} />
      ) : (
        <Input {...rest} />
      )}
    </Form.Item>
  );
}
