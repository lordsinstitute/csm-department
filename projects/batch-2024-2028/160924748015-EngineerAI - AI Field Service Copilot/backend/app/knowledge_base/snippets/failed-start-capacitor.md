---
title: "Failed Start Capacitor"
problem_tags: ["Won't Start"]
source: "EngineerAI KB"
---

**Symptom:** Motor hums loudly when energized but does not turn, or turns only if the shaft is nudged by hand, after which it may run normally. This behavior is specific to single-phase induction motors that rely on a start capacitor to produce starting torque.

**Likely cause:** The start capacitor has failed open, shorted, or lost capacitance with age and heat cycling — a very common failure mode since capacitors are typically the shortest-lived component in a single-phase motor circuit. Without adequate starting torque from the auxiliary winding circuit, the rotor cannot begin rotating on its own even though the main winding is energized and humming.

**How to confirm:** With power locked out and the capacitor safely discharged, remove it and test with a capacitor meter or multimeter's capacitance function. Compare the reading to the capacitor's rated microfarad (µF) value printed on its case — a reading significantly below rated value, an open circuit, or a shorted reading confirms failure. Visually inspect for a bulging or leaking capacitor case, which is a clear sign of failure even without testing.

**Fix:** Replace the capacitor with one of the same microfarad rating and equal or higher voltage rating. Never substitute a lower voltage-rated capacitor. After replacement, verify the motor starts smoothly under normal load without manual assistance.

**Parts/tools:** Capacitor meter or multimeter with capacitance function, replacement capacitor (matching µF/voltage rating), insulated discharge tool.
