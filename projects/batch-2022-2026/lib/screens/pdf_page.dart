import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';

class PdfPage extends StatefulWidget {
  const PdfPage({super.key});

  @override
  State<PdfPage> createState() => _PdfPageState();
}

class _PdfPageState extends State<PdfPage> {
  final GlobalKey<SfPdfViewerState> _pdfViewerKey = GlobalKey();
  final PdfViewerController _pdfViewerController = PdfViewerController();
  final TextEditingController _textEditingController = TextEditingController();
  List _explainChat = [];
  String? _selectedText;
  Rect? _selectionRect;

  Future<void> fetchExplanation(String topic, Function setState) async {
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
      setState(() {
        _explainChat.add(data['explanation']);
      });
    } else {
      print("Error: ${response.body}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PDF Viewer'),
      ),
      body: Stack(
        children: [
          SfPdfViewer.asset(
            'assets/dummy.pdf',
            key: _pdfViewerKey,
            controller: _pdfViewerController,
            canShowTextSelectionMenu: false,
            onTextSelectionChanged: (PdfTextSelectionChangedDetails details) {
              // Manage the selection state manually
              if (details.selectedText != null &&
                  details.selectedText!.isNotEmpty) {
                setState(() {
                  _selectedText = details.selectedText;
                  _textEditingController.text = _selectedText!;
                  _selectionRect = details.globalSelectedRegion;
                });
              } else {
                setState(() {
                  _selectedText = null;
                  _selectionRect = null;
                });
              }
            },
          ),
          if (_selectedText != null && _selectionRect != null)
            Positioned(
              top: _selectionRect!.top -
                  50, // Position the toolbar above the selected text
              left: _selectionRect!
                  .left, // Align the toolbar with the left edge of the selection
              child: Material(
                elevation: 2,
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextButton.icon(
                        onPressed: () {
                          showDialog(
                            context: context,
                            builder: (context) {
                              return StatefulBuilder(
                                  builder: (context, setState) => AlertDialog(
                                        alignment: Alignment.bottomCenter,
                                        shape: RoundedRectangleBorder(
                                          borderRadius:
                                              BorderRadius.circular(20),
                                        ),
                                        insetPadding: const EdgeInsets.all(10),
                                        content: Container(
                                          width:
                                              MediaQuery.of(context).size.width,
                                          constraints: BoxConstraints(
                                            maxHeight: MediaQuery.of(context)
                                                    .size
                                                    .height *
                                                0.8,
                                          ),
                                          child: Column(
                                            mainAxisSize: MainAxisSize.min,
                                            mainAxisAlignment:
                                                MainAxisAlignment.end,
                                            children: [
                                              Expanded(
                                                child: ListView.builder(
                                                  itemCount:
                                                      _explainChat.length,
                                                  itemBuilder:
                                                      (context, index) {
                                                    return Align(
                                                      alignment: index % 2 == 0
                                                          ? Alignment
                                                              .centerRight
                                                          : Alignment
                                                              .centerLeft,
                                                      child: Container(
                                                        margin: const EdgeInsets
                                                            .only(
                                                            top: 0, bottom: 0),
                                                        padding:
                                                            const EdgeInsets
                                                                .all(0),
                                                        decoration:
                                                            BoxDecoration(
                                                                // color: Colors.blue,
                                                                borderRadius:
                                                                    BorderRadius
                                                                        .circular(
                                                                            10)),
                                                        child: IntrinsicWidth(
                                                          child: ListTile(
                                                            contentPadding:
                                                                const EdgeInsets
                                                                    .all(0),
                                                            minVerticalPadding:
                                                                0,
                                                            horizontalTitleGap:
                                                                0,
                                                            title: Row(
                                                              children: [
                                                                CircleAvatar(
                                                                  radius: 7,
                                                                  backgroundColor: index % 2 ==
                                                                          0
                                                                      ? Colors
                                                                          .blue
                                                                      : Colors
                                                                          .deepOrangeAccent,
                                                                ),
                                                                const SizedBox(
                                                                    width: 5),
                                                                Text(
                                                                  index % 2 == 0
                                                                      ? 'You'
                                                                      : 'AI',
                                                                  style: const TextStyle(
                                                                      fontSize:
                                                                          15),
                                                                )
                                                              ],
                                                            ),
                                                            subtitle: Text(
                                                                _explainChat[
                                                                    index]),
                                                          ),
                                                        ),
                                                      ),
                                                    );
                                                  },
                                                ),
                                              ),
                                              const SizedBox(
                                                height: 10,
                                              ),
                                              IntrinsicHeight(
                                                child: Row(
                                                  mainAxisAlignment:
                                                      MainAxisAlignment
                                                          .spaceBetween,
                                                  crossAxisAlignment:
                                                      CrossAxisAlignment
                                                          .stretch,
                                                  children: [
                                                    Expanded(
                                                        child: TextField(
                                                      controller:
                                                          _textEditingController,
                                                      keyboardType:
                                                          TextInputType
                                                              .multiline,
                                                      minLines: 1,
                                                      maxLines: 2,
                                                      scrollPadding:
                                                          const EdgeInsets.all(
                                                              10),
                                                      decoration:
                                                          const InputDecoration(
                                                              border:
                                                                  OutlineInputBorder()),
                                                    )),
                                                    const SizedBox(width: 5),
                                                    FilledButton(
                                                        style: FilledButton.styleFrom(
                                                            padding:
                                                                const EdgeInsets
                                                                    .all(0),
                                                            shape: RoundedRectangleBorder(
                                                                borderRadius:
                                                                    BorderRadius
                                                                        .circular(
                                                                            10))),
                                                        onPressed: () async {
                                                          if (_textEditingController
                                                              .text
                                                              .isNotEmpty) {
                                                            setState(() {
                                                              _explainChat.add(
                                                                  _textEditingController
                                                                      .text);
                                                            });
                                                            await fetchExplanation(
                                                                _textEditingController
                                                                    .text,
                                                                setState);
                                                          }
                                                        },
                                                        child: const Icon(Icons
                                                            .question_answer_outlined))
                                                  ],
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ));
                            },
                          );
                          setState(() {
                            _selectedText = null;
                          });
                        },
                        icon: const Icon(Icons.question_answer_outlined,
                            size: 18),
                        label: const Text('Explain'),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () {
                          setState(() {
                            _selectedText = null; // Hide the toolbar
                            _pdfViewerController
                                .clearSelection(); // Clear the selection explicitly
                          });
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
