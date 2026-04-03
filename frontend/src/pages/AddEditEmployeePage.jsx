import { useEffect, useRef } from "react";
import { useNavigate, useParams, useBlocker } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Form, Button, Radio, Select, Modal, message, Typography, Space, Spin } from "antd";

import TextInput from "../components/TextInput";
import { getEmployees, createEmployee, updateEmployee } from "../api/employees";
import { getCafes } from "../api/cafes";

const { Title } = Typography;
const { Option } = Select;

const PHONE_REGEX = /^[89]\d{7}$/;

export default function AddEditEmployeePage() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  // Ref instead of state so navigate() in onSuccess sees the updated value immediately
  const isDirtyRef = useRef(false);

  // ── Block in-app navigation when the form has unsaved changes ─────────
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirtyRef.current && currentLocation.pathname !== nextLocation.pathname
  );

  // Depend on blocker.STATE — the blocker object itself is a new reference every
  // render, which would re-open the modal on every keystroke.
  useEffect(() => {
    if (blocker.state === "blocked") {
      Modal.confirm({
        title: "Unsaved changes",
        content: "You have unsaved changes. Are you sure you want to leave?",
        okText: "Leave",
        cancelText: "Stay",
        onOk: () => blocker.proceed(),
        onCancel: () => blocker.reset(),
      });
    }
  }, [blocker.state]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Fetch cafes for the Assigned Café dropdown ────────────────────────
  const { data: cafes = [] } = useQuery({
    queryKey: ["cafes"],
    queryFn: () => getCafes(null),
  });

  // ── In edit mode: pre-fill form without marking it dirty ──────────────
  const { data: employees = [], isLoading: employeesLoading } = useQuery({
    queryKey: ["employees"],
    queryFn: () => getEmployees(null),
    enabled: isEditMode,
  });

  useEffect(() => {
    if (isEditMode && employees.length > 0 && cafes.length > 0) {
      const emp = employees.find((e) => e.id === id);
      if (emp) {
        const matchedCafe = cafes.find((c) => c.name === emp.cafe);
        form.setFieldsValue({
          name: emp.name,
          email_address: emp.email_address,
          phone_number: emp.phone_number,
          gender: emp.gender,
          cafe_id: matchedCafe ? matchedCafe.id : undefined,
        });
        // setFieldsValue triggers onValuesChange — reset dirty flag immediately after
        isDirtyRef.current = false;
      }
    }
  }, [isEditMode, employees, cafes, id, form]);

  // ── Mutations ─────────────────────────────────────────────────────────
  const mutation = useMutation({
    mutationFn: (values) =>
      isEditMode
        ? updateEmployee(id, { ...values, cafe_id: values.cafe_id || null })
        : createEmployee({ ...values, cafe_id: values.cafe_id || null }),
    onSuccess: () => {
      message.success(isEditMode ? "Employee updated" : "Employee created");
      isDirtyRef.current = false; // synchronous — blocker sees false before navigate() fires
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      navigate("/employees");
    },
    onError: (err) => {
      const detail = err?.response?.data?.detail || "Something went wrong";
      message.error(detail);
    },
  });

  if (isEditMode && employeesLoading) {
    return <Spin style={{ margin: "80px auto", display: "block" }} />;
  }

  return (
    <div className="form-card">
      <Title level={3} className="page-title">
        {isEditMode ? "Edit Employee" : "Add New Employee"}
      </Title>

      <Form
        form={form}
        layout="vertical"
        onFinish={(values) => mutation.mutate(values)}
        onValuesChange={() => { isDirtyRef.current = true; }}
      >
        <TextInput
          label="Name"
          name="name"
          rules={[
            { required: true, message: "Name is required" },
            { min: 6, message: "Name must be at least 6 characters" },
            { max: 10, message: "Name must be at most 10 characters" },
          ]}
          placeholder="e.g. Alice Tan"
        />

        <TextInput
          label="Email Address"
          name="email_address"
          rules={[
            { required: true, message: "Email is required" },
            { type: "email", message: "Enter a valid email address" },
          ]}
          placeholder="e.g. alice@email.com"
        />

        <TextInput
          label="Phone Number"
          name="phone_number"
          rules={[
            { required: true, message: "Phone number is required" },
            {
              validator: (_, value) =>
                PHONE_REGEX.test(value)
                  ? Promise.resolve()
                  : Promise.reject("Phone must start with 8 or 9 and be exactly 8 digits"),
            },
          ]}
          placeholder="e.g. 91234567"
          maxLength={8}
        />

        <Form.Item
          label="Gender"
          name="gender"
          rules={[{ required: true, message: "Please select a gender" }]}
        >
          <Radio.Group>
            <Radio value="Male">Male</Radio>
            <Radio value="Female">Female</Radio>
          </Radio.Group>
        </Form.Item>

        <Form.Item label="Assigned Café" name="cafe_id">
          <Select
            placeholder="Select a café (optional)"
            allowClear
            showSearch
            optionFilterProp="children"
          >
            {cafes.map((cafe) => (
              <Option key={cafe.id} value={cafe.id}>
                {cafe.name} — {cafe.location}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={mutation.isPending}>
              {isEditMode ? "Update Employee" : "Create Employee"}
            </Button>
            <Button className="btn-gic" onClick={() => navigate("/employees")}>Cancel</Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
}
