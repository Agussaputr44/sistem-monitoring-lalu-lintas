import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// === COLORS ===
const Color kBackgroundDark = Color(0xFF0D1117);
const Color kSurfaceDark = Color(0xFF161B22);
const Color kPrimaryTeal = Color(0xFF00C6AE);
const Color kSecondaryBlue = Color(0xFF1E88E5);
const Color kWarningYellow = Color(0xFFFFB300);
const Color kDangerRed = Color(0xFFE53935);
const Color kSuccessGreen = Color(0xFF43A047);
const Color kTextPrimary = Colors.white;
final Color kTextSecondary = Colors.grey.shade400;

// === TEXT STYLES ===
final TextStyle kHeading5 = GoogleFonts.poppins(
  fontSize: 22,
  fontWeight: FontWeight.w600,
  color: kTextPrimary,
);
final TextStyle kHeading6 = GoogleFonts.poppins(
  fontSize: 18,
  fontWeight: FontWeight.w500,
  color: kTextPrimary,
);
final TextStyle kSubtitle = GoogleFonts.poppins(
  fontSize: 15,
  fontWeight: FontWeight.w400,
  color: kTextSecondary,
);
final TextStyle kBodyText = GoogleFonts.poppins(
  fontSize: 13,
  fontWeight: FontWeight.w400,
  color: kTextPrimary,
);

// === TEXT THEME ===
final kTextTheme = TextTheme(
  headlineMedium: kHeading5,
  headlineSmall: kHeading6,
  labelMedium: kSubtitle,
  bodyMedium: kBodyText,
);

// === DRAWER ===
final kDrawerTheme = DrawerThemeData(
  backgroundColor: kSurfaceDark,
);

// === COLOR SCHEME ===
const kColorScheme = ColorScheme(
  primary: kPrimaryTeal,
  secondary: kSecondaryBlue,
  surface: kSurfaceDark,
  error: kDangerRed,
  onPrimary: Colors.white,
  onSecondary: Colors.white,
  onSurface: Colors.white,
  onError: Colors.white,
  brightness: Brightness.dark,
);
