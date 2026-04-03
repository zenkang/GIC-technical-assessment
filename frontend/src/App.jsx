import { Outlet, Link, useLocation } from "react-router-dom";
import { Layout, Menu, Typography } from "antd";
import { CoffeeOutlined, TeamOutlined } from "@ant-design/icons";

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

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
      <Header style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <Title level={4} style={{ color: "#fff", margin: 0, whiteSpace: "nowrap" }}>
          ☕ Café Manager
        </Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={NAV_ITEMS}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>

      {/* <Outlet> renders the matched child route (replaces <Routes><Route> from before) */}
      <Content style={{ padding: "24px 48px" }}>
        <Outlet />
      </Content>

      <Footer style={{ textAlign: "center", color: "#aaa" }}>
        Café Employee Manager © {new Date().getFullYear()}
      </Footer>
    </Layout>
  );
}
