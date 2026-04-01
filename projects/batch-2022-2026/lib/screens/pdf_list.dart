import 'package:flutter/material.dart';

class PdfList extends StatefulWidget {
  const PdfList({super.key});

  @override
  State<PdfList> createState() => _PdfListState();
}

class _PdfListState extends State<PdfList> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('PDF List'),
      ),
      body: ListView.builder(
        itemCount: 5,
        itemBuilder: (context, index) {
          return ListTile(
            leading: Icon(Icons.picture_as_pdf),
            title: Text('PDF Document ${index + 1}'),
            onTap: () {
              // Handle PDF document tap
              print('Tapped on PDF Document ${index + 1}');
            },
          );
        },
      ),
    );
  }
}
