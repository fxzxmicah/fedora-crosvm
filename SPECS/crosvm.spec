%global setenv export CROSVM_USE_SYSTEM_MINIGBM=1 CROSVM_USE_SYSTEM_VIRGLRENDERER=1
%global CARGO_FLAGS -n -f "audio balloon config-file net pvclock swap usb gpu virgl_renderer vulkan_display video-decoder vaapi media"

Name:           crosvm
Version:        1.0
Release:        1%{?dist}
Summary:        CrosVM - Chrome OS Virtual Machine Monitor

License:        BSD
URL:            https://chromium.googlesource.com/crosvm/crosvm

Source:         https://chromium.googlesource.com/crosvm/crosvm/+archive/refs/heads/main.tar.gz

Source1:        https://chromium.googlesource.com/chromiumos/platform/minijail/+archive/refs/heads/main.tar.gz#/minijail-main.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  rust-packaging
BuildRequires:  crate(anyhow/default)
BuildRequires:  crate(argh/default)
BuildRequires:  crate(cfg-if/default)

BuildRequires:  clang
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(virglrenderer)
BuildRequires:  pkgconfig(wayland-protocols)

%description
CrosVM is a virtual machine monitor (VMM) based on Linux’s KVM hypervisor, with a focus on simplicity, security, and speed.
CrosVM is intended to run Linux guests, originally as a security boundary for running native applications on the ChromeOS
platform. Compared to QEMU, CrosVM doesn’t emulate architectures or real hardware, instead concentrating on paravirtualized
devices, such as the virtio standard.

CrosVM is currently used to run Linux/Android guests on ChromeOS devices.

%prep
%autosetup -c
tar -xf %{SOURCE1} -C third_party/minijail

echo '
[profile.rpm]
inherits = "release"
opt-level = 3
strip = "symbols"
' >> Cargo.toml

%cargo_prep

%build
%{setenv}
%cargo_build %{CARGO_FLAGS}

%install
%cargo_install

install -d -m0755 %{buildroot}%{_datadir}/policy/crosvm
install -Dp -m0644 jail/seccomp/x86_64/*.policy -t %{buildroot}%{_datadir}/policy/crosvm

%files
%license LICENSE
%doc ARCHITECTURE.md
%doc CONTRIBUTING.md
%doc README.chromeos.md
%doc README.md
%{_bindir}/crosvm
%{_datadir}/policy/crosvm

%changelog
* Wed Aug 14 2024 Fxzxmicah <48860358+fxzxmicah@users.noreply.github.com> - 1.0-1
- Initial package
