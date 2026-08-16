import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

/// Session stream -- widgets can watch this to react to sign-in/sign-out.
final authStateChangesProvider = StreamProvider<AuthState>((ref) {
  return Supabase.instance.client.auth.onAuthStateChange;
});

Future<void> signInAnonymously() async {
  await Supabase.instance.client.auth.signInAnonymously();
}

bool get isSignedIn => Supabase.instance.client.auth.currentSession != null;
