Name:           crosvm
Version:        1.0
Release:        1%{?dist}
Summary:        Crosvm - Chrome OS Virtual Machine Monitor

License:        BSD
URL:            https://chromium.googlesource.com/crosvm/crosvm

ExclusiveArch:  x86_64

BuildRequires:  rust-packaging
BuildRequires:  clang
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(virglrenderer)

%description
Crosvm is a virtual machine monitor that runs on Linux and is used primarily for running Chrome OS virtual machines.

%prep

%cargo_prep
cargo fetch

%build

export CROSVM_USE_SYSTEM_MINIGBM=1
export CROSVM_USE_SYSTEM_VIRGLRENDERER=1

cargo build --profile release --no-default-features --features "audio balloon config-file net pvclock swap usb gpu virgl_renderer vulkan_display video-decoder vaapi"

%install

%cargo_install

install -d -m0755 %{buildroot}%{_datadir}/policy/crosvm
install -Dp -m0644 seccomp/x86_64/*.policy -t %{buildroot}%{_datadir}/policy/crosvm

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
