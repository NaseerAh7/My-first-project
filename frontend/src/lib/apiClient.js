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
