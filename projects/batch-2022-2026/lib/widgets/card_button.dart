import 'package:flutter/material.dart';

Widget cardButton(Icon icon, String text, {Function()? onPressed}) {
  return GestureDetector(
    onTap: onPressed ?? () {},
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(25),
        child: Column(
          children: [
            icon,
            const SizedBox(
              height: 5,
            ),
            Text(text)
          ],
        ),
      ),
    ),
  );
}
