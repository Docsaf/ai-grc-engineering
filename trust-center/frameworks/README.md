# Framework crosswalks

Generated from `trust-center/controls/` — do not edit by hand. Run:

```bash
python scripts/validate_controls.py --crosswalks
```

to regenerate one table per framework the validator knows (SOC 2, ISO 27001:2022, NIST CSF 2.0, CIS v8.1, NIST SP 800-53 Rev. 5, FedRAMP Moderate, StateRAMP, TX-RAMP, CJIS, FERPA, HECVAT, NIST SP 800-171, CMMC, PCI DSS 4, HIPAA). A table is written only for frameworks at least one control maps to. Criteria with zero mapped controls are your gap backlog.
