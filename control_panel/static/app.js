const state = {
  tasks: [],
  groupedTasks: {},
  selectedTask: null,
  jobs: [],
  activeJobId: null,
  selectedJobId: null,
  artifactPath: ".",
  artifactParent: null,
  selectedArtifactPath: null,
  selectedResultPath: null,
  envFields: [],
  pollTimer: null,
};

const els = {
  envStatus: document.getElementById("env-status"),
  groupNav: document.getElementById("group-nav"),
  featuredStrip: document.getElementById("featured-strip"),
  taskList: document.getElementById("task-list"),
  taskTitle: document.getElementById("task-title"),
  taskSummary: document.getElementById("task-summary"),
  taskForm: document.getElementById("task-form"),
  taskOutputs: document.getElementById("task-outputs"),
  taskCaution: document.getElementById("task-caution"),
  runTaskButton: document.getElementById("run-task-button"),
  logConsole: document.getElementById("log-console"),
  jobSummary: document.getElementById("job-summary"),
  jobQueue: document.getElementById("job-queue"),
  activeJobIndicator: document.getElementById("active-job-indicator"),
  cancelJobButton: document.getElementById("cancel-job-button"),
  artifacts: document.getElementById("artifacts"),
  artifactCurrent: document.getElementById("artifact-current"),
  artifactPreview: document.getElementById("artifact-preview"),
  artifactPreviewTitle: document.getElementById("artifact-preview-title"),
  artifactDownload: document.getElementById("artifact-download"),
  artifactUpButton: document.getElementById("artifact-up-button"),
  artifactOpenFolder: document.getElementById("artifact-open-folder"),
  envForm: document.getElementById("env-form"),
  reloadEnvButton: document.getElementById("reload-env-button"),
  saveEnvButton: document.getElementById("save-env-button"),
  envSaveStatus: document.getElementById("env-save-status"),
  resultSummary: document.getElementById("result-summary"),
  resultMetrics: document.getElementById("result-metrics"),
  resultTableShell: document.getElementById("result-table-shell"),
};

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `HTTP ${response.status}`);
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function groupTasks(tasks) {
  return tasks.reduce((acc, task) => {
    acc[task.group] ??= [];
    acc[task.group].push(task);
    return acc;
  }, {});
}

function renderEnvStatus(status) {
  const entries = [
    ["Env file", status.env_file_exists],
    ["Gemini key", status.google_api_key || status.gemini_api_key],
    ["Langfuse", status.langfuse_config],
    ["Neo4j", status.neo4j_credentials],
  ];
  els.envStatus.innerHTML = entries
    .map(
      ([label, ok]) => `
        <div class="status-pill">
          <strong>${escapeHtml(label)}</strong>
          <span class="${ok ? "artifact-status ok" : "artifact-status missing"}">
            ${ok ? "ready" : "missing"}
          </span>
        </div>
      `,
    )
    .join("");
}

function renderGroupNav() {
  els.groupNav.innerHTML = Object.keys(state.groupedTasks)
    .map((group) => `<button type="button" data-group="${escapeHtml(group)}">${escapeHtml(group)}</button>`)
    .join("");

  els.groupNav.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      const group = button.dataset.group;
      const firstTask = state.groupedTasks[group]?.[0];
      if (firstTask) selectTask(firstTask.task_id);
    });
  });
}

function renderFeaturedStrip() {
  const featured = state.tasks.filter((task) => task.featured);
  els.featuredStrip.innerHTML = featured
    .map(
      (task) => `
        <div class="feature-tile">
          <button type="button" data-task-id="${escapeHtml(task.task_id)}">
            <strong>${escapeHtml(task.title)}</strong>
            <small>${escapeHtml(task.summary)}</small>
          </button>
        </div>
      `,
    )
    .join("");

  els.featuredStrip.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => selectTask(button.dataset.taskId));
  });
}

function renderTaskList() {
  const markup = Object.entries(state.groupedTasks)
    .map(([group, tasks]) => {
      const items = tasks
        .map(
          (task) => `
            <div class="task-item ${state.selectedTask?.task_id === task.task_id ? "is-active" : ""}">
              <button type="button" data-task-id="${escapeHtml(task.task_id)}">
                <strong>${escapeHtml(task.title)}</strong>
                <small>${escapeHtml(task.summary)}</small>
                ${task.manual ? `<span class="task-badge">manual / interactive</span>` : ""}
              </button>
            </div>
          `,
        )
        .join("");
      return `<section><p class="eyebrow">${escapeHtml(group)}</p>${items}</section>`;
    })
    .join("");

  els.taskList.innerHTML = markup;
  els.taskList.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => selectTask(button.dataset.taskId));
  });
}

function buildTaskField(field) {
  const wrapper = document.createElement("div");
  wrapper.className = "field";

  const label = document.createElement("label");
  label.setAttribute("for", `field-${field.name}`);
  label.textContent = field.label;

  let input;
  if (field.field_type === "select") {
    input = document.createElement("select");
    field.options.forEach((option) => {
      const opt = document.createElement("option");
      opt.value = option.value;
      opt.textContent = option.label;
      if (String(option.value) === String(field.default ?? "")) opt.selected = true;
      input.appendChild(opt);
    });
  } else {
    input = document.createElement("input");
    input.type = field.field_type === "number" ? "number" : "text";
    if (field.default !== null && field.default !== undefined) input.value = field.default;
  }
  input.id = `field-${field.name}`;
  input.name = field.name;
  input.required = Boolean(field.required);
  wrapper.appendChild(label);
  wrapper.appendChild(input);

  if (field.help_text) {
    const help = document.createElement("div");
    help.className = "help";
    help.textContent = field.help_text;
    wrapper.appendChild(help);
  }
  return wrapper;
}

function collectTaskParams() {
  const params = {};
  if (!state.selectedTask) return params;
  state.selectedTask.fields.forEach((field) => {
    const input = document.getElementById(`field-${field.name}`);
    if (!input) return;
    const value = input.value;
    if (value === "") return;
    params[field.name] = field.field_type === "number" ? Number(value) : value;
  });
  return params;
}

async function renderExpectedOutputs(task) {
  let outputs = (task.expected_outputs || []).map((item) => String(item));
  try {
    const preview = await fetchJson("/api/tasks/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: task.task_id, params: collectTaskParams() }),
    });
    outputs = (preview.expected_outputs || []).map((item) => String(item));
  } catch (error) {
    console.warn("Preview outputs failed", error);
  }
  els.taskOutputs.innerHTML = outputs.length
    ? outputs.map((path) => `<li>${escapeHtml(path)}</li>`).join("")
    : "<li>No direct file output declared.</li>";
}

function renderTaskDetail() {
  const task = state.selectedTask;
  if (!task) {
    els.runTaskButton.disabled = true;
    return;
  }
  els.taskTitle.textContent = task.title;
  els.taskSummary.textContent = task.summary;
  els.taskForm.innerHTML = "";
  task.fields.forEach((field) => els.taskForm.appendChild(buildTaskField(field)));
  void renderExpectedOutputs(task);
  els.taskCaution.textContent = task.caution || "No caution notes for this task.";
  els.runTaskButton.disabled = false;
}

function selectTask(taskId) {
  state.selectedTask = state.tasks.find((task) => task.task_id === taskId) || null;
  renderTaskList();
  renderTaskDetail();
}

function formatDate(timestamp) {
  if (!timestamp) return "-";
  return new Date(timestamp * 1000).toLocaleString();
}

function renderJobQueue() {
  if (!state.jobs.length) {
    els.jobQueue.innerHTML = `<div class="muted">No jobs queued yet.</div>`;
    return;
  }
  els.jobQueue.innerHTML = state.jobs
    .map(
      (job) => `
        <button type="button" class="queue-item ${state.selectedJobId === job.job_id ? "is-active" : ""}" data-job-id="${escapeHtml(job.job_id)}">
          <strong>${escapeHtml(job.task_title)}</strong>
          <small>
            ${escapeHtml(job.status)}
            ${job.queue_position ? ` | queue #${escapeHtml(job.queue_position)}` : ""}
          </small>
        </button>
      `,
    )
    .join("");
  els.jobQueue.querySelectorAll(".queue-item").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedJobId = button.dataset.jobId;
      updateJobPane();
      renderJobQueue();
    });
  });
}

function updateJobPane() {
  const targetJob =
    state.jobs.find((job) => job.job_id === state.selectedJobId) ??
    state.jobs.find((job) => job.job_id === state.activeJobId) ??
    state.jobs[0] ??
    null;

  if (!targetJob) {
    els.jobSummary.textContent = "No job recorded yet.";
    els.logConsole.textContent = "Waiting for a task...";
    els.activeJobIndicator.textContent = "Idle";
    els.cancelJobButton.disabled = true;
    return;
  }

  state.selectedJobId = targetJob.job_id;
  const indicatorStatus =
    targetJob.status === "running" || targetJob.status === "starting"
      ? "Running"
      : targetJob.status === "queued"
        ? "Queued"
        : targetJob.status;

  els.activeJobIndicator.textContent = `${indicatorStatus}\n${targetJob.task_title}`;
  els.jobSummary.innerHTML = `
    <strong>${escapeHtml(targetJob.task_title)}</strong><br />
    Status: ${escapeHtml(targetJob.status)}<br />
    Queue position: ${escapeHtml(targetJob.queue_position ?? "-")}<br />
    Return code: ${escapeHtml(targetJob.return_code ?? "-")}<br />
    Created: ${escapeHtml(formatDate(targetJob.created_at))}<br />
    Started: ${escapeHtml(formatDate(targetJob.started_at))}<br />
    Ended: ${escapeHtml(formatDate(targetJob.ended_at))}
  `;
  els.logConsole.textContent = targetJob.logs.join("\n") || "No logs captured.";
  els.logConsole.scrollTop = els.logConsole.scrollHeight;
  els.cancelJobButton.disabled = ["completed", "failed", "cancelled"].includes(targetJob.status);
}

async function browseArtifacts(path = ".") {
  const query = path ? `?path=${encodeURIComponent(path)}` : "";
  const listing = await fetchJson(`/api/artifacts${query}`);
  state.artifactPath = listing.current.path;
  state.artifactParent = listing.parent?.path || null;
  els.artifactCurrent.textContent = listing.current.path;
  els.artifactUpButton.disabled = !state.artifactParent;
  els.artifacts.innerHTML = listing.children
    .map(
      (artifact) => `
        <button type="button" class="artifact-item artifact-button" data-path="${escapeHtml(artifact.path)}" data-is-dir="${artifact.is_dir}">
          <div class="artifact-status ${artifact.exists ? "ok" : "missing"}">
            ${artifact.is_dir ? "directory" : artifact.exists ? "available" : "missing"}
          </div>
          <strong>${escapeHtml(artifact.path.split("/").slice(-1)[0])}</strong>
          <small>${artifact.is_dir ? "folder" : artifact.size_bytes ? `${artifact.size_bytes} bytes` : "file"}</small>
        </button>
      `,
    )
    .join("");

  els.artifacts.querySelectorAll(".artifact-button").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = button.dataset.path;
      const isDir = button.dataset.isDir === "true";
      if (isDir) {
        await browseArtifacts(target);
        return;
      }
      await previewArtifact(target);
    });
  });
}

function renderEmptyResult(message) {
  state.selectedResultPath = null;
  els.resultSummary.textContent = message;
  els.resultMetrics.innerHTML = "";
  els.resultTableShell.innerHTML = `<div class="muted">${escapeHtml(message)}</div>`;
}

function renderResultPreview(payload) {
  const { artifact, summary, metric_cards: metricCards, rows } = payload;
  state.selectedResultPath = artifact.path;
  els.resultSummary.innerHTML = `
    <strong>${escapeHtml(artifact.path)}</strong><br />
    Rows: ${escapeHtml(summary.row_count)} | Columns: ${escapeHtml(summary.column_count)}
  `;

  els.resultMetrics.innerHTML = metricCards.length
    ? metricCards
        .map(
          (card) => `
            <article class="metric-card">
              <span>${escapeHtml(card.name)}</span>
              <strong>${escapeHtml(card.mean)}</strong>
              <small>min ${escapeHtml(card.min)} | max ${escapeHtml(card.max)}</small>
            </article>
          `,
        )
        .join("")
    : `<div class="muted">No numeric metric columns detected in this CSV.</div>`;

  if (!rows.length) {
    els.resultTableShell.innerHTML = `<div class="muted">CSV is empty.</div>`;
    return;
  }

  const columns = summary.columns || Object.keys(rows[0]);
  const header = columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("");
  const body = rows
    .map(
      (row) =>
        `<tr>${columns
          .map((column) => `<td>${escapeHtml(row[column] ?? "")}</td>`)
          .join("")}</tr>`,
    )
    .join("");

  els.resultTableShell.innerHTML = `
    <table class="result-table">
      <thead>
        <tr>${header}</tr>
      </thead>
      <tbody>${body}</tbody>
    </table>
  `;
}

async function loadResultPreview(path) {
  try {
    const preview = await fetchJson(`/api/results/preview?path=${encodeURIComponent(path)}`);
    renderResultPreview(preview);
  } catch (error) {
    renderEmptyResult(`Failed to load CSV preview: ${error.message}`);
  }
}

async function previewArtifact(path) {
  const preview = await fetchJson(`/api/artifacts/preview?path=${encodeURIComponent(path)}`);
  state.selectedArtifactPath = preview.artifact.path;
  els.artifactPreviewTitle.textContent = preview.artifact.path;
  els.artifactOpenFolder.disabled = false;

  if (preview.kind === "directory") {
    els.artifactDownload.classList.add("hidden");
    els.artifactPreview.textContent =
      preview.children.length > 0
        ? preview.children.map((child) => `${child.is_dir ? "[dir]" : "[file]"} ${child.path}`).join("\n")
        : "Empty directory.";
    renderEmptyResult("Select a CSV file to inspect result metrics.");
    return;
  }

  if (preview.download_url) {
    els.artifactDownload.href = preview.download_url;
    els.artifactDownload.classList.remove("hidden");
  } else {
    els.artifactDownload.classList.add("hidden");
  }
  els.artifactPreview.textContent = preview.content || "No text preview available for this file type.";

  if (preview.artifact.path.toLowerCase().endsWith(".csv")) {
    await loadResultPreview(preview.artifact.path);
  } else {
    renderEmptyResult("Selected artifact is not a CSV result file.");
  }
}

async function openArtifactFolder() {
  const target = state.selectedArtifactPath || state.artifactPath || ".";
  try {
    await fetchJson(`/api/artifacts/open-folder?path=${encodeURIComponent(target)}`, { method: "POST" });
  } catch (error) {
    els.artifactPreview.textContent = `Failed to open folder:\n${error.message}`;
  }
}

function buildEnvField(field) {
  const wrapper = document.createElement("div");
  wrapper.className = "field env-field";

  const label = document.createElement("label");
  label.setAttribute("for", `env-${field.name}`);
  label.textContent = field.label;

  const input = document.createElement("input");
  input.id = `env-${field.name}`;
  input.name = field.name;
  input.type = field.sensitive ? "password" : "text";
  input.value = field.value || "";

  const help = document.createElement("div");
  help.className = "help";
  help.textContent = field.description;

  wrapper.appendChild(label);
  wrapper.appendChild(input);
  wrapper.appendChild(help);
  return wrapper;
}

function renderEnvEditor() {
  if (!state.envFields.length) {
    els.envForm.innerHTML = `<div class="muted">No editable environment fields were returned.</div>`;
    return;
  }

  const grouped = state.envFields.reduce((acc, field) => {
    acc[field.group] ??= [];
    acc[field.group].push(field);
    return acc;
  }, {});

  els.envForm.innerHTML = "";
  Object.entries(grouped).forEach(([group, fields]) => {
    const section = document.createElement("section");
    section.className = "env-group";

    const title = document.createElement("p");
    title.className = "eyebrow";
    title.textContent = group;
    section.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "env-grid";
    fields.forEach((field) => grid.appendChild(buildEnvField(field)));
    section.appendChild(grid);
    els.envForm.appendChild(section);
  });
}

function collectEnvValues() {
  const values = {};
  state.envFields.forEach((field) => {
    const input = document.getElementById(`env-${field.name}`);
    values[field.name] = input ? input.value : "";
  });
  return values;
}

async function loadEnvConfig() {
  const payload = await fetchJson("/api/env");
  state.envFields = payload.fields || [];
  renderEnvEditor();
  renderEnvStatus(payload.env_status);
  els.envSaveStatus.textContent = payload.env_file_exists
    ? `Loaded ${payload.env_file_path}`
    : "No .env file yet. Save once to create it.";
}

async function saveEnvConfig() {
  try {
    const payload = await fetchJson("/api/env", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ values: collectEnvValues() }),
    });
    state.envFields = payload.fields || [];
    renderEnvEditor();
    renderEnvStatus(payload.env_status);
    els.envSaveStatus.textContent = `Saved ${payload.env_file_path}`;
    await refreshOverview();
  } catch (error) {
    els.envSaveStatus.textContent = `Failed to save .env: ${error.message}`;
  }
}

async function refreshJobs() {
  const jobs = await fetchJson("/api/jobs");
  state.jobs = jobs;
  const active =
    jobs.find((job) => job.status === "running" || job.status === "starting") ||
    jobs.find((job) => job.status === "queued") ||
    null;
  state.activeJobId = active?.job_id || null;
  if (!state.selectedJobId && jobs.length) state.selectedJobId = jobs[0].job_id;
  renderJobQueue();
  updateJobPane();
}

async function refreshOverview() {
  const overview = await fetchJson("/api/overview");
  state.tasks = overview.tasks;
  state.groupedTasks = groupTasks(overview.tasks);
  state.activeJobId = overview.active_job_id || state.activeJobId;
  renderEnvStatus(overview.env_status);
  renderGroupNav();
  renderFeaturedStrip();
  if (!state.selectedTask && state.tasks.length) {
    state.selectedTask = state.tasks[0];
  } else if (state.selectedTask) {
    state.selectedTask = state.tasks.find((task) => task.task_id === state.selectedTask.task_id) || state.tasks[0];
  }
  renderTaskList();
  renderTaskDetail();
}

async function runSelectedTask() {
  if (!state.selectedTask) return;
  const params = collectTaskParams();
  try {
    const job = await fetchJson("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: state.selectedTask.task_id, params }),
    });
    state.selectedJobId = job.job_id;
    await refreshJobs();
  } catch (error) {
    els.logConsole.textContent = `Failed to queue task:\n${error.message}`;
  }
}

async function cancelSelectedJob() {
  if (!state.selectedJobId) return;
  try {
    await fetchJson(`/api/jobs/${encodeURIComponent(state.selectedJobId)}/cancel`, { method: "POST" });
    await refreshJobs();
  } catch (error) {
    els.logConsole.textContent = `Failed to cancel job:\n${error.message}`;
  }
}

async function boot() {
  await refreshOverview();
  await refreshJobs();
  await browseArtifacts(".");
  await loadEnvConfig();

  els.runTaskButton.addEventListener("click", runSelectedTask);
  els.cancelJobButton.addEventListener("click", cancelSelectedJob);
  els.taskForm.addEventListener("input", () => {
    if (state.selectedTask) void renderExpectedOutputs(state.selectedTask);
  });
  els.artifactUpButton.addEventListener("click", async () => {
    if (state.artifactParent) await browseArtifacts(state.artifactParent);
  });
  els.artifactOpenFolder.addEventListener("click", openArtifactFolder);
  els.reloadEnvButton.addEventListener("click", loadEnvConfig);
  els.saveEnvButton.addEventListener("click", saveEnvConfig);

  state.pollTimer = window.setInterval(async () => {
    await refreshOverview();
    await refreshJobs();
    await browseArtifacts(state.artifactPath || ".");
    if (state.selectedResultPath) {
      await loadResultPreview(state.selectedResultPath);
    }
  }, 3000);
}

boot().catch((error) => {
  els.logConsole.textContent = `Failed to boot control room:\n${error.message}`;
});
