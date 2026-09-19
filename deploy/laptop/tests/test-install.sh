#!/bin/bash
# End-to-end test of install-thermal-guard.sh against a throwaway SYSROOT, with
# systemctl stubbed.  The point is to prove the interlock drop-ins land, and in
# a form systemd will actually accept, BEFORE this runs on a box that powers
# itself off when it gets it wrong.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$HERE/.." && pwd)"

pass=0; fail=0
ok()  { pass=$((pass+1)); printf 'ok   %s\n' "$1"; }
bad() { fail=$((fail+1)); printf 'FAIL %s\n     %s\n' "$1" "${2:-}"; }

T=$(mktemp -d)
mkdir -p "$T/bin" "$T/root" "$T/stage/tests"
cat > "$T/bin/systemctl" <<'STUB'
#!/bin/bash
printf '%s\n' "$*" >> "$T/systemctl.log"
STUB
chmod +x "$T/bin/systemctl"
: > "$T/systemctl.log"

cp "$SRC/erdos-thermal-guard" "$SRC/erdos-thermal-guard.service" "$SRC/install-thermal-guard.sh" "$T/stage/"
cp "$HERE/test-thermal-guard.sh" "$T/stage/tests/"
chmod +x "$T/stage/erdos-thermal-guard" "$T/stage/install-thermal-guard.sh"

out=$(cd "$T/stage" && PATH="$T/bin:$PATH" T="$T" SYSROOT="$T/root" \
      GUARD_LOG_PATH="$T/nonexistent.log" bash install-thermal-guard.sh 2>&1)
rc=$?

if [ "$rc" -eq 0 ]; then ok "installer exits 0 on a clean install"
else bad "installer exits 0 on a clean install" "rc=$rc
$out"; fi

if printf '%s' "$out" | grep -q 'passed, 0 failed'; then ok "installer ran the guard self-test and it passed"
else bad "installer ran the guard self-test and it passed" "$out"; fi

[ -x "$T/root/usr/local/sbin/erdos-thermal-guard" ] \
  && ok "guard binary installed executable" \
  || bad "guard binary installed executable" "$(ls -l "$T/root/usr/local/sbin" 2>&1)"

[ -f "$T/root/etc/systemd/system/erdos-thermal-guard.service" ] \
  && ok "guard unit installed" || bad "guard unit installed" ""

for unit in erdos-descent erdos-laptop-chain; do
  f="$T/root/etc/systemd/system/${unit}.service.d/thermal.conf"
  if grep -q '^Requires=erdos-thermal-guard.service' "$f" 2>/dev/null \
     && grep -q '^After=erdos-thermal-guard.service' "$f" 2>/dev/null; then
    ok "$unit is interlocked with the guard"
  else
    bad "$unit is interlocked with the guard" "$(cat "$f" 2>&1)"
  fi
done

# The CPU trim has to be under a [Service] header, not swallowed by [Unit].
f="$T/root/etc/systemd/system/erdos-descent.service.d/thermal.conf"
if awk '/^\[Service\]/{s=1} s&&/^CPUQuota=200%/{found=1} END{exit !found}' "$f"; then
  ok "descent CPUQuota=200% sits under [Service]"
else
  bad "descent CPUQuota=200% sits under [Service]" "$(cat "$f" 2>&1)"
fi
# ...and CPUQuota must not appear before [Service], which systemd would reject.
if awk '/^CPUQuota=/{if(!s) bad=1} /^\[Service\]/{s=1} END{exit bad?1:0}' "$f"; then
  ok "no directive lands in the wrong section"
else
  bad "no directive lands in the wrong section" "$(cat "$f" 2>&1)"
fi

grep -q 'enable --now erdos-thermal-guard.service' "$T/systemctl.log" \
  && ok "guard is enabled and started" || bad "guard is enabled and started" "$(cat "$T/systemctl.log")"
grep -q 'daemon-reload' "$T/systemctl.log" \
  && ok "systemd is reloaded before the units are touched" || bad "systemd is reloaded" ""

# Re-running must not double up the drop-in: the appended [Service] block would
# otherwise accumulate every time the catcher fires.
before=$(grep -c 'CPUQuota=200%' "$f")
(cd "$T/stage" && PATH="$T/bin:$PATH" T="$T" SYSROOT="$T/root" \
   GUARD_LOG_PATH="$T/nonexistent.log" bash install-thermal-guard.sh >/dev/null 2>&1)
after=$(grep -c 'CPUQuota=200%' "$f")
if [ "$before" = "1" ] && [ "$after" = "1" ]; then ok "re-running the installer is idempotent"
else bad "re-running the installer is idempotent" "CPUQuota lines before=$before after=$after
$(cat "$f")"; fi

rm -rf "$T"
printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
