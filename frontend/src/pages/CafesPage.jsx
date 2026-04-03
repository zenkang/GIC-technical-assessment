/**
 * CafesPage — displays all cafes in an AG Grid table.
 *
 * Features:
 * - Location filter (free-text input) that re-fetches with the query param
 * - Clicking the employee count navigates to /employees?cafe=<name>
 * - Edit button → /cafes/edit/:id
 * - Delete button → Antd Modal confirm → DELETE /cafes/:id → refetch
 * - "Add New Café" button → /cafes/add
 */
import { useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button, Input, Space, Modal, message, Avatar, Typography } from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from "@ant-design/icons";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

import { getCafes, deleteCafe } from "../api/cafes";

const { Title } = Typography;

export default function CafesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // The location filter value (controlled input)
  const [locationFilter, setLocationFilter] = useState("");
  // The applied location — only updates when the user presses Enter or clicks Search
  const [appliedLocation, setAppliedLocation] = useState("");

  // Fetch cafes; re-fetches whenever appliedLocation changes
  const { data: cafes = [], isLoading } = useQuery({
    queryKey: ["cafes", appliedLocation],
    queryFn: () => getCafes(appliedLocation || null),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCafe,
    onSuccess: () => {
      message.success("Cafe deleted");
      queryClient.invalidateQueries({ queryKey: ["cafes"] });
    },
    onError: () => message.error("Failed to delete cafe"),
  });

  const handleDelete = useCallback((cafe) => {
    Modal.confirm({
      title: `Delete "${cafe.name}"?`,
      content: "This will permanently remove the cafe, its assignments, and employees currently assigned to this cafe.",
      okText: "Delete",
      okType: "danger",
      cancelText: "Cancel",
      onOk: () => deleteMutation.mutate(cafe.id),
    });
  }, [deleteMutation]);

  // AG Grid column definitions
  const columnDefs = useMemo(() => [
    {
      headerName: "Logo",
      field: "logo",
      width: 80,
      sortable: false,
      filter: false,
      cellRenderer: ({ value }) =>
        value ? (
          <Avatar src={value} shape="square" size={40} style={{ marginTop: 4 }} />
        ) : (
          <Avatar shape="square" size={40} style={{ marginTop: 4, background: "#d9d9d9" }}>
            ☕
          </Avatar>
        ),
    },
    { headerName: "Name", field: "name", flex: 1, minWidth: 120 },
    { headerName: "Description", field: "description", flex: 2, minWidth: 160 },
    {
      headerName: "Employees",
      field: "employees",
      width: 120,
      // Clicking the employee count navigates to the employees page filtered by cafe
      cellRenderer: ({ value, data }) => (
        <Button
          type="link"
          style={{ padding: 0 }}
          onClick={() => navigate(`/employees?cafe=${encodeURIComponent(data.name)}`)}
        >
          {value}
        </Button>
      ),
    },
    { headerName: "Location", field: "location", flex: 1, minWidth: 100 },
    {
      headerName: "Actions",
      width: 130,
      sortable: false,
      filter: false,
      cellRenderer: ({ data }) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => navigate(`/cafes/edit/${data.id}`)}
          >
            Edit
          </Button>
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
            onClick={() => handleDelete(data)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ], [navigate, handleDelete]);

  const defaultColDef = useMemo(() => ({
    sortable: true,
    filter: true,
    resizable: true,
  }), []);

  return (
    <div>
      {/* ── Page header ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Cafes</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate("/cafes/add")}
        >
          Add New Café
        </Button>
      </div>

      {/* ── Location filter ── */}
      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="Filter by location (press Enter to search)"
          prefix={<SearchOutlined />}
          value={locationFilter}
          onChange={(e) => {
            setLocationFilter(e.target.value);
            // When the clear (×) button is clicked, allowClear fires onChange with ""
            if (!e.target.value) setAppliedLocation("");
          }}
          onPressEnter={() => setAppliedLocation(locationFilter)}
          allowClear
          style={{ maxWidth: 320 }}
        />
      </div>

      {/* ── AG Grid table ── */}
      <div className="ag-theme-alpine" style={{ height: 480 }}>
        <AgGridReact
          rowData={cafes}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          rowHeight={56}
          loading={isLoading}
          overlayNoRowsTemplate="No cafes found"
        />
      </div>
    </div>
  );
}
