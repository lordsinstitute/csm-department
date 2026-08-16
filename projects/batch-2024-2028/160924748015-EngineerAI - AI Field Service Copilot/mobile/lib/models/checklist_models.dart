class ChecklistItem {
  final String step;
  final bool checked;

  const ChecklistItem({required this.step, required this.checked});

  factory ChecklistItem.fromJson(Map<String, dynamic> json) => ChecklistItem(
        step: json['step'] as String,
        checked: json['checked'] as bool,
      );

  Map<String, dynamic> toJson() => {'step': step, 'checked': checked};

  ChecklistItem copyWith({bool? checked}) => ChecklistItem(
        step: step,
        checked: checked ?? this.checked,
      );
}

class ReportRequest {
  final List<ChecklistItem> checklistState;

  const ReportRequest({required this.checklistState});

  Map<String, dynamic> toJson() => {
        'checklist_state': checklistState.map((e) => e.toJson()).toList(),
      };
}

class ReportResponse {
  final String pdfUrl;

  const ReportResponse({required this.pdfUrl});

  factory ReportResponse.fromJson(Map<String, dynamic> json) => ReportResponse(
        pdfUrl: json['pdf_url'] as String,
      );
}
