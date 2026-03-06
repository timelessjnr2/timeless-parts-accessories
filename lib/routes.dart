import 'package:flutter/material.dart';

class Routes {
  static Map<String, WidgetBuilder> get routes {
    return {
      '/inventory': (context) => InventoryScreen(),
      '/vehicles': (context) => VehiclesScreen(),
      '/invoices': (context) => InvoicesScreen(),
      '/customers': (context) => CustomersScreen(),
      '/settings': (context) => SettingsScreen(),
    };
  }
}

class InventoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Inventory')), 
      drawer: Drawer(),
      body: Center(child: Text('Inventory Screen')), 
    );
  }
}

class VehiclesScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Vehicles')), 
      drawer: Drawer(),
      body: Center(child: Text('Vehicles Screen')), 
    );
  }
}

class InvoicesScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Invoices')), 
      drawer: Drawer(),
      body: Center(child: Text('Invoices Screen')), 
    );
  }
}

class CustomersScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Customers')), 
      drawer: Drawer(),
      body: Center(child: Text('Customers Screen')), 
    );
  }
}

class SettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Settings')), 
      drawer: Drawer(),
      body: Center(child: Text('Settings Screen')), 
    );
  }
}
