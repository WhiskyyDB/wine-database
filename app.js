/**
 * WineDB Sommelier Explorer & Interactive Frontend Logic
 */

const FALLBACK_VINTAGES = [
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, abv_percent: 14.5, bottle_volume_ml: 750, release_price_usd: 315, valuation_index_usd: 315, source_url: "https://josephphelps.com/wines/insignia/2019" },
    { vintage_id: 2, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2018, abv_percent: 14.5, bottle_volume_ml: 750, release_price_usd: 300, valuation_index_usd: null, source_url: "https://josephphelps.com/wines/insignia/2018" },
    { vintage_id: 3, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2017, abv_percent: 14.2, bottle_volume_ml: 750, release_price_usd: 285, valuation_index_usd: null, source_url: "https://josephphelps.com/wines/insignia/2017" },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, abv_percent: 14.0, bottle_volume_ml: 750, release_price_usd: 385, valuation_index_usd: null, source_url: "https://www.opusonewinery.com/" },
    { vintage_id: 5, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2018, abv_percent: 14.0, bottle_volume_ml: 750, release_price_usd: 365, valuation_index_usd: null, source_url: "https://www.opusonewinery.com/" },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, abv_percent: 13.7, bottle_volume_ml: 750, release_price_usd: 240, valuation_index_usd: null, source_url: "https://www.ridgewine.com/wines/monte-bello/" },
    { vintage_id: 7, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2018, abv_percent: 13.8, bottle_volume_ml: 750, release_price_usd: 230, valuation_index_usd: null, source_url: "https://www.ridgewine.com/wines/monte-bello/" }
];

const FALLBACK_BLENDS = [
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, variety_name: "Cabernet Sauvignon", percent: 92.0 },
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, variety_name: "Merlot", percent: 6.0 },
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, variety_name: "Petit Verdot", percent: 2.0 },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, variety_name: "Cabernet Sauvignon", percent: 78.0 },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, variety_name: "Merlot", percent: 8.0 },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, variety_name: "Petit Verdot", percent: 6.0 },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, variety_name: "Cabernet Franc", percent: 6.0 },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, variety_name: "Malbec", percent: 2.0 },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, variety_name: "Cabernet Sauvignon", percent: 77.0 },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, variety_name: "Merlot", percent: 14.0 },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, variety_name: "Petit Verdot", percent: 9.0 }
];

const FALLBACK_TASTING = [
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, descriptor: "Black currant" },
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, descriptor: "Graphite" },
    { vintage_id: 1, winery_name: "Joseph Phelps Vineyards", wine_name: "Insignia", vintage_year: 2019, descriptor: "Cocoa powder" },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, descriptor: "Dark blackberry" },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, descriptor: "Cassis" },
    { vintage_id: 4, winery_name: "Opus One Winery", wine_name: "Opus One", vintage_year: 2019, descriptor: "Cigar box" },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, descriptor: "Crushed rock" },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, descriptor: "Cedar" },
    { vintage_id: 6, winery_name: "Ridge Vineyards", wine_name: "Monte Bello", vintage_year: 2019, descriptor: "Red plum" }
];

let vintagesData = [];
let blendsData = [];
let tastingData = [];

document.addEventListener("DOMContentLoaded", async () => {
    setupTabs();
    setupSearchAndFilters();
    setupModalButtons();
    await loadData();
    renderAllTables();
    animateStats();
});

function setupModalButtons() {
    const stripeBtn = document.getElementById("btn-stripe-modal");
    const customBtn = document.getElementById("btn-custom-modal");
    if (stripeBtn) stripeBtn.addEventListener("click", openStripeModal);
    if (customBtn) customBtn.addEventListener("click", openCustomRequestModal);

    // Modals are class-driven only (CSS :target is not used: clearing the hash
    // via history.pushState never un-matches :target, which made them unclosable).
    // Support old deep links by opening via JS instead.
    if (window.location.hash === "#stripe-modal") openStripeModal();
    if (window.location.hash === "#custom-request-modal") openCustomRequestModal();
}

function setupTabs() {
    const buttons = document.querySelectorAll(".tab-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            
            btn.classList.add("active");
            const targetId = btn.getAttribute("data-target");
            document.getElementById(targetId).classList.add("active");
        });
    });
}

function setupSearchAndFilters() {
    const searchInput = document.getElementById("search-input");
    const filterAppellation = document.getElementById("filter-appellation");
    const filterVariety = document.getElementById("filter-variety");

    const triggerUpdate = () => {
        renderAllTables();
    };

    if (searchInput) searchInput.addEventListener("input", triggerUpdate);
    if (filterAppellation) filterAppellation.addEventListener("change", triggerUpdate);
    if (filterVariety) filterVariety.addEventListener("change", triggerUpdate);
}

async function loadData() {
    try {
        // Fetch from samples/ directory where CSV files actually reside, with cache buster so CDN never serves stale data
        const cacheBuster = `?v=${Date.now()}`;
        const [vResp, bResp, tResp] = await Promise.all([
            fetch(`samples/vintages.csv${cacheBuster}`),
            fetch(`samples/blends.csv${cacheBuster}`),
            fetch(`samples/tasting_profiles.csv${cacheBuster}`)
        ]);

        if (vResp.ok && bResp.ok && tResp.ok) {
            const vText = await vResp.text();
            const bText = await bResp.text();
            const tText = await tResp.text();

            // Safeguard: If hosting returns HTML index fallback instead of CSV, use JS fallbacks
            if (vText.includes("<!DOCTYPE html>") || vText.includes("<html")) {
                throw new Error("Server returned HTML fallback instead of CSV");
            }

            vintagesData = parseCSV(vText);
            blendsData = parseCSV(bText);
            tastingData = parseCSV(tText);
        } else {
            throw new Error("Local fallback triggered");
        }
    } catch (err) {
        // Fallback for file:// or offline preview
        vintagesData = [...FALLBACK_VINTAGES];
        blendsData = [...FALLBACK_BLENDS];
        tastingData = [...FALLBACK_TASTING];
    }
}

function parseCSV(csvText) {
    if (!csvText) return [];
    // Strip UTF-8 BOM (\uFEFF) and carriage returns (\r) completely
    const cleanText = csvText.replace(/^\uFEFF/, "").replace(/\r/g, "");
    
    // Parse character by character handling quotes
    const rows = [];
    let currentRow = [];
    let currentVal = "";
    let inQuotes = false;

    for (let i = 0; i < cleanText.length; i++) {
        const char = cleanText[i];
        const nextChar = cleanText[i + 1];

        if (char === '"') {
            if (inQuotes && nextChar === '"') {
                currentVal += '"';
                i++; // skip escaped quote
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            currentRow.push(currentVal.trim());
            currentVal = "";
        } else if (char === '\n' && !inQuotes) {
            currentRow.push(currentVal.trim());
            if (currentRow.some(v => v.length > 0)) {
                rows.push(currentRow);
            }
            currentRow = [];
            currentVal = "";
        } else {
            currentVal += char;
        }
    }
    // Push last row if exists
    if (currentVal.length > 0 || currentRow.length > 0) {
        currentRow.push(currentVal.trim());
        if (currentRow.some(v => v.length > 0)) {
            rows.push(currentRow);
        }
    }

    if (rows.length < 2) return [];

    const headers = rows[0].map(h => h.replace(/^"|"$/g, "").trim());
    const results = [];

    for (let i = 1; i < rows.length; i++) {
        const cols = rows[i];
        const row = {};
        headers.forEach((h, idx) => {
            let val = cols[idx] !== undefined ? cols[idx].replace(/^"|"$/g, "").trim() : null;
            if (val === "" || val === undefined || val === null || val === "null" || val === "NULL") {
                val = null;
            } else if (!isNaN(val) && val !== null && val !== "") {
                val = Number(val);
            }
            row[h] = val;
        });
        results.push(row);
    }
    return results;
}

function filterMatches(row) {
    if (!row || !row.vintage_id) return false;
    const wineryName = (row.winery_name || "").toString();

    const searchInput = document.getElementById("search-input") ? document.getElementById("search-input").value.toLowerCase().trim() : "";
    const filterApp = document.getElementById("filter-appellation") ? document.getElementById("filter-appellation").value : "ALL";
    const filterVar = document.getElementById("filter-variety") ? document.getElementById("filter-variety").value : "ALL";

    // Appellation logic (mock mapped based on producer for display if not explicitly joined)
    if (filterApp !== "ALL") {
        if (filterApp === "Napa Valley" && !wineryName.includes("Phelps") && !wineryName.includes("Opus")) return false;
        if (filterApp === "Santa Cruz Mountains" && !wineryName.includes("Ridge")) return false;
    }

    // Variety filter check against blends table
    if (filterVar !== "ALL") {
        const hasVar = blendsData.some(b => b.vintage_id == row.vintage_id && b.variety_name === filterVar);
        if (!hasVar) return false;
    }

    // Text query
    if (searchInput) {
        const text = Object.values(row).map(v => v ? String(v).toLowerCase() : "").join(" ");
        if (!text.includes(searchInput)) return false;
    }

    return true;
}

function renderAllTables() {
    renderVintagesTable();
    renderBlendsTable();
    renderTastingTable();
}

function renderVintagesTable() {
    const tbody = document.getElementById("vintages-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    const filtered = vintagesData.filter(filterMatches);

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 2rem; color: #a69b9e;">No vintages match your current filters.</td></tr>`;
        return;
    }

    filtered.forEach(row => {
        const tr = document.createElement("tr");
        const valBadge = row.valuation_index_usd 
            ? `<span class="badge-valuation">$${Number(row.valuation_index_usd).toLocaleString()} USD</span>`
            : `<span class="badge-no-obs">NULL (&lt; 3 Obs)</span>`;

        tr.innerHTML = `
            <td><code>#${row.vintage_id}</code></td>
            <td><strong>${row.winery_name}</strong></td>
            <td>${row.wine_name}</td>
            <td><span class="badge-format">${row.vintage_year}</span></td>
            <td><code>${row.abv_percent || 'N/A'}%</code></td>
            <td><span class="badge-format">${row.bottle_volume_ml} ml</span></td>
            <td class="badge-price">$${row.release_price_usd || '—'}</td>
            <td>${valBadge}</td>
            <td><a href="${row.source_url || '#'}" target="_blank" rel="noopener" style="color: #d4af37; text-decoration: underline;">Tech Sheet &nearr;</a></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderBlendsTable() {
    const tbody = document.getElementById("blends-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    const filtered = blendsData.filter(b => {
        const v = vintagesData.find(vt => vt.vintage_id == b.vintage_id);
        return v ? filterMatches(v) : true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #a69b9e;">No varietal blend records match.</td></tr>`;
        return;
    }

    filtered.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><code>#${row.vintage_id}</code></td>
            <td><strong>${row.winery_name}</strong></td>
            <td>${row.wine_name}</td>
            <td><span class="badge-format">${row.vintage_year}</span></td>
            <td><strong>${row.variety_name}</strong></td>
            <td><code style="color: #d4af37; font-weight: 700;">${row.percent}%</code></td>
            <td>
                <span class="badge-trigger-ok">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>
                    OK (&le; 100.001%)
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderTastingTable() {
    const tbody = document.getElementById("tasting-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    const filtered = tastingData.filter(t => {
        const v = vintagesData.find(vt => vt.vintage_id == t.vintage_id);
        return v ? filterMatches(v) : true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #a69b9e;">No organoleptic descriptors match.</td></tr>`;
        return;
    }

    filtered.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><code>#${row.vintage_id}</code></td>
            <td><strong>${row.winery_name}</strong></td>
            <td>${row.wine_name}</td>
            <td><span class="badge-format">${row.vintage_year}</span></td>
            <td><strong style="color: #ffd1dc;">${row.descriptor}</strong></td>
            <td><span class="badge-format">Aromatic / Palate</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function animateStats() {
    const stats = [
        { id: "stat-wineries", target: 26, suffix: "+" },
        { id: "stat-vintages", target: 59, suffix: "+" },
        { id: "stat-blends", target: 171, suffix: "+" },
        { id: "stat-tasting", target: 236, suffix: "+" }
    ];

    stats.forEach(st => {
        const el = document.getElementById(st.id);
        if (!el) return;
        
        let current = 0;
        const step = Math.ceil(st.target / 30);
        const timer = setInterval(() => {
            current += step;
            if (current >= st.target) {
                current = st.target;
                clearInterval(timer);
            }
            el.textContent = current + st.suffix;
        }, 35);
    });
}

/* ==========================================================================
   Modal & Checkout Handlers (Stripe & Enterprise Custom Form)
   ========================================================================== */
// Overlays carry inline display:none so the modal markup can never appear in
// the document flow (e.g. for a client stuck on a stale stylesheet). JS owns
// display; the stylesheet only animates opacity/transform via .active.
function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.style.display = "flex";
    void modal.offsetWidth; // commit display change so the opacity fade still runs
    modal.classList.add("active");
    modal.style.opacity = "1";
    modal.style.pointerEvents = "auto";
    const container = modal.querySelector(".modal-container");
    if (container) container.style.transform = "translateY(0) scale(1)";
}

function openStripeModal() { openModal("stripe-modal"); }

function openCustomRequestModal() { openModal("custom-request-modal"); }

function closeModals() {
    document.querySelectorAll(".modal-overlay").forEach(m => {
        m.classList.remove("active");
        m.style.opacity = "";
        m.style.pointerEvents = "";
        const container = m.querySelector(".modal-container");
        if (container) container.style.transform = "";
        setTimeout(() => {
            if (!m.classList.contains("active")) m.style.display = "none";
        }, 350);
    });
    if (window.location.hash === "#stripe-modal" || window.location.hash === "#custom-request-modal") {
        history.pushState("", document.title, window.location.pathname + window.location.search);
    }
}

// Close modals when clicking outside the container
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
        closeModals();
    }
});

// ESC key closes modals
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModals();
});

function initiateStripePayment() {
    // Merchant configurable Stripe Payment Link URL
    // To set your live Stripe Payment Link (from your Stripe Dashboard -> Payment Links),
    // update STRIPE_PAYMENT_LINK below or set window.STRIPE_PAYMENT_LINK.
    const STRIPE_PAYMENT_LINK = window.STRIPE_PAYMENT_LINK || "https://buy.stripe.com/bJe8wQf3GdrobDZ0A038407";

    // Stripe redirects to the delivery worker after payment, which verifies the
    // checkout session before serving the snapshot. No client-side success page.
    window.location.href = STRIPE_PAYMENT_LINK;
}

async function handleEnterpriseSubmit(event) {
    event.preventDefault();
    const isPageForm = event.target.id === "onpage-enterprise-form";
    const prefix = isPageForm ? "page-" : "";

    const btn = document.getElementById(`${prefix}submit-btn`) || document.getElementById("submit-btn");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span>⏳ Submitting to Engineering...</span>`;
    }

    const name = document.getElementById(`${prefix}req-name`)?.value || document.getElementById("req-name")?.value || "";
    const org = document.getElementById(`${prefix}req-org`)?.value || document.getElementById("req-org")?.value || "";
    const email = document.getElementById(`${prefix}req-email`)?.value || document.getElementById("req-email")?.value || "";
    const format = document.getElementById(`${prefix}req-format`)?.value || document.getElementById("req-format")?.value || "";
    const scope = document.getElementById(`${prefix}req-scope`)?.value || document.getElementById("req-scope")?.value || "";
    
    const checkedOpts = [];
    document.querySelectorAll(`input[name="${prefix}req-opts"]:checked, input[name="req-opts"]:checked`).forEach(cb => {
        if (!checkedOpts.includes(cb.value)) checkedOpts.push(cb.value);
    });

    const payload = {
        access_key: "bf34ff48-fcc6-4823-b386-9ae3d0712797",
        subject: `[WineDB Enterprise Scope] Request from ${org} (${name})`,
        from_name: "WineDB Enterprise Form",
        name: name,
        organization: org,
        email: email,
        format: format,
        enrichment_options: checkedOpts.join(", "),
        detailed_scope: scope
    };

    const plainSubject = `[WineDB Enterprise Scope] Request from ${org}`;
    const plainBody =
        `Hello WineDB Engineering Team,\n\n` +
        `We are requesting a custom enterprise extraction scope with the following requirements:\n\n` +
        `Name: ${name}\n` +
        `Organization: ${org}\n` +
        `Work Email: ${email}\n` +
        `Preferred Format: ${format}\n` +
        `Enrichment Options: ${checkedOpts.join(", ")}\n\n` +
        `Detailed Scope Spec:\n${scope}\n\n` +
        `Please send us our schema proposal and pricing quote.\n\nBest regards,\n${name}`;
    const fallbackUrl = `mailto:winedb.obedient560@aleeas.com?subject=${encodeURIComponent(plainSubject)}&body=${encodeURIComponent(plainBody)}`;

    const sentDisplay = document.getElementById(`${prefix}sent-email-display`) || document.getElementById("sent-email-display");
    if (sentDisplay) sentDisplay.textContent = email;

    const mailtoBtn = document.getElementById(`${prefix}fallback-mailto-btn`) || document.getElementById("fallback-mailto-btn");
    if (mailtoBtn) {
        mailtoBtn.href = fallbackUrl;
        // mailto does nothing on machines without a default mail app, so also
        // copy the composed request to the clipboard as a guaranteed path.
        mailtoBtn.onclick = () => {
            const text = `To: winedb.obedient560@aleeas.com\nSubject: ${plainSubject}\n\n${plainBody}`;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(() => {
                    mailtoBtn.textContent = "Copied! If no email app opened, paste it into any email to winedb.obedient560@aleeas.com";
                }).catch(() => {});
            }
        };
    }

    // Only report success when Web3Forms confirms delivery: fetch() resolves on
    // HTTP errors too, and the API replies with success:false on rejection
    // (bad key, spam filter, quota).
    let delivered = false;
    try {
        const res = await fetch("https://api.web3forms.com/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json().catch(() => null);
        delivered = res.ok && !!data && (data.success === true || data.success === "true");
    } catch (err) {
        console.warn("Web3Forms request failed:", err);
    }

    const successBox = document.getElementById(`${prefix}form-success-box`) || document.getElementById("form-success-box");
    if (successBox) {
        if (!delivered) {
            const heading = successBox.querySelector("h4");
            const para = successBox.querySelector("p");
            if (heading) heading.textContent = "⚠️ Your request was not sent";
            if (para) para.innerHTML = "Our form service is unreachable right now. Use the button below to send the same request from your email app — it is pre-filled and goes straight to <code>winedb.obedient560@aleeas.com</code>.";
            successBox.style.background = "rgba(191, 54, 12, 0.18)";
            successBox.style.borderColor = "#e64a19";
            successBox.style.color = "#ffab91";
        }
        successBox.style.display = "block";
        successBox.classList.add("active");
    }
    if (btn) {
        if (delivered) {
            btn.style.display = "none";
        } else {
            btn.disabled = false;
            btn.innerHTML = "<span>Retry sending &rarr;</span>";
        }
    }
}

// Global scope exports for reliable HTML inline attribute wiring
window.openStripeModal = openStripeModal;
window.openCustomRequestModal = openCustomRequestModal;
window.closeModals = closeModals;
window.initiateStripePayment = initiateStripePayment;
window.handleEnterpriseSubmit = handleEnterpriseSubmit;

