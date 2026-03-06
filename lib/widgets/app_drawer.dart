import 'package:flutter/material.dart';

class AppDrawer extends StatelessWidget {
  final String companyName = 'Timeless Auto Imports Limited';
  final String tagline = "Don't Just Dream, Drive it";
  final String phone = '876 403 8436';
  final String email = 'timelessautoimportslimited@gmail.com';
  final String address = 'Lot 36 Bustamante Highway, May Pen, Clarendon';

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[ 
          UserAccountsDrawerHeader(
            accountName: Text(companyName),
            accountEmail: Text(email),
            decoration: BoxDecoration(
              color: Colors.blue,
            ),
            otherAccountsPictures: [CircleAvatar(child: Text("T"))],
          ),
          ListTile(
            title: Text('Tagline'),
            subtitle: Text(tagline),
          ),
          ListTile(
            title: Text('Phone: ' + phone),
          ),
          ListTile(
            title: Text('Address: ' + address),
          ),
        ],
      ),
    );
  }
}