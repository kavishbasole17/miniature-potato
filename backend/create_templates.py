import os

templates = {
    "admin_login.html": """<!DOCTYPE html>
<html><body>
    <h2>Admin Login</h2>
    {% if error %}<p style="color:red">{{error}}</p>{% endif %}
    <form method="post" action="/admin/login">
        <label>Username: <input type="text" name="username" required></label><br>
        <label>Password: <input type="password" name="password" required></label><br>
        <button type="submit">Login</button>
    </form>
</body></html>""",
    "admin_disabled.html": """<!DOCTYPE html>
<html><body>
    <h2>Admin Disabled</h2>
    <p>Admin is disabled. Please set ADMIN_PASSWORD in .env</p>
</body></html>""",
    "admin/base.html": """<!DOCTYPE html>
<html><head><script src="/static/theme.js"></script></head>
<body>
    <nav>
        <a href="/">Home</a> | 
        <a href="/admin/opportunities">Opportunities</a> | 
        <a href="/admin/regions">Regions</a> | 
        <a href="/admin/sources">Sources</a> | 
        <a href="/admin/types">Types</a> | 
        <a href="/admin/import-logs">Import Logs</a> | 
        <a href="/admin/scrape">Run Scrape</a> | 
        <a href="/admin/users">Users</a> | 
        <a href="/admin/logout">Sign Out</a>
    </nav>
    <hr>
    {% block content %}{% endblock %}
</body></html>""",
    "admin/opportunities.html": """{% extends 'admin/base.html' %}
{% block content %}
    <h2>Opportunities</h2>
    <ul>
    {% for opp in data.items %}
        <li>{{ opp.title }}</li>
    {% endfor %}
    </ul>
{% endblock %}""",
    "admin/regions.html": """{% extends 'admin/base.html' %}
{% block content %}
    <h2>Regions</h2>
    <ul>
    {% for r in data %}
        <li>{{ r }}</li>
    {% endfor %}
    </ul>
{% endblock %}""",
    "admin/sources.html": """{% extends 'admin/base.html' %}
{% block content %}
    <h2>Scrape Sources</h2>
    <ul>
    {% for s in data %}
        <li>{{ s.name }} ({{ s.kind }})</li>
    {% endfor %}
    </ul>
{% endblock %}""",
    "admin/types.html": """{% extends 'admin/base.html' %}{% block content %}<h2>Types</h2>{% endblock %}""",
    "admin/import-logs.html": """{% extends 'admin/base.html' %}{% block content %}<h2>Import Logs</h2>{% endblock %}""",
    "admin/scrape.html": """{% extends 'admin/base.html' %}{% block content %}<h2>Run Scrape</h2>
    <form action="/api/admin/scrape" method="post"><button type="submit">Run</button></form>{% endblock %}""",
    "admin/users.html": """{% extends 'admin/base.html' %}{% block content %}<h2>Users</h2>{% endblock %}"""
}

os.makedirs("backend/templates/admin", exist_ok=True)
for k, v in templates.items():
    with open(f"backend/templates/{k}", "w") as f:
        f.write(v)

os.makedirs("backend/static", exist_ok=True)
with open("backend/static/theme.js", "w") as f:
    f.write('''
function toggleTheme() {
    let theme = localStorage.getItem('soa-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('soa-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
}
document.addEventListener("DOMContentLoaded", () => {
    let theme = localStorage.getItem('soa-theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
});
''')

print("Templates created successfully")
