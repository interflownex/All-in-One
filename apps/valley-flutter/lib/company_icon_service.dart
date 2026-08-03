import 'dart:convert';

import 'package:flutter/services.dart';

class CompanyIconService {
  const CompanyIconService();

  static const MethodChannel _channel = MethodChannel(
    'com.interflownex.valley/company_icon',
  );

  Future<bool> isSupported() async {
    return await _channel.invokeMethod<bool>('isSupported') ?? false;
  }

  Future<bool> pinShortcut({
    required String companyId,
    required String label,
    required String logoBase64,
    required String variant,
  }) async {
    _validate(companyId, label, logoBase64, variant);
    return await _channel.invokeMethod<bool>('pinShortcut', {
          'companyId': companyId,
          'label': label,
          'logoBase64': logoBase64,
          'variant': variant,
        }) ??
        false;
  }

  Future<bool> updateShortcut({
    required String companyId,
    required String label,
    required String logoBase64,
    required String variant,
  }) async {
    _validate(companyId, label, logoBase64, variant);
    return await _channel.invokeMethod<bool>('updateShortcut', {
          'companyId': companyId,
          'label': label,
          'logoBase64': logoBase64,
          'variant': variant,
        }) ??
        false;
  }

  void _validate(
    String companyId,
    String label,
    String logoBase64,
    String variant,
  ) {
    if (companyId.trim().isEmpty || label.trim().isEmpty) {
      throw const FormatException('Empresa e rótulo são obrigatórios.');
    }
    if (!{'consumer', 'rider'}.contains(variant)) {
      throw const FormatException('Variante Valley inválida.');
    }
    final payload = logoBase64.contains('base64,')
        ? logoBase64.split('base64,').last
        : logoBase64;
    final bytes = base64Decode(payload);
    if (bytes.isEmpty || bytes.length > 4 * 1024 * 1024) {
      throw const FormatException('Logomarca inválida ou acima do limite.');
    }
  }
}
