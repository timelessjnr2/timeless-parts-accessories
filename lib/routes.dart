import 'package:flutter/material.dart';
import 'widgets/app_drawer.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: const AppDrawer(),
      appBar: AppBar(title: Text('Home')), // Example
      body: Center(child: Text('Welcome to your app!')), // Example
    );
  }
}

// Repeat for other screens as necessary
