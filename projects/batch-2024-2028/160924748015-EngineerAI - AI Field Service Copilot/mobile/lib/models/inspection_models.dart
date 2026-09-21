import 'answers_models.dart';
import 'checklist_models.dart';
import 'reasoning_models.dart';
import 'repair_models.dart';
import 'vision_models.dart';

class Inspection {
  final String id;
  final String userId;
  final String machineId;
  final String problemId;
  final String? photoUrl;
  final AnswersPayload? answers;
  final VisionResult? visionResult;
  final DiagnosisResult? diagnosis;
  final RepairPlan? repairPlan;
  final List<ChecklistItem>? checklistState;
  final String? pdfUrl;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Inspection({
    required this.id,
    required this.userId,
    required this.machineId,
    required this.problemId,
    this.photoUrl,
    this.answers,
    this.visionResult,
    this.diagnosis,
    this.repairPlan,
    this.checklistState,
    this.pdfUrl,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Inspection.fromJson(Map<String, dynamic> json) => Inspection(
        id: json['id'] as String,
        userId: json['user_id'] as String,
        machineId: json['machine_id_fk'] as String,
        problemId: json['problem_id_fk'] as String,
        photoUrl: json['photo_url'] as String?,
        answers: json['answers'] == null
            ? null
            : AnswersPayload.fromJson(json['answers'] as Map<String, dynamic>),
        visionResult: json['vision_result'] == null
            ? null
            : VisionResult.fromJson(json['vision_result'] as Map<String, dynamic>),
        diagnosis: json['diagnosis'] == null
            ? null
            : DiagnosisResult.fromJson(json['diagnosis'] as Map<String, dynamic>),
        repairPlan: json['repair_plan'] == null
            ? null
            : RepairPlan.fromJson(json['repair_plan'] as Map<String, dynamic>),
        checklistState: json['checklist_state'] == null
            ? null
            : (json['checklist_state'] as List)
                .map((e) => ChecklistItem.fromJson(e as Map<String, dynamic>))
                .toList(),
        pdfUrl: json['pdf_url'] as String?,
        status: json['status'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
        updatedAt: DateTime.parse(json['updated_at'] as String),
      );
}

class InspectionSummary {
  final String id;
  final String machineId;
  final String problemId;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;

  const InspectionSummary({
    required this.id,
    required this.machineId,
    required this.problemId,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory InspectionSummary.fromJson(Map<String, dynamic> json) =>
      InspectionSummary(
        id: json['id'] as String,
        machineId: json['machine_id_fk'] as String,
        problemId: json['problem_id_fk'] as String,
        status: json['status'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
        updatedAt: DateTime.parse(json['updated_at'] as String),
      );
}

class CreateInspectionRequest {
  final String machineId;
  final String problemId;

  const CreateInspectionRequest({
    required this.machineId,
    required this.problemId,
  });

  Map<String, dynamic> toJson() => {
        'machine_id': machineId,
        'problem_id': problemId,
      };
}

class VisionAnalysisRequest {
  final String photoUrl;

  const VisionAnalysisRequest({required this.photoUrl});

  Map<String, dynamic> toJson() => {'photo_url': photoUrl};
}
