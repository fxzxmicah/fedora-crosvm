%global commit ca4ee802a94ea2861fa03872fa263fcea744d83d
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global commitdate 20260410
%global minijail_commit bfd22f25fd2302fe4ae5121d80c836e0f124e742
%global minijail_shortcommit %(c=%{minijail_commit}; echo ${c:0:8})

%global crosvm_features audio,balloon,net,pci-hotplug,pvclock,swap,stats,tokio,usb,wl-dmabuf,gpu,gfxstream,gfxstream_display,virgl_renderer,vulkan_display,video-decoder,vaapi,media

Name:           crosvm
Version:        0^git%{commitdate}
Release:        1%{?dist}
Summary:        ChromeOS Virtual Machine Monitor based on KVM

License:        BSD-3-Clause
URL:            https://chromium.googlesource.com/crosvm/crosvm
Source0:        https://chromium.googlesource.com/crosvm/crosvm/+archive/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz
Source1:        https://chromium.googlesource.com/chromiumos/platform/minijail/+archive/%{minijail_commit}.tar.gz#/minijail-%{minijail_shortcommit}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  rust-packaging
BuildRequires:  clang
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libcap)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(virglrenderer)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(gfxstream_backend)
BuildRequires:  python3

%description
Crosvm is a virtual machine monitor (VMM) based on Linux KVM, with a focus on
simplicity, security, and speed. It is used by ChromeOS to run Linux and
Android guests with paravirtualized devices instead of emulating full hardware
platforms.

This package builds the `crosvm` binary for Linux x86_64 with audio, balloon,
network, PCI hotplug, pvclock, swap, stats, tokio, USB, virtio-gpu, wl-dmabuf,
gfxstream, virglrenderer, Vulkan display, VA-API video decoding, and
virtio-media support.

%package policy
Summary:        ChromeOS Virtual Machine Monitor policy files
Requires:       %{name}%{?_isa}

%description policy
The package installs the x86_64 seccomp policy files that can be referenced
explicitly through `--seccomp-policy-dir`; normal builds embed precompiled
seccomp BPF programs and do not require these files at runtime.

%prep
%autosetup -c -n %{name}-%{version}

install -d third_party/minijail
tar -xf %{SOURCE1} -C third_party/minijail

python3 - <<'PY'
from pathlib import Path

path = Path("Cargo.toml")
lines = path.read_text().splitlines()

headers_to_remove = {
    "[target.'cfg(windows)'.dependencies]",
    "[target.'cfg(target_arch = \"riscv64\")'.dependencies]",
    "[target.'cfg(target_arch = \"aarch64\")'.dependencies]",
}

out = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    if stripped in headers_to_remove:
        i += 1
        while i < len(lines) and not lines[i].startswith('['):
            i += 1
        continue

    out.append(line)
    i += 1

path.write_text("\n".join(out) + "\n")
PY

# Make gpu_display resilient in isolated RPM buildroots by explicitly probing
# wayland-client for include and link paths instead of assuming compiler default
# system include paths are sufficient.
python3 - <<'PY'
from pathlib import Path

path = Path("gpu_display/build.rs")
text = path.read_text()
old = """fn build_wayland() {\n    println!(\"cargo:rerun-if-env-changed=WAYLAND_PROTOCOLS_PATH\");\n    let out_dir = env::var(\"OUT_DIR\").unwrap();\n\n    let mut build = cc::Build::new();\n    build.warnings(true);\n    build.warnings_into_errors(true);\n    build.include(&out_dir);\n    build.flag(\"-std=gnu11\");\n"""
new = """fn build_wayland() {\n    println!(\"cargo:rerun-if-env-changed=WAYLAND_PROTOCOLS_PATH\");\n    let out_dir = env::var(\"OUT_DIR\").unwrap();\n    let wayland_client = pkg_config::Config::new()\n        .cargo_metadata(false)\n        .probe(\"wayland-client\")\n        .expect(\"missing wayland-client development files - please install libwayland-dev\");\n\n    let mut build = cc::Build::new();\n    build.warnings(true);\n    build.warnings_into_errors(true);\n    build.include(&out_dir);\n    for include_path in &wayland_client.include_paths {\n        build.include(include_path);\n    }\n    build.flag(\"-std=gnu11\");\n"""
if old not in text:
    raise SystemExit("failed to patch gpu_display/build.rs (prologue)")
text = text.replace(old, new, 1)

old = """    build.compile(\"display_wl\");\n\n    println!(\"cargo:rustc-link-lib=dylib=wayland-client\");\n}\n"""
new = """    build.compile(\"display_wl\");\n\n    for link_path in &wayland_client.link_paths {\n        println!(\"cargo:rustc-link-search=native={}\", link_path.display());\n    }\n    for lib in &wayland_client.libs {\n        println!(\"cargo:rustc-link-lib=dylib={lib}\");\n    }\n}\n"""
if old not in text:
    raise SystemExit("failed to patch gpu_display/build.rs (link epilogue)")
text = text.replace(old, new, 1)
path.write_text(text)
PY

%cargo_prep

%generate_buildrequires
%cargo_generate_buildrequires -n -f %{crosvm_features}

%build
%cargo_build -n -f %{crosvm_features}

%install
%cargo_install

install -d %{buildroot}%{_datadir}/policy/crosvm
find jail/seccomp/x86_64 -maxdepth 1 -type f \
    \( -name '*.policy' -o -name '*.frequency' \) \
    -exec install -pm0644 -t %{buildroot}%{_datadir}/policy/crosvm {} +

%files
%license LICENSE
%doc ARCHITECTURE.md
%doc CONTRIBUTING.md
%doc README.chromeos.md
%doc README.md
%{_bindir}/crosvm

%files policy
%dir %{_datadir}/crosvm
%dir %{_datadir}/crosvm/policy
%{_datadir}/crosvm/policy/*.policy
%{_datadir}/crosvm/policy/*.frequency

%changelog
* Fri Apr 10 2026 Fxzxmicah <48860358+fxzxmicah@users.noreply.github.com> - 0^git20260410-1
- Package crosvm snapshot %{shortcommit} for x86_64
