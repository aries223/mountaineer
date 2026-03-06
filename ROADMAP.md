# Mountaineer Roadmap

Current release: **v1.4.0**
Next release: **v1.5.0**

---

## Unreleased

- [ ] **Auto Progressive compatibility check** — detect jpegoptim version at startup and disable the Auto Progressive option if the version is below 1.5.0 

---

## v1.4.0 — Released

### App

- [x] **Redesign Preferences dialog** — replaced single tall vertical layout with a horizontal tabbed layout (General, JPEG, PNG, WebP, GIF tabs)
- [x] **File Name column now expands on window resize** instead of the Saved column
- [x] **Preferences schema version migration** — resets dialog size to new default on upgrade

### Packaging

- [x] **Update RPM spec to v1.4.0**
- [x] **Fix .desktop file** — remove invalid Version key, set Categories to Graphics only

---

## v1.3.0 — Released

### App

- [x] **Bump minimum Python version to 3.12**
- [x] **Improve  **Options groups in Preferences for JPEG, PNG, WebP, and GIF (including advanced GIF options)**
- [x] **About dialog version bump** — centralized to src/version.py

### Packaging

- [x] **Update RPM spec to v1.3.0**

---

## Backlog (unscheduled)
