import { Outlet, Link, useLocation } from "react-router-dom";
import { Layout, Menu } from "antd";
import { CoffeeOutlined, TeamOutlined } from "@ant-design/icons";

const { Header, Content, Footer } = Layout;

const NAV_ITEMS = [
  {
    key: "/",
    icon: <CoffeeOutlined />,
    label: <Link to="/">Cafes</Link>,
  },
  {
    key: "/employees",
    icon: <TeamOutlined />,
    label: <Link to="/employees">Employees</Link>,
  },
];

export default function App() {
  const location = useLocation();
  const selectedKey = location.pathname.startsWith("/employees") ? "/employees" : "/";

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header className="app-header" style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <span className="app-logo">Cafe Manager</span>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={NAV_ITEMS}
          style={{ flex: 1, minWidth: 0, background: "transparent" }}
        />
      </Header>

      <Content className="app-content">
        <div className="fade-in">
          <Outlet />
        </div>
      </Content>

      <Footer className="app-footer">
        Built for GIC Digital Platform Assessment &middot; {new Date().getFullYear()}
      </Footer>
    </Layout>
  );
}
