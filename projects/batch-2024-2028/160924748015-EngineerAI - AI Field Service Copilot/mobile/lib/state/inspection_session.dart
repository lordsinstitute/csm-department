import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/answers_models.dart';
import '../models/checklist_models.dart';
import '../models/reasoning_models.dart';
import '../models/repair_models.dart';
import '../models/vision_models.dart';

/// Mirrors the backend `inspections` row exactly, accumulated client-side as
/// the technician moves through the guided flow.
class InspectionSessionState {
  final String? inspectionId;
  final String? machineId;
  final String? problemId;
  final String? photoUrl;
  final AnswersPayload? answers;
  final VisionResult? visionResult;
  final DiagnosisResult? diagnosis;
  final RepairPlan? repairPlan;
  final List<ChecklistItem>? checklistState;

  const InspectionSessionState({
    this.inspectionId,
    this.machineId,
    this.problemId,
    this.photoUrl,
    this.answers,
    this.visionResult,
    this.diagnosis,
    this.repairPlan,
    this.checklistState,
  });

  InspectionSessionState copyWith({
    String? inspectionId,
    String? machineId,
    String? problemId,
    String? photoUrl,
    AnswersPayload? answers,
    VisionResult? visionResult,
    DiagnosisResult? diagnosis,
    RepairPlan? repairPlan,
    List<ChecklistItem>? checklistState,
  }) {
    return InspectionSessionState(
      inspectionId: inspectionId ?? this.inspectionId,
      machineId: machineId ?? this.machineId,
      problemId: problemId ?? this.problemId,
      photoUrl: photoUrl ?? this.photoUrl,
      answers: answers ?? this.answers,
      visionResult: visionResult ?? this.visionResult,
      diagnosis: diagnosis ?? this.diagnosis,
      repairPlan: repairPlan ?? this.repairPlan,
      checklistState: checklistState ?? this.checklistState,
    );
  }
}

class InspectionSessionNotifier extends Notifier<InspectionSessionState> {
  @override
  InspectionSessionState build() => const InspectionSessionState();

  void selectMachine(String machineId) {
    state = state.copyWith(machineId: machineId);
  }

  void selectProblem(String problemId) {
    state = state.copyWith(problemId: problemId);
  }

  void setInspectionId(String inspectionId) {
    state = state.copyWith(inspectionId: inspectionId);
  }

  void setPhotoUrl(String photoUrl) {
    state = state.copyWith(photoUrl: photoUrl);
  }

  void setAnswers(AnswersPayload answers) {
    state = state.copyWith(answers: answers);
  }

  void setVisionResult(VisionResult visionResult) {
    state = state.copyWith(visionResult: visionResult);
  }

  void setDiagnosis(DiagnosisResult diagnosis) {
    state = state.copyWith(diagnosis: diagnosis);
  }

  void setRepairPlan(RepairPlan repairPlan) {
    state = state.copyWith(repairPlan: repairPlan);
  }

  void setChecklistState(List<ChecklistItem> checklistState) {
    state = state.copyWith(checklistState: checklistState);
  }

  void toggleChecklistItem(int index) {
    final current = state.checklistState;
    if (current == null) return;
    final updated = [...current];
    updated[index] = updated[index].copyWith(checked: !updated[index].checked);
    state = state.copyWith(checklistState: updated);
  }

  void reset() {
    state = const InspectionSessionState();
  }
}

final inspectionSessionProvider =
    NotifierProvider<InspectionSessionNotifier, InspectionSessionState>(
  InspectionSessionNotifier.new,
);
