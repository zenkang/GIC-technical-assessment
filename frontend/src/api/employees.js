import axios from "axios";
import { API_BASE } from "./base";

const BASE = `${API_BASE}/employees`;

export async function getEmployees(cafe) {
  const params = cafe ? { cafe } : {};
  const { data } = await axios.get(BASE, { params });
  return data;
}

export async function createEmployee(fields) {
  const { data } = await axios.post(BASE, fields);
  return data;
}

export async function updateEmployee(id, fields) {
  const { data } = await axios.put(`${BASE}/${id}`, fields);
  return data;
}

export async function deleteEmployee(id) {
  const { data } = await axios.delete(`${BASE}/${id}`);
  return data;
}
