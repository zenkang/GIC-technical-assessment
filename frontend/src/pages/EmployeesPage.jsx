/**
 * EmployeesPage — displays all employees in an AG Grid table.
 *
 * Features:
 * - Reads optional ?cafe= query param from the URL (set by CafesPage employee count click)
 * - Displays all employees or only those in the specified cafe
 * - Edit button → /employees/edit/:id
 * - Delete button → Antd Modal confirm → DELETE /employees/:id → refetch
 * - "Add New Employee" button → /employees/add
 */
import { useCallback, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button, Space, Modal, message, Typography, Tag } from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { AgGridReact } from "ag-grid-react";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

import { getEmployees, deleteEmployee } from "../api/employees";

const { Title } = Typography;

export default function EmployeesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  // ?cafe= query param: if present, filter employees to that cafe
  const cafeFilter = searchParams.get("cafe") || null;

  const { data: employees = [], isLoading } = useQuery({
    queryKey: ["employees", cafeFilter],
    queryFn: () => getEmployees(cafeFilter),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEmployee,
    onSuccess: () => {
      message.success("Employee deleted");
      queryClient.invalidateQueries({ queryKey: ["employees"] });
    },
    onError: () => message.error("Failed to delete employee"),
  });

  const handleDelete = useCallback((employee) => {
    Modal.confirm({
      title: `Delete "${employee.name}"?`,
      content: "This will permanently remove the employee.",
      okText: "Delete",
      okType: "danger",
      cancelText: "Cancel",
      onOk: () => deleteMutation.mutate(employee.id),
    });
  }, [deleteMutation]);

  const columnDefs = useMemo(() => [
    { headerName: "Employee ID", field: "id", width: 130 },
    { headerName: "Name", field: "name", flex: 1, minWidth: 120 },
    { headerName: "Email", field: "email_address", flex: 1, minWidth: 160 },
    { headerName: "Phone", field: "phone_number", width: 120 },
    {
      headerName: "Days Worked",
      field: "days_worked",
      width: 130,
      cellRenderer: ({ value }) => <Tag color="blue">{value} days</Tag>,
    },
    {
      headerName: "Café",
      field: "cafe",
      flex: 1,
      minWidth: 120,
      cellRenderer: ({ value }) =>
        value ? <Tag color="green">{value}</Tag> : <Tag>Unassigned</Tag>,
    },
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
            onClick={() => navigate(`/employees/edit/${data.id}`)}
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
        <div>
          <Title level={3} className="page-title" style={{ margin: 0 }}>
            Employees
            {cafeFilter && (
              <Tag color="processing" style={{ marginLeft: 12, fontWeight: "normal", fontSize: 14 }}>
                {cafeFilter}
              </Tag>
            )}
          </Title>
          {cafeFilter && (
            <Button type="link" style={{ padding: 0 }} onClick={() => navigate("/employees")}>
              ← Show all employees
            </Button>
          )}
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate("/employees/add")}
        >
          Add New Employee
        </Button>
      </div>

      {/* ── AG Grid table ── */}
      <div className="ag-theme-alpine-dark grid-wrapper" style={{ height: 480 }}>
        <AgGridReact
          rowData={employees}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          rowHeight={48}
          loading={isLoading}
          overlayNoRowsTemplate="No employees found"
        />
      </div>
    </div>
  );
}
