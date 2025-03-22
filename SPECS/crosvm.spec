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
BuildRequires:  crate(proc-macro2/default)
BuildRequires:  crate(unicode-ident/default)
BuildRequires:  crate(autocfg/default)
BuildRequires:  crate(thiserror/default)
BuildRequires:  crate(cfg-if/default)
BuildRequires:  crate(serde/default)
BuildRequires:  crate(libc/default)
BuildRequires:  crate(getrandom/default)
BuildRequires:  crate(quote/default)
BuildRequires:  crate(syn/default)
BuildRequires:  crate(memchr/default)
BuildRequires:  crate(anyhow/default)
BuildRequires:  crate(zerocopy/default)
BuildRequires:  crate(slab/default)
BuildRequires:  crate(futures-sink/default)
BuildRequires:  crate(futures-core/default)
BuildRequires:  crate(futures-channel/default)
BuildRequires:  crate(num-traits/default)
BuildRequires:  crate(futures-task/default)
BuildRequires:  crate(futures-io/default)
BuildRequires:  crate(pin-utils/default)
BuildRequires:  crate(pin-project-lite/default)
BuildRequires:  crate(log/default)
BuildRequires:  crate(serde_json/default)
BuildRequires:  crate(itoa/default)
BuildRequires:  crate(ryu/default)
BuildRequires:  crate(env_logger/default)
BuildRequires:  crate(smallvec/default)
BuildRequires:  crate(bitflags/default)
BuildRequires:  crate(rustix/default)
BuildRequires:  crate(either/default)
BuildRequires:  crate(aho-corasick/default)
BuildRequires:  crate(regex-syntax/default)
BuildRequires:  crate(linux-raw-sys/default)
BuildRequires:  crate(regex-automata/default)
BuildRequires:  crate(home/default)
BuildRequires:  crate(which/default)
BuildRequires:  crate(regex/default)
BuildRequires:  crate(glob/default)
BuildRequires:  crate(pkg-config/default)
BuildRequires:  crate(clang-sys/default)
BuildRequires:  crate(shlex/default)
BuildRequires:  crate(minimal-lexical/default)
BuildRequires:  crate(nom/default)
BuildRequires:  crate(libloading/default)
BuildRequires:  crate(memoffset/default)
BuildRequires:  crate(crossbeam-utils/default)
BuildRequires:  crate(cexpr/default)
BuildRequires:  crate(lazy_static/default)
BuildRequires:  crate(once_cell/default)
BuildRequires:  crate(static_assertions/default)
BuildRequires:  crate(rustc-hash/default)
BuildRequires:  crate(rust-fuzzy-search/default)
BuildRequires:  crate(lazycell/default)
BuildRequires:  crate(peeking_take_while/default)
BuildRequires:  crate(thiserror-impl/default)
BuildRequires:  crate(serde_derive/default)
BuildRequires:  crate(zerocopy-derive/default)
BuildRequires:  crate(remain/default)
BuildRequires:  crate(futures-macro/default)
BuildRequires:  crate(async-trait/default)
BuildRequires:  crate(futures-util/default)
BuildRequires:  crate(futures-executor/default)
BuildRequires:  crate(futures/default)
BuildRequires:  crate(uuid/default)
BuildRequires:  crate(chrono/default)
BuildRequires:  crate(argh_shared/default)
BuildRequires:  crate(paste/default)
BuildRequires:  crate(half/default)
BuildRequires:  crate(ciborium-io/default)
BuildRequires:  crate(ciborium-ll/default)
BuildRequires:  crate(intrusive-collections/default)
BuildRequires:  crate(async-task/default)
BuildRequires:  crate(argh_derive/default)
BuildRequires:  crate(bindgen/default)
BuildRequires:  crate(zeroize/default)
BuildRequires:  crate(protobuf/default)
BuildRequires:  crate(crossbeam-epoch/default)
BuildRequires:  crate(ciborium/default)
BuildRequires:  crate(twox-hash/default)
BuildRequires:  crate(cc/default)
BuildRequires:  crate(lock_api/default)
BuildRequires:  crate(rayon-core/default)
BuildRequires:  crate(parking_lot_core/default)
BuildRequires:  crate(argh/default)
BuildRequires:  crate(lz4_flex/default)
BuildRequires:  crate(crossbeam-deque/default)
BuildRequires:  crate(scopeguard/default)
BuildRequires:  crate(protobuf-support/default)
BuildRequires:  crate(enumn/default)
BuildRequires:  crate(hashbrown/default)
BuildRequires:  crate(equivalent/default)
BuildRequires:  crate(fastrand/default)
BuildRequires:  crate(tempfile/default)
BuildRequires:  crate(indexmap/default)
BuildRequires:  crate(rayon/default)
BuildRequires:  crate(parking_lot/default)
BuildRequires:  crate(cfg_aliases/default)
BuildRequires:  crate(nix/default)
BuildRequires:  crate(protobuf-parse/default)
BuildRequires:  crate(named-lock/default)
BuildRequires:  crate(version_check/default)
BuildRequires:  crate(protobuf-codegen/default)
BuildRequires:  crate(userfaultfd-sys/default)
BuildRequires:  crate(userfaultfd/default)
BuildRequires:  crate(cros-libva/default)
BuildRequires:  crate(num_cpus/default)
BuildRequires:  crate(downcast-rs/default)
BuildRequires:  crate(fnv/default)
BuildRequires:  crate(rand_core/default)
BuildRequires:  crate(proc-macro-error-attr/default)
BuildRequires:  crate(ppv-lite86/default)
BuildRequires:  crate(rand_chacha/default)
BuildRequires:  crate(proc-macro-error/default)
BuildRequires:  crate(p9_wire_format_derive/default)
BuildRequires:  crate(crc32fast/default)
BuildRequires:  crate(bitreader/default)
BuildRequires:  crate(byteorder/default)
BuildRequires:  crate(bytes/default)
BuildRequires:  crate(p9/default)
BuildRequires:  crate(cros-codecs/default)
BuildRequires:  crate(rand/default)
BuildRequires:  crate(merge_derive/default)
BuildRequires:  crate(merge/default)

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
