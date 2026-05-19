const TOKEN_KEY = "taskflow_token";
const TEAM_KEY = "taskflow_team";

export function getToken() { return localStorage.getItem(TOKEN_KEY); }
export function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
export function removeToken() { localStorage.removeItem(TOKEN_KEY); }

export function getTeam() {
  const raw = localStorage.getItem(TEAM_KEY);
  return raw ? JSON.parse(raw) : null;
}
export function setTeam(team) { localStorage.setItem(TEAM_KEY, JSON.stringify(team)); }
export function removeTeam() { localStorage.removeItem(TEAM_KEY); }

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, { ...options, headers });

  if (res.status === 401) {
    removeToken();
    removeTeam();
    window.location.href = "/static/login.html";
    return null;
  }
  return res;
}

export function requireAuth() {
  if (!getToken()) {
    window.location.href = "/static/login.html";
    return false;
  }
  return true;
}

export function requireTeam() {
  if (!getTeam()) {
    window.location.href = "/static/team.html";
    return false;
  }
  return true;
}
