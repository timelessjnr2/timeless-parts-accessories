import 'package:flutter/foundation.dart';

class AppSettings with ChangeNotifier {
  static final AppSettings _instance = AppSettings._internal();
  factory AppSettings() => _instance;
  AppSettings._internal();

  String _someSetting = 'default';

  String get someSetting => _someSetting;

  void updateSomeSetting(String newValue) {
    _someSetting = newValue;
    notifyListeners();
  }
}

// Usage example:
// final settings = AppSettings();
// settings.updateSomeSetting('new value');

