let organizations = [];
let selectedOrg = null;
let currentDraft = null;
let pendingAttachments = [];
let currentDraftId = null;
let discoveryCandidates = [];
let interactions = [];

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showError(message) {
  document.getElementById("ai-output").textContent = message;
}

function setActivePage(pathname = window.location.pathname) {
  const known = ["/research-intake", "/organization-discovery", "/integrations", "/data-tools", "/analytics", "/priority-queue", "/follow-ups", "/knowledge-search"];
  const route = known.includes(pathname) ? pathname : "/";
  const pageMap = {
    "/": "crm-page",
    "/research-intake": "research-intake-page",
    "/organization-discovery": "organization-discovery-page",
    "/integrations": "integrations-page",
    "/data-tools": "data-tools-page",
    "/analytics": "analytics-page",
    "/priority-queue": "priority-queue-page",
    "/follow-ups": "follow-ups-page",
    "/knowledge-search": "knowledge-search-page",
  };

  Object.values(pageMap).forEach(pageId => {
    const el = document.getElementById(pageId);
    if (el) el.classList.add("hidden");
  });
  const page = document.getElementById(pageMap[route]);
  if (page) page.classList.remove("hidden");
  dispatchPage(route);
}

// ---- Phase 3: Timeline ----

async function loadTimeline() {
  if (!requireSelected()) return;
  const el = document.getElementById("timeline-output");
  el.innerHTML = "<p class='muted'>Loading timeline...</p>";
  try {
    const events = await api(`/api/organizations/${selectedOrg.id}/timeline`);
    renderTimeline(events);
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderTimeline(events) {
  const el = document.getElementById("timeline-output");
  if (!events.length) {
    el.innerHTML = '<p class="muted">No timeline events available.</p>';
    return;
  }

  const eventIcon = (type) => {
    const icons = {
      organization_created: "🏢",
      interaction: "💬",
      task_created: "📋",
      task_completed: "✅",
      draft_saved: "📝",
    };
    return icons[type] || "📌";
  };

  const eventLabel = (type) => {
    const labels = {
      organization_created: "Created",
      interaction: "Interaction",
      task_created: "Task",
      task_completed: "Completed",
      draft_saved: "Draft",
    };
    return labels[type] || type;
  };

  const today = new Date().toISOString().split("T")[0];

  el.innerHTML = `<div class="tl-container">
    ${events.map(e => {
      const isOverdue = e.date && e.date < today && e.event_type !== "organization_created";
      return `
      <div class="tl-item ${isOverdue ? 'tl-overdue' : ''}">
        <div class="tl-icon">${eventIcon(e.event_type)}</div>
        <div class="tl-content">
          <div class="tl-header">
            <span class="tl-date">${escapeHtml(e.date || "—")}</span>
            <span class="tl-badge tl-badge-${e.event_type}">${eventLabel(e.event_type)}</span>
          </div>
          <div class="tl-title">${escapeHtml(e.title)}</div>
          ${e.description ? `<div class="tl-desc">${escapeHtml(e.description.substring(0, 200))}</div>` : ""}
        </div>
      </div>`;
    }).join("")}
  </div>`;
}

// ---- Phase 3: Knowledge Search ----

function ksValue(id) {
  return document.getElementById(id).value;
}

function ksSet(id, val) {
  document.getElementById(id).value = val;
}

async function loadKnowledgeSearch() {
  const orgSel = document.getElementById("ks-filter-org");
  orgSel.innerHTML = '<option value="">All</option>';
  for (const org of organizations) {
    orgSel.innerHTML += `<option value="${org.id}">${escapeHtml(org.name)}</option>`;
  }
  const params = new URLSearchParams(window.location.search);
  const qParam = params.get("q") || "";
  const orgParam = params.get("org_id") || "";
  if (qParam) ksSet("ks-query", qParam);
  if (orgParam) ksSet("ks-filter-org", orgParam);
  if (qParam) doKnowledgeSearch();
}

async function doKnowledgeSearch() {
  const q = ksValue("ks-query").trim();
  const orgId = ksValue("ks-filter-org");
  const contentType = ksValue("ks-filter-type");
  const loadingEl = document.getElementById("ks-loading");
  const errorEl = document.getElementById("ks-error");
  const resultsEl = document.getElementById("ks-results");
  const countEl = document.getElementById("ks-count");

  errorEl.classList.add("hidden");
  resultsEl.innerHTML = "";
  countEl.textContent = "";

  if (!q) {
    resultsEl.innerHTML = '<p class="muted">Enter a keyword to search.</p>';
    return;
  }

  loadingEl.classList.remove("hidden");

  let url = `/api/knowledge/search?q=${encodeURIComponent(q)}`;
  if (orgId) url += `&org_id=${orgId}`;
  if (contentType) url += `&content_type=${contentType}`;

  try {
    const results = await api(url);
    loadingEl.classList.add("hidden");
    renderKnowledgeResults(results, q);
  } catch (error) {
    loadingEl.classList.add("hidden");
    errorEl.textContent = "Search failed: " + error.message;
    errorEl.classList.remove("hidden");
  }
}

function renderKnowledgeResults(results, query) {
  const el = document.getElementById("ks-results");
  const countEl = document.getElementById("ks-count");

  if (!results.length) {
    el.innerHTML = `<p class="muted">No results found for "${escapeHtml(query)}".</p>`;
    countEl.textContent = "";
    return;
  }

  countEl.textContent = `${results.length} result(s) found.`;

  const typeLabels = {
    organization: "Organization",
    interaction: "Interaction",
    task: "Task",
    draft: "Draft",
    lesson: "Lesson Learned",
    insight: "Reusable Insight",
    playbook: "Playbook Candidate",
    "workflow-opportunity": "Workflow Opportunity",
    "knowledge-source": "Knowledge Source",
    "failure-case": "Failure Case",
    "adoption-risk": "Adoption Risk",
  };

  const typeIcons = {
    organization: "🏢",
    interaction: "💬",
    task: "📋",
    draft: "📝",
    lesson: "💡",
    insight: "🔍",
    playbook: "📖",
    "workflow-opportunity": "⚙️",
    "knowledge-source": "📚",
    "failure-case": "⚠️",
    "adoption-risk": "🛡️",
  };

  el.innerHTML = `<div class="ks-grid">
    ${results.map(r => `
      <article class="ks-card">
        <div class="ks-card-header">
          <span class="ks-type-badge ks-type-${r.content_type}">${typeIcons[r.content_type] || "📌"} ${typeLabels[r.content_type] || r.content_type}</span>
          ${r.date ? `<span class="ks-date">${escapeHtml(r.date)}</span>` : ""}
        </div>
        <div class="ks-org">${escapeHtml(r.organization_name)}</div>
        <div class="ks-title">${escapeHtml(r.title)}</div>
        ${r.excerpt ? `<div class="ks-excerpt">${escapeHtml(r.excerpt.substring(0, 300))}</div>` : ""}
        <div class="ks-link">
          <button onclick="navigateTo('${r.link}')" class="btn-small">View Organization</button>
        </div>
      </article>
    `).join("")}
  </div>`;
}

// ---- Phase 3: Lessons Learned ----

async function loadLessons() {
  if (!requireSelected()) return;
  const el = document.getElementById("lessons-output");
  el.innerHTML = "<p class='muted'>Loading lessons...</p>";
  try {
    const lessons = await api(`/api/organizations/${selectedOrg.id}/lessons-learned`);
    if (!lessons.length) {
      el.innerHTML = '<p class="muted">No lessons learned yet. Run AI Note Summary on an interaction to extract lessons.</p>';
      return;
    }
    el.innerHTML = lessons.map(l => `
      <article class="lesson-card">
        <div class="lesson-header">
          <strong>${escapeHtml(l.title)}</strong>
          <span class="lesson-date">${escapeHtml(l.date || "")}</span>
        </div>
        <p class="lesson-desc">${escapeHtml(l.description)}</p>
        <div class="lesson-meta">
          <span class="muted">Source: ${escapeHtml(l.source_interaction)}</span>
          ${l.tags && l.tags.length ? `<div class="lesson-tags">${l.tags.map(t => `<span class="int-tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
        </div>
      </article>
    `).join("");
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---- Phase 3: Playbook Candidates ----

async function loadPlaybooks() {
  if (!requireSelected()) return;
  const el = document.getElementById("playbook-output");
  el.innerHTML = "<p class='muted'>Loading playbook candidates...</p>";
  try {
    const candidates = await api(`/api/organizations/${selectedOrg.id}/playbook-candidates`);
    if (!candidates.length) {
      el.innerHTML = '<p class="muted">No playbook candidates yet. Run AI Note Summary on an interaction to generate playbooks.</p>';
      return;
    }
    el.innerHTML = candidates.map(pb => `
      <article class="playbook-card">
        <h4 class="pb-title">${escapeHtml(pb.title)}</h4>
        <div class="pb-section">
          <strong>When to use:</strong>
          <p>${escapeHtml(pb.when_to_use)}</p>
        </div>
        <div class="pb-section">
          <strong>Suggested process:</strong>
          <p>${escapeHtml(pb.suggested_process)}</p>
        </div>
        <div class="lesson-meta">
          <span class="muted">Source: ${escapeHtml(pb.source_interaction)}</span>
          ${pb.tags && pb.tags.length ? `<div class="lesson-tags">${pb.tags.map(t => `<span class="int-tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
        </div>
      </article>
    `).join("");
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---- Phase 3: Workflow Opportunities ----

async function loadWorkflowOpps() {
  if (!requireSelected()) return;
  const el = document.getElementById("workflow-opps-output");
  el.innerHTML = "<p class='muted'>Loading workflow opportunities...</p>";
  try {
    const opps = await api(`/api/organizations/${selectedOrg.id}/workflow-opportunities`);
    if (!opps.length) {
      el.innerHTML = '<p class="muted">No workflow opportunities yet. Run AI Note Summary on an interaction to identify opportunities.</p>';
      return;
    }
    el.innerHTML = opps.map(o => `
      <article class="wf-card">
        <div class="wf-header">
          <strong>${escapeHtml(o.title)}</strong>
          <span class="wf-status ${o.status ? 'wf-status--' + o.status.replace(/\\s+/g, '-').toLowerCase() : ''}">${escapeHtml(o.status || "Identified")}</span>
        </div>
        <div class="wf-section"><strong>Current process:</strong> ${escapeHtml(o.current_process)}</div>
        <div class="wf-section"><strong>Pain point:</strong> ${escapeHtml(o.pain_point)}</div>
        <div class="wf-section"><strong>Possible AI support:</strong> ${escapeHtml(o.possible_ai_support)}</div>
        ${o.knowledge_sources_needed && o.knowledge_sources_needed.length ? `<div class="wf-section"><strong>Knowledge sources needed:</strong> ${o.knowledge_sources_needed.map(s => `<span class="int-tag">${escapeHtml(s)}</span>`).join(" ")}</div>` : ""}
        ${o.human_review_points && o.human_review_points.length ? `<div class="wf-section"><strong>Human review points:</strong><ul>${o.human_review_points.map(p => `<li>${escapeHtml(p)}</li>`).join("")}</ul></div>` : ""}
        ${o.risks_or_exceptions && o.risks_or_exceptions.length ? `<div class="wf-section"><strong>Risks / exceptions:</strong><ul>${o.risks_or_exceptions.map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul></div>` : ""}
        ${o.staff_impact ? `<div class="wf-section"><strong>Staff impact:</strong> ${escapeHtml(o.staff_impact)}</div>` : ""}
        ${o.adoption_risk_level && o.adoption_risk_level !== 'Unknown' ? `<div class="wf-section"><strong>Adoption risk level:</strong> <span class="int-tag">${escapeHtml(o.adoption_risk_level)}</span></div>` : ""}
        ${o.next_discovery_questions && o.next_discovery_questions.length ? `<div class="wf-section"><strong>Next discovery questions:</strong><ul>${o.next_discovery_questions.map(q => `<li>${escapeHtml(q)}</li>`).join("")}</ul></div>` : ""}
        ${o.known_failure_cases && o.known_failure_cases.length ? `<div class="wf-section"><strong>Known failure cases:</strong><ul>${o.known_failure_cases.map(f => `<li>${escapeHtml(f)}</li>`).join("")}</ul></div>` : ""}
        <div class="lesson-meta">
          <span class="muted">Source: ${escapeHtml(o.source_interaction_title)}</span>
          ${o.tags && o.tags.length ? `<div class="lesson-tags">${o.tags.map(t => `<span class="int-tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
        </div>
      </article>
    `).join("");
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---- Phase 3: Knowledge Sources ----

async function loadKnowledgeSources() {
  if (!requireSelected()) return;
  const el = document.getElementById("knowledge-sources-output");
  el.innerHTML = "<p class='muted'>Loading knowledge sources...</p>";
  try {
    const sources = await api(`/api/organizations/${selectedOrg.id}/knowledge-sources`);
    if (!sources.length) {
      el.innerHTML = '<p class="muted">No knowledge sources recorded. Run AI Note Summary on an interaction to identify knowledge sources.</p>';
      return;
    }
    el.innerHTML = sources.map(s => `
      <div class="ks-item">
        <span class="ks-type-badge">${escapeHtml(s.source_type)}</span>
        <strong>${escapeHtml(s.name)}</strong>
        ${s.description ? `<p class="muted">${escapeHtml(s.description)}</p>` : ""}
        ${s.location_note ? `<p class="muted">${escapeHtml(s.location_note)}</p>` : ""}
      </div>
    `).join("");
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---- Phase 3: Failure Cases / Exceptions ----

async function loadFailureCases() {
  if (!requireSelected()) return;
  const el = document.getElementById("failure-cases-output");
  el.innerHTML = "<p class='muted'>Loading failure cases...</p>";
  try {
    const cases = await api(`/api/organizations/${selectedOrg.id}/failure-cases`);
    if (!cases.length) {
      el.innerHTML = '<p class="muted">No failure cases recorded. Run AI Note Summary on an interaction to extract failure cases.</p>';
      return;
    }
    el.innerHTML = cases.map(fc => `
      <article class="fc-card">
        <div class="fc-header">
          <strong>${escapeHtml(fc.what_failed)}</strong>
        </div>
        <div class="fc-section"><strong>Why it failed:</strong> ${escapeHtml(fc.why_it_failed)}</div>
        <div class="fc-section"><strong>Missing context:</strong> ${escapeHtml(fc.missing_context)}</div>
        <div class="fc-section"><strong>Human review required:</strong> ${escapeHtml(fc.human_review_required)}</div>
        <div class="fc-section"><strong>Suggested prevention:</strong> ${escapeHtml(fc.suggested_prevention)}</div>
        <div class="lesson-meta">
          <span class="muted">Source: ${escapeHtml(fc.source_interaction_title)}</span>
          ${fc.tags && fc.tags.length ? `<div class="lesson-tags">${fc.tags.map(t => `<span class="int-tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
        </div>
      </article>
    `).join("");
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---- Phase 3: Adoption Risk Notes ----

async function loadAdoptionRisks() {
  if (!requireSelected()) return;
  const el = document.getElementById("adoption-risk-output");
  el.innerHTML = "<p class='muted'>Loading adoption risk notes...</p>";
  try {
    const risks = await api(`/api/organizations/${selectedOrg.id}/adoption-risk-notes`);
    if (!risks.length) {
      el.innerHTML = '<p class="muted">No adoption risk notes yet. Run AI Note Summary on an interaction to identify adoption risks.</p>';
      return;
    }
    el.innerHTML = risks.map(ar => `
      <article class="ar-card">
        <div class="ar-header">
          <span class="ar-type-badge ar-type--${escapeHtml(ar.risk_type.toLowerCase().replace(/\\s+/g, '-'))}">${escapeHtml(ar.risk_type)}</span>
          <span class="ar-severity ar-severity--${escapeHtml(ar.severity.toLowerCase())}">${escapeHtml(ar.severity)}</span>
        </div>
        <div class="ar-section"><strong>Description:</strong> ${escapeHtml(ar.description)}</div>
        ${ar.related_staff_role ? `<div class="ar-section"><strong>Related staff role:</strong> ${escapeHtml(ar.related_staff_role)}</div>` : ""}
        ${ar.suggested_mitigation ? `<div class="ar-section"><strong>Suggested mitigation:</strong> ${escapeHtml(ar.suggested_mitigation)}</div>` : ""}
        <div class="lesson-meta">
          <span class="muted">Source: ${escapeHtml(ar.source_interaction_title)}</span>
          ${ar.tags && ar.tags.length ? `<div class="lesson-tags">${ar.tags.map(t => `<span class="int-tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
        </div>
      </article>
    `).join("");
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

// ---- Phase 3: Knowledge Analytics ----

function renderOrganizationalKnowledge(knowledge) {
  if (!knowledge) return "";

  const tagEntries = Object.entries(knowledge.most_common_tags || {});
  const recentEntries = knowledge.recent_knowledge_activity || [];

  let html = `<section class="analytics-section"><h3>Workflow Transformation Knowledge</h3>`;

  html += `<div class="metric-grid">
    <div class="metric-card">
      <div class="metric-value">${knowledge.total_knowledge_items != null ? knowledge.total_knowledge_items : "—"}</div>
      <div class="metric-label">Total Knowledge Items</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.organizations_with_interaction_history != null ? knowledge.organizations_with_interaction_history : "—"}</div>
      <div class="metric-label">Orgs with Interactions</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.organizations_without_interaction_history != null ? knowledge.organizations_without_interaction_history : "—"}</div>
      <div class="metric-label">Orgs without Interactions</div>
    </div>
  </div>`;

  html += `<div class="metric-grid">
    <div class="metric-card">
      <div class="metric-value">${knowledge.workflow_opportunities_identified != null ? knowledge.workflow_opportunities_identified : "—"}</div>
      <div class="metric-label">Workflow Opps Identified</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.workflow_opps_with_human_review != null ? knowledge.workflow_opps_with_human_review : "—"}</div>
      <div class="metric-label">Workflow Opps w/ Human Review</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.organizations_with_workflow_opportunities != null ? knowledge.organizations_with_workflow_opportunities : "—"}</div>
      <div class="metric-label">Orgs with Workflow Opps</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.organizations_missing_knowledge_source_notes != null ? knowledge.organizations_missing_knowledge_source_notes : "—"}</div>
      <div class="metric-label">Orgs Missing Knowledge Sources</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.failure_cases_recorded != null ? knowledge.failure_cases_recorded : "—"}</div>
      <div class="metric-label">Failure Cases Recorded</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.candidate_pilot_workflows != null ? knowledge.candidate_pilot_workflows : "—"}</div>
      <div class="metric-label">Candidate Pilot Workflows</div>
    </div>
  </div>`;

  html += `<div class="metric-grid">
    <div class="metric-card">
      <div class="metric-value">${knowledge.adoption_risk_notes_recorded != null ? knowledge.adoption_risk_notes_recorded : "—"}</div>
      <div class="metric-label">Adoption Risk Notes</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.organizations_with_adoption_risk_notes != null ? knowledge.organizations_with_adoption_risk_notes : "—"}</div>
      <div class="metric-label">Orgs with Risk Notes</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.staff_concern_notes != null ? knowledge.staff_concern_notes : "—"}</div>
      <div class="metric-label">Staff Concern Notes</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.evaluation_risk_notes != null ? knowledge.evaluation_risk_notes : "—"}</div>
      <div class="metric-label">Evaluation Risk Notes</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${knowledge.high_severity_adoption_risks != null ? knowledge.high_severity_adoption_risks : "—"}</div>
      <div class="metric-label">High-Severity Risks</div>
    </div>
  </div>`;

  if (tagEntries.length) {
    html += `<h4>Most Common Tags</h4><table class="analytics-table"><thead><tr><th>Tag</th><th class="num">Count</th></tr></thead><tbody>`;
    html += tagEntries.map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="num">${v}</td></tr>`).join("");
    html += `</tbody></table>`;
  }

  if (recentEntries.length) {
    html += `<h4>Recent Knowledge Activity</h4><table class="analytics-table"><thead><tr><th>Date</th><th>Event</th></tr></thead><tbody>`;
    html += recentEntries.map(e =>
      `<tr><td>${escapeHtml(e.date || "")}</td><td>${escapeHtml(e.description || "")}</td></tr>`
    ).join("");
    html += `</tbody></table>`;
  }

  html += `</section>`;
  return html;
}

function dispatchPage(route) {
  document.querySelectorAll(".main-nav a").forEach(link => {
    link.classList.toggle("active", link.dataset.route === route);
  });

  if (route === "/analytics") {
    loadAnalytics();
  }
  if (route === "/priority-queue") {
    loadPriorityQueue();
  }
  if (route === "/follow-ups") {
    loadFollowUps();
  }
  if (route === "/knowledge-search") {
    loadKnowledgeSearch();
  }
}

function navigateTo(pathname) {
  window.history.pushState({}, "", pathname);
  setActivePage(pathname);
  selectOrgFromQuery(pathname);
}

function selectOrgFromQuery(url) {
  const qIndex = url.indexOf('?');
  if (qIndex === -1) return;
  const params = new URLSearchParams(url.substring(qIndex));
  const orgId = params.get('org');
  if (!orgId) return;
  const numericId = Number(orgId);
  if (isNaN(numericId) || numericId <= 0) return;
  const org = organizations.find(o => o.id === numericId);
  if (org) {
    selectOrganization(numericId);
  } else {
    const check = setInterval(() => {
      const found = organizations.find(o => o.id === numericId);
      if (found) {
        clearInterval(check);
        selectOrganization(numericId);
      }
    }, 100);
    setTimeout(() => clearInterval(check), 5000);
  }
}

function titleize(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, letter => letter.toUpperCase());
}

function formatValue(key, value) {
  if (key === "ai_readiness_score" && typeof value === "number") {
    return `${value} / 100`;
  }
  return value;
}

function renderList(items) {
  return `
    <ul class="ai-list">
      ${items.map(item => `<li>${renderInlineValue(item)}</li>`).join("")}
    </ul>
  `;
}

function renderInlineValue(value) {
  if (Array.isArray(value)) {
    return renderList(value);
  }
  if (value && typeof value === "object") {
    return `
      <div class="ai-nested-card">
        ${Object.entries(value).map(([key, nestedValue]) => `
          <div class="ai-nested-row">
            <strong>${escapeHtml(titleize(key))}:</strong>
            <span>${renderInlineValue(formatValue(key, nestedValue))}</span>
          </div>
        `).join("")}
      </div>
    `;
  }
  return escapeHtml(value);
}

function renderField(key, value) {
  if (key === "organization_id") return "";

  return `
    <section class="ai-field">
      <h4>${escapeHtml(titleize(key))}</h4>
      ${Array.isArray(value)
        ? renderList(value)
        : `<div class="ai-value">${renderInlineValue(formatValue(key, value))}</div>`}
    </section>
  `;
}

function renderAiResult(title, data) {
  const rawJson = escapeHtml(JSON.stringify(data, null, 2));
  document.getElementById("ai-output").innerHTML = `
    <article class="ai-card">
      <h3>${escapeHtml(title)}</h3>
      ${Object.entries(data).map(([key, value]) => renderField(key, value)).join("")}
      <details class="raw-json">
        <summary>View Raw JSON</summary>
        <pre>${rawJson}</pre>
      </details>
    </article>
  `;
}

function candidateFieldId(index, key) {
  return `candidate-${index}-${key}`;
}

function renderCandidateValue(index, key, value, multiline = false) {
  if (!discoveryCandidates[index].editing) {
    return escapeHtml(value || "Not available");
  }
  if (multiline) {
    return `<textarea id="${candidateFieldId(index, key)}" rows="3">${escapeHtml(value)}</textarea>`;
  }
  return `<input id="${candidateFieldId(index, key)}" value="${escapeHtml(value)}" />`;
}

function renderCandidateCard(candidate, index) {
  if (candidate.rejected) {
    return `
      <article class="candidate-card rejected">
        <h3>${escapeHtml(candidate.organization_name)}</h3>
        <p class="muted">Rejected - not saved to CRM.</p>
      </article>
    `;
  }

  return `
    <article class="candidate-card ${candidate.approved ? "approved" : ""}">
      <div class="candidate-header">
        <h3>${renderCandidateValue(index, "organization_name", candidate.organization_name)}</h3>
        <span class="fit-score">Fit Score: ${escapeHtml(candidate.fit_score)} / 100</span>
      </div>
      ${candidate.editing ? `
        <div class="candidate-field">
          <strong>Fit Score</strong>
          <div>${renderCandidateValue(index, "fit_score", candidate.fit_score)}</div>
        </div>
      ` : ""}
      <div class="candidate-field">
        <strong>Organization Type</strong>
        <div>${renderCandidateValue(index, "organization_type", candidate.organization_type)}</div>
      </div>
      <div class="candidate-field">
        <strong>Website</strong>
        <div>${renderCandidateValue(index, "website", candidate.website)}</div>
      </div>
      <div class="candidate-field">
        <strong>General Contact Email</strong>
        <div>${renderCandidateValue(index, "general_contact_email", candidate.general_contact_email || "")}</div>
      </div>
      <div class="candidate-field">
        <strong>Phone Number</strong>
        <div>${renderCandidateValue(index, "phone_number", candidate.phone_number || "")}</div>
      </div>
      <div class="candidate-field">
        <strong>Program Area</strong>
        <div>${renderCandidateValue(index, "program_area", candidate.program_area)}</div>
      </div>
      <div class="candidate-field">
        <strong>Why It May Be Relevant</strong>
        <div>${renderCandidateValue(index, "why_it_may_be_relevant", candidate.why_it_may_be_relevant, true)}</div>
      </div>
      <div class="candidate-field">
        <strong>Suggested Outreach Angle</strong>
        <div>${renderCandidateValue(index, "suggested_outreach_angle", candidate.suggested_outreach_angle, true)}</div>
      </div>
      <div class="candidate-field">
        <strong>Source Note</strong>
        <div>${renderCandidateValue(index, "source_note", candidate.source_note, true)}</div>
      </div>
      <div class="candidate-actions">
        ${candidate.editing
          ? `<button onclick="saveCandidateEdits(${index})">Save Edits</button>`
          : `<button onclick="approveCandidate(${index})" ${candidate.approved ? "disabled" : ""}>Approve</button>
             <button onclick="editCandidate(${index})" ${candidate.approved ? "disabled" : ""}>Edit</button>
             <button onclick="rejectCandidate(${index})" ${candidate.approved ? "disabled" : ""}>Reject</button>`}
      </div>
      ${candidate.approved ? `<p class="success">Approved and saved to CRM.</p>` : ""}
      ${candidate.error ? `<p class="error">${escapeHtml(candidate.error)}</p>` : ""}
    </article>
  `;
}

function renderDiscoveryResults() {
  const el = document.getElementById("discovery-results");
  if (!discoveryCandidates.length) {
    el.innerHTML = "";
    return;
  }
  el.innerHTML = discoveryCandidates
    .map((candidate, index) => renderCandidateCard(candidate, index))
    .join("");
}

async function discoverOrganizations() {
  const input = document.getElementById("research-theme");
  const researchTheme = input.value.trim();
  const el = document.getElementById("discovery-results");

  if (!researchTheme) {
    el.innerHTML = `<p class="error">Enter a research theme before discovering organizations.</p>`;
    return;
  }

  el.innerHTML = `<p class="muted">Finding local mock candidates for review...</p>`;
  try {
    const data = await api("/api/research/discover", {
      method: "POST",
      body: JSON.stringify({ research_theme: researchTheme })
    });
    discoveryCandidates = data.candidates.map(candidate => ({
      ...candidate,
      approved: false,
      editing: false,
      rejected: false,
      error: "",
    }));
    renderDiscoveryResults();
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function editCandidate(index) {
  discoveryCandidates[index].editing = true;
  discoveryCandidates[index].error = "";
  renderDiscoveryResults();
}

function saveCandidateEdits(index) {
  [
    "organization_name",
    "fit_score",
    "organization_type",
    "website",
    "general_contact_email",
    "phone_number",
    "program_area",
    "why_it_may_be_relevant",
    "suggested_outreach_angle",
    "source_note",
  ].forEach(key => {
    discoveryCandidates[index][key] = document.getElementById(candidateFieldId(index, key)).value.trim();
  });
  discoveryCandidates[index].fit_score = Number(discoveryCandidates[index].fit_score) || 0;
  discoveryCandidates[index].editing = false;
  renderDiscoveryResults();
}

async function approveCandidate(index) {
  const candidate = discoveryCandidates[index];
  candidate.error = "";
  try {
    const saved = await api("/api/research/approve", {
      method: "POST",
      body: JSON.stringify({ candidate })
    });
    candidate.approved = true;
    candidate.saved_organization_id = saved.id;
    renderDiscoveryResults();
    await loadOrganizations();
  } catch (error) {
    candidate.error = error.message;
    renderDiscoveryResults();
  }
}

function rejectCandidate(index) {
  discoveryCandidates.splice(index, 1);
  renderDiscoveryResults();
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function loadOrganizations() {
  try {
    organizations = await api("/api/organizations");
    renderOrganizations();
  } catch (error) {
    document.getElementById("organizations").innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function intakeValue(id) {
  return document.getElementById(id).value.trim();
}

async function saveResearchIntake(event) {
  event.preventDefault();
  const resultEl = document.getElementById("intake-result");
  const payload = {
    organization_name: intakeValue("intake-organization-name"),
    website: intakeValue("intake-website"),
    general_contact_email: intakeValue("intake-general-contact-email"),
    phone_number: intakeValue("intake-phone-number"),
    organization_type: intakeValue("intake-organization-type"),
    program_area: intakeValue("intake-program-area"),
    description: intakeValue("intake-description"),
    why_it_may_benefit: intakeValue("intake-why-benefit"),
    suggested_outreach_angle: intakeValue("intake-outreach-angle"),
    source_url: intakeValue("intake-source-url"),
    notes: intakeValue("intake-notes"),
  };

  resultEl.innerHTML = `<p class="muted">Saving to Local CRM...</p>`;
  try {
    const saved = await api("/api/research/intake", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    resultEl.innerHTML = `
      <div class="success-box">
        <strong>${escapeHtml(saved.name)}</strong> saved to the Local CRM.
        <button onclick="navigateTo('/')">View Organization List</button>
      </div>
    `;
    event.target.reset();
    await loadOrganizations();
  } catch (error) {
    resultEl.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderOrganizations() {
  const query = document.getElementById("search").value.toLowerCase();
  const el = document.getElementById("organizations");
  const filtered = organizations.filter(org =>
    org.name.toLowerCase().includes(query) ||
    org.category.toLowerCase().includes(query) ||
    org.status.toLowerCase().includes(query)
  );
  el.innerHTML = filtered.map(org => `
    <div class="org-card" onclick="selectOrganization(${org.id})">
      <div class="org-name">${escapeHtml(org.name)}</div>
      <div class="muted">${escapeHtml(org.category)}</div>
      <div>${escapeHtml(org.contact_name)}</div>
      <div class="muted">${escapeHtml(org.contact_email)}</div>
      <span class="status">${escapeHtml(org.status)}</span>
    </div>
  `).join("");
}

function orgFieldId(key) {
  return `org-field-${key}`;
}

function renderOrgDetails(org) {
  const editing = org._editing;
  const v = (key) => org[key] || "";
  const input = (key, type = "text") =>
    `<input id="${orgFieldId(key)}" type="${type}" value="${escapeHtml(v(key))}" />`;
  const text = (key) => escapeHtml(v(key));

  return `
    <strong>Category:</strong> ${text("category")}<br>
    <strong>Website:</strong> ${editing ? input("website", "url") : `<a href="${escapeHtml(v("website"))}" target="_blank" rel="noreferrer">${text("website")}</a>`}<br>
    <strong>Contact:</strong> ${editing ? input("contact_name") : text("contact_name")}<br>
    <strong>Email:</strong> ${editing ? input("contact_email", "email") : text("contact_email")}<br>
    <strong>Phone:</strong> ${editing ? input("phone_number") : (v("phone_number") || "Not available")}<br>
    <strong>Status:</strong> ${text("status")}<br>
    <strong>Notes:</strong> ${text("mission_notes")}<br>
    <strong>Last interaction:</strong> ${text("last_interaction")}<br>
    <div class="actions" style="margin-top:8px">
      ${editing
        ? `<button onclick="saveOrgContact()">Save Contact</button><button onclick="cancelOrgEdit()">Cancel</button>`
        : `<button onclick="editOrgContact()">Edit Contact</button>`
      }
    </div>
  `;
}

async function selectOrganization(id) {
  try {
    selectedOrg = await api(`/api/organizations/${id}`);
    selectedOrg._editing = false;
    document.getElementById("detail-title").textContent = selectedOrg.name;
    document.getElementById("details").innerHTML = renderOrgDetails(selectedOrg);
    document.getElementById("ai-output").textContent = "";
    document.getElementById("draft-section").classList.add("hidden");
    document.getElementById("interaction-history-section").classList.remove("hidden");
    document.getElementById("knowledge-summary-section").classList.remove("hidden");
    document.getElementById("readiness-section").classList.remove("hidden");
    document.getElementById("timeline-section").classList.remove("hidden");
    document.getElementById("lessons-section").classList.remove("hidden");
    document.getElementById("playbook-section").classList.remove("hidden");
    document.getElementById("workflow-opps-section").classList.remove("hidden");
    document.getElementById("knowledge-sources-section").classList.remove("hidden");
    document.getElementById("failure-cases-section").classList.remove("hidden");
    document.getElementById("adoption-risk-section").classList.remove("hidden");
    document.getElementById("tasks-section").classList.remove("hidden");
    await loadInteractions();
    await loadKnowledgeSummary();
    await loadTasksForOrg();
    await loadLessons();
    await loadPlaybooks();
    await loadWorkflowOpps();
    await loadKnowledgeSources();
    await loadFailureCases();
    await loadAdoptionRisks();
  } catch (error) {
    showError(error.message);
  }
}

function editOrgContact() {
  if (!selectedOrg) return;
  selectedOrg._editing = true;
  document.getElementById("details").innerHTML = renderOrgDetails(selectedOrg);
}

function cancelOrgEdit() {
  if (!selectedOrg) return;
  selectedOrg._editing = false;
  document.getElementById("details").innerHTML = renderOrgDetails(selectedOrg);
}

async function saveOrgContact() {
  if (!selectedOrg) return;
  const updates = {};
  ["contact_name", "contact_email", "phone_number", "website"].forEach(key => {
    const el = document.getElementById(orgFieldId(key));
    if (el) updates[key] = el.value.trim();
  });
  if (!updates.contact_name && !updates.contact_email && !updates.phone_number && !updates.website) return;
  try {
    const saved = await api(`/api/organizations/${selectedOrg.id}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
    Object.assign(selectedOrg, saved);
    selectedOrg._editing = false;
    document.getElementById("details").innerHTML = renderOrgDetails(selectedOrg);
  } catch (error) {
    alert(error.message);
  }
}

function requireSelected() {
  if (!selectedOrg) {
    alert("Select an organization first.");
    return false;
  }
  return true;
}

async function loadSummary() {
  if (!requireSelected()) return;
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/summary`);
    renderAiResult("AI Summary", data);
  } catch (error) {
    showError(error.message);
  }
}

async function loadOpportunities() {
  if (!requireSelected()) return;
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/opportunities`);
    renderAiResult("AI Opportunity Analysis", data);
  } catch (error) {
    showError(error.message);
  }
}

async function loadMeetingBrief() {
  if (!requireSelected()) return;
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/meeting-brief`);
    renderAiResult("Meeting Brief", data);
  } catch (error) {
    showError(error.message);
  }
}

function renderContextUsed(context) {
  return Object.entries(context).map(([key, value]) => {
    const display = Array.isArray(value) ? value.join(", ") : String(value);
    return `<div class="context-row"><strong>${escapeHtml(key)}:</strong> <span>${escapeHtml(display)}</span></div>`;
  }).join("");
}

async function generateNextBestEmail() {
  if (!requireSelected()) return;
  pendingAttachments = [];
  renderPendingAttachments();
  try {
    currentDraft = await api("/api/drafts/generate", {
      method: "POST",
      body: JSON.stringify({ organization_id: selectedOrg.id })
    });
    document.getElementById("draft-section").classList.remove("hidden");

    const badge = document.getElementById("email-type-badge");
    badge.textContent = currentDraft.email_type || "Email Draft";
    badge.className = "email-type-badge";

    const stageEl = document.getElementById("email-detected-stage");
    if (currentDraft.detected_stage) {
      stageEl.textContent = currentDraft.detected_stage;
      stageEl.className = "email-detected-stage";
      stageEl.classList.remove("hidden");
    } else {
      stageEl.classList.add("hidden");
    }

    document.getElementById("email-reason").textContent = currentDraft.reason || "";

    const missingEl = document.getElementById("email-missing-context");
    if (currentDraft.missing_context && currentDraft.missing_context.length) {
      missingEl.classList.remove("hidden");
      missingEl.innerHTML = "<strong>Note:</strong> " + currentDraft.missing_context.join(" ");
    } else {
      missingEl.classList.add("hidden");
    }

    document.getElementById("draft-to").value = currentDraft.to || "";
    document.getElementById("draft-subject").value = currentDraft.subject || "";
    document.getElementById("draft-body").value = currentDraft.body || "";

    const nextActionSection = document.getElementById("email-next-action-section");
    if (currentDraft.next_action || currentDraft.follow_up_date) {
      nextActionSection.classList.remove("hidden");
      document.getElementById("draft-next-action").value = currentDraft.next_action || "";
      document.getElementById("draft-follow-up-date").value = currentDraft.follow_up_date || "";
    } else {
      nextActionSection.classList.add("hidden");
    }

    const contextDetails = document.getElementById("email-context-details");
    const contextEl = document.getElementById("email-context-used");
    if (currentDraft.context_used) {
      contextDetails.classList.remove("hidden");
      contextEl.innerHTML = renderContextUsed(currentDraft.context_used);
    } else {
      contextDetails.classList.add("hidden");
    }

    renderAiResult("Next Best Email", currentDraft);
  } catch (error) {
    showError(error.message);
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

function renderPendingAttachments() {
  const el = document.getElementById("draft-attachment-list");
  if (!pendingAttachments.length) {
    el.innerHTML = '<p class="muted">No files selected.</p>';
    return;
  }
  el.innerHTML = pendingAttachments.map((f, i) => `
    <div class="attachment-item pending">
      <span class="att-name">${escapeHtml(f.name)}</span>
      <span class="att-size">${formatFileSize(f.size)}</span>
      <button onclick="removePendingAttachment(${i})" class="att-remove">Remove</button>
    </div>
  `).join("");
}

function onAttachFilesSelected() {
  const input = document.getElementById("draft-file-input");
  for (const file of input.files) {
    pendingAttachments.push(file);
  }
  input.value = "";
  renderPendingAttachments();
}

function removePendingAttachment(index) {
  pendingAttachments.splice(index, 1);
  renderPendingAttachments();
}

async function uploadPendingAttachments(draftId) {
  for (const file of pendingAttachments) {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await fetch(`/api/outbox/${draftId}/attachments`, { method: "POST", body: formData });
    } catch (e) {
      console.error("Failed to upload", file.name, e);
    }
  }
  pendingAttachments = [];
  renderPendingAttachments();
}

async function loadAttachments(draftId) {
  try {
    const response = await fetch(`/api/outbox/${draftId}/attachments`);
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
}

async function detachAttachment(draftId, attachmentId) {
  if (!confirm("Remove this attachment from the draft?")) return;
  try {
    const response = await fetch(`/api/outbox/${draftId}/attachments/${attachmentId}`, { method: "DELETE" });
    if (!response.ok) throw new Error("Failed to detach");
    await loadOutbox();
  } catch (error) {
    alert(error.message);
  }
}

function renderAttachmentMeta(meta) {
  return `
    <div class="attachment-item saved">
      <span class="att-name">${escapeHtml(meta.original_filename)}</span>
      <span class="att-type">${escapeHtml(meta.mime_type)}</span>
      <span class="att-size">${formatFileSize(meta.size_bytes)}</span>
      <span class="att-date">${escapeHtml(meta.uploaded_at)}</span>
      <button onclick="detachAttachment(${currentDraftId}, '${meta.attachment_id}')" class="att-detach">Detach</button>
    </div>
  `;
}

// ---- Data Tools ----

async function previewCsvImport() {
  const input = document.getElementById("csv-file-input");
  const file = input.files[0];
  if (!file) { alert("Select a CSV file first."); return; }
  const previewEl = document.getElementById("csv-preview");
  const resultEl = document.getElementById("csv-import-result");
  previewEl.classList.remove("hidden");
  resultEl.classList.add("hidden");
  previewEl.innerHTML = "<p class='muted'>Parsing CSV...</p>";

  const formData = new FormData();
  formData.append("file", file);
  try {
    const resp = await fetch("/api/data/import/csv", { method: "POST", body: formData });
    if (!resp.ok) { previewEl.innerHTML = `<p class='error'>${escapeHtml(await resp.text())}</p>`; return; }
    const data = await resp.json();
    const hasErrors = data.parse_errors && data.parse_errors.length;
    previewEl.innerHTML = `
      <p><strong>Rows read:</strong> ${data.rows_read} | <strong>Valid:</strong> ${data.imported} | <strong>Duplicates:</strong> 0 (checked on confirm) | <strong>Invalid:</strong> ${data.parse_errors ? data.parse_errors.length : 0}</p>
      ${hasErrors ? `<div class="import-errors"><strong>Row errors:</strong><ul>${data.parse_errors.map(e => `<li>${escapeHtml(e)}</li>`).join("")}</ul></div>` : ""}
      <div class="actions">
        ${data.imported > 0 ? `<button onclick="confirmCsvImport()">Import ${data.imported} Valid Records</button>` : ""}
      </div>
    `;
    window._lastImportData = data;
  } catch (e) {
    previewEl.innerHTML = `<p class='error'>${escapeHtml(e.message)}</p>`;
  }
}

async function confirmCsvImport() {
  if (!window._lastImportData || !window._lastImportData.imported) return;
  const resultEl = document.getElementById("csv-import-result");
  resultEl.classList.remove("hidden");
  resultEl.innerHTML = "<p class='muted'>Importing...</p>";
  try {
    const resp = await fetch("/api/data/import/csv/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: window._lastImportData.upload_id }),
    });
    if (!resp.ok) { resultEl.innerHTML = `<p class='error'>${escapeHtml(await resp.text())}</p>`; return; }
    const data = await resp.json();
    resultEl.innerHTML = `
      <div class="success-box">
        <strong>Import complete.</strong>
        ${data.imported} record(s) imported. ${data.duplicates_skipped} duplicate(s) skipped.
      </div>
    `;
    window._lastImportData = null;
    document.getElementById("csv-preview").classList.add("hidden");
    loadOrganizations();
  } catch (e) {
    resultEl.innerHTML = `<p class='error'>${escapeHtml(e.message)}</p>`;
  }
}

async function exportCsv() {
  try {
    const resp = await fetch("/api/data/export/csv");
    if (!resp.ok) { alert("Export failed"); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "organizations_export.csv"; a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert(e.message);
  }
}

async function exportJson() {
  try {
    const resp = await fetch("/api/data/export/json");
    if (!resp.ok) { alert("Export failed"); return; }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "outreach_intelligence_export.json"; a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert(e.message);
  }
}

async function saveDraft() {
  if (!requireSelected()) return;
  const draft = {
    organization_id: selectedOrg.id,
    to: document.getElementById("draft-to").value,
    subject: document.getElementById("draft-subject").value,
    body: document.getElementById("draft-body").value,
  };
  try {
    const saved = await api("/api/outbox", { method: "POST", body: JSON.stringify(draft) });
    currentDraftId = saved.id;
    if (pendingAttachments.length) {
      await uploadPendingAttachments(saved.id);
    }
    alert(saved.status);
    loadOutbox();
  } catch (error) {
    showError(error.message);
  }
}

async function loadOutbox() {
  try {
    const rows = await api("/api/outbox");
    const el = document.getElementById("outbox");
    if (!rows.length) {
      el.innerHTML = "<p class='muted'>No saved drafts yet.</p>";
      return;
    }
    const htmlRows = await Promise.all(rows.map(async (row) => {
      let attachmentsHtml = "";
      const atts = await loadAttachments(row.id);
      if (atts.length) {
        currentDraftId = row.id;
        attachmentsHtml = `<div class="outbox-attachments">${atts.map(a => renderAttachmentMeta(a)).join("")}</div>`;
        currentDraftId = null;
      }
      return `
        <div class="outbox-item">
          <strong>${escapeHtml(row.subject)}</strong><br>
          <span class="muted">To: ${escapeHtml(row.to)}</span><br>
          <span class="status">${escapeHtml(row.status)}</span>
          ${attachmentsHtml}
        </div>
      `;
    }));
    el.innerHTML = htmlRows.join("");
  } catch (error) {
    document.getElementById("outbox").innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

async function summarizeNotes() {
  if (!requireSelected()) return;
  const notes = document.getElementById("meeting-notes").value;
  try {
    const data = await api("/api/meeting-notes/summarize", {
      method: "POST",
      body: JSON.stringify({ organization_id: selectedOrg.id, notes })
    });
    renderAiResult("Meeting Notes Summary", data);
  } catch (error) {
    document.getElementById("notes-output").textContent = error.message;
  }
}

function showAddInteractionForm() {
  document.getElementById("add-interaction-form").classList.remove("hidden");
  document.getElementById("int-date").value = new Date().toISOString().split("T")[0];
}

function hideAddInteractionForm() {
  document.getElementById("add-interaction-form").classList.add("hidden");
}

async function saveNewInteraction() {
  if (!requireSelected()) return;
  const tags = document.getElementById("int-tags").value
    .split(",")
    .map(t => t.trim())
    .filter(t => t);
  const payload = {
    organization_id: selectedOrg.id,
    interaction_type: document.getElementById("int-type").value,
    date: document.getElementById("int-date").value,
    title: document.getElementById("int-title").value.trim(),
    notes: document.getElementById("int-notes").value.trim(),
    outcome: document.getElementById("int-outcome").value.trim(),
    next_action: document.getElementById("int-next-action").value.trim(),
    follow_up_date: document.getElementById("int-follow-up-date").value,
    tags,
  };
  if (!payload.title) { alert("Title is required."); return; }
  try {
    await api(`/api/organizations/${selectedOrg.id}/interactions`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    hideAddInteractionForm();
    document.getElementById("int-title").value = "";
    document.getElementById("int-notes").value = "";
    document.getElementById("int-outcome").value = "";
    document.getElementById("int-next-action").value = "";
    document.getElementById("int-follow-up-date").value = "";
    document.getElementById("int-tags").value = "";
    await loadInteractions();
    await loadKnowledgeSummary();
  } catch (error) {
    alert(error.message);
  }
}

function interactionFieldId(interactionId, key) {
  return `int-${interactionId}-${key}`;
}

async function loadInteractions() {
  if (!selectedOrg) return;
  try {
    interactions = await api(`/api/organizations/${selectedOrg.id}/interactions`);
    renderInteractions();
  } catch (error) {
    document.getElementById("interactions-list").innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderInteractions() {
  const el = document.getElementById("interactions-list");
  if (!interactions.length) {
    el.innerHTML = "<p class='muted'>No interactions recorded yet.</p>";
    return;
  }
  el.innerHTML = interactions.map(int => {
    const editing = int._editing;
    const v = (key) => int[key] || "";
    return `
      <article class="interaction-card">
        <div class="interaction-header">
          <strong>${escapeHtml(v("title"))}</strong>
          <span class="int-type-badge">${escapeHtml(v("interaction_type"))}</span>
        </div>
        <div class="interaction-meta">
          ${v("date") ? `<span>${escapeHtml(v("date"))}</span>` : ""}
          ${v("tags") && int.tags.length ? `<span>${int.tags.map(t => `<span class="int-tag">${escapeHtml(t)}</span>`).join(" ")}</span>` : ""}
        </div>
        ${editing ? `
          <div class="interaction-edit-form">
            <label>Interaction Type</label>
            <select id="${interactionFieldId(int.id, "interaction_type")}">
              ${["Meeting","Call","Email","Research Note","Follow-up","Other"].map(t =>
                `<option value="${t}" ${t === int.interaction_type ? "selected" : ""}>${t}</option>`
              ).join("")}
            </select>
            <label>Date</label>
            <input id="${interactionFieldId(int.id, "date")}" type="date" value="${escapeHtml(v("date"))}" />
            <label>Title</label>
            <input id="${interactionFieldId(int.id, "title")}" value="${escapeHtml(v("title"))}" />
            <label>Notes</label>
            <textarea id="${interactionFieldId(int.id, "notes")}" rows="3">${escapeHtml(v("notes"))}</textarea>
            <label>Outcome</label>
            <textarea id="${interactionFieldId(int.id, "outcome")}" rows="2">${escapeHtml(v("outcome"))}</textarea>
            <label>Next Action</label>
            <input id="${interactionFieldId(int.id, "next_action")}" value="${escapeHtml(v("next_action"))}" />
            <label>Follow-up Date</label>
            <input id="${interactionFieldId(int.id, "follow_up_date")}" type="date" value="${escapeHtml(v("follow_up_date"))}" />
            <label>Tags (comma separated)</label>
            <input id="${interactionFieldId(int.id, "tags")}" value="${escapeHtml((int.tags || []).join(", "))}" />
            <div class="actions">
              <button onclick="saveInteractionEdit(${int.id})">Save</button>
              <button onclick="cancelInteractionEdit(${int.id})">Cancel</button>
            </div>
          </div>
        ` : `
          <div class="interaction-details">
            ${v("notes") ? `<div class="int-field"><strong>Notes:</strong> ${escapeHtml(v("notes"))}</div>` : ""}
            ${v("outcome") ? `<div class="int-field"><strong>Outcome:</strong> ${escapeHtml(v("outcome"))}</div>` : ""}
            ${v("next_action") ? `<div class="int-field"><strong>Next Action:</strong> ${escapeHtml(v("next_action"))}</div>` : ""}
            ${v("follow_up_date") ? `<div class="int-field"><strong>Follow-up Date:</strong> ${escapeHtml(v("follow_up_date"))}</div>` : ""}
          </div>
          <div class="actions int-actions">
            <button onclick="summarizeInteractionNote(${int.id})">AI Note Summary</button>
            <button onclick="editInteraction(${int.id})">Edit</button>
            <button onclick="deleteInteraction(${int.id})">Delete</button>
          </div>
        `}
        <div id="int-summary-${int.id}" class="output hidden"></div>
      </article>
    `;
  }).join("");
}

function editInteraction(id) {
  const int = interactions.find(i => i.id === id);
  if (int) int._editing = true;
  renderInteractions();
}

function cancelInteractionEdit(id) {
  const int = interactions.find(i => i.id === id);
  if (int) int._editing = false;
  renderInteractions();
}

async function saveInteractionEdit(id) {
  const int = interactions.find(i => i.id === id);
  if (!int) return;
  const updates = {
    interaction_type: document.getElementById(interactionFieldId(id, "interaction_type")).value,
    date: document.getElementById(interactionFieldId(id, "date")).value,
    title: document.getElementById(interactionFieldId(id, "title")).value.trim(),
    notes: document.getElementById(interactionFieldId(id, "notes")).value.trim(),
    outcome: document.getElementById(interactionFieldId(id, "outcome")).value.trim(),
    next_action: document.getElementById(interactionFieldId(id, "next_action")).value.trim(),
    follow_up_date: document.getElementById(interactionFieldId(id, "follow_up_date")).value,
    tags: document.getElementById(interactionFieldId(id, "tags")).value.split(",").map(t => t.trim()).filter(t => t),
  };
  try {
    const saved = await api(`/api/organizations/${selectedOrg.id}/interactions/${id}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    });
    Object.assign(int, saved);
    int._editing = false;
    renderInteractions();
    await loadKnowledgeSummary();
  } catch (error) {
    alert(error.message);
  }
}

async function deleteInteraction(id) {
  if (!confirm("Delete this interaction?")) return;
  try {
    await api(`/api/organizations/${selectedOrg.id}/interactions/${id}`, { method: "DELETE" });
    interactions = interactions.filter(i => i.id !== id);
    renderInteractions();
    await loadKnowledgeSummary();
  } catch (error) {
    alert(error.message);
  }
}

async function summarizeInteractionNote(id) {
  const summaryEl = document.getElementById(`int-summary-${id}`);
  if (!summaryEl) return;
  summaryEl.classList.remove("hidden");
  summaryEl.innerHTML = "<p class='muted'>Generating AI note summary...</p>";
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/interactions/${id}/summarize`, {
      method: "POST",
    });
    if (data.follow_up_tasks && data.follow_up_tasks.length) {
      taskSuggestions = data.follow_up_tasks;
      await loadTasksForOrg();
    }
    summaryEl.innerHTML = `
      <article class="ai-card">
        ${Object.entries(data).map(([key, value]) => renderField(key, value)).join("")}
        <details class="raw-json">
          <summary>View Raw JSON</summary>
          <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
        </details>
      </article>
    `;
  } catch (error) {
    summaryEl.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

async function loadKnowledgeSummary() {
  if (!selectedOrg) return;
  const el = document.getElementById("knowledge-summary-output");
  el.innerHTML = "<p class='muted'>Loading knowledge summary...</p>";
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/knowledge-summary`);
    el.innerHTML = `
      <article class="ai-card">
        ${Object.entries(data).map(([key, value]) => renderField(key, value)).join("")}
        <details class="raw-json">
          <summary>View Raw JSON</summary>
          <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
        </details>
      </article>
    `;
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderReadinessAssessment(data) {
  const scoreBar = (score, max) => {
    const pct = Math.round((score / max) * 100);
    const color = pct >= 70 ? "#16a34a" : pct >= 40 ? "#ca8a04" : "#dc2626";
    return `<div class="ra-bar-bg"><div class="ra-bar-fill" style="width:${pct}%;background:${color}"></div></div><span class="ra-bar-label">${score}/${max}</span>`;
  };

  const levelBadge = (level) => {
    const color = level === "High" ? "#16a34a" : level === "Moderate" ? "#ca8a04" : "#dc2626";
    return `<span class="ra-level-badge" style="background:${color};color:#fff">${escapeHtml(level)}</span>`;
  };

  const categoryCards = (data.categories || []).map(c => `
    <div class="ra-category">
      <div class="ra-cat-header">
        <strong>${escapeHtml(c.name)}</strong>
        ${scoreBar(c.score, c.max)}
      </div>
      <p class="ra-cat-explanation">${escapeHtml(c.explanation)}</p>
    </div>
  `).join("");

  return `
    <article class="ai-card ra-card">
      <div class="ra-summary-row">
        <div class="ra-level-section">
          <span class="ra-label">Overall Level</span>
          ${levelBadge(data.overall_level)}
        </div>
        <div class="ra-score-section">
          <span class="ra-label">Readiness Score</span>
          <div class="ra-score-row">
            ${scoreBar(data.total_score, 100)}
          </div>
        </div>
      </div>

      <h4 class="ra-section-title">Category Scores</h4>
      ${categoryCards}

      <h4 class="ra-section-title">Best Starting AI Use Case</h4>
      <p class="ra-value">${escapeHtml(data.best_starting_use_case || "")}</p>

      <h4 class="ra-section-title">Why This Organization May Be Ready</h4>
      <p class="ra-value">${escapeHtml(data.why_ready || "")}</p>

      <h4 class="ra-section-title">Gaps or Missing Information</h4>
      <ul class="ai-list">
        ${(data.gaps || []).map(g => `<li>${escapeHtml(g)}</li>`).join("")}
      </ul>

      <h4 class="ra-section-title">Risks or Concerns</h4>
      <ul class="ai-list">
        ${(data.risks_or_concerns || []).map(r => `<li>${escapeHtml(r)}</li>`).join("")}
      </ul>

      <h4 class="ra-section-title">Recommended Pilot Project</h4>
      <p class="ra-value">${escapeHtml(data.recommended_pilot || "")}</p>

      <h4 class="ra-section-title">Human Oversight Requirements</h4>
      <p class="ra-value">${escapeHtml(data.human_oversight || "")}</p>

      <h4 class="ra-section-title">Suggested Questions for Next Meeting</h4>
      <ul class="ai-list">
        ${(data.suggested_questions || []).map(q => `<li>${escapeHtml(q)}</li>`).join("")}
      </ul>

      <details class="context-details">
        <summary>View Context Used</summary>
        <div class="context-used">
          ${data.context_used ? renderContextUsed(data.context_used) : "<p class='muted'>No context data available.</p>"}
        </div>
      </details>

      <details class="raw-json">
        <summary>View Raw JSON</summary>
        <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
      </details>
    </article>
  `;
}

async function loadReadinessAssessment() {
  if (!requireSelected()) return;
  const el = document.getElementById("readiness-output");
  el.innerHTML = "<p class='muted'>Generating AI Readiness Assessment...</p>";
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/readiness-assessment`, {
      method: "POST",
    });
    el.innerHTML = renderReadinessAssessment(data);
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

async function loadOutreachRecommendation() {
  if (!requireSelected()) return;
  const el = document.getElementById("ai-output");
  el.innerHTML = "<p class='muted'>Generating outreach recommendation...</p>";
  try {
    const data = await api(`/api/organizations/${selectedOrg.id}/outreach-recommendation`);
    el.innerHTML = renderOutreachRecommendation(data);
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderOutreachRecommendation(data) {
  const priorityBadge = (level) => {
    const cls = level === "High" ? "badge-high" : level === "Medium" ? "badge-moderate" : "badge-low";
    return `<span class="badge ${cls}">${escapeHtml(level)}</span>`;
  };

  let html = `<article class="ai-card">`;

  html += `<div class="rec-header">
    <div class="metric-card" style="flex:0 1 auto">
      <div class="metric-value">${priorityBadge(data.outreach_priority)}</div>
      <div class="metric-label">Priority: ${data.priority_score}/100</div>
    </div>
  </div>`;

  html += `<h4>Recommended Next Action</h4><p>${escapeHtml(data.recommended_next_action)}</p>`;
  html += `<h4>Recommended Follow-up Date</h4><p>${escapeHtml(data.recommended_follow_up_date)}</p>`;
  html += `<h4>Recommended Email Type</h4><p>${escapeHtml(data.recommended_email_type)}</p>`;

  if (data.recommended_collaboration_angles && data.recommended_collaboration_angles.length) {
    html += `<h4>Recommended Collaboration Angles</h4>`;
    for (const angle of data.recommended_collaboration_angles) {
      html += `<div class="collab-angle">
        <strong>${escapeHtml(angle.title)}</strong><br>
        <span class="muted">${escapeHtml(angle.description)}</span><br>
        <span class="muted">Effort: ${escapeHtml(angle.estimated_effort)} | Expected Value: ${escapeHtml(angle.expected_value)}</span><br>
        <span class="muted">Oversight: ${escapeHtml(angle.human_oversight)}</span>
      </div>`;
    }
  }

  html += `<h4>Reasoning</h4><p>${escapeHtml(data.reasoning)}</p>`;

  if (data.risks_or_concerns && data.risks_or_concerns.length) {
    html += `<h4>Risks / Concerns</h4><ul class="rec-list">`;
    for (const r of data.risks_or_concerns) {
      html += `<li>${escapeHtml(r)}</li>`;
    }
    html += `</ul>`;
  }

  if (data.missing_information && data.missing_information.length) {
    html += `<h4>Missing Information</h4><ul class="rec-list">`;
    for (const m of data.missing_information) {
      html += `<li>${escapeHtml(m)}</li>`;
    }
    html += `</ul>`;
  }

  if (data.context_used) {
    html += `<details class="context-details">
      <summary>View Context Used</summary>
      <div class="context-used">${renderContextUsed(data.context_used)}</div>
    </details>`;
  }

  html += `<details class="raw-json">
    <summary>View Raw JSON</summary>
    <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
  </details>`;

  html += `</article>`;
  return html;
}

async function loadAnalytics() {
  const contentEl = document.getElementById("analytics-content");
  const errorEl = document.getElementById("analytics-error");
  const loadingEl = document.getElementById("analytics-loading");
  errorEl.classList.add("hidden");
  contentEl.innerHTML = "";
  loadingEl.classList.remove("hidden");

  try {
    const data = await api("/api/analytics/summary");
    loadingEl.classList.add("hidden");
    contentEl.innerHTML = renderAnalytics(data);
  } catch (error) {
    loadingEl.classList.add("hidden");
    errorEl.textContent = "Failed to load analytics: " + error.message;
    errorEl.classList.remove("hidden");
  }
}

function renderAnalytics(data) {
  const parts = [];

  parts.push(renderMetricCards(data.overview_metrics));
  parts.push(renderPipelineTable(data.outreach_pipeline));
  parts.push(renderOrgBreakdown(data.organization_breakdown));
  parts.push(renderAiReadiness(data.ai_readiness));
  parts.push(renderFollowUpWorkload(data.follow_up_workload));
  parts.push(renderDraftActivity(data.draft_activity));
  if (data.priority_analytics) {
    parts.push(renderPriorityAnalytics(data.priority_analytics));
  }
  if (data.organizational_knowledge) {
    parts.push(renderOrganizationalKnowledge(data.organizational_knowledge));
  }

  return parts.join("\n");
}

function renderMetricCards(metrics) {
  const items = [
    { label: "Total Organizations", value: metrics.total_organizations },
    { label: "Total Interactions", value: metrics.total_interactions },
    { label: "Drafts in Outbox", value: metrics.drafts_in_outbox },
    { label: "Interaction Follow-ups Due", value: metrics.follow_ups_due },
    { label: "Avg Readiness Score", value: metrics.average_readiness_score != null ? metrics.average_readiness_score + "/100" : "N/A" },
    { label: "Avg Priority Score", value: metrics.average_priority_score != null ? metrics.average_priority_score + "/100" : "N/A" },
    { label: "High-Priority Targets", value: metrics.high_priority_targets },
    { label: "From Research Intake", value: metrics.organizations_from_research_intake == null ? "Not tracked" : metrics.organizations_from_research_intake },
    { label: "From Discovery", value: metrics.organizations_from_discovery == null ? "Not tracked" : metrics.organizations_from_discovery },
  ];

  const cards = items.map(m => `
    <div class="metric-card">
      <div class="metric-value">${escapeHtml(String(m.value))}</div>
      <div class="metric-label">${escapeHtml(m.label)}</div>
    </div>
  `).join("");

  return `<section class="analytics-section"><h3>Overview Metrics</h3><div class="metric-grid">${cards}</div></section>`;
}

function renderPipelineTable(pipeline) {
  const entries = Object.entries(pipeline);
  if (!entries.length) return "";

  const rows = entries.map(([status, count]) =>
    `<tr><td>${escapeHtml(status)}</td><td class="num">${count}</td></tr>`
  ).join("");

  return `
    <section class="analytics-section">
      <h3>Outreach Pipeline</h3>
      <table class="analytics-table">
        <thead><tr><th>Status</th><th class="num">Count</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </section>
  `;
}

function renderOrgBreakdown(breakdown) {
  let html = `<section class="analytics-section"><h3>Organization Breakdown</h3>`;

  const typeEntries = Object.entries(breakdown.by_type);
  if (typeEntries.length) {
    html += `<h4>By Organization Type</h4><table class="analytics-table"><thead><tr><th>Type</th><th class="num">Count</th></tr></thead><tbody>`;
    html += typeEntries.map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="num">${v}</td></tr>`).join("");
    html += `</tbody></table>`;
  }

  const progEntries = Object.entries(breakdown.by_program_area);
  if (progEntries.length) {
    html += `<h4>By Program Area</h4><table class="analytics-table"><thead><tr><th>Program Area</th><th class="num">Count</th></tr></thead><tbody>`;
    html += progEntries.map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="num">${v}</td></tr>`).join("");
    html += `</tbody></table>`;
  }

  if (!typeEntries.length && !progEntries.length) {
    html += `<p class="muted">No breakdown data available.</p>`;
  }

  html += `</section>`;
  return html;
}

function renderAiReadiness(readiness) {
  const levelBadge = (level) => {
    const cls = level.toLowerCase() === "high" ? "badge-high" :
                level.toLowerCase() === "moderate" ? "badge-moderate" : "badge-low";
    return `<span class="badge ${cls}">${escapeHtml(level)}</span>`;
  };

  let html = `
    <section class="analytics-section">
      <h3>AI Readiness</h3>
      <div class="metric-grid">
        <div class="metric-card">
          <div class="metric-value">${readiness.average_score != null ? readiness.average_score + "/100" : "N/A"}</div>
          <div class="metric-label">Average Score</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${readiness.low_count}</div>
          <div class="metric-label">Low Readiness</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${readiness.moderate_count}</div>
          <div class="metric-label">Moderate Readiness</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${readiness.high_count}</div>
          <div class="metric-label">High Readiness</div>
        </div>
      </div>
  `;

  if (readiness.top_5 && readiness.top_5.length) {
    html += `<h4>Top 5 Highest-Readiness Organizations</h4><table class="analytics-table"><thead><tr><th>Organization</th><th class="num">Score</th><th>Level</th></tr></thead><tbody>`;
    html += readiness.top_5.map(o =>
      `<tr><td>${escapeHtml(o.org_name)}</td><td class="num">${o.score}</td><td>${levelBadge(o.level)}</td></tr>`
    ).join("");
    html += `</tbody></table>`;
  }

  if (readiness.organizations_missing_readiness && readiness.organizations_missing_readiness.length) {
    html += `<h4>Organizations Missing Readiness Assessments</h4><ul class="analytics-list">`;
    html += readiness.organizations_missing_readiness.map(o =>
      `<li>${escapeHtml(o.org_name)}</li>`
    ).join("");
    html += `</ul>`;
  }

  html += `</section>`;
  return html;
}

function renderFollowUpWorkload(workload) {
  const items = [
    { label: "Follow-ups Due Today", value: workload.due_today },
    { label: "Follow-ups Due This Week", value: workload.due_this_week },
    { label: "Follow-ups Overdue", value: workload.overdue },
    { label: "No Next Action", value: workload.orgs_with_no_next_action },
    { label: "Open Tasks", value: workload.open_tasks },
    { label: "Tasks Due This Week", value: workload.tasks_due_this_week },
    { label: "Overdue Tasks", value: workload.overdue_tasks },
    { label: "High-Priority Tasks", value: workload.high_priority_open_tasks },
    { label: "Completed Tasks", value: workload.completed_tasks },
  ];

  const cards = items.map(m => `
    <div class="metric-card">
      <div class="metric-value">${m.value != null ? m.value : 0}</div>
      <div class="metric-label">${escapeHtml(m.label)}</div>
    </div>
  `).join("");

  return `<section class="analytics-section"><h3>Follow-up Workload</h3><div class="metric-grid">${cards}</div></section>`;
}

function renderDraftActivity(drafts) {
  let html = `
    <section class="analytics-section">
      <h3>Draft Activity</h3>
      <div class="metric-grid">
        <div class="metric-card">
          <div class="metric-value">${drafts.total_drafts}</div>
          <div class="metric-label">Total Drafts</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${drafts.drafts_with_attachments_count}</div>
          <div class="metric-label">Drafts with Attachments</div>
        </div>
      </div>
  `;

  const orgEntries = Object.entries(drafts.drafts_by_organization);
  if (orgEntries.length) {
    html += `<h4>Drafts by Organization</h4><table class="analytics-table"><thead><tr><th>Organization</th><th class="num">Drafts</th></tr></thead><tbody>`;
    html += orgEntries.map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="num">${v}</td></tr>`).join("");
    html += `</tbody></table>`;
  }

  if (drafts.most_recent_drafts && drafts.most_recent_drafts.length) {
    html += `<h4>Most Recent Drafts</h4><table class="analytics-table"><thead><tr><th>Subject</th><th>To</th></tr></thead><tbody>`;
    html += drafts.most_recent_drafts.map(d =>
      `<tr><td>${escapeHtml(d.subject)}</td><td>${escapeHtml(d.to)}</td></tr>`
    ).join("");
    html += `</tbody></table>`;
  }

  html += `</section>`;
  return html;
}

let pqData = [];
let ftData = [];
let taskSuggestions = [];

async function loadFollowUps() {
  const contentEl = document.getElementById("follow-ups-content");
  const errorEl = document.getElementById("follow-ups-error");
  const loadingEl = document.getElementById("follow-ups-loading");
  errorEl.classList.add("hidden");
  contentEl.innerHTML = "";
  loadingEl.classList.remove("hidden");

  try {
    ftData = await api("/api/tasks");
    loadingEl.classList.add("hidden");
    populateFollowUpFilters(ftData);
    renderFollowUpsPage();
  } catch (error) {
    loadingEl.classList.add("hidden");
    errorEl.textContent = "Failed to load follow-up tasks: " + error.message;
    errorEl.classList.remove("hidden");
  }
}

function populateFollowUpFilters(data) {
  const orgs = [...new Set(data.map(t => t.organization_id))].sort();
  const orgSel = document.getElementById("fu-filter-org");
  orgSel.innerHTML = '<option value="">All</option>';
  for (const oid of orgs) {
    const org = organizations.find(o => o.id === oid);
    orgSel.innerHTML += `<option value="${oid}">${escapeHtml(org ? org.name : `Org #${oid}`)}</option>`;
  }
}

function renderFollowUpsPage() {
  const filterStatus = document.getElementById("fu-filter-status").value;
  const filterPriority = document.getElementById("fu-filter-priority").value;
  const filterOrg = document.getElementById("fu-filter-org").value;

  const today = new Date().toISOString().split("T")[0];
  const nextWeek = new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0];

  let rows = ftData.filter(t => {
    if (filterStatus === "Overdue" && (t.status !== "Open" || (t.due_date && t.due_date >= today))) return false;
    if (filterStatus === "Due This Week" && (!t.due_date || t.due_date < today || t.due_date > nextWeek)) return false;
    if (filterStatus && filterStatus !== "Overdue" && filterStatus !== "Due This Week" && t.status !== filterStatus) return false;
    if (filterPriority && t.priority !== filterPriority) return false;
    if (filterOrg && String(t.organization_id) !== filterOrg) return false;
    return true;
  });

  rows.sort((a, b) => {
    if (a.status !== b.status) return a.status === "Open" ? -1 : 1;
    const p = { High: 3, Medium: 2, Low: 1 };
    return (p[b.priority] || 0) - (p[a.priority] || 0);
  });

  const el = document.getElementById("follow-ups-content");
  if (!rows.length) {
    el.innerHTML = '<p class="muted">No tasks match the current filters.</p>';
    return;
  }

  const priorityBadge = (lvl) => {
    const cls = lvl === "High" ? "badge-high" : lvl === "Medium" ? "badge-moderate" : "badge-low";
    return `<span class="badge ${cls}">${escapeHtml(lvl)}</span>`;
  };
  const statusBadge = (task) => {
    if (task.status === "Completed") return `<span class="badge badge-completed">Completed</span>`;
    if (task.due_date && task.due_date < today) return `<span class="badge badge-overdue">Overdue</span>`;
    return `<span class="badge badge-open">Open</span>`;
  };

  const rowsHtml = rows.map(t => {
    const org = organizations.find(o => o.id === t.organization_id);
    return `
      <tr>
        <td><strong>${escapeHtml(org ? org.name : `Org #${t.organization_id}`)}</strong></td>
        <td>${escapeHtml(t.title)}</td>
        <td>${escapeHtml(t.due_date || "")}</td>
        <td>${priorityBadge(t.priority)}</td>
        <td>${statusBadge(t)}</td>
        <td><span title="${escapeHtml(t.description || "")}">${escapeHtml((t.description || "").substring(0, 60))}${t.description && t.description.length > 60 ? "..." : ""}</span></td>
        <td class="fu-actions">
          ${t.status === "Open" ? `<button onclick="completeTask(${t.task_id})" class="btn-small">Complete</button>` : ""}
          <button onclick="deleteTask(${t.task_id})" class="btn-small btn-danger">Delete</button>
        </td>
      </tr>`;
  }).join("");

  el.innerHTML = `
    <table class="analytics-table fu-table">
      <thead><tr>
        <th>Organization</th>
        <th>Task</th>
        <th>Due</th>
        <th>Priority</th>
        <th>Status</th>
        <th>Description</th>
        <th>Actions</th>
      </tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
    <p class="muted" style="margin-top:8px">${rows.length} task(s) displayed.</p>
  `;
}

async function completeTask(taskId) {
  try {
    await api(`/api/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify({ status: "Completed" }) });
    ftData = await api("/api/tasks");
    renderFollowUpsPage();
  } catch (error) {
    alert(error.message);
  }
}

async function deleteTask(taskId) {
  if (!confirm("Delete this task?")) return;
  try {
    await api(`/api/tasks/${taskId}`, { method: "DELETE" });
    ftData = ftData.filter(t => t.task_id !== taskId);
    renderFollowUpsPage();
  } catch (error) {
    alert(error.message);
  }
}

async function loadTasksForOrg() {
  if (!selectedOrg) return;
  const el = document.getElementById("tasks-output");
  try {
    const tasks = await api(`/api/tasks?organization_id=${selectedOrg.id}`);
    renderOrgTasks(tasks);
  } catch (error) {
    el.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

function renderOrgTasks(tasks) {
  const el = document.getElementById("tasks-output");
  const today = new Date().toISOString().split("T")[0];
  const openTasks = tasks.filter(t => t.status === "Open");
  const completedTasks = tasks.filter(t => t.status === "Completed");

  let html = "";

  if (taskSuggestions && taskSuggestions.length) {
    html += `<h4>Suggested Tasks (Review before saving)</h4>`;
    for (const st of taskSuggestions) {
      html += `<div class="task-card suggested-task">
        <strong>${escapeHtml(st.title)}</strong><br>
        <span class="muted">${escapeHtml(st.description)}</span><br>
        <span class="muted">Due: ${escapeHtml(st.due_date)} | Priority: ${escapeHtml(st.priority)}</span>
        <div class="actions" style="margin:6px 0 0">
          <button onclick="saveSuggestedTask(${escapeHtml(JSON.stringify(st).replace(/"/g, "'"))})">Save Task</button>
        </div>
      </div>`;
    }
    html += `<hr>`;
  }

  if (openTasks.length) {
    html += `<h4>Open Tasks</h4>`;
    for (const t of openTasks) {
      const isOverdue = t.due_date && t.due_date < today;
      html += `<div class="task-card ${isOverdue ? 'overdue-task' : ''}">
        <div class="task-header">
          <strong>${escapeHtml(t.title)}</strong>
          ${isOverdue ? `<span class="badge badge-overdue">Overdue</span>` : ""}
        </div>
        <div class="muted">${escapeHtml(t.description || "")}</div>
        <div class="task-meta">
          <span>Due: ${escapeHtml(t.due_date || "—")}</span>
          <span>Priority: ${escapeHtml(t.priority)}</span>
        </div>
        <div class="actions" style="margin:6px 0 0">
          <button onclick="completeTask(${t.task_id})">Complete</button>
          <button onclick="deleteTask(${t.task_id})">Delete</button>
        </div>
      </div>`;
    }
  }

  if (completedTasks.length) {
    html += `<details style="margin-top:12px">
      <summary style="cursor:pointer;color:#6b7280">Completed Tasks (${completedTasks.length})</summary>
      ${completedTasks.map(t => `
        <div class="task-card completed-task" style="opacity:0.7">
          <strong>${escapeHtml(t.title)}</strong>
          <div class="muted">Completed: ${escapeHtml(t.updated_at || "")}</div>
        </div>
      `).join("")}
    </details>`;
  }

  if (!openTasks.length && !completedTasks.length && (!taskSuggestions || !taskSuggestions.length)) {
    html = `<p class="muted">No follow-up tasks for this organization.</p>`;
  }

  el.innerHTML = html;
}

async function saveSuggestedTask(taskData) {
  const payload = {
    organization_id: selectedOrg.id,
    title: taskData.title,
    description: taskData.description,
    due_date: taskData.due_date,
    priority: taskData.priority,
  };
  try {
    await api("/api/tasks", { method: "POST", body: JSON.stringify(payload) });
    taskSuggestions = [];
    await loadTasksForOrg();
  } catch (error) {
    alert(error.message);
  }
}

function dismissSuggestedTasks() {
  taskSuggestions = [];
  loadTasksForOrg();
}

async function loadPriorityQueue() {
  const contentEl = document.getElementById("priority-queue-content");
  const errorEl = document.getElementById("priority-queue-error");
  const loadingEl = document.getElementById("priority-queue-loading");
  errorEl.classList.add("hidden");
  contentEl.innerHTML = "";
  loadingEl.classList.remove("hidden");

  try {
    pqData = await api("/api/analytics/priority-queue");
    loadingEl.classList.add("hidden");
    populateFilters(pqData);
    renderPriorityQueue();
  } catch (error) {
    loadingEl.classList.add("hidden");
    errorEl.textContent = "Failed to load priority queue: " + error.message;
    errorEl.classList.remove("hidden");
  }
}

function populateFilters(data) {
  const statuses = [...new Set(data.map(r => r.status))].sort();
  const types = [...new Set(data.map(r => r.category))].sort();

  const statusSel = document.getElementById("pq-filter-status");
  statusSel.innerHTML = '<option value="">All</option>' +
    statuses.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join("");

  const typeSel = document.getElementById("pq-filter-type");
  typeSel.innerHTML = '<option value="">All</option>' +
    types.map(t => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join("");
}

function renderPriorityQueue() {
  const filterPriority = document.getElementById("pq-filter-priority").value;
  const filterStatus = document.getElementById("pq-filter-status").value;
  const filterReadiness = document.getElementById("pq-filter-readiness").value;
  const filterType = document.getElementById("pq-filter-type").value;
  const sortBy = document.getElementById("pq-sort-by").value;

  let rows = pqData.filter(r => {
    if (filterPriority && r.outreach_priority !== filterPriority) return false;
    if (filterStatus && r.status !== filterStatus) return false;
    if (filterReadiness && r.readiness_level !== filterReadiness) return false;
    if (filterType && r.category !== filterType) return false;
    return true;
  });

  rows.sort((a, b) => {
    if (sortBy === "name") return a.name.localeCompare(b.name);
    if (sortBy === "readiness_score") return (b.readiness_score || 0) - (a.readiness_score || 0);
    return (b.priority_score || 0) - (a.priority_score || 0);
  });

  const priorityBadge = (level) => {
    const cls = level === "High" ? "badge-high" : level === "Medium" ? "badge-moderate" : "badge-low";
    return `<span class="badge ${cls}">${escapeHtml(level)}</span>`;
  };

  if (!rows.length) {
    document.getElementById("priority-queue-content").innerHTML = '<p class="muted">No organizations match the current filters.</p>';
    return;
  }

  const tableHtml = `
    <table class="analytics-table pq-table">
      <thead>
        <tr>
          <th>Organization</th>
          <th>Type</th>
          <th>Status</th>
          <th>Priority</th>
          <th class="num">Score</th>
          <th class="num">Readiness</th>
          <th>Next Action</th>
          <th>Follow-up</th>
          <th>Reasoning</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(r => `
          <tr>
            <td><strong>${escapeHtml(r.name)}</strong></td>
            <td>${escapeHtml(r.category)}</td>
            <td>${escapeHtml(r.status)}</td>
            <td>${priorityBadge(r.outreach_priority)}</td>
            <td class="num">${r.priority_score}</td>
            <td class="num">${r.readiness_score != null ? r.readiness_score + '/100' : 'N/A'}</td>
            <td>${escapeHtml(r.recommended_next_action)}</td>
            <td>${escapeHtml(r.recommended_follow_up_date)}</td>
            <td class="pq-reason">${escapeHtml(r.reasoning)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;

  document.getElementById("priority-queue-content").innerHTML = tableHtml;
}

function renderPriorityAnalytics(pa) {
  let html = `<section class="analytics-section"><h3>Priority Analytics</h3>`;

  const byP = pa.by_priority || {};
  const priorityCards = [
    { label: "High Priority", value: byP.High || 0 },
    { label: "Medium Priority", value: byP.Medium || 0 },
    { label: "Low Priority", value: byP.Low || 0 },
    { label: "High-Prio w/o Follow-up", value: pa.high_priority_without_follow_up },
  ];

  html += `<div class="metric-grid">`;
  html += priorityCards.map(m => `
    <div class="metric-card">
      <div class="metric-value">${m.value}</div>
      <div class="metric-label">${escapeHtml(m.label)}</div>
    </div>
  `).join("");
  html += `</div>`;

  const actions = Object.entries(pa.top_next_actions || {});
  if (actions.length) {
    html += `<h4>Top Recommended Next Actions</h4><table class="analytics-table"><thead><tr><th>Action</th><th class="num">Count</th></tr></thead><tbody>`;
    html += actions.map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="num">${v}</td></tr>`).join("");
    html += `</tbody></table>`;
  }

  const fudByP = Object.entries(pa.follow_ups_due_by_priority || {});
  if (fudByP.length) {
    html += `<h4>Follow-ups Due by Priority</h4><table class="analytics-table"><thead><tr><th>Priority</th><th class="num">Count</th></tr></thead><tbody>`;
    html += fudByP.map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td class="num">${v}</td></tr>`).join("");
    html += `</tbody></table>`;
  }

  html += `</section>`;
  return html;
}

document.querySelectorAll(".main-nav a").forEach(link => {
  link.addEventListener("click", event => {
    event.preventDefault();
    navigateTo(link.getAttribute("href"));
  });
});

window.addEventListener("popstate", () => setActivePage());

setActivePage();
loadOrganizations();
loadOutbox();

// Handle ?org=N from search result links
selectOrgFromQuery(window.location.href);
