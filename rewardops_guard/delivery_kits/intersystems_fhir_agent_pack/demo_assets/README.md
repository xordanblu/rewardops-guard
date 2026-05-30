# Demo Assets

Generated local screenshots for the dependency-free FHIR Care Brief Agent demo.
They are review artifacts only; no browser upload or external submission was
performed.

## Files

- `care_brief_demo_desktop.png` - desktop viewport, care manager role.
  - sha256: `7b18296d025d1e7f4b2d061400911cc10f71e1ccdf6af07ab4244fb97ac6fbdf`
- `care_brief_demo_mobile.png` - mobile viewport, patient role.
  - sha256: `50566ab707aca7254d1fce23b40164661231ec77838f2306f0ef64a2b3339200`

## Reproduce

```bash
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_server.py --port 8765
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars --window-size=1280,900 --screenshot=rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_assets/care_brief_demo_desktop.png "http://127.0.0.1:8765/?role=care_manager"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --hide-scrollbars --window-size=390,844 --screenshot=rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_assets/care_brief_demo_mobile.png "http://127.0.0.1:8765/?role=patient"
```
