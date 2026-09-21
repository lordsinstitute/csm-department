class Question {
  final String text;
  final String questionType;
  final List<String>? options;

  const Question({
    required this.text,
    required this.questionType,
    this.options,
  });

  factory Question.fromJson(Map<String, dynamic> json) => Question(
        text: json['text'] as String,
        questionType: json['question_type'] as String,
        options: json['options'] == null
            ? null
            : List<String>.from(json['options'] as List),
      );

  Map<String, dynamic> toJson() => {
        'text': text,
        'question_type': questionType,
        'options': options,
      };
}

class QuestionSet {
  final List<Question> questions;

  const QuestionSet({required this.questions});

  factory QuestionSet.fromJson(Map<String, dynamic> json) => QuestionSet(
        questions: (json['questions'] as List)
            .map((e) => Question.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'questions': questions.map((e) => e.toJson()).toList(),
      };
}
