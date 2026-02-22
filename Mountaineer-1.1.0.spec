Name:           Mountaineer
Version:        1.1.0
Release:        1%{?dist}
Summary:     A high quality image compression utility.

License:       AGPL-3.0
URL:             https://github.com/aries223/mountaineer
Source0:         %_sourcedir/Mountaineer-1.1.0.tar.gz

BuildArch:      x86_64
Requires:       python >= 3.8, jpegoptim, oxipng, gifsicle, libwebp-tools

# Disable debug package generation
%define _enable_debug_package 0
%define __find_debuginfo false
%define debug_package %{nil}

%description
Powerfull high quality image compression utility.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/usr/bin/
cp -a mountaineer %{buildroot}/usr/bin/

# Install .desktop file to /usr/share/applications
mkdir -p %{buildroot}/usr/share/applications/
cp mountaineer.desktop %{buildroot}/usr/share/applications/

# Install logo image to /usr/share/pixmaps
mkdir -p %{buildroot}/usr/share/pixmaps/
cp mountaineer.png %{buildroot}/usr/share/pixmaps/mountaineer.png

%files
/usr/bin/mountaineer
/usr/share/applications/mountaineer.desktop
/usr/share/pixmaps/mountaineer.png

%post
update-desktop-database /usr/share/applications/

%postun
if [ $1 -eq 0 ]; then
    update-desktop-database /usr/share/applications/
fi

%changelog
* Fri Feb 21 2026 Mountaineer - 1.1.0
- Add GIF and WebP compression support
- Add keyboard shortcuts (Ctrl+O, Ctrl+Shift+O, Ctrl+A, Ctrl+,, Delete, Ctrl+Q)
- Add Preferences dialog tooltips and visual improvements
- Add user guide documentation
- Fix preferences data loss on save
- Fix sort desync data corruption
- Fix thread-safety race condition in compression worker
- Fix lossless JPEG stub

* Fri Oct 3 2025 Mountaineer - 1.1.0
* Wed Oct 1 2025 Mountaineer - 1.0.2
* Wed Oct 1 2025 Mountaineer - 1.0.1
* Wed Oct 1 2025 Mountaineer - 1.0
- Initial package
