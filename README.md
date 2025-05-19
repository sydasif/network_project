# 🛠️ Network Automation Dashboard

A **Django-based** web application for network engineers to manage Cisco devices. Built with **Nornir** and **Netmiko**, this project allows you to push configurations, monitor devices, back up configs, and log operations through a centralized interface.

---

## ✅ Features

- 🔧 Configuration management for Cisco devices  
- 📊 Device monitoring (e.g., interface status)  
- 📁 Automated backup of running configurations  
- 🧾 Logging of task results, user actions, and errors  
- 🔐 Role-based access using Django Admin  

---

## 🔧 Tech Stack

- [Django](https://www.djangoproject.com/) – Backend framework  
- [Nornir](https://nornir.tech/) – Network automation engine  
- [Netmiko](https://github.com/ktbyers/netmiko) – SSH connection to Cisco devices  
- [Poetry](https://python-poetry.org/) – Environment and dependency manager  

---

## 📂 Project Structure

```

network\_project/
├── manage.py
├── network\_project/       # Django settings
├── automation/            # Tasks, inventory, and logic
│   ├── tasks/
│   ├── inventory/
│   └── nornir\_init.py
├── logs/                  # Task logs
├── pyproject.toml         # Poetry dependency config
├── README.md
└── .gitignore

````

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/network_project.git
   cd network_project
````

2. **Install dependencies using Poetry**

   ```bash
   poetry install
   poetry shell
   ```

3. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

4. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**

   ```bash
   python manage.py runserver
   ```

6. **Access the Admin Panel**

   * Visit: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 🗂️ Sample Inventory File (`hosts.yaml`)

```yaml
r1:
  hostname: 192.168.158.1
  platform: ios
  groups:
    - cisco
```

---

## 📌 Notes

* No Celery or distributed task system — jobs are run locally in-process.
* Logs are written to the `logs/` directory.
* Designed for small to mid-sized network environments or labs.

---

## 🤝 Contributing

Pull requests are welcome!
Please open an issue to discuss any significant changes before submitting a PR.

---

## 📄 License

MIT License
