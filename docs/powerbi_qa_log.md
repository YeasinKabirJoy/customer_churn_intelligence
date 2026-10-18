# Power BI Phase 5 QA log

## Completed and verified

- Governed DAX measures documented in both `.dax` and TMDL forms
- Explicit Power Query type contract
- Flat-table model decision and future star-schema proposal
- Executive Overview layout and verified values
- Segment Explorer layout with volume and rate together
- Validation page with governed KPI targets and SQL check status
- Theme palette, accessibility guidance, tooltip rules, and interaction test plan
- Static previews rendered and visually inspected for clipping, overlap, contrast, labels, and denominator context
- Automated source-asset tests passed

## Desktop report status

Power BI Desktop is installed and was launched, but the current Codex Windows-control session exposes no native-app window inventory or input interface. Therefore an interactive `.pbix` could not be safely authored or inspected in this session.

This limitation is not represented as a successful desktop build. The following ready-to-apply assets reduce the remaining Desktop work:

1. Open a blank Power BI Desktop report.
2. Open Model > TMDL view.
3. Paste `reports/powerbi/model.tmdl` and select Apply.
4. Import `reports/powerbi/theme.json`.
5. Reproduce the three visually reviewed page previews.
6. Clear all filters and verify the validation page before saving the `.pbix`.

## Required final desktop evidence

- Saved `.pbix` or `.pbip`
- Screenshot or PDF export of all three report pages
- Screenshot of the model and measures
- Validation-difference measures all equal zero
- Tested slicers, visual interactions, tooltips, alt text, and final display size
