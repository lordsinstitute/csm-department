---
title: "Low or Unbalanced Supply Voltage"
problem_tags: ["Overheating"]
source: "EngineerAI KB"
---

**Symptom:** Overheating that correlates with time of day or plant load (e.g., worse when other heavy equipment is running nearby), rather than with this motor's own load. May be accompanied by slightly higher than normal running current on one or more phases and, in severe cases, an audible growl.

**Likely cause:** Supply voltage that is below nameplate rating, or unevenly distributed across the three phases, forces the motor to draw more current to deliver the same torque, and voltage imbalance in particular causes disproportionately large current imbalance (roughly 6-10x the voltage imbalance percentage), concentrating heat in one or two windings.

**How to confirm:** Measure phase-to-phase voltage at the motor terminals under load with a multimeter or power quality meter. Calculate voltage imbalance as the maximum deviation from the average of the three readings, divided by that average. Imbalance above 1-2% is generally considered a contributing cause; above 5% is a serious problem. Cross-check current draw per phase with a clamp meter — the phase with the highest voltage deviation typically shows the highest current.

**Fix:** This is typically a supply-side issue, not a motor defect. Report findings to facilities/electrical maintenance to investigate the feeder, transformer loading, or a loose connection upstream. Temporary mitigation includes reducing load on the affected circuit; the motor itself does not need replacement unless the imbalance has already caused a winding fault.

**Parts/tools:** Multimeter or power quality meter, clamp meter, single-line diagram of the supply circuit.
