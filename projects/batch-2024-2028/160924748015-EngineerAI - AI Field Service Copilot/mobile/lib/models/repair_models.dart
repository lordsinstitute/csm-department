class RepairStep {
  final int stepNumber;
  final String instruction;
  final String? safetyWarning;

  const RepairStep({
    required this.stepNumber,
    required this.instruction,
    this.safetyWarning,
  });

  factory RepairStep.fromJson(Map<String, dynamic> json) => RepairStep(
        stepNumber: json['step_number'] as int,
        instruction: json['instruction'] as String,
        safetyWarning: json['safety_warning'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'step_number': stepNumber,
        'instruction': instruction,
        'safety_warning': safetyWarning,
      };
}

class SparePart {
  final String partName;
  final String spec;

  const SparePart({required this.partName, required this.spec});

  factory SparePart.fromJson(Map<String, dynamic> json) => SparePart(
        partName: json['part_name'] as String,
        spec: json['spec'] as String,
      );

  Map<String, dynamic> toJson() => {'part_name': partName, 'spec': spec};
}

class RepairPlan {
  final List<RepairStep> steps;
  final List<String> tools;
  final int estMinutes;
  final List<String> safetyWarnings;
  final List<SparePart> spareParts;

  const RepairPlan({
    required this.steps,
    required this.tools,
    required this.estMinutes,
    required this.safetyWarnings,
    required this.spareParts,
  });

  factory RepairPlan.fromJson(Map<String, dynamic> json) => RepairPlan(
        steps: (json['steps'] as List)
            .map((e) => RepairStep.fromJson(e as Map<String, dynamic>))
            .toList(),
        tools: List<String>.from(json['tools'] as List),
        estMinutes: json['est_minutes'] as int,
        safetyWarnings: List<String>.from(json['safety_warnings'] as List),
        spareParts: (json['spare_parts'] as List)
            .map((e) => SparePart.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'steps': steps.map((e) => e.toJson()).toList(),
        'tools': tools,
        'est_minutes': estMinutes,
        'safety_warnings': safetyWarnings,
        'spare_parts': spareParts.map((e) => e.toJson()).toList(),
      };
}
