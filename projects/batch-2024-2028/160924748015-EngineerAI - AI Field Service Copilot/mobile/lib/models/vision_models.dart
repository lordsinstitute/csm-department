class VisionResult {
  final List<String> visibleIssues;
  final List<String> damagedComponents;
  final String severityEstimate;
  final bool machineConfirmed;

  const VisionResult({
    required this.visibleIssues,
    required this.damagedComponents,
    required this.severityEstimate,
    required this.machineConfirmed,
  });

  factory VisionResult.fromJson(Map<String, dynamic> json) => VisionResult(
        visibleIssues: List<String>.from(json['visible_issues'] as List),
        damagedComponents: List<String>.from(json['damaged_components'] as List),
        severityEstimate: json['severity_estimate'] as String,
        machineConfirmed: json['machine_confirmed'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'visible_issues': visibleIssues,
        'damaged_components': damagedComponents,
        'severity_estimate': severityEstimate,
        'machine_confirmed': machineConfirmed,
      };
}
