import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function getApiBase() {
  if (!BACKEND_URL) return "/api";
  return `${BACKEND_URL}/api`;
}

export const api = axios.create({
  baseURL: getApiBase(),
  timeout: 20000,
});

export const AdminAuthStorage = {
  key: "portfolio_admin_jwt",
  getToken() {
    try {
      return window.sessionStorage.getItem(this.key) || "";
    } catch {
      return "";
    }
  },
  setToken(token) {
    try {
      window.sessionStorage.setItem(this.key, token);
    } catch {
      // ignore
    }
  },
  clear() {
    try {
      window.sessionStorage.removeItem(this.key);
    } catch {
      // ignore
    }
  },
};
