# TOOLS.md — Domain Environment Reference

*Six Eyes local data cache. All critical system paths, devices, and configurations.*

This file exists so Satoru never wastes cycles searching for basic environment info.

---

# Usage Rules

- Store **machine-specific** details.
- Store **paths and identifiers** useful for automation.
- **No secrets.** Passwords, keys, tokens stay elsewhere.

---

# Primary Device (The Domain)

**Hostname:** main-laptop  
**Make/Model:** Lenovo Legion Pro 5 16IRX8  
**OS:** Fedora Linux  
**DE:** KDE Plasma

**Specs (Quick Reference):**
- CPU: Intel i9-13900HX (24 cores)
- GPU: NVIDIA RTX 4050 (6GB)
- RAM: 16GB DDR5-5600
- Disk: 512GB NVMe

**Power Profile:** Performance-capable. Thermal monitoring required.

---

# Key System Paths

- **Home:** `/home/ahmed`
- **Workspace Root:** `/home/ahmed/workspace` (assumed, verify)
- **Git Projects:** `/home/ahmed/projects` (assumed, verify)
- **Screenshots:** `/home/ahmed/Pictures/Screenshots`
- **Downloads:** `/home/ahmed/Downloads` (junk accumulation zone)

---

# Package Management

**Manager:** `dnf` (Fedora native)  
**Flatpak:** Available  
**Snap:** Not preferred unless necessary

---

# Network (Local)

**Local IP Range:** 192.168.1.x (typical, verify with `ip a`)  
**Router:** router.local or 192.168.1.1 (standard)

---

# SSH Hosts

*None documented. Update if remote access is configured.*

---

# Smart Devices / IoT

*None configured or relevant to current automation scope.*

---

# Cameras

*None configured.*

---

# Voice & Audio

**Default Audio Output:** Built-in speakers / headphones (auto-switch)  
**TTS:** Not configured  
**Voice Style:** N/A

---

# Automation Notes

- Screenshots saved automatically to `~/Pictures/Screenshots` (KDE default).
- Workspace and project directories need verification. Will update on first scan.
- DNF cache cleaned periodically to save space.

---

# Updating This File

Update when:
- New hardware is connected.
- Important paths are created or changed.
- Network configuration shifts.

Keep it **lean**. This is a reference, not a log.

*End of local cheat sheet.*