/* Shared JS for all tool frontends */

const API_BASE = "http://localhost:5000";

/**
 * Send a POST request to a tool endpoint.
 * @param {string} endpoint  e.g. "/api/tool/order"
 * @param {object} payload   request body
 * @returns {Promise<object>} parsed JSON response
 */
async function callTool(endpoint, payload) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return await res.json();
}

/**
 * Render a result box inside a container.
 * @param {string} containerId  HTML element id
 * @param {object} response      API response {success, data, error, error_type}
 */
function renderResult(containerId, response) {
    const box = document.getElementById(containerId);
    box.classList.add("show");

    const success = response.success;
    const icon = success ? "✓" : "✗";
    const statusText = success ? "Success" : `Failed — ${response.error_type || "error"}`;

    let html = `
        <div class="result-status ${success ? "success" : "failed"}">
            <div class="icon">${icon}</div>
            ${statusText}
        </div>
    `;

    if (success && response.data) {
        const lines = [];
        for (const [k, v] of Object.entries(response.data)) {
            let val = v;
            if (typeof v === "object") val = JSON.stringify(v, null, 2);
            lines.push(`${k}: ${val}`);
        }
        html += `<div class="result-data">${lines.join("\n")}</div>`;
    }

    if (!success && response.error) {
        html += `<div class="result-error">Error: ${response.error}</div>`;
    }

    box.innerHTML = html;
}

/**
 * Show loading state in a result box.
 */
function showLoading(containerId) {
    const box = document.getElementById(containerId);
    box.classList.add("show");
    box.innerHTML = `<div class="loading"><span class="spinner"></span> Calling API...</div>`;
}

/**
 * Set up the button click handler for a tool page.
 * @param {string} btnId        button element id
 * @param {string} resultId     result container id
 * @param {string} endpoint     API endpoint
 * @param {function} buildPayload  returns payload object from form inputs
 */
function setupToolButton(btnId, resultId, endpoint, buildPayload) {
    document.getElementById(btnId).addEventListener("click", async () => {
        const btn = document.getElementById(btnId);
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> Calling...';
        showLoading(resultId);

        try {
            const payload = buildPayload();
            const response = await callTool(endpoint, payload);
            renderResult(resultId, response);
        } catch (e) {
            renderResult(resultId, {
                success: false,
                error: `Cannot connect to API. Is the server running on port 5000? (${e.message})`,
                error_type: "connection",
                data: null,
            });
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    });
}
