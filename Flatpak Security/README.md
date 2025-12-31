# Systems Security & Least Privilege in Flatpak Applications

This project explores the concept of **least privilege access** in Linux desktop applications using **Flatpak sandboxing** as a case study. The analysis focuses on how sandboxed and non-sandboxed applications differ in security guarantees, how permissions affect real-world isolation, and how display server choices (X11 vs Wayland) impact application security.

Through hands-on experimentation, proof-of-concept demonstrations, and policy analysis, the project evaluates whether Flatpak applications are meaningfully isolated in practice and where security assumptions can break down.

---

## Project Goals

The primary goals of this project were to:

- Understand sandboxing and least-privilege enforcement in desktop Linux applications  
- Compare sandboxed vs non-sandboxed application behavior  
- Analyze Flatpak permission models and real-world security implications  
- Demonstrate practical risks related to display servers and over-permissioning  
- Evaluate the gap between Flatpak’s theoretical security model and real-world usage  

---

## Methodology

### Environment & Platform
- Linux desktop environment using Flatpak-packaged applications
- Fedora-based system with both X11 and Wayland sessions

### Areas of Analysis
- Sandboxed vs non-sandboxed application behavior
- Flatpak permission inspection and modification
- File system, device, and IPC permissions
- Display server security (X11 vs Wayland)

### Techniques Used
- Permission analysis of real Flatpak applications
- Proof-of-concept keylogging under X11
- Sandbox escape pattern demonstrations
- Manual inspection of Flatpak configuration and policy files
- Comparative analysis of application permissions and usability tradeoffs

---

## Key Findings

- Sandboxed applications significantly reduce risk **only when permissions are tightly scoped**.
- Many Flatpak applications request broad permissions (e.g., `filesystem=host`) that effectively bypass sandbox isolation.
- Under **X11**, applications with display socket access can capture global input events, enabling keylogging across applications.
- Under **Wayland**, strict input isolation prevents this class of attack, even when user-level permissions persist.
- User-level Flatpak overrides persist across logouts, which can maintain elevated privileges without user awareness.
- The use of `--persist` provides a safer alternative to full filesystem access by allowing isolated, app-specific persistent storage.

---

## Demonstrations & Experiments

- **X11 Keylogger Proof of Concept**  
  Demonstrated how an application with X11 access can capture global keystrokes using `xinput` and `xmodmap`.

- **Sandbox Escape Pattern (Non-Destructive)**  
  Showed how modifying and sourcing user-writable files can lead to unintended command execution without violating sandbox rules.

- **Permission Reduction Case Study**  
  Evaluated common desktop apps (LibreOffice, GIMP, Inkscape, Krita, FreeFileSync) and assessed usability vs security when removing `filesystem=host`.

---

## Tools & Technologies

- Flatpak & Flatpak permission system
- Linux namespaces, sandboxing concepts
- X11 and Wayland display servers
- Bash scripting (proof-of-concept demonstrations)
- Flatpak configuration and policy files
- Manual security inspection and threat modeling

---

## Security Model Analysis

Flatpak’s security model assumes:
- Trusted host OS, kernel, and Flatpak infrastructure
- Untrusted applications running inside sandboxes
- User-mediated permission granting via portals

While the model is architecturally sound, the project finds that **real-world security heavily depends on user decisions, repository trust, and permission discipline**. Overly permissive defaults and shared runtimes can significantly weaken isolation guarantees.

---

## Takeaways

This project demonstrates that Flatpak provides meaningful security benefits **in theory**, but those benefits can be undermined by permissive permissions, legacy display systems like X11, and user assumptions about “sandboxed” safety.

Effective sandbox security requires:
- Minimal permissions
- Wayland-based isolation
- Informed user decisions
- Ongoing review of app privileges

Flatpak improves desktop security, but it should not be treated as a hard security boundary without careful configuration and oversight.
