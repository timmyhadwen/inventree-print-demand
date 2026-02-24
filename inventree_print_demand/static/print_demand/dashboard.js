/**
 * 3D Print Demand dashboard panel for InvenTree.
 *
 * Fetches aggregated demand data from the plugin API and renders
 * a colour-coded table showing stock vs demand for every 3D-printed part.
 */

export function renderDashboardItem(target, data) {
    if (!target) {
        console.error("No target provided to renderDashboardItem");
        return;
    }

    target.innerHTML = '<em>Loading 3D print demand data...</em>';

    const headers = {
        'Accept': 'application/json',
    };

    // Include CSRF token if available
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }

    fetch('/plugin/print-demand/api/demand/', { headers, credentials: 'same-origin' })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => { throw new Error(data.error || response.statusText); });
            }
            return response.json();
        })
        .then(data => {
            if (!data.length) {
                target.innerHTML = '<em>No parts found in the configured category.</em>';
                return;
            }
            target.innerHTML = buildTable(data);
        })
        .catch(err => {
            target.innerHTML = `<em style="color:#c00;">Error: ${escapeHtml(err.message)}</em>`;
        });
}

function buildTable(parts) {
    const rows = parts.map(p => {
        const deficitStyle = p.deficit < 0
            ? 'color:#c00;font-weight:bold;'
            : (p.deficit > 0 ? 'color:#080;' : '');

        return `<tr>
            <td><a href="/part/${p.pk}/">${escapeHtml(p.IPN ? p.IPN + ' - ' + p.name : p.name)}</a></td>
            <td style="text-align:right;">${fmt(p.in_stock)}</td>
            <td style="text-align:right;">${fmt(p.allocated_build + p.allocated_sales)}</td>
            <td style="text-align:right;">${fmt(p.available)}</td>
            <td style="text-align:right;">${fmt(p.required_build + p.required_sales)}</td>
            <td style="text-align:right;${deficitStyle}">${fmt(p.deficit)}</td>
        </tr>`;
    }).join('');

    return `
        <div style="overflow-x:auto;">
            <table style="width:100%;border-collapse:collapse;font-size:0.9em;">
                <thead>
                    <tr style="border-bottom:2px solid #ccc;text-align:left;">
                        <th style="padding:6px 8px;">Part</th>
                        <th style="padding:6px 8px;text-align:right;">In Stock</th>
                        <th style="padding:6px 8px;text-align:right;">Allocated</th>
                        <th style="padding:6px 8px;text-align:right;">Available</th>
                        <th style="padding:6px 8px;text-align:right;">Required</th>
                        <th style="padding:6px 8px;text-align:right;">Deficit</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>`;
}

function fmt(n) {
    return Number.isInteger(n) ? n.toString() : n.toFixed(1);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}
