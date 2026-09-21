import 'investigation_models.dart';

class RuledOutHypothesis {
  final String cause;
  final String reason;

  const RuledOutHypothesis({required this.cause, required this.reason});

  factory RuledOutHypothesis.fromJson(Map<String, dynamic> json) =>
      RuledOutHypothesis(
        cause: json['cause'] as String,
        reason: json['reason'] as String,
      );

  Map<String, dynamic> toJson() => {'cause': cause, 'reason': reason};
}

class ReasoningResult {
  final String rootCause;
  final double confidence;
  final String explanation;
  final List<RuledOutHypothesis> ruledOut;
  final List<String> citedSources;

  const ReasoningResult({
    required this.rootCause,
    required this.confidence,
    required this.explanation,
    required this.ruledOut,
    required this.citedSources,
  });

  factory ReasoningResult.fromJson(Map<String, dynamic> json) => ReasoningResult(
        rootCause: json['root_cause'] as String,
        confidence: (json['confidence'] as num).toDouble(),
        explanation: json['explanation'] as String,
        ruledOut: (json['ruled_out'] as List)
            .map((e) => RuledOutHypothesis.fromJson(e as Map<String, dynamic>))
            .toList(),
        citedSources: List<String>.from(json['cited_sources'] as List),
      );

  Map<String, dynamic> toJson() => {
        'root_cause': rootCause,
        'confidence': confidence,
        'explanation': explanation,
        'ruled_out': ruledOut.map((e) => e.toJson()).toList(),
        'cited_sources': citedSources,
      };
}

class DiagnosisResult {
  final List<Hypothesis> hypotheses;
  final String rootCause;
  final double confidence;
  final String explanation;
  final List<RuledOutHypothesis> ruledOut;
  final List<String> citedSources;

  const DiagnosisResult({
    required this.hypotheses,
    required this.rootCause,
    required this.confidence,
    required this.explanation,
    required this.ruledOut,
    required this.citedSources,
  });

  factory DiagnosisResult.fromJson(Map<String, dynamic> json) => DiagnosisResult(
        hypotheses: (json['hypotheses'] as List)
            .map((e) => Hypothesis.fromJson(e as Map<String, dynamic>))
            .toList(),
        rootCause: json['root_cause'] as String,
        confidence: (json['confidence'] as num).toDouble(),
        explanation: json['explanation'] as String,
        ruledOut: (json['ruled_out'] as List)
            .map((e) => RuledOutHypothesis.fromJson(e as Map<String, dynamic>))
            .toList(),
        citedSources: List<String>.from(json['cited_sources'] as List),
      );

  Map<String, dynamic> toJson() => {
        'hypotheses': hypotheses.map((e) => e.toJson()).toList(),
        'root_cause': rootCause,
        'confidence': confidence,
        'explanation': explanation,
        'ruled_out': ruledOut.map((e) => e.toJson()).toList(),
        'cited_sources': citedSources,
      };
}
