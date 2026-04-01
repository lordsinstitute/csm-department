import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:smart_classroom_assist/screens/api.dart';
import 'package:smart_classroom_assist/screens/pdf_list.dart';
import 'package:smart_classroom_assist/screens/pdf_page.dart';
import 'package:smart_classroom_assist/widgets/card_button.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:url_launcher/url_launcher_string.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  File? image;
  int index = 0;

  Future<void> _pickImage(BuildContext context) async {
    try {
      final XFile? image =
          await ImagePicker().pickImage(source: ImageSource.camera);
      if (image != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('Image selected: ${image.path.split('/').last}')),
        );
        setState(() {
          this.image = File(image.path);
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No image selected')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error picking image: $e')),
      );
    }
  }

  Future<String> fetchExplanation(String topic) async {
    final url = Uri.parse(
        "http://127.0.1.2:5000/teach"); // Replace <YOUR_IP> with your PC's IP

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"topic": topic}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      print("Topic: ${data['topic']}");
      print("Explanation: ${data['explanation']}");
      return data['explanation'];
    } else {
      print("Error: ${response.body}");
      return "Error: ${response.body}";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
      ),
      drawer: Drawer(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const DrawerHeader(
              child: Text(
                'Menu',
                style: TextStyle(color: Colors.white, fontSize: 30),
              ),
              decoration: BoxDecoration(color: Colors.blue),
            ),
            ListTile(
              leading: const Icon(Icons.photo_camera_rounded),
              title: const Text('Camera'),
              onTap: () => _pickImage(context),
            ),
            ListTile(
              leading: const Icon(Icons.camera_outlined),
              title: const Text('CCTV Feed'),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.insert_drive_file_rounded),
              title: const Text('Notes Section'),
              onTap: () {},
            ),
            ListTile(
              leading: const Icon(Icons.groups_2_rounded),
              title: const Text('Attendance'),
              onTap: () {},
            ),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(15),
        child: SingleChildScrollView(
          child: Column(
            spacing: 5,
            children: [
              image != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(20),
                      child: Image.file(
                        image!,
                        height: 200,
                        fit: BoxFit.scaleDown,
                      ),
                    )
                  : const SizedBox(),
              ListTile(
                leading: const Icon(Icons.photo_camera_rounded),
                title: const Text('Camera'),
                onTap: () => _pickImage(context),
              ),
              ListTile(
                leading: const Icon(Icons.camera_outlined),
                title: const Text('CCTV Feed'),
                onTap: () {},
              ),
              ListTile(
                leading: const Icon(Icons.insert_drive_file_rounded),
                title: const Text('Notes Section'),
                onTap: () {},
              ),
              ListTile(
                leading: const Icon(Icons.groups_2_rounded),
                title: const Text('Attendance'),
                onTap: () {},
              ),
              ListTile(
                leading: const Icon(Icons.picture_as_pdf_rounded),
                title: const Text('Open PDF'),
                onTap: () {
                  Navigator.push(context,
                      MaterialPageRoute(builder: (context) => const PdfPage()));
                },
              ),
              ListTile(
                leading: const Icon(Icons.api),
                title: const Text('Call API'),
                onTap: () {
                  Navigator.push(context,
                      MaterialPageRoute(builder: (context) => const CallAPI()));
                },
              ),
              ListTile(
                leading: const Icon(Icons.picture_as_pdf_rounded),
                title: const Text('PDF List'),
                onTap: () {
                  Navigator.push(context,
                      MaterialPageRoute(builder: (context) => const PdfList()));
                },
              ),
              // cardButton(const Icon(Icons.photo_camera_rounded), 'Camera',
              //     onPressed: () => _pickImage(context)),
              // cardButton(
              //   const Icon(Icons.camera_outlined),
              //   'CCTV Feed',
              // ),
              // cardButton(
              //   const Icon(Icons.note_rounded),
              //   'Notes Section',
              // ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: SizedBox(
        height: 56,
        child: BottomNavigationBar(
          currentIndex: index,
          // type: BottomNavigationBarType.shifting,
          // showSelectedLabels: false,
          // showUnselectedLabels: false,
          onTap: (value) => setState(() {
            index = value;
          }),
          // selectedItemColor: Colors.deepPurple,
          // unselectedItemColor: Colors.deepPurpleAccent,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
            BottomNavigationBarItem(
                icon: Icon(Icons.settings), label: 'Settings'),
          ],
          selectedFontSize: 15,
          unselectedFontSize: 12,
          iconSize: 20,
        ),
      ),
    );
  }
}
