Name:           crosvm
Version:        1.0
Release:        1%{?dist}
Summary:        Crosvm - Chrome OS Virtual Machine Monitor

License:        BSD
URL:            https://chromium.googlesource.com/crosvm/crosvm

ExclusiveArch:  x86_64

BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  clang
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libdrm)

%description
Crosvm is a virtual machine monitor that runs on Linux and is used primarily for running Chrome OS virtual machines.

%prep
cd %{_builddir}/%{name}

pkg-config --cflags libdrm && exit 1
cargo fetch

%build
cd %{_builddir}/%{name}

cargo build --profile release --no-default-features --features "audio balloon config-file net pvclock swap stats usb wl-dmabuf gpu virgl_renderer vulkan_display video-decoder video-encoder vaapi"

%install
cd %{_builddir}/%{name}

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
