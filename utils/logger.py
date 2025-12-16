# utils/logger.py
import os
import json
import datetime
from pathlib import Path

# Configuration
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "prism.log"
REPORT_HTML = LOG_DIR / "report.html"
REPORT_JSON = LOG_DIR / "report_data.json"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)

# Initialize JSON data structure if it doesn't exist
if not REPORT_JSON.exists():
    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump({"events": []}, f, indent=2)

def log_event(event: dict):
    """Logs moderation events to both .log and update the dashboard"""
    ts = datetime.datetime.now().isoformat()
    log_entry = {
        "timestamp": ts,
        "action": event.get('action', 'unknown'),
        "user": event.get('user', 'unknown'),
        "user_id": event.get('user_id', 0),
        "channel": event.get('channel', 'unknown'),
        "label": event.get('label', 'unknown'),
        "prob": float(event.get('prob', 0)),
        "content": event.get('content', '')
    }

    # Append to JSON log
    _update_json_log(log_entry)
    
    # Update HTML dashboard
    _update_html_dashboard()

def _update_json_log(entry):
    """Update the JSON log file with new entry"""
    try:
        # Read existing data
        if REPORT_JSON.exists() and REPORT_JSON.stat().st_size > 0:
            with open(REPORT_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"events": []}

        # Add new entry
        data["events"].append(entry)
        
        # Keep only last 1000 events to prevent file bloat
        if len(data["events"]) > 1000:
            data["events"] = data["events"][-1000:]

        # Save back to file
        with open(REPORT_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error updating JSON log: {e}")

def _update_html_dashboard():
    """Regenerate the HTML dashboard with current data"""
    try:
        # Read the latest data
        with open(REPORT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Sort events by timestamp (newest first)
        events = sorted(data.get("events", []), 
                       key=lambda x: x.get("timestamp", ""), 
                       reverse=True)
        
        # Generate rows
        rows = []
        for event in events:
            timestamp = datetime.datetime.fromisoformat(event["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            prob_percent = f"{event['prob']*100:.1f}%"
            
            # Determine row class based on action
            row_class = ""
            if event["action"] == "deleted":
                row_class = "deleted"
            elif event["action"] == "flagged":
                row_class = "flagged"
                
            rows.append(f"""
            <tr class="{row_class}">
                <td>{timestamp}</td>
                <td><span class="badge {row_class}">{event['action'].upper()}</span></td>
                <td><strong>{event['user']}</strong><br><small>ID: {event['user_id']}</small></td>
                <td><span class="label">{event['label']}</span></td>
                <td><div class="confidence">
                    <div class="confidence-bar" style="width: {event['prob']*100}%"></div>
                    <span>{prob_percent}</span>
                </div></td>
                <td class="message">{_escape_html(event['content'])}</td>
                <td>{event['channel']}</td>
            </tr>
            """)
        
        # Generate the complete HTML
        html = _html_template_start() + "\n".join(rows) + _html_template_end()
        
        # Write to file
        with open(REPORT_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
            
    except Exception as e:
        print(f"Error updating HTML dashboard: {e}")

def _escape_html(text):
    """Escape HTML special characters"""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def _html_template_start():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔒 PRISM Moderation Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --danger: #ef4444;
            --warning: #f59e0b;
            --success: #10b981;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.5;
            padding: 2rem 1rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        h1 {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .stats {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: var(--card-bg);
            border-radius: 0.5rem;
            padding: 1rem 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            min-width: 180px;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        
        .dashboard {
            background: var(--card-bg);
            border-radius: 0.75rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }
        
        .filters {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        label {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-muted);
        }
        
        select, input[type="text"] {
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--border);
            border-radius: 0.375rem;
            font-family: inherit;
            font-size: 0.875rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }
        
        th {
            background-color: #f8fafc;
            color: var(--text-muted);
            font-weight: 600;
            text-align: left;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }
        
        td {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tr.deleted {
            background-color: #fef2f2;
        }
        
        tr.flagged {
            background-color: #fffbeb;
        }
        
        tr:hover {
            background-color: #f8fafc;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .badge.flagged {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .badge.deleted {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        .confidence {
            position: relative;
            height: 24px;
            background-color: #e2e8f0;
            border-radius: 0.25rem;
            overflow: hidden;
        }
        
        .confidence-bar {
            height: 100%;
            background-color: var(--primary);
            min-width: 2px;
            transition: width 0.3s ease;
        }
        
        .confidence span {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            text-shadow: 0 0 2px rgba(0,0,0,0.3);
        }
        
        .message {
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .label {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            background-color: #e0f2fe;
            color: #0369a1;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .empty-state {
            padding: 3rem 1.5rem;
            text-align: center;
            color: var(--text-muted);
        }
        
        @media (max-width: 1024px) {
            .container {
                padding: 0 1rem;
            }
            
            .stat-card {
                flex: 1 1 100%;
            }
            
            table {
                display: block;
                overflow-x: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🔒 PRISM Moderation Dashboard</h1>
                <p>Real-time monitoring of flagged and moderated content</p>
            </div>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-flagged">0</div>
                    <div class="stat-label">Total Flagged</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-deleted">0</div>
                    <div class="stat-label">Messages Deleted</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-users">0</div>
                    <div class="stat-label">Unique Users</div>
                </div>
            </div>
        </header>
        
        <div class="dashboard">
            <div class="filters">
                <div class="filter-group">
                    <label for="filter-action">Action:</label>
                    <select id="filter-action">
                        <option value="">All Actions</option>
                        <option value="flagged">Flagged</option>
                        <option value="deleted">Deleted</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="filter-user">User:</label>
                    <input type="text" id="filter-user" placeholder="Filter by username">
                </div>
                <div class="filter-group">
                    <label for="filter-content">Message:</label>
                    <input type="text" id="filter-content" placeholder="Search in messages">
                </div>
            </div>
            
            <div style="overflow-x: auto;">
                <table id="moderation-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Action</th>
                            <th>User</th>
                            <th>Category</th>
                            <th>Confidence</th>
                            <th>Message</th>
                            <th>Channel</th>
                        </tr>
                    </thead>
                    <tbody>
"""

def _html_template_end():
    return """
                    </tbody>
                </table>
            </div>
            
            <div id="empty-state" class="empty-state" style="display: none;">
                <p>No moderation events found matching your filters.</p>
            </div>
        </div>
    </div>
    
    <script>
        // Load data from JSON file
        async function loadData() {
            try {
                const response = await fetch('report_data.json');
                const data = await response.json();
                return data.events || [];
            } catch (error) {
                console.error('Error loading data:', error);
                return [];
            }
        }
        
        // Filter and display data
        async function updateDashboard() {
            const events = await loadData();
            const actionFilter = document.getElementById('filter-action').value.toLowerCase();
            const userFilter = document.getElementById('filter-user').value.toLowerCase();
            const contentFilter = document.getElementById('filter-content').value.toLowerCase();
            
            const filteredEvents = events.filter(event => {
                const matchesAction = !actionFilter || event.action.toLowerCase() === actionFilter;
                const matchesUser = !userFilter || event.user.toLowerCase().includes(userFilter);
                const matchesContent = !contentFilter || 
                    (event.content && event.content.toLowerCase().includes(contentFilter));
                
                return matchesAction && matchesUser && matchesContent;
            });
            
            // Update stats
            updateStats(events);
            
            // Render table
            renderTable(filteredEvents);
        }
        
        // Update statistics
        function updateStats(events) {
            const flaggedCount = events.filter(e => e.action === 'flagged').length;
            const deletedCount = events.filter(e => e.action === 'deleted').length;
            const uniqueUsers = new Set(events.map(e => e.user_id)).size;
            
            document.getElementById('total-flagged').textContent = flaggedCount;
            document.getElementById('total-deleted').textContent = deletedCount;
            document.getElementById('total-users').textContent = uniqueUsers;
        }
        
        // Render table rows
        function renderTable(events) {
            const tbody = document.querySelector('#moderation-table tbody');
            const emptyState = document.getElementById('empty-state');
            
            if (!events.length) {
                tbody.innerHTML = '';
                emptyState.style.display = 'block';
                return;
            }
            
            emptyState.style.display = 'none';
            
            const rows = events.map(event => {
                const date = new Date(event.timestamp);
                const formattedDate = date.toLocaleString();
                const probPercent = (event.prob * 100).toFixed(1) + '%';
                
                return `
                    <tr class="${event.action}">
                        <td>${formattedDate}</td>
                        <td><span class="badge ${event.action}">${event.action.toUpperCase()}</span></td>
                        <td><strong>${escapeHtml(event.user)}</strong><br><small>ID: ${event.user_id}</small></td>
                        <td><span class="label">${escapeHtml(event.label)}</span></td>
                        <td>
                            <div class="confidence">
                                <div class="confidence-bar" style="width: ${event.prob * 100}%"></div>
                                <span>${probPercent}</span>
                            </div>
                        </td>
                        <td class="message" title="${escapeHtml(event.content)}">${escapeHtml(truncate(event.content, 50))}</td>
                        <td>${escapeHtml(event.channel)}</td>
                    </tr>
                `;
            }).join('');
            
            tbody.innerHTML = rows;
        }
        
        // Helper functions
        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return String(unsafe)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
        
        function truncate(str, length) {
            if (!str) return '';
            return str.length > length ? str.substring(0, length) + '...' : str;
        }
        
        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            // Initial load
            updateDashboard();
            
            // Set up filter event listeners
            document.getElementById('filter-action').addEventListener('change', updateDashboard);
            document.getElementById('filter-user').addEventListener('input', updateDashboard);
            document.getElementById('filter-content').addEventListener('input', updateDashboard);
            
            // Auto-refresh every 30 seconds
            setInterval(updateDashboard, 30000);
        });
    </script>
</body>
</html>
"""
