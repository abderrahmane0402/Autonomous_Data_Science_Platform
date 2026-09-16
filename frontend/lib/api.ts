const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- Helpers ---
function getAuthHeaders() {
    // In a real app, this would get the token from cookies or localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    return token ? { "Authorization": `Bearer ${token}` } : {};
}

// --- Authentication ---
export async function login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append("username", email); // FastAPI OAuth2 expects 'username'
    formData.append("password", password);

    const res = await fetch(`${API_BASE_URL}/auth/token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
    });
    
    if (!res.ok) throw new Error("Login failed");
    return res.json();
}

export async function signup(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Signup failed");
    return res.json();
}

export async function getMe() {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
        method: "GET",
        headers: { ...getAuthHeaders() },
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch user");
    return res.json();
}

// --- Projects & Datasets ---
export async function getProjects() {
    const res = await fetch(`${API_BASE_URL}/projects/`, {
        method: "GET",
        headers: { ...getAuthHeaders() },
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch projects");
    return res.json();
}

export async function createProject(name: string) {
    const res = await fetch(`${API_BASE_URL}/projects/`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            ...getAuthHeaders() 
        },
        body: JSON.stringify({ name }),
    });
    if (!res.ok) throw new Error("Failed to create project");
    return res.json();
}

export async function deleteProject(projectId: string) {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        method: "DELETE",
        headers: { ...getAuthHeaders() },
    });
    if (!res.ok) throw new Error("Failed to delete project");
    return res.json();
}

export async function getProject(projectId: string) {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
        method: "GET",
        headers: { ...getAuthHeaders() },
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch project");
    return res.json();
}

export async function getProjectReport(projectId: string) {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/report`, {
        method: "GET",
        headers: { ...getAuthHeaders() },
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch report");
    return res.json();
}

export async function uploadDataset(file: File, projectId?: string, redactPii: boolean = false) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("redact_pii", redactPii.toString());
    if (projectId) formData.append("project_id", projectId);

    const res = await fetch(`${API_BASE_URL}/datasets/upload`, {
        method: "POST",
        headers: { ...getAuthHeaders() },
        body: formData,
    });
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Upload failed: ${errorText}`);
    }
    return res.json();
}

export async function removeDataset(projectId: string) {
    const res = await fetch(`${API_BASE_URL}/datasets/project/${projectId}`, {
        method: "DELETE",
        headers: { ...getAuthHeaders() },
    });
    if (!res.ok) throw new Error("Failed to remove dataset");
    return res.json();
}

export async function getUploadProgress(filename: string) {
    const res = await fetch(`${API_BASE_URL}/datasets/progress/${encodeURIComponent(filename)}`, {
        method: "GET",
        headers: { ...getAuthHeaders() },
        cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch progress");
    return res.json();
}

// --- Agent Pipeline ---
export async function runAIWorkflow(datasetMetadata: any, projectId: string) {
    const res = await fetch(`${API_BASE_URL}/agents/test-ml-engineer`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            ...getAuthHeaders() 
        },
        body: JSON.stringify({ 
            dataset_metadata: datasetMetadata,
            project_id: parseInt(projectId) 
        }),
    });
    if (!res.ok) throw new Error("AI Workflow failed");
    return res.json();
}
