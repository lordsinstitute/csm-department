class Hypothesis {
  final String cause;
  final double confidence;
  final String reasoning;

  const Hypothesis({
    required this.cause,
    required this.confidence,
    required this.reasoning,
  });

  factory Hypothesis.fromJson(Map<String, dynamic> json) => Hypothesis(
        cause: json['cause'] as String,
        confidence: (json['confidence'] as num).toDouble(),
        reasoning: json['reasoning'] as String,
      );

  Map<String, dynamic> toJson() => {
        'cause': cause,
        'confidence': confidence,
        'reasoning': reasoning,
      };
}

class InvestigationResult {
  final List<Hypothesis> hypotheses;

  const InvestigationResult({required this.hypotheses});

  factory InvestigationResult.fromJson(Map<String, dynamic> json) =>
      InvestigationResult(
        hypotheses: (json['hypotheses'] as List)
            .map((e) => Hypothesis.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'hypotheses': hypotheses.map((e) => e.toJson()).toList(),
      };
}
