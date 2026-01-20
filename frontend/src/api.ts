import { getAccessToken } from './auth';

const API = import.meta.env.VITE_API_BASE_URL || (window as any).ENV?.VITE_API_BASE_URL || 'http://localhost:8123/api/v1';

export async function api(path: string, init: RequestInit = {}) {
  const token = await getAccessToken();
  const headers = new Headers(init.headers || {});
  // Only set JSON content-type if body is not FormData
  const isFormData = typeof FormData !== 'undefined' && init.body instanceof FormData;
  if (!isFormData) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const res = await fetch(`${API}${path}`, { ...init, headers, credentials: 'include' });
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}
