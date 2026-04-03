import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams, useBlocker } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Form, Button, Upload, Modal, message, Typography, Space, Spin } from "antd";
import { UploadOutlined } from "@ant-design/icons";

import TextInput from "../components/TextInput";
import { getCafes, createCafe, updateCafe } from "../api/cafes";

const { Title } = Typography;
const MAX_LOGO_BYTES = 2 * 1024 * 1024; // 2 MB

export default function AddEditCafePage() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [logoFile, setLogoFile] = useState(null);

  // Use a ref (not state) so the update is synchronous.
  // If we used setState, navigate() in onSuccess would fire before the re-render
  // and the blocker would still see isDirty=true, triggering a false warning.
  const isDirtyRef = useRef(false);

  // ── Block in-app navigation when the form has unsaved changes ─────────
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirtyRef.current && currentLocation.pathname !== nextLocation.pathname
  );

  // Depend on blocker.STATE (not the blocker object itself — that's a new
  // reference every render, which would re-fire the modal on every keystroke).
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

  // ── In edit mode: pre-fill the form without marking it dirty ──────────
  const { data: cafes = [], isLoading: cafesLoading } = useQuery({
    queryKey: ["cafes"],
    queryFn: () => getCafes(null),
    enabled: isEditMode,
  });

  useEffect(() => {
    if (isEditMode && cafes.length > 0) {
      const cafe = cafes.find((c) => c.id === id);
      if (cafe) {
        form.setFieldsValue({
          name: cafe.name,
          description: cafe.description,
          location: cafe.location,
        });
        // setFieldsValue fires onValuesChange, so reset the dirty flag immediately after
        isDirtyRef.current = false;
      }
    }
  }, [isEditMode, cafes, id, form]);

  // ── Mutations ─────────────────────────────────────────────────────────
  const mutation = useMutation({
    mutationFn: (fields) =>
      isEditMode ? updateCafe(id, fields) : createCafe(fields),
    onSuccess: () => {
      message.success(isEditMode ? "Cafe updated" : "Cafe created");
      isDirtyRef.current = false; // synchronous — blocker sees false before navigate() fires
      queryClient.invalidateQueries({ queryKey: ["cafes"] });
      navigate("/");
    },
    onError: (err) => {
      const detail = err?.response?.data?.detail || "Something went wrong";
      message.error(detail);
    },
  });

  if (isEditMode && cafesLoading) {
    return <Spin style={{ margin: "80px auto", display: "block" }} />;
  }

  return (
    <div className="form-card">
      <Title level={3} className="page-title">
        {isEditMode ? "Edit Cafe" : "Add New Cafe"}
      </Title>

      <Form
        form={form}
        layout="vertical"
        onFinish={(values) => mutation.mutate({ ...values, logo: logoFile })}
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
          placeholder="e.g. Bean There"
        />

        <TextInput
          label="Description"
          name="description"
          multiline
          rows={4}
          rules={[
            { required: true, message: "Description is required" },
            { max: 256, message: "Description must be at most 256 characters" },
          ]}
          placeholder="A short description of the cafe"
        />

        <TextInput
          label="Location"
          name="location"
          rules={[{ required: true, message: "Location is required" }]}
          placeholder="e.g. Orchard"
        />

        <Form.Item label="Logo (optional)">
          <Upload
            beforeUpload={(file) => {
              if (file.size > MAX_LOGO_BYTES) {
                message.error("Logo must be 2 MB or smaller");
                return Upload.LIST_IGNORE;
              }
              setLogoFile(file);
              isDirtyRef.current = true;
              return false;
            }}
            onRemove={() => setLogoFile(null)}
            maxCount={1}
            accept="image/*"
          >
            <Button icon={<UploadOutlined />}>Select Logo</Button>
          </Upload>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={mutation.isPending}>
              {isEditMode ? "Update Café" : "Create Café"}
            </Button>
            <Button className="btn-gic" onClick={() => navigate("/")}>Cancel</Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
}
