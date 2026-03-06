import 'package:flutter/material.dart';
import 'routes.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Timeless Parts & Accessories',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      initialRoute: '/inventory',
      routes: Routes.routes,
    );
  }
}