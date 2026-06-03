import { fetchJson } from "./api.js";

const state = {
  skills: [],
  runs: [],
};

const skillSelect = document.getElementById("skill-select");
const skillMeta = document.getElementById("skill-meta");
const skillInput = document.getElementById("skill-input");
const skillResult = document.getElementById("skill-result");
const runsList = document.getElementById("runs-list");
const runLog = document.getElementById("run-log");
const memoryContent = document.getElementById("memory-content");
const cronEnabled = document.getElementById("cron-enabled");
const cronSchedule = document.getElementById("cron-schedule");
const cronCommand = document.getElementById("cron-command");
const cronResult = document.getElementById("cron-result");
const apiStatus = document.getElementById("api-status");
const currentTime = document.getElementById("current-time");
const lastRunStatus = document.getElementById("last-run-status");

async function loadHealth() {
  try {
    const data = await fetchJson("/api/health");
    apiStatus.textContent = `API: ${data.status}`;
    apiStatus.dataset.status = data.status === "ok" ? "ok" : "error";
  } catch (err) {
    apiStatus.textContent = `API: error (${err.message})`;
    apiStatus.dataset.status = "error";
  }
}

async function loadSkills() {
  const data = await fetchJson("/api/skills");
  state.skills = data.skills || [];
  skillSelect.innerHTML = "";

  for (const skill of state.skills) {
    const option = document.createElement("option");
    option.value = skill.name;
    option.textContent = skill.name;
    skillSelect.appendChild(option);
  }

  renderSelectedSkill();
}

function renderSelectedSkill() {
  const selected = state.skills.find((s) => s.name === skillSelect.value) || state.skills[0];
  if (!selected) {
    skillMeta.textContent = "No skills found.";
    return;
  }
  skillSelect.value = selected.name;
  skillMeta.textContent = JSON.stringify(selected, null, 2);
}

async function runSkill() {
  const skillName = skillSelect.value;
  let parsedInput = {};
  try {
    parsedInput = JSON.parse(skillInput.value || "{}");
  } catch (err) {
    skillResult.textContent = `Invalid JSON input: ${err.message}`;
    return;
  }

  try {
    const result = await fetchJson(`/api/skills/${encodeURIComponent(skillName)}/run`, {
      method: "POST",
      body: JSON.stringify({ input: parsedInput }),
    });
    skillResult.textContent = JSON.stringify(result, null, 2);
    lastRunStatus.textContent = `Last run: ${result.status} (${result.skill})`;
    lastRunStatus.dataset.status = result.status;
    await loadRuns();
    await loadMemory();
  } catch (err) {
    skillResult.textContent = `Run failed: ${err.message}`;
    lastRunStatus.textContent = "Last run: failed";
    lastRunStatus.dataset.status = "failed";
  }
}

async function loadRuns() {
  const data = await fetchJson("/api/runs?limit=25");
  state.runs = data.runs || [];
  runsList.innerHTML = "";

  for (const run of state.runs) {
    const row = document.createElement("div");
    row.className = "run-item-row";

    const btn = document.createElement("button");
    btn.className = "run-item";
    btn.dataset.status = run.status || "unknown";
    btn.textContent = `${run.run_id} | ${run.skill} | ${run.status} | ${run.duration_ms}ms`;
    btn.addEventListener("click", () => loadRunLog(run.run_id));

    const tip = document.createElement("span");
    tip.className = "tooltip-trigger";
    tip.tabIndex = 0;
    tip.textContent = "?";
    tip.dataset.tooltip = "Open the full structured log for this run id.";

    row.appendChild(btn);
    row.appendChild(tip);
    runsList.appendChild(row);
  }
}

async function loadRunLog(runId) {
  try {
    const data = await fetchJson(`/api/runs/${encodeURIComponent(runId)}/log`);
    runLog.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    runLog.textContent = `Could not load log: ${err.message}`;
  }
}

async function loadMemory() {
  const data = await fetchJson("/api/memory");
  memoryContent.textContent = data.content || "";
}

async function loadCron() {
  try {
    const data = await fetchJson("/api/cron");
    cronEnabled.checked = Boolean(data.enabled);
    cronSchedule.value = data.schedule || "";
    cronCommand.value = data.command || "thin-runner run-pipeline pipelines/hello_pipeline.yaml";
    cronResult.textContent = data.managed
      ? "Loaded current Thin Runner cron block."
      : "No Thin Runner-managed cron block found yet.";
  } catch (err) {
    cronResult.textContent = `Could not read cron: ${err.message}`;
  }
}

async function saveCron() {
  const confirmation = confirm(
    "This will update only the Thin Runner-managed cron block and create a backup. Continue?"
  );
  if (!confirmation) {
    return;
  }

  try {
    const data = await fetchJson("/api/cron", {
      method: "PUT",
      body: JSON.stringify({
        enabled: cronEnabled.checked,
        schedule: cronSchedule.value,
        command: cronCommand.value,
      }),
    });
    cronResult.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    cronResult.textContent = `Could not save cron: ${err.message}`;
  }
}

function updateClock() {
  currentTime.textContent = `Current time: ${new Date().toLocaleString()}`;
}

document.getElementById("run-skill").addEventListener("click", runSkill);
document.getElementById("refresh-runs").addEventListener("click", loadRuns);
document.getElementById("refresh-memory").addEventListener("click", loadMemory);
document.getElementById("save-cron").addEventListener("click", saveCron);
skillSelect.addEventListener("change", renderSelectedSkill);

async function boot() {
  updateClock();
  setInterval(updateClock, 1000);
  await loadHealth();
  await loadSkills();
  await loadRuns();
  await loadMemory();
  await loadCron();
}

boot();
