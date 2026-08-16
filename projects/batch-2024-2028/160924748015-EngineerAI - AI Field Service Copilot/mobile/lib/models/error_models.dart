class ErrorEnvelope {
  final String errorCode;
  final String message;

  const ErrorEnvelope({required this.errorCode, required this.message});

  factory ErrorEnvelope.fromJson(Map<String, dynamic> json) => ErrorEnvelope(
        errorCode: json['error_code'] as String,
        message: json['message'] as String,
      );
}
