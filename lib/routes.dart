import 'package:flutter/material.dart';
import 'widgets/app_drawer.dart';

class Routes {
  static const String inventory = '/inventory';
  static const String vehicles = '/vehicles';
  static const String invoices = '/invoices';
  static const String customers = '/customers';
  static const String settings = '/settings';
}

// Example of how to utilize the routes and AppDrawer in a screen
class InventoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Inventory')), 
      drawer: const AppDrawer(),
      body: Center(child: Text('Inventory Screen Content')), 
    );
  }
}

// Repeat similar structure for Vehicles, Invoices, Customers, Settings screens