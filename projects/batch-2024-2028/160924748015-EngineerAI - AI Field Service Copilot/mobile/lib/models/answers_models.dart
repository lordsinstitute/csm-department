class AnswerEntry {
  final String question;
  final String answer;

  const AnswerEntry({required this.question, required this.answer});

  factory AnswerEntry.fromJson(Map<String, dynamic> json) => AnswerEntry(
        question: json['question'] as String,
        answer: json['answer'] as String,
      );

  Map<String, dynamic> toJson() => {'question': question, 'answer': answer};
}

class AnswersPayload {
  final List<AnswerEntry> answers;

  const AnswersPayload({required this.answers});

  factory AnswersPayload.fromJson(Map<String, dynamic> json) => AnswersPayload(
        answers: (json['answers'] as List)
            .map((e) => AnswerEntry.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'answers': answers.map((e) => e.toJson()).toList(),
      };
}
