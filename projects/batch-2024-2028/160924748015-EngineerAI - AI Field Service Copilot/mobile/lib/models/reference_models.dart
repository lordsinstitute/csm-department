class Department {
  final String id;
  final String name;

  const Department({required this.id, required this.name});

  factory Department.fromJson(Map<String, dynamic> json) => Department(
        id: json['id'] as String,
        name: json['name'] as String,
      );

  Map<String, dynamic> toJson() => {'id': id, 'name': name};
}

class Machine {
  final String id;
  final String departmentId;
  final String name;
  final String? imageUrl;

  const Machine({
    required this.id,
    required this.departmentId,
    required this.name,
    this.imageUrl,
  });

  factory Machine.fromJson(Map<String, dynamic> json) => Machine(
        id: json['id'] as String,
        departmentId: json['department_id'] as String,
        name: json['name'] as String,
        imageUrl: json['image_url'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'department_id': departmentId,
        'name': name,
        'image_url': imageUrl,
      };
}

class Problem {
  final String id;
  final String machineId;
  final String name;
  final String? description;

  const Problem({
    required this.id,
    required this.machineId,
    required this.name,
    this.description,
  });

  factory Problem.fromJson(Map<String, dynamic> json) => Problem(
        id: json['id'] as String,
        machineId: json['machine_id'] as String,
        name: json['name'] as String,
        description: json['description'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'machine_id': machineId,
        'name': name,
        'description': description,
      };
}
