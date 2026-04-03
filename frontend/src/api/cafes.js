import axios from "axios";
import { API_BASE } from "./base";

const BASE = `${API_BASE}/cafes`;

export async function getCafes(location) {
  const params = location ? { location } : {};
  const { data } = await axios.get(BASE, { params });
  return data;
}

export async function createCafe(fields) {
  const form = new FormData();
  form.append("name", fields.name);
  form.append("description", fields.description);
  form.append("location", fields.location);
  if (fields.logo) form.append("logo", fields.logo);
  const { data } = await axios.post(BASE, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function updateCafe(id, fields) {
  const form = new FormData();
  form.append("name", fields.name);
  form.append("description", fields.description);
  form.append("location", fields.location);
  if (fields.logo) form.append("logo", fields.logo);
  const { data } = await axios.put(`${BASE}/${id}`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function deleteCafe(id) {
  const { data } = await axios.delete(`${BASE}/${id}`);
  return data;
}
