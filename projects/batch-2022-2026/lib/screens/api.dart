import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class CallAPI extends StatefulWidget {
  const CallAPI({super.key});

  @override
  State<CallAPI> createState() => _CallAPIState();
}

class _CallAPIState extends State<CallAPI> {
  TextEditingController _controller = TextEditingController();
  String _response = '';
  bool _loading = false;

  Future<void> fetchExplanation(String topic) async {
    final url = Uri.parse('http://127.0.1.2:5000/teach'); // Replace <YOUR_IP>

    setState(() {
      _loading = true;
      _response = '';
    });

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"topic": topic}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _response = data["explanation"];
        });
      } else {
        setState(() {
          _response = "Server error: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _response = "Connection error: $e";
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('QueryBox'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: 'Enter Topic',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 12),
            ElevatedButton(
              onPressed: () {
                final topic = _controller.text.trim();
                if (topic.isNotEmpty) {
                  fetchExplanation(topic);
                }
              },
              child: Text('Get Explanation'),
            ),
            SizedBox(height: 20),
            _loading
                ? CircularProgressIndicator()
                : Expanded(
                    child: SingleChildScrollView(
                      child: Text(
                        _response,
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
          ],
        ),
      ),
    );
  }
}
