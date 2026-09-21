---
title: "Tripped Thermal Overload"
problem_tags: ["Won't Start"]
source: "EngineerAI KB"
---

**Symptom:** Motor does not start, but the circuit otherwise appears to have power — control lights are on, contactor may audibly click, yet the motor never energizes. On some starters, a small reset button on the overload relay is visibly popped out.

**Likely cause:** The thermal overload relay in the motor starter has tripped, opening the control circuit to protect the motor from a previous overcurrent event (a prior overload, a recent locked-rotor attempt, or an ambient temperature effect), and has not yet been reset. This is a protective device doing its job, not a defect in itself — but the underlying cause of the trip must be identified.

**How to confirm:** Visually inspect the overload relay on the motor starter for a tripped indicator or popped reset button. Check any event/fault log on the starter or PLC if available for a recorded overload trip and timestamp. Before resetting, measure motor winding resistance and insulation resistance to rule out an internal fault as the reason for the original trip.

**Fix:** Identify and resolve the root cause of the original overload (mechanical binding, single-phasing, undersized overload setting) before resetting. Press the reset button or cycle control power per the starter's design, then observe the motor through a full start cycle to confirm normal current draw.

**Parts/tools:** Multimeter, megohmmeter, starter documentation for reset procedure, clamp meter to verify post-reset current.
