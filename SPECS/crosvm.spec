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
import re

ANDROID_DEPS_HEADER = "[target.'cfg(target_os = \"android\")'.dependencies]"
DEPENDENCIES_HEADER = "[dependencies]"
FEATURES_HEADER = "[features]"
WORKSPACE_HEADER = "[workspace]"
TARGET_ANDROID_LINUX_DEPS = (
    "[target.'cfg(any(target_os = \"android\", target_os = \"linux\"))'.dependencies]"
)
TARGET_AARCH64_DEPS = "[target.'cfg(target_arch = \"aarch64\")'.dependencies]"
TARGET_RISCV64_DEPS = "[target.'cfg(target_arch = \"riscv64\")'.dependencies]"
DEPENDENCY_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*=")
FEATURE_REF_RE = re.compile(r'"([^"]+)"')

DROP_WORKSPACE_MEMBERS = {
    '"crosvm_control",',
    '"e2e_tests",',
    '"fuzz",',
}


def cargo_toml_files(root: Path) -> list[Path]:
    manifests = []
    for path in root.rglob("Cargo.toml"):
        if "target" in path.parts:
            continue
        manifests.append(path)
    return sorted(manifests)


def parse_feature_dependency_refs(text: str):
    refs = set()
    section = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            continue
        if section != FEATURES_HEADER or "=" not in stripped:
            continue
        _, rhs = stripped.split("=", 1)
        for item in FEATURE_REF_RE.findall(rhs):
            ref = item
            if ref.startswith("dep:"):
                ref = ref[4:]
            if "/" in ref:
                ref = ref.split("/", 1)[0]
            if ref:
                refs.add(ref)

    return refs


def strip_windows_target_blocks(text: str, *, feature_refs):
    lines = text.splitlines()
    out = []
    i = 0
    moved_deps = []
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("[target.'cfg(windows)'."):
            i += 1
            while i < len(lines) and not lines[i].startswith("["):
                entry = lines[i].strip()
                match = DEPENDENCY_NAME_RE.match(entry)
                if match and match.group(1) in feature_refs:
                    moved_deps.append(entry)
                i += 1
            while out and out[-1] == "":
                out.pop()
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out) + "\n", moved_deps


def strip_target_block(text: str, header: str, *, feature_refs=None):
    lines = text.splitlines()
    out = []
    i = 0
    moved_deps = []
    while i < len(lines):
        if lines[i].strip() == header:
            i += 1
            while i < len(lines) and not lines[i].startswith("["):
                stripped = lines[i].strip()
                if feature_refs is not None:
                    match = DEPENDENCY_NAME_RE.match(stripped)
                    if match and match.group(1) in feature_refs:
                        moved_deps.append(stripped)
                i += 1
            while out and out[-1] == "":
                out.pop()
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out) + "\n", moved_deps


def ensure_dependencies(text: str, dependency_lines) -> str:
    if not dependency_lines:
        return text

    lines = text.splitlines()
    out = []
    inserted = False
    in_dependencies = False
    existing = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_dependencies = stripped == DEPENDENCIES_HEADER
            continue
        if in_dependencies:
            match = DEPENDENCY_NAME_RE.match(stripped)
            if match:
                existing.add(match.group(1))

    to_insert = []
    for dep_line in dependency_lines:
        match = DEPENDENCY_NAME_RE.match(dep_line)
        if match and match.group(1) not in existing:
            to_insert.append(dep_line)

    if not to_insert:
        return text

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_dependencies and not inserted:
                out.extend(to_insert)
                inserted = True
            in_dependencies = stripped == DEPENDENCIES_HEADER
            out.append(line)
            continue
        out.append(line)

    if in_dependencies and not inserted:
        out.extend(to_insert)

    return "\n".join(out) + "\n"


def rewrite_workspace_members(lines):
    out = []
    section = None
    in_members = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            in_members = False
            out.append(line)
            continue
        if section == WORKSPACE_HEADER and stripped == "members = [":
            in_members = True
            out.append(line)
            continue
        if in_members:
            if stripped == "]":
                in_members = False
                out.append(line)
                continue
            if stripped in DROP_WORKSPACE_MEMBERS:
                continue
        out.append(line)
    return out

def rewrite_root_manifest(path: Path) -> bool:
    original = path.read_text()
    feature_refs = parse_feature_dependency_refs(original)
    text, moved_deps = strip_windows_target_blocks(original, feature_refs=feature_refs)
    text = ensure_dependencies(text, moved_deps)
    text, _ = strip_target_block(text, TARGET_AARCH64_DEPS)
    text, _ = strip_target_block(text, TARGET_RISCV64_DEPS)
    text = "\n".join(rewrite_workspace_members(text.splitlines())) + "\n"
    out = []
    section = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            out.append(line)
            continue

        if section == FEATURES_HEADER:
            if stripped in {'"aarch64/gdb",', '"riscv64/gdb",'}:
                continue
            if stripped == 'swap = ["aarch64/swap", "arch/swap", "devices/swap", "vm_control/swap", "x86_64/swap", "swap/enable"]':
                out.append('swap = ["arch/swap", "devices/swap", "vm_control/swap", "x86_64/swap", "swap/enable"]')
                continue
            if stripped == 'libaaudio_stub = ["android_audio/libaaudio_stub"]':
                out.append('libaaudio_stub = []')
                continue

        if section == TARGET_ANDROID_LINUX_DEPS and stripped == "android_audio = { workspace = true }":
            continue

        out.append(line)

    text = "\n".join(out) + "\n"
    if text != original:
        path.write_text(text)
        return True
    return False


def rewrite_devices_manifest(path: Path) -> bool:
    original = path.read_text()
    feature_refs = parse_feature_dependency_refs(original)
    text, moved_deps = strip_windows_target_blocks(original, feature_refs=feature_refs)
    text = ensure_dependencies(text, moved_deps)

    lines = text.splitlines()
    out = []
    section = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
            out.append(line)
            continue
        if section == TARGET_ANDROID_LINUX_DEPS and stripped == "android_audio = { workspace = true }":
            continue
        out.append(line)

    text = "\n".join(out) + "\n"
    if text != original:
        path.write_text(text)
        return True
    return False


def rewrite_generic_manifest(path: Path) -> bool:
    original = path.read_text()
    feature_refs = parse_feature_dependency_refs(original)
    text, moved_deps = strip_windows_target_blocks(original, feature_refs=feature_refs)
    text = ensure_dependencies(text, moved_deps)
    text, _ = strip_target_block(text, ANDROID_DEPS_HEADER)
    if text != original:
        path.write_text(text)
        return True
    return False


root = Path(".")
for manifest in cargo_toml_files(root):
    if manifest == root / "Cargo.toml":
        rewrite_root_manifest(manifest)
    elif manifest == root / "devices" / "Cargo.toml":
        rewrite_devices_manifest(manifest)
    else:
        rewrite_generic_manifest(manifest)
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
