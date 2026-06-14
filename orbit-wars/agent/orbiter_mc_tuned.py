# self-contained: greedy reference policy embedded in an isolated module
import base64 as _b64, types as _types
_orb = _types.ModuleType("_orb_ref_fast")
exec(compile(_b64.b64decode(
    "IiIiCk9yYml0ZXIg4oCUIE9yYml0IFdhcnMgYWdlbnQgKGhldXJpc3RpYyBjb3JlLCBwYXJhbWV0ZXJpc2VkIGZvciBDTUEtRVMgdHVuaW5nKS4KCkRlc2lnbiBmb2xsb3dzIHRoZSBlbmdpbmUgcmVhZGluZyAoa2FnZ2xlX2Vudmlyb25tZW50cy9lbnZzL29yYml0X3dhcnMvb3JiaXRfd2Fycy5weSk6CgogICogTmV1dHJhbCBwbGFuZXRzIChvd25lciA9PSAtMSkgZG8gTk9UIHByb2R1Y2U7IG93bmVkL2VuZW15IHBsYW5ldHMgZ3JvdyBieQogICAgYHByb2R1Y3Rpb25gIGV2ZXJ5IHR1cm4uICA9PiBjYXB0dXJlLWNvc3QgZm9yIGEgbmV1dHJhbCBpcyBmaXhlZCwgZm9yIGFuIGVuZW15CiAgICBpdCBncm93cyB3aXRoIHRyYXZlbCB0aW1lLCBzbyB3ZSBzaXplIGZsZWV0cyBhZ2FpbnN0IHRoZSBnYXJyaXNvbiBBVCBBUlJJVkFMLgogICogT3JiaXQgaXMgZGV0ZXJtaW5pc3RpYzogYSBwbGFuZXQncyBmdXR1cmUgYW5nbGUgPSBjdXJyZW50X2FuZ2xlICsgYXYqZHQsIHdoZXJlCiAgICBjdXJyZW50X2FuZ2xlIGlzIHJlYWQgc3RyYWlnaHQgb2ZmIHRoZSBsaXZlICh4LHkpLiAgV2UgbGVhZCBtb3ZpbmcgdGFyZ2V0cwogICAgKGludGVyY2VwdGlvbikgaW5zdGVhZCBvZiBhaW1pbmcgYXQgdGhlIHN0YWxlIHBvc2l0aW9uICh3aGF0IHJhbmRvbS9zdGFydGVyIGRvKS4KICAqIEZsZWV0IHNwZWVkIHNjYWxlcyB3aXRoIHNpemU6IHYobikgPSAxICsgKG1heFMtMSkqKGxvZyhuKS9sb2coMTAwMCkpXjEuNSwgY2FwcGVkCiAgICBhdCBtYXhTIChkZWZhdWx0IDYpLiBuPTEgLT4gdj0xIChzbG93KS4gPT4gY29uY2VudHJhdGUgZm9yY2UsIGRvbid0IGRyaWJibGUuCiAgKiBDb2xsaXNpb24gaXMgY29udGludW91cyAoc3dlcHQpOiBhIGZsZWV0IHRoYXQgZ3JhemVzIHRoZSBzdW4gb3IgYW4gdW5pbnRlbmRlZAogICAgcGxhbmV0IGlzIGNvbnN1bWVkIC8gZmlnaHRzIHRoZXJlLiAgV2Uga2VlcCBsYXVuY2ggbGluZXMgY2xlYXIgb2YgdGhlIHN1biBhbmQKICAgIG9mIG5vbi10YXJnZXQgcGxhbmV0cy4KICAqIENvbWJhdDogYXR0YWNrZXJzIGdyb3VwZWQgcGVyIG93bmVyICYgc3VtbWVkOyBjYXB0dXJlIGlmZiBzdXJ2aXZpbmcgYXR0YWNrZXJzCiAgICBTVFJJQ1RMWSBleGNlZWQgZ2Fycmlzb24uICBFbGltaW5hdGluZyBldmVyeSBvcHBvbmVudCBlbmRzIHRoZSBnYW1lIGFzIGEgd2luLgoKVGhlIHdob2xlIHBvbGljeSBpcyB3cmFwcGVkIGluIHRyeS9leGNlcHQg4oCUIGFuIHVuaGFuZGxlZCBleGNlcHRpb24gaXMgYW4gaW5zdGFudAplcGlzb2RlIGxvc3MsIHNvIGFueSBmYWlsdXJlIGRlZ3JhZGVzIHRvICJkbyBub3RoaW5nIHRoaXMgdHVybiIuCgpgUEFSQU1TYCBpcyB0aGUgdHVuYWJsZSB3ZWlnaHQgdmVjdG9yIChDTUEtRVMgZXZvbHZlcyBpdCB2aWEgdGhlIHNlbGYtcGxheSBsZWFndWUpLgpGb3Igc3VibWlzc2lvbiwgdGhlIGRlZmF1bHRzIGJlbG93IGFyZSBiYWtlZCBpbi4KIiIiCgppbXBvcnQgbWF0aAoKQk9BUkQgPSAxMDAuMApDRU5URVIgPSA1MC4wClNVTl9SID0gMTAuMApST1RfTElNSVQgPSA1MC4wCk1BWF9TUEVFRF9ERUZBVUxUID0gNi4wCgpQQVJBTVMgPSB7CiAgICAicmVzZXJ2ZV9mcmFjIjogMC4zMCwgICAgICAgICMga2VlcCB0aGlzIGZyYWN0aW9uIG9mIGEgcGxhbmV0J3Mgc2hpcHMgaG9tZQogICAgInJlc2VydmVfbWluIjogMy4wLCAgICAgICAgICAjIGFic29sdXRlIGZsb29yIG9uIHRoZSBrZXB0IHJlc2VydmUKICAgICJjYXB0dXJlX21hcmdpbiI6IDIuMCwgICAgICAgIyBleHRyYSBzaGlwcyBiZXlvbmQgdGhlIHN0cmljdCByZXF1aXJlbWVudCAoYWJzKQogICAgImNhcHR1cmVfbWFyZ2luX2ZyYWMiOiAwLjA4LCAjIGV4dHJhIHNoaXBzIGFzIGEgZnJhY3Rpb24gb2YgcmVxdWlyZW1lbnQKICAgICJwcm9kX3dlaWdodCI6IDEuNCwgICAgICAgICAgIyB2YWx1ZSBleHBvbmVudCBvbiBwcm9kdWN0aW9uCiAgICAiZGlzdF93ZWlnaHQiOiAwLjksICAgICAgICAgICMgRVRBIHBlbmFsdHkgaW4gdGhlIHZhbHVlIGRlbm9taW5hdG9yCiAgICAiY29zdF93ZWlnaHQiOiAxLjAsICAgICAgICAgICMgc2hpcC1jb3N0IHBlbmFsdHkgaW4gdGhlIHZhbHVlIGRlbm9taW5hdG9yCiAgICAiZW5lbXlfYm9udXMiOiAxLjM1LCAgICAgICAgICMgbXVsdGlwbGllciBvbiBlbmVteS1vd25lZCB0YXJnZXQgdmFsdWUgKGRlbmlhbCkKICAgICJjb21ldF9wZW5hbHR5IjogMC40NSwgICAgICAgIyBtdWx0aXBsaWVyIG9uIGNvbWV0IHRhcmdldCB2YWx1ZSAodGhleSB2YW5pc2gpCiAgICAibmV1dHJhbF9iaWFzIjogMS4wLCAgICAgICAgICMgbXVsdGlwbGllciBvbiBuZXV0cmFsIHRhcmdldCB2YWx1ZQogICAgIm1heF9sYXVuY2hlcyI6IDYsICAgICAgICAgICAjIGxhdW5jaGVzIHBlciB0dXJuIGNhcCAoc3BlZWQgKyBmb2N1cykKICAgICJtaW5fZmxlZXQiOiAyLCAgICAgICAgICAgICAgIyBuZXZlciBzZW5kIGEgc21hbGxlciBmbGVldCB0aGFuIHRoaXMKICAgICJlbmRnYW1lX3R1cm4iOiA0NzgsICAgICAgICAgIyBhZnRlciB0aGlzLCBvbmx5IHN1cmUgY2FwdHVyZXMgLyByZWluZm9yY2VtZW50CiAgICAic3VuX21hcmdpbiI6IDEuNSwgICAgICAgICAgICMgZXh0cmEgY2xlYXJhbmNlIGJleW9uZCBzdW4gcmFkaXVzCiAgICAiZ3JhemVfbWFyZ2luIjogMC44LCAgICAgICAgICMgZXh0cmEgY2xlYXJhbmNlIHBhc3QgYSBub24tdGFyZ2V0IHBsYW5ldCByYWRpdXMKICAgICJpbnRlcmNlcHRfaXRlcnMiOiA1LCAgICAgICAgIyBmaXhlZC1wb2ludCBpdGVyYXRpb25zIGZvciB0aGUgaW50ZXJjZXB0IHNvbHZlCiAgICAiZGVmZW5zZV90b2wiOiAwLjMwLCAgICAgICAgICMgaGVhZGluZyB0b2xlcmFuY2UgKHJhZCkgZm9yICJmbGVldCBhaW1lZCBhdCB1cyIKICAgICJ0aHJlYXRfcmVzZXJ2ZSI6IDEuMTAsICAgICAgIyBob2xkIGdhcnJpc29uICogdGhpcyB3aGVuIGEgcGxhbmV0IGlzIHRocmVhdGVuZWQKICAgICJtYXhfZXRhIjogMjIwLjAsICAgICAgICAgICAgIyBpZ25vcmUgdGFyZ2V0cyBmYXJ0aGVyIHRoYW4gdGhpcyBtYW55IHRpY2tzCn0KCgpkZWYgX2Rpc3QoYXgsIGF5LCBieCwgYnkpOgogICAgcmV0dXJuIG1hdGguaHlwb3QoYXggLSBieCwgYXkgLSBieSkKCgpkZWYgX3NlZ19wb2ludF9kaXN0KHB4LCBweSwgYXgsIGF5LCBieCwgYnkpOgogICAgbDIgPSAoYXggLSBieCkgKiogMiArIChheSAtIGJ5KSAqKiAyCiAgICBpZiBsMiA9PSAwLjA6CiAgICAgICAgcmV0dXJuIF9kaXN0KHB4LCBweSwgYXgsIGF5KQogICAgdCA9ICgocHggLSBheCkgKiAoYnggLSBheCkgKyAocHkgLSBheSkgKiAoYnkgLSBheSkpIC8gbDIKICAgIHQgPSBtYXgoMC4wLCBtaW4oMS4wLCB0KSkKICAgIHJldHVybiBfZGlzdChweCwgcHksIGF4ICsgdCAqIChieCAtIGF4KSwgYXkgKyB0ICogKGJ5IC0gYXkpKQoKCmRlZiBfZmxlZXRfc3BlZWQobiwgbWF4X3NwZWVkKToKICAgIGlmIG4gPD0gMToKICAgICAgICByZXR1cm4gMS4wCiAgICB2ID0gMS4wICsgKG1heF9zcGVlZCAtIDEuMCkgKiAobWF0aC5sb2cobikgLyBtYXRoLmxvZygxMDAwLjApKSAqKiAxLjUKICAgIHJldHVybiBtaW4odiwgbWF4X3NwZWVkKQoKCmRlZiBfaXNfb3JiaXRpbmcocHgsIHB5LCByYWRpdXMpOgogICAgcmV0dXJuIF9kaXN0KHB4LCBweSwgQ0VOVEVSLCBDRU5URVIpICsgcmFkaXVzIDwgUk9UX0xJTUlUCgoKZGVmIF9mdXR1cmVfcG9zKHAsIGR0LCBhdik6CiAgICAiIiJQb3NpdGlvbiBvZiBwbGFuZXQgdHVwbGUgcCA9IFtpZCxvd25lcix4LHkscixzaGlwcyxwcm9kXSBhZnRlciBkdCB0aWNrcy4iIiIKICAgIHgsIHksIHIgPSBwWzJdLCBwWzNdLCBwWzRdCiAgICBpZiBhdiA9PSAwIG9yIG5vdCBfaXNfb3JiaXRpbmcoeCwgeSwgcik6CiAgICAgICAgcmV0dXJuIHgsIHkKICAgIG9yYiA9IF9kaXN0KHgsIHksIENFTlRFUiwgQ0VOVEVSKQogICAgYW5nID0gbWF0aC5hdGFuMih5IC0gQ0VOVEVSLCB4IC0gQ0VOVEVSKSArIGF2ICogZHQKICAgIHJldHVybiBDRU5URVIgKyBvcmIgKiBtYXRoLmNvcyhhbmcpLCBDRU5URVIgKyBvcmIgKiBtYXRoLnNpbihhbmcpCgoKZGVmIF9pbnRlcmNlcHQoc3gsIHN5LCBzcmNfciwgdGFyZ2V0LCBhdiwgbWF4X3NwZWVkLCBzaGlwc19ndWVzcywgaXRlcnMpOgogICAgIiIiU29sdmUgbGF1bmNoIGFuZ2xlICsgRVRBICsgYXJyaXZhbCBwb3MgZm9yIGEgZmxlZXQgb2YgfnNoaXBzX2d1ZXNzIHNoaXBzCiAgICBsZWF2aW5nIChzeCxzeSkgdG93YXJkIGB0YXJnZXRgLiBSZXR1cm5zIChhbmdsZSwgZXRhLCBheCwgYXkpLiIiIgogICAgdiA9IF9mbGVldF9zcGVlZChzaGlwc19ndWVzcywgbWF4X3NwZWVkKQogICAgYXgsIGF5ID0gdGFyZ2V0WzJdLCB0YXJnZXRbM10KICAgIGV0YSA9IDAuMAogICAgZm9yIF8gaW4gcmFuZ2UoaXRlcnMpOgogICAgICAgIGQgPSBfZGlzdChzeCwgc3ksIGF4LCBheSkgLSBzcmNfciAtIDAuMQogICAgICAgIGQgPSBtYXgoZCwgMC4wKQogICAgICAgIGV0YSA9IGQgLyB2IGlmIHYgPiAwIGVsc2UgMC4wCiAgICAgICAgYXgsIGF5ID0gX2Z1dHVyZV9wb3ModGFyZ2V0LCBldGEsIGF2KQogICAgYW5nbGUgPSBtYXRoLmF0YW4yKGF5IC0gc3ksIGF4IC0gc3gpCiAgICByZXR1cm4gYW5nbGUsIGV0YSwgYXgsIGF5CgoKZGVmIF9zZWdfY2xvc2VzdF90KHB4LCBweSwgYXgsIGF5LCBieCwgYnkpOgogICAgbDIgPSAoYXggLSBieCkgKiogMiArIChheSAtIGJ5KSAqKiAyCiAgICBpZiBsMiA9PSAwLjA6CiAgICAgICAgcmV0dXJuIDAuMAogICAgdCA9ICgocHggLSBheCkgKiAoYnggLSBheCkgKyAocHkgLSBheSkgKiAoYnkgLSBheSkpIC8gbDIKICAgIHJldHVybiBtYXgoMC4wLCBtaW4oMS4wLCB0KSkKCgpkZWYgX3BhdGhfY2xlYXIoc3gsIHN5LCBheCwgYXksIHNyY19pZCwgdGFyZ2V0X2lkLCBwbGFuZXRzLCBzdW5fbWFyZ2luLCBncmF6ZV9tYXJnaW4pOgogICAgIyBzdW4gY3Jvc3Npbmcga2lsbHMgdGhlIGZsZWV0CiAgICBpZiBfc2VnX3BvaW50X2Rpc3QoQ0VOVEVSLCBDRU5URVIsIHN4LCBzeSwgYXgsIGF5KSA8IFNVTl9SICsgc3VuX21hcmdpbjoKICAgICAgICByZXR1cm4gRmFsc2UKICAgICMgYW4gVU5JTlRFTkRFRCBwbGFuZXQgc2l0dGluZyBpbiB0aGUgbWlkZGxlIG9mIHRoZSBwYXRoIGRpdmVydHMgdGhlIGZsZWV0LgogICAgIyBTa2lwIHRoZSBzb3VyY2UgJiB0YXJnZXQsIGFuZCBpZ25vcmUgcGxhbmV0cyB3aG9zZSBjbG9zZXN0IGFwcHJvYWNoIGlzIGF0CiAgICAjIHRoZSBlbmRwb2ludHMgKHRoZXkgYXJlIG5vdCBlbi1yb3V0ZSBvYnN0YWNsZXMpLgogICAgZm9yIHAgaW4gcGxhbmV0czoKICAgICAgICBpZiBwWzBdID09IHNyY19pZCBvciBwWzBdID09IHRhcmdldF9pZDoKICAgICAgICAgICAgY29udGludWUKICAgICAgICB0ID0gX3NlZ19jbG9zZXN0X3QocFsyXSwgcFszXSwgc3gsIHN5LCBheCwgYXkpCiAgICAgICAgaWYgdCA8PSAwLjAyIG9yIHQgPj0gMC45OToKICAgICAgICAgICAgY29udGludWUKICAgICAgICBjeCA9IHN4ICsgdCAqIChheCAtIHN4KQogICAgICAgIGN5ID0gc3kgKyB0ICogKGF5IC0gc3kpCiAgICAgICAgaWYgX2Rpc3QocFsyXSwgcFszXSwgY3gsIGN5KSA8IHBbNF0gKyBncmF6ZV9tYXJnaW46CiAgICAgICAgICAgIHJldHVybiBGYWxzZQogICAgcmV0dXJuIFRydWUKCgpkZWYgbWFrZV9hZ2VudChwYXJhbXM9Tm9uZSk6CiAgICBQID0gZGljdChQQVJBTVMpCiAgICBpZiBwYXJhbXM6CiAgICAgICAgUC51cGRhdGUocGFyYW1zKQoKICAgIGRlZiBhZ2VudChvYnMsIGNvbmZpZz1Ob25lKToKICAgICAgICB0cnk6CiAgICAgICAgICAgIHJldHVybiBfZGVjaWRlKG9icywgY29uZmlnLCBQKQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb246CiAgICAgICAgICAgIHJldHVybiBbXQoKICAgIHJldHVybiBhZ2VudAoKCmRlZiBfZGVjaWRlKG9icywgY29uZmlnLCBQKToKICAgIGlmIGlzaW5zdGFuY2Uob2JzLCBkaWN0KToKICAgICAgICBnID0gb2JzLmdldAogICAgZWxzZToKICAgICAgICBnID0gbGFtYmRhIGssIGQ9Tm9uZTogZ2V0YXR0cihvYnMsIGssIGQpCgogICAgbWUgPSBnKCJwbGF5ZXIiLCAwKQogICAgcmF3X3BsYW5ldHMgPSBnKCJwbGFuZXRzIiwgW10pIG9yIFtdCiAgICByYXdfZmxlZXRzID0gZygiZmxlZXRzIiwgW10pIG9yIFtdCiAgICBhdiA9IGcoImFuZ3VsYXJfdmVsb2NpdHkiLCAwLjApIG9yIDAuMAogICAgc3RlcCA9IGcoInN0ZXAiLCAwKSBvciAwCiAgICBjb21ldF9pZHMgPSBzZXQoZygiY29tZXRfcGxhbmV0X2lkcyIsIFtdKSBvciBbXSkKICAgIG1heF9zcGVlZCA9IE1BWF9TUEVFRF9ERUZBVUxUCiAgICBpZiBjb25maWcgaXMgbm90IE5vbmU6CiAgICAgICAgY3MgPSBjb25maWcuZ2V0KCJzaGlwU3BlZWQiKSBpZiBpc2luc3RhbmNlKGNvbmZpZywgZGljdCkgZWxzZSBnZXRhdHRyKGNvbmZpZywgInNoaXBTcGVlZCIsIE5vbmUpCiAgICAgICAgaWYgY3M6CiAgICAgICAgICAgIG1heF9zcGVlZCA9IGZsb2F0KGNzKQoKICAgIHBsYW5ldHMgPSBsaXN0KHJhd19wbGFuZXRzKQogICAgbWluZSA9IFtwIGZvciBwIGluIHBsYW5ldHMgaWYgcFsxXSA9PSBtZV0KICAgIGlmIG5vdCBtaW5lOgogICAgICAgIHJldHVybiBbXQogICAgdGFyZ2V0cyA9IFtwIGZvciBwIGluIHBsYW5ldHMgaWYgcFsxXSAhPSBtZV0KICAgIHJlbWFpbmluZyA9IG1heCgxLjAsIDUwMC4wIC0gc3RlcCkKICAgIGVuZGdhbWUgPSBzdGVwID49IFBbImVuZGdhbWVfdHVybiJdCgogICAgIyAtLS0gZGVmZW5zZTogaW5jb21pbmcgZW5lbXkgc2hpcHMgcGVyIG93bmVkIHBsYW5ldCAtLS0tLS0tLS0tLS0tLS0tLS0tCiAgICB0aHJlYXQgPSB7cFswXTogMC4wIGZvciBwIGluIG1pbmV9CiAgICBtaW5lX2J5X2lkID0ge3BbMF06IHAgZm9yIHAgaW4gbWluZX0KICAgIGZvciBmIGluIHJhd19mbGVldHM6CiAgICAgICAgZm8gPSBmWzFdCiAgICAgICAgaWYgZm8gPT0gbWU6CiAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgZngsIGZ5LCBmYW5nLCBmc2hpcHMgPSBmWzJdLCBmWzNdLCBmWzRdLCBmWzZdCiAgICAgICAgZnYgPSBfZmxlZXRfc3BlZWQoZnNoaXBzLCBtYXhfc3BlZWQpCiAgICAgICAgZm9yIHAgaW4gbWluZToKICAgICAgICAgICAgYXgsIGF5ID0gcFsyXSwgcFszXQogICAgICAgICAgICBhbmdfdG8gPSBtYXRoLmF0YW4yKGF5IC0gZnksIGF4IC0gZngpCiAgICAgICAgICAgIGRhbmcgPSBhYnMoKGZhbmcgLSBhbmdfdG8gKyBtYXRoLnBpKSAlICgyICogbWF0aC5waSkgLSBtYXRoLnBpKQogICAgICAgICAgICBpZiBkYW5nIDwgUFsiZGVmZW5zZV90b2wiXToKICAgICAgICAgICAgICAgIHRocmVhdFtwWzBdXSArPSBmc2hpcHMKCiAgICAjIC0tLSBhdmFpbGFibGUgc2hpcHMgcGVyIHNvdXJjZSAoYWZ0ZXIgcmVzZXJ2ZSAvIHRocmVhdCkgLS0tLS0tLS0tLS0tLS0KICAgIGF2YWlsID0ge30KICAgIGZvciBwIGluIG1pbmU6CiAgICAgICAgc2hpcHMgPSBwWzVdCiAgICAgICAgYmFzZV9yZXMgPSBtYXgoUFsicmVzZXJ2ZV9taW4iXSwgUFsicmVzZXJ2ZV9mcmFjIl0gKiBzaGlwcykKICAgICAgICBpZiB0aHJlYXQuZ2V0KHBbMF0sIDAuMCkgPiAwOgogICAgICAgICAgICBiYXNlX3JlcyA9IG1heChiYXNlX3JlcywgUFsidGhyZWF0X3Jlc2VydmUiXSAqIHNoaXBzKQogICAgICAgIGF2YWlsW3BbMF1dID0gbWF4KDAuMCwgc2hpcHMgLSBiYXNlX3JlcykKCiAgICAjIC0tLSBzY29yZSBldmVyeSAodGFyZ2V0KSB3aXRoIGl0cyBiZXN0IGNsZWFyK2FmZm9yZGFibGUgc291cmNlIC0tLS0tLS0KICAgIHBsYW5zID0gW10KICAgIGZvciB0IGluIHRhcmdldHM6CiAgICAgICAgaXNfY29tZXQgPSB0WzBdIGluIGNvbWV0X2lkcwogICAgICAgIGlzX2VuZW15ID0gdFsxXSAhPSAtMQogICAgICAgIGJlc3QgPSBOb25lCiAgICAgICAgZm9yIHMgaW4gbWluZToKICAgICAgICAgICAgaWYgYXZhaWxbc1swXV0gPCBQWyJtaW5fZmxlZXQiXToKICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAgICMgaXRlcmF0ZSBzaGlwLWNvdW50IDwtPiBpbnRlcmNlcHQgKGVuZW15IGdhcnJpc29uIGdyb3dzIGluIHRyYW5zaXQpCiAgICAgICAgICAgIG5lZWQgPSB0WzVdICsgMS4wCiAgICAgICAgICAgIGFuZ2xlID0gZXRhID0gYXggPSBheSA9IDAuMAogICAgICAgICAgICBmb3IgXyBpbiByYW5nZSgzKToKICAgICAgICAgICAgICAgIHNoaXBzX2d1ZXNzID0gbWF4KG5lZWQsIFBbIm1pbl9mbGVldCJdKQogICAgICAgICAgICAgICAgYW5nbGUsIGV0YSwgYXgsIGF5ID0gX2ludGVyY2VwdCgKICAgICAgICAgICAgICAgICAgICBzWzJdLCBzWzNdLCBzWzRdLCB0LCBhdiwgbWF4X3NwZWVkLCBzaGlwc19ndWVzcywgUFsiaW50ZXJjZXB0X2l0ZXJzIl0KICAgICAgICAgICAgICAgICkKICAgICAgICAgICAgICAgIGdhcnJpc29uID0gdFs1XSArICh0WzZdICogZXRhIGlmIGlzX2VuZW15IGVsc2UgMC4wKQogICAgICAgICAgICAgICAgbmVlZCA9IGdhcnJpc29uICsgMS4wCiAgICAgICAgICAgICAgICBuZWVkICs9IFBbImNhcHR1cmVfbWFyZ2luIl0gKyBQWyJjYXB0dXJlX21hcmdpbl9mcmFjIl0gKiBuZWVkCiAgICAgICAgICAgIG5lZWQgPSBtYXRoLmNlaWwobmVlZCkKICAgICAgICAgICAgaWYgZXRhID4gUFsibWF4X2V0YSJdOgogICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgaWYgbmVlZCA+IGF2YWlsW3NbMF1dIG9yIG5lZWQgPiBzWzVdOgogICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgaWYgbm90IF9wYXRoX2NsZWFyKHNbMl0sIHNbM10sIGF4LCBheSwgc1swXSwgdFswXSwgcGxhbmV0cywKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFBbInN1bl9tYXJnaW4iXSwgUFsiZ3JhemVfbWFyZ2luIl0pOgogICAgICAgICAgICAgICAgY29udGludWUKICAgICAgICAgICAgIyB2YWx1ZTogcHJvZHVjdGlvbiBoZWxkIG92ZXIgcmVtYWluaW5nIHRpbWUsIHBlciB1bml0IGNvc3QrZGlzdGFuY2UKICAgICAgICAgICAgaG9sZCA9IG1pbihyZW1haW5pbmcsIDUwMC4wKQogICAgICAgICAgICBiYXNlID0gKHRbNl0gKiogUFsicHJvZF93ZWlnaHQiXSkgKiBob2xkCiAgICAgICAgICAgIGJhc2UgKj0gUFsiZW5lbXlfYm9udXMiXSBpZiBpc19lbmVteSBlbHNlIFBbIm5ldXRyYWxfYmlhcyJdCiAgICAgICAgICAgIGlmIGlzX2NvbWV0OgogICAgICAgICAgICAgICAgYmFzZSAqPSBQWyJjb21ldF9wZW5hbHR5Il0KICAgICAgICAgICAgZGVub20gPSBQWyJjb3N0X3dlaWdodCJdICogbmVlZCArIFBbImRpc3Rfd2VpZ2h0Il0gKiBldGEgKyAxLjAKICAgICAgICAgICAgdmFsID0gYmFzZSAvIGRlbm9tCiAgICAgICAgICAgIGlmIGJlc3QgaXMgTm9uZSBvciB2YWwgPiBiZXN0WzBdOgogICAgICAgICAgICAgICAgYmVzdCA9ICh2YWwsIHMsIG5lZWQsIGFuZ2xlKQogICAgICAgIGlmIGJlc3QgaXMgbm90IE5vbmU6CiAgICAgICAgICAgIHBsYW5zLmFwcGVuZCgoYmVzdFswXSwgdCwgYmVzdFsxXSwgYmVzdFsyXSwgYmVzdFszXSkpCgogICAgcGxhbnMuc29ydChrZXk9bGFtYmRhIHo6IHpbMF0sIHJldmVyc2U9VHJ1ZSkKCiAgICBtb3ZlcyA9IFtdCiAgICBsYXVuY2hlcyA9IDAKICAgIGZvciB2YWwsIHQsIHMsIG5lZWQsIGFuZ2xlIGluIHBsYW5zOgogICAgICAgIGlmIGxhdW5jaGVzID49IFBbIm1heF9sYXVuY2hlcyJdOgogICAgICAgICAgICBicmVhawogICAgICAgIGlmIGVuZGdhbWUgYW5kIHRbMV0gIT0gLTE6CiAgICAgICAgICAgICMgbGF0ZSBnYW1lOiBkb24ndCBwaWNrIGZpZ2h0cywgb25seSBuZXV0cmFscyB0aGF0IGFyZSBzdXJlICYgY2hlYXAKICAgICAgICAgICAgcGFzcwogICAgICAgIGlmIGF2YWlsW3NbMF1dID49IG5lZWQgYW5kIHNbNV0gPj0gbmVlZDoKICAgICAgICAgICAgbiA9IGludChuZWVkKQogICAgICAgICAgICBpZiBuIDwgUFsibWluX2ZsZWV0Il06CiAgICAgICAgICAgICAgICBjb250aW51ZQogICAgICAgICAgICBtb3Zlcy5hcHBlbmQoW3NbMF0sIGFuZ2xlLCBuXSkKICAgICAgICAgICAgYXZhaWxbc1swXV0gLT0gbmVlZAogICAgICAgICAgICBzWzVdIC09IG4KICAgICAgICAgICAgbGF1bmNoZXMgKz0gMQogICAgcmV0dXJuIG1vdmVzCgoKIyBkZWZhdWx0IGFnZW50IGZvciBzdWJtaXNzaW9uIChzaW5nbGUtZmlsZSBtYWluLnB5IGltcG9ydHMgdGhpcyBuYW1lKQphZ2VudCA9IG1ha2VfYWdlbnQoKQo="
).decode(), "_orb_ref_fast", "exec"), _orb.__dict__)
_orbiter_make_agent = _orb.make_agent
# Baked-in CMA-ES tuned params (from artifacts/tuning/BEST_heuristic.json, 832-core run).
# Applied here so ALL greedy-policy uses (candidate gen + rollout ref) run the tuned policy.
_orb.PARAMS.update({
    "reserve_frac":        0.030581131806447184,
    "reserve_min":         0.6149199225996143,
    "capture_margin":      0.3876755548688749,
    "capture_margin_frac": 0.001927340577365945,
    "prod_weight":         1.0468393316064732,
    "dist_weight":         2.9562746203903223,
    "cost_weight":         1.7906005585298337,
    "enemy_bonus":         2.404734313501816,
    "comet_penalty":       0.24760771652574104,
    "neutral_bias":        1.1749349262500572,
    "max_launches":        2,
    "min_fleet":           3,
    "endgame_turn":        461,
    "sun_margin":          4.89880763782912,
    "graze_margin":        2.0934587988801323,
    "defense_tol":         0.2541288908753509,
    "threat_reserve":      0.8867961005564717,
    "max_eta":             285.7703296281106,
})

"""
Orbiter-MC-FAST — forward-model SEARCH agent for Orbit Wars (optimized).

SAME decision logic & PARAMS as bots/orbiter_mc.py, but with a re-engineered
forward model so that, inside the same ~1s/turn budget, we can search MORE
candidates / DEEPER horizon -> stronger ladder play.

Optimizations vs orbiter_mc.py (all preserve EXACT engine semantics):
  * Inlined geometry (swept_pair_hit / point_to_segment_distance) — no engine
    import, fully self-contained for Kaggle submission.
  * Orbit data (init angle, orbital radius, is_orbiting, av*1 cos/sin) is
    precomputed ONCE per turn; per-tick rotation is an incremental complex
    rotation (one complex multiply per orbiting planet) instead of an atan2 +
    cos + sin every tick.
  * Planet end-of-tick positions vectorized into numpy arrays once per tick.
  * Fleet movement vectorized; squared-distance broad-phase against ALL planets
    done in numpy, exact swept test only on the few candidate pairs.
  * Combat / production stay scalar (cheap, branchy) but use preallocated dicts.

PARAMS is identical to orbiter_mc.py so the same CMA-ES tuning transfers.  The
search budget (horizon / max_candidates) is raised to spend the headroom.
"""

import math
import time

try:
    import numpy as _np
except Exception:  # numpy missing -> graceful scalar fallback
    _np = None

BOARD = 100.0
CENTER = 50.0
SUN_R = 10.0
SUN_R2 = SUN_R * SUN_R
ROT_LIMIT = 50.0
MAX_SPEED_DEFAULT = 6.0
LN1000 = math.log(1000.0)
TWO_PI = 2.0 * math.pi

PARAMS = {
    # --- search budget (raised vs orbiter_mc: faster model -> deeper search) ---
    "horizon": 22,            # rollout depth (turns) per candidate (was 14)
    "time_budget": 0.72,      # seconds/turn soft cap (ladder timeout safety)
    "overage_budget": 0.86,   # allowed when remainingOverageTime is plentiful
    "overage_plenty": 20.0,   # >this many sec of overage -> use overage_budget
    "max_candidates": 9,      # hard cap on candidates considered (== #moods+idle)
    # --- economic eval weights (identical to orbiter_mc) ---
    "prod_weight": 5.0,
    "pos_weight": 0.04,
    "fleet_weight": 1.0,
    "win_bonus": 4000.0,
    "loss_penalty": 4000.0,
    # --- candidate generation ---
    "n_perturb": 0,
}

# Identical candidate "moods" to orbiter_mc.py (same decision logic).
_CANDIDATE_MOODS = [
    {},  # the tuned incumbent itself
    {"reserve_frac": 0.10, "reserve_min": 1.0, "max_launches": 10},   # aggressive
    {"reserve_frac": 0.02, "reserve_min": 1.0, "max_launches": 14,
     "enemy_bonus": 2.2, "capture_margin": 0.0, "min_fleet": 1},      # all-in rush
    {"reserve_frac": 0.50, "reserve_min": 8.0, "max_launches": 3,
     "threat_reserve": 1.5},                                          # turtle
    {"prod_weight": 2.6, "neutral_bias": 2.0, "enemy_bonus": 0.7,
     "max_launches": 8},                                              # expander
    {"enemy_bonus": 2.4, "max_launches": 12, "dist_weight": 0.3,
     "capture_margin": 1.0},                                          # denial
    {"reserve_frac": 0.35, "max_launches": 5, "capture_margin": 3.0,
     "capture_margin_frac": 0.12},                                    # safe/solid
    {"max_eta": 60.0, "neutral_bias": 1.6, "max_launches": 6},        # local expand
]


def _obs_get(obs):
    if isinstance(obs, dict):
        return obs.get
    return lambda k, d=None: getattr(obs, k, d)


def _fleet_speed(n, max_speed):
    if n <= 1:
        return 1.0
    v = 1.0 + (max_speed - 1.0) * (math.log(n) / LN1000) ** 1.5
    return min(v, max_speed)


# ----------------------------------------------------------------------------
# Inlined engine geometry (EXACT copies of engine semantics, self-contained)
# ----------------------------------------------------------------------------

def _point_to_segment_distance(px, py, vx, vy, wx, wy):
    """Min distance from point (px,py) to segment (vx,vy)-(wx,wy). Mirrors
    engine point_to_segment_distance((50,50), old, new)."""
    l2 = (vx - wx) ** 2 + (vy - wy) ** 2
    if l2 == 0.0:
        return math.hypot(px - vx, py - vy)
    t = ((px - vx) * (wx - vx) + (py - vy) * (wy - vy)) / l2
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    qx = vx + t * (wx - vx)
    qy = vy + t * (wy - vy)
    return math.hypot(px - qx, py - qy)


def _swept_pair_hit(ax, ay, bx, by, p0x, p0y, p1x, p1y, r):
    """True iff fleet A->B and planet P0->P1 come within r at some t in [0,1].
    Exact copy of engine swept_pair_hit (scalar form)."""
    d0x = ax - p0x
    d0y = ay - p0y
    dvx = (bx - ax) - (p1x - p0x)
    dvy = (by - ay) - (p1y - p0y)
    a = dvx * dvx + dvy * dvy
    b = 2.0 * (d0x * dvx + d0y * dvy)
    c = d0x * d0x + d0y * d0y - r * r
    if a < 1e-12:
        return c <= 0.0
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return False
    sq = math.sqrt(disc)
    t1 = (-b - sq) / (2.0 * a)
    t2 = (-b + sq) / (2.0 * a)
    return t2 >= 0.0 and t1 <= 1.0


# ----------------------------------------------------------------------------
# Compact forward model (preallocated arrays; orbit precomputed once per turn)
# ----------------------------------------------------------------------------
# State layout matches the engine so the greedy reference policy can be called
# on a synthesized obs each rollout step:
#   planets[i] = [id, owner, x, y, radius, ships, production]
#   fleets[i]  = [id, owner, x, y, angle, from_planet_id, ships]
# Comets are ignored in the rollout (hidden schedule; economic noise).


class _Sim:
    """Holds per-turn precomputed, immutable scene data shared by every rollout.

    Precomputes, ONCE per decision:
      * planet ids and index map
      * for each planet: orbital radius, base cos/sin of current angle, and the
        per-tick incremental rotation (cos(av), sin(av)); whether it orbits.
      * radius array, (radius + reach-slack) broad-phase squared radii base.
    Each rollout copies only the mutable ship/owner/position state.
    """

    __slots__ = ("n", "ids", "id2idx", "radius", "is_orb", "orb_r",
                 "cos0", "sin0", "cos_av", "sin_av", "av", "max_speed",
                 "use_np", "radius_np")

    def __init__(self, planets, av, max_speed):
        n = len(planets)
        self.n = n
        self.av = av
        self.max_speed = max_speed
        self.ids = [p[0] for p in planets]
        self.id2idx = {p[0]: i for i, p in enumerate(planets)}
        self.radius = [p[4] for p in planets]
        self.is_orb = [False] * n
        self.orb_r = [0.0] * n
        self.cos0 = [0.0] * n
        self.sin0 = [0.0] * n
        cav = math.cos(av)
        sav = math.sin(av)
        self.cos_av = cav
        self.sin_av = sav
        for i, p in enumerate(planets):
            dx = p[2] - CENTER
            dy = p[3] - CENTER
            orb = math.hypot(dx, dy)
            self.orb_r[i] = orb
            if av != 0.0 and (orb + p[4]) < ROT_LIMIT and orb > 0.0:
                self.is_orb[i] = True
                self.cos0[i] = dx / orb
                self.sin0[i] = dy / orb
        self.use_np = _np is not None and n > 0
        self.radius_np = _np.array(self.radius, dtype=_np.float64) if self.use_np else None


def _build_initial(planets):
    """Compat shim (kept for parity with orbiter_mc API; unused fast-path)."""
    info = {}
    for p in planets:
        dx = p[2] - CENTER
        dy = p[3] - CENTER
        orb_r = math.hypot(dx, dy)
        is_orb = (orb_r + p[4]) < ROT_LIMIT
        info[p[0]] = (math.atan2(dy, dx), orb_r, p[4], is_orb)
    return info


def _make_obs(planets, fleets, player, av, step):
    return {
        "player": player,
        "planets": [list(p) for p in planets],
        "fleets": [list(f) for f in fleets],
        "angular_velocity": av,
        "step": step,
        "comets": [],
        "comet_planet_ids": [],
        "initial_planets": [list(p) for p in planets],
        "next_fleet_id": 0,
    }


def _apply_launch(planets, fleets, next_fid, action, player, pmap):
    if not action or not isinstance(action, (list, tuple)):
        return next_fid
    for move in action:
        if len(move) != 3:
            continue
        from_id = move[0]
        angle = move[1]
        ships = int(move[2])
        fp = pmap.get(from_id)
        if fp is not None and fp[1] == player and fp[5] >= ships and ships > 0:
            fp[5] -= ships
            sx = fp[2] + math.cos(angle) * (fp[4] + 0.1)
            sy = fp[3] + math.sin(angle) * (fp[4] + 0.1)
            fleets.append([next_fid, player, sx, sy, angle, from_id, ships])
            next_fid += 1
    return next_fid


def _step_forward(sim, planets, fleets, next_fid, actions, dt_next, pmap):
    """Advance the rollout one engine tick.  Mirrors engine turn order:
    launch -> production(owned) -> compute planet end-pos -> fleet move w/
    swept collision (planet -> OOB -> sun) -> apply planet move -> combat."""
    n = sim.n
    max_speed = sim.max_speed
    radius = sim.radius

    # 0. Launch (all players, in seat order)
    for player, act in enumerate(actions):
        next_fid = _apply_launch(planets, fleets, next_fid, act, player, pmap)

    # 1. Production (owned planets only)
    for p in planets:
        if p[1] != -1:
            p[5] += p[6]

    # 2. Planet end-of-tick positions (old = current p[2],p[3]; new = rotated)
    old_x = [p[2] for p in planets]
    old_y = [p[3] for p in planets]
    new_x = list(old_x)
    new_y = list(old_y)
    if sim.av != 0.0:
        ang = sim.av * dt_next
        ca = math.cos(ang)
        sa = math.sin(ang)
        is_orb = sim.is_orb
        orb_r = sim.orb_r
        cos0 = sim.cos0
        sin0 = sim.sin0
        for i in range(n):
            if is_orb[i]:
                c = cos0[i] * ca - sin0[i] * sa
                s = sin0[i] * ca + cos0[i] * sa
                r = orb_r[i]
                new_x[i] = CENTER + r * c
                new_y[i] = CENTER + r * s

    nf = len(fleets)

    # 3. Fleet movement w/ continuous swept collision.
    combat = None  # lazily build dict only if needed
    survivors = []
    # numpy broad-phase only pays off when fleet*planet work is large; for the
    # typical small fleet counts the array build overhead dominates, so gate it.
    use_np = sim.use_np and nf >= 24
    if use_np:
        # Vectorized broad-phase: compute fleet new positions and squared
        # distance from each fleet's OLD position to each planet's OLD center.
        np = _np
        fx = np.empty(nf); fy = np.empty(nf)
        ang = np.empty(nf); shp = np.empty(nf)
        for k, f in enumerate(fleets):
            fx[k] = f[2]; fy[k] = f[3]; ang[k] = f[4]; shp[k] = f[6]
        # speeds
        spd = np.where(shp <= 1, 1.0,
                       np.minimum(max_speed,
                                  1.0 + (max_speed - 1.0)
                                  * (np.log(np.maximum(shp, 1.0)) / LN1000) ** 1.5))
        nx = fx + np.cos(ang) * spd
        ny = fy + np.sin(ang) * spd
        oxp = np.array(old_x); oyp = np.array(old_y)
        rad = sim.radius_np
        # broad-phase reach: speed + max planet travel + slack (matches orbiter_mc)
        # ddx,ddy : (nf, n)
        ddx = oxp[None, :] - fx[:, None]
        ddy = oyp[None, :] - fy[:, None]
        reach = spd[:, None] + 3.0
        rr = reach + rad[None, :]
        near = (ddx * ddx + ddy * ddy) <= (rr * rr)  # (nf, n) bool
        nxl = nx.tolist(); nyl = ny.tolist()
    else:
        nxl = [0.0] * nf
        nyl = [0.0] * nf

    for k in range(nf):
        f = fleets[k]
        if use_np:
            nx_k = nxl[k]; ny_k = nyl[k]
            ox_k = f[2]; oy_k = f[3]
        else:
            angle = f[4]
            speed = _fleet_speed(f[6], max_speed)
            ox_k = f[2]; oy_k = f[3]
            nx_k = ox_k + math.cos(angle) * speed
            ny_k = oy_k + math.sin(angle) * speed
        f[2] = nx_k
        f[3] = ny_k

        hit = False
        if use_np:
            near_row = near[k]
            for i in range(n):
                if not near_row[i]:
                    continue
                if _swept_pair_hit(ox_k, oy_k, nx_k, ny_k,
                                   old_x[i], old_y[i], new_x[i], new_y[i],
                                   radius[i]):
                    if combat is None:
                        combat = {}
                    pid = sim.ids[i]
                    lst = combat.get(pid)
                    if lst is None:
                        combat[pid] = [f]
                    else:
                        lst.append(f)
                    hit = True
                    break
        else:
            speed = _fleet_speed(f[6], max_speed)
            reach = speed + 3.0
            for i in range(n):
                ddx = old_x[i] - ox_k
                ddy = old_y[i] - oy_k
                rr = reach + radius[i]
                if ddx * ddx + ddy * ddy > rr * rr:
                    continue
                if _swept_pair_hit(ox_k, oy_k, nx_k, ny_k,
                                   old_x[i], old_y[i], new_x[i], new_y[i],
                                   radius[i]):
                    if combat is None:
                        combat = {}
                    pid = sim.ids[i]
                    lst = combat.get(pid)
                    if lst is None:
                        combat[pid] = [f]
                    else:
                        lst.append(f)
                    hit = True
                    break
        if hit:
            continue
        if not (0.0 <= nx_k <= BOARD and 0.0 <= ny_k <= BOARD):
            continue
        # sun: distance from center to segment old->new < SUN_R
        if _point_to_segment_distance(CENTER, CENTER, ox_k, oy_k, nx_k, ny_k) < SUN_R:
            continue
        survivors.append(f)

    # 4. Apply planet movement
    for i, p in enumerate(planets):
        p[2] = new_x[i]
        p[3] = new_y[i]

    fleets[:] = survivors

    # 5. Combat resolution
    if combat:
        for pid, plist in combat.items():
            planet = pmap.get(pid)
            if planet is None:
                continue
            ps = {}
            for f in plist:
                o = f[1]
                ps[o] = ps.get(o, 0) + f[6]
            if not ps:
                continue
            if len(ps) == 1:
                surv_owner, surv = next(iter(ps.items()))
            else:
                sorted_p = sorted(ps.items(), key=lambda kv: kv[1], reverse=True)
                top_owner, top_ships = sorted_p[0]
                second = sorted_p[1][1]
                surv = top_ships - second
                if top_ships == second:
                    surv = 0
                surv_owner = top_owner if surv > 0 else -1
            if surv > 0:
                if planet[1] == surv_owner:
                    planet[5] += surv
                else:
                    planet[5] -= surv
                    if planet[5] < 0:
                        planet[1] = surv_owner
                        planet[5] = -planet[5]
    return next_fid


def _evaluate_state(planets, fleets, me, n_players, P):
    """Economic eval: my (ships + prod*w + pos) minus best opponent's.
    Identical to orbiter_mc._evaluate_state."""
    score = [0.0] * n_players
    prod = [0.0] * n_players
    pos = [0.0] * n_players
    alive = [False] * n_players
    pw = P["prod_weight"]
    psw = P["pos_weight"]
    fw = P["fleet_weight"]
    for p in planets:
        o = p[1]
        if 0 <= o < n_players:
            score[o] += p[5]
            prod[o] += p[6]
            d = math.hypot(p[2] - CENTER, p[3] - CENTER)
            v = BOARD - d
            if v > 0.0:
                pos[o] += v
            alive[o] = True
    for f in fleets:
        o = f[1]
        if 0 <= o < n_players:
            score[o] += f[6] * fw
            alive[o] = True

    my = score[me] + pw * prod[me] + psw * pos[me]
    best_opp = None
    for i in range(n_players):
        if i == me:
            continue
        t = score[i] + pw * prod[i] + psw * pos[i]
        if best_opp is None or t > best_opp:
            best_opp = t
    if best_opp is None:
        best_opp = 0.0
    val = my - best_opp

    opp_alive = False
    for i in range(n_players):
        if i != me and alive[i]:
            opp_alive = True
            break
    if not opp_alive:
        val += P["win_bonus"]
    if not alive[me]:
        val -= P["loss_penalty"]
    return val


# ----------------------------------------------------------------------------
# Optimized reference policy (BYTE-IDENTICAL output to the embedded greedy
# Orbiter, just faster).  The rollout calls this thousands of times per turn,
# so it -- not the forward model -- is the true hot path.  Speedups here are
# what let us search deeper.  Validated to match _orb._decide exactly.
#
# Hot-path wins vs orbiter._decide (all arithmetic kept identical):
#   * planet orbit params (orbital radius, is_orbiting, base angle) precomputed
#     ONCE per call instead of recomputed inside every _future_pos invocation;
#   * _dist / _is_orbiting / atan2 inlined out of the intercept inner loop;
#   * local-variable hoisting of all params and math functions.
# ----------------------------------------------------------------------------

def _make_fast_ref(params):
    P = dict(_orb.PARAMS)
    if params:
        P.update(params)
    rf = P["reserve_frac"]; rm = P["reserve_min"]
    cm = P["capture_margin"]; cmf = P["capture_margin_frac"]
    pw = P["prod_weight"]; dw = P["dist_weight"]; cw = P["cost_weight"]
    eb = P["enemy_bonus"]; cp = P["comet_penalty"]; nb = P["neutral_bias"]
    maxl = P["max_launches"]; minf = P["min_fleet"]; egt = P["endgame_turn"]
    sunm = P["sun_margin"]; grm = P["graze_margin"]; iters = P["intercept_iters"]
    dtol = P["defense_tol"]; thr = P["threat_reserve"]; maxeta = P["max_eta"]
    _cos = math.cos; _sin = math.sin; _atan2 = math.atan2
    _hyp = math.hypot; _ceil = math.ceil; _log = math.log
    PI = math.pi; TWO = TWO_PI

    def ref(obs, config=None):
        try:
            g = obs.get  # rollout always passes a dict obs
            me = g("player", 0)
            planets = g("planets", []) or []
            raw_fleets = g("fleets", []) or []
            av = g("angular_velocity", 0.0) or 0.0
            step = g("step", 0) or 0
            comet_ids = g("comet_planet_ids", []) or []
            max_speed = MAX_SPEED_DEFAULT
            if config is not None:
                cs = config.get("shipSpeed") if isinstance(config, dict) \
                    else getattr(config, "shipSpeed", None)
                if cs:
                    max_speed = float(cs)
            comet_set = set(comet_ids) if comet_ids else None

            # one pass over planets: split mine/targets + precompute orbit data
            # keyed by target identity (orb_r, base_angle, is_orbiting).
            mine = []
            targets = []
            t_orb = {}  # id(p) -> (is_orb, orb_r, base_ang)
            for p in planets:
                if p[1] == me:
                    mine.append(p)
                else:
                    targets.append(p)
                px = p[2]; py = p[3]
                dx = px - CENTER; dy = py - CENTER
                orb = _hyp(dx, dy)
                is_orb = av != 0.0 and (orb + p[4]) < ROT_LIMIT
                if is_orb:
                    t_orb[id(p)] = (True, orb, _atan2(dy, dx))
                else:
                    t_orb[id(p)] = (False, 0.0, 0.0)
            if not mine:
                return []
            remaining = 500.0 - step
            if remaining < 1.0:
                remaining = 1.0
            endgame = step >= egt

            # defense: incoming enemy ships per owned planet
            threat = {}
            for f in raw_fleets:
                if f[1] == me:
                    continue
                fx = f[2]; fy = f[3]; fang = f[4]; fships = f[6]
                for p in mine:
                    ang_to = _atan2(p[3] - fy, p[2] - fx)
                    dang = abs((fang - ang_to + PI) % TWO - PI)
                    if dang < dtol:
                        pid = p[0]
                        threat[pid] = threat.get(pid, 0.0) + fships

            # available ships per source
            avail = {}
            for p in mine:
                ships = p[5]
                base_res = rm if rm > rf * ships else rf * ships
                if threat.get(p[0], 0.0) > 0:
                    tr = thr * ships
                    if tr > base_res:
                        base_res = tr
                a = ships - base_res
                avail[p[0]] = a if a > 0.0 else 0.0

            ln1000 = LN1000
            plans = []
            for t in targets:
                tid = t[0]
                is_comet = comet_set is not None and tid in comet_set
                is_enemy = t[1] != -1
                tx0 = t[2]; ty0 = t[3]; t_ships = t[5]; t_prod = t[6]
                torb, torbr, tbase = t_orb[id(t)]
                best_val = None; best_s = None; best_need = 0.0; best_ang = 0.0
                for s in mine:
                    sid = s[0]
                    if avail[sid] < minf:
                        continue
                    sx = s[2]; sy = s[3]; src_r = s[4]
                    # iterate ship-count <-> intercept (3 outer iters)
                    need = t_ships + 1.0
                    angle = 0.0; eta = 0.0; ax = tx0; ay = ty0
                    for _o in range(3):
                        ships_guess = need if need > minf else minf
                        # _fleet_speed inline
                        if ships_guess <= 1:
                            v = 1.0
                        else:
                            v = 1.0 + (max_speed - 1.0) * (_log(ships_guess) / ln1000) ** 1.5
                            if v > max_speed:
                                v = max_speed
                        ax = tx0; ay = ty0
                        for _i in range(iters):
                            d = _hyp(sx - ax, sy - ay) - src_r - 0.1
                            if d < 0.0:
                                d = 0.0
                            eta = d / v if v > 0 else 0.0
                            if torb:
                                ang = tbase + av * eta
                                ax = CENTER + torbr * _cos(ang)
                                ay = CENTER + torbr * _sin(ang)
                            # else ax,ay stay at tx0,ty0 (static)
                        angle = _atan2(ay - sy, ax - sx)
                        garrison = t_ships + (t_prod * eta if is_enemy else 0.0)
                        need = garrison + 1.0
                        need += cm + cmf * need
                    need = _ceil(need)
                    if eta > maxeta:
                        continue
                    if need > avail[sid] or need > s[5]:
                        continue
                    # path clear: sun + unintended-planet graze (inline)
                    if _point_to_segment_distance(CENTER, CENTER, sx, sy, ax, ay) < SUN_R + sunm:
                        continue
                    blocked = False
                    abx = ax - sx; aby = ay - sy
                    l2 = abx * abx + aby * aby
                    if l2 != 0.0:
                        for q in planets:
                            qid = q[0]
                            if qid == sid or qid == tid:
                                continue
                            qx = q[2]; qy = q[3]
                            tt = ((qx - sx) * abx + (qy - sy) * aby) / l2
                            if tt <= 0.02 or tt >= 0.99:
                                continue
                            cx = sx + tt * abx; cy = sy + tt * aby
                            if _hyp(qx - cx, qy - cy) < q[4] + grm:
                                blocked = True
                                break
                    if blocked:
                        continue
                    hold = remaining if remaining < 500.0 else 500.0
                    base = (t_prod ** pw) * hold
                    base *= eb if is_enemy else nb
                    if is_comet:
                        base *= cp
                    denom = cw * need + dw * eta + 1.0
                    val = base / denom
                    if best_val is None or val > best_val:
                        best_val = val; best_s = s; best_need = need; best_ang = angle
                if best_val is not None:
                    plans.append((best_val, t, best_s, best_need, best_ang))

            plans.sort(key=lambda z: z[0], reverse=True)
            moves = []
            launches = 0
            for val, t, s, need, angle in plans:
                if launches >= maxl:
                    break
                if avail[s[0]] >= need and s[5] >= need:
                    n = int(need)
                    if n < minf:
                        continue
                    moves.append([s[0], angle, n])
                    avail[s[0]] -= need
                    s[5] -= n
                    launches += 1
            return moves
        except Exception:
            return []

    return ref


def _rollout(sim, planets0, fleets0, my_action, me, n_players, ref_policies,
             av, horizon, start_step, P):
    """Apply my_action this turn (opponents use ref policy), then roll H turns
    with BOTH players following the greedy Orbiter reference policy."""
    planets = [list(p) for p in planets0]
    fleets = [list(f) for f in fleets0]
    next_fid = (max((f[0] for f in fleets), default=-1)) + 1
    pmap = {p[0]: p for p in planets}

    # First tick: me plays my_action, opponents play reference.
    actions = [None] * n_players
    for pl in range(n_players):
        if pl == me:
            actions[pl] = my_action
        else:
            obs = _make_obs(planets, fleets, pl, av, start_step)
            actions[pl] = ref_policies[pl](obs, None)
    next_fid = _step_forward(sim, planets, fleets, next_fid, actions, 1, pmap)

    # Remaining ticks: everyone plays reference policy.
    for h in range(1, horizon):
        owners = set(p[1] for p in planets if p[1] != -1)
        owners.update(f[1] for f in fleets)
        if len(owners) <= 1:
            break
        actions = [None] * n_players
        for pl in range(n_players):
            obs = _make_obs(planets, fleets, pl, av, start_step + h)
            actions[pl] = ref_policies[pl](obs, None)
        next_fid = _step_forward(sim, planets, fleets, next_fid, actions,
                                 h + 1, pmap)

    return _evaluate_state(planets, fleets, me, n_players, P)


# ----------------------------------------------------------------------------
# Candidate generation (identical logic to orbiter_mc.py)
# ----------------------------------------------------------------------------

def _gen_candidates(obs, config, me, n_players, av, step, max_speed, P):
    cands = []
    seen = set()

    def add(label, action):
        key = tuple(sorted(
            (m[0], round(m[1], 4), int(m[2])) for m in action
            if isinstance(m, (list, tuple)) and len(m) == 3
        ))
        if key in seen:
            return
        seen.add(key)
        cands.append((label, action))

    add("idle", [])

    moods = _CANDIDATE_MOODS[: max(1, P["max_candidates"] - 1)]
    for i, ov in enumerate(moods):
        try:
            ag = _orbiter_make_agent(ov)
            action = ag(obs, config) or []
        except Exception:
            action = []
        add("mood%d" % i, action)

    return cands[: P["max_candidates"]]


# ----------------------------------------------------------------------------
# Main decision (identical control flow to orbiter_mc.py)
# ----------------------------------------------------------------------------

def _decide(obs, config, P, ref_default):
    t0 = time.time()
    g = _obs_get(obs)
    me = g("player", 0) or 0
    raw_planets = g("planets", []) or []
    raw_fleets = g("fleets", []) or []
    av = g("angular_velocity", 0.0) or 0.0
    step = g("step", 0) or 0
    overage = g("remainingOverageTime", 0.0) or 0.0

    max_speed = MAX_SPEED_DEFAULT
    if config is not None:
        cs = config.get("shipSpeed") if isinstance(config, dict) \
            else getattr(config, "shipSpeed", None)
        if cs:
            max_speed = float(cs)

    planets = [list(p) for p in raw_planets]
    fleets = [list(f) for f in raw_fleets]
    mine = [p for p in planets if p[1] == me]
    if not mine:
        return []

    owners = set(p[1] for p in planets if p[1] != -1)
    owners.update(f[1] for f in fleets)
    owners.add(me)
    n_players = max(2, max(owners) + 1)

    ref_policies = [ref_default] * n_players

    budget = P["time_budget"]
    if overage > P["overage_plenty"]:
        budget = max(budget, P["overage_budget"])

    sim = _Sim(planets, av, max_speed)
    horizon = int(P["horizon"])
    work = max(1, len(planets)) * max(1, len(fleets))
    if work > 1200:
        horizon = max(6, int(horizon * 1200.0 / work))

    candidates = _gen_candidates(obs, config, me, n_players, av, step,
                                 max_speed, P)
    if not candidates:
        return []

    best_action = candidates[0][1]
    best_val = -float("inf")

    n_done = 0
    per_rollout = 0.0
    for label, action in candidates:
        elapsed = time.time() - t0
        if n_done > 0 and elapsed + per_rollout * 1.15 > budget:
            break
        r0 = time.time()
        try:
            val = _rollout(sim, planets, fleets, action, me, n_players,
                           ref_policies, av, horizon, step, P)
        except Exception:
            val = -float("inf")
        rt = time.time() - r0
        per_rollout = rt if per_rollout == 0.0 else max(per_rollout, rt)
        n_done += 1
        if val > best_val:
            best_val = val
            best_action = action

    return best_action


def make_agent(params=None):
    P = dict(PARAMS)
    if params:
        P.update(params)
    ref_default = _orbiter_make_agent()

    def agent(obs, config=None):
        try:
            return _decide(obs, config, P, ref_default)
        except Exception:
            return []

    return agent


# module-level default agent (league.py loads `mod.agent` for file: specs)
agent = make_agent()
