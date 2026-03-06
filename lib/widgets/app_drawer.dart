import 'package:flutter/material.dart';

class AppDrawer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: <Widget>[
          // Company Info
          Container(
            padding: EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Company Name', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                Text('Company Tagline', style: TextStyle(fontSize: 16)),
                Text('Phone: (123) 456-7890'),
                Text('Email: info@company.com'),
                Text('Address: 123 Business Rd, City, State, 12345'),
              ],
            ),
          ),
          Divider(),
          // Navigation List
          ListTile(
            title: Text('Inventory'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/inventory');
            },
          ),
          ListTile(
            title: Text('Vehicles'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/vehicles');
            },
          ),
          ListTile(
            title: Text('Invoices'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/invoices');
            },
          ),
          ListTile(
            title: Text('Customers'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/customers');
            },
          ),
          ListTile(
            title: Text('Settings'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/settings');
            },
          ),
        ],
      ),
    );
  }
}