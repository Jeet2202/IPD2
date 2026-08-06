# Fixing Dark Mode & UI Consistency in Flutter

This document outlines the steps and best practices to resolve the bug where text is invisible in dark mode (e.g., white text on a white background or dark text on a dark background) and to ensure consistent styling for placeholders and UI components across both the Customer and Worker sides of the application.

## 1. The Root Cause of Dark Mode Bugs

The primary reason text disappears or looks incorrect when switching between light and dark modes is the use of **hardcoded colors** instead of **theme-based colors**. 

For example, if you set a `Container` background to `Colors.white` and text color to `Colors.black`, it might look fine in light mode. But in dark mode, if the app automatically switches default text to white while your container remains hardcoded to white, the text becomes invisible (white on white).

## 2. Best Practices for Colors (Avoid Hardcoding)

To make the app dynamically adapt to `AppTheme.lightTheme` and `AppTheme.darkTheme`, **never hardcode colors** in your widgets. Instead, use the `Theme` context.

**❌ Incorrect (Hardcoded):**
```dart
Text(
  "Hello World",
  style: TextStyle(color: Colors.black), // Will be invisible on a black background in dark mode
)

Container(
  color: Colors.white, // Will clash in dark mode
)
```

**✅ Correct (Theme-based):**
```dart
Text(
  "Hello World",
  style: TextStyle(
    // Adapts to light/dark mode automatically
    color: Theme.of(context).colorScheme.onSurface, 
  ),
)

Container(
  // Uses the background color defined in your active theme
  color: Theme.of(context).colorScheme.surface, 
)
```

## 3. Fixing Placeholder (Hint Text) Colors

Placeholders (hint texts) inside `TextField` or `TextFormField` looking bad or changing colors inconsistently usually means the `InputDecorationTheme` is not properly configured for both light and dark modes in your `app/theme/app_theme.dart`.

**How to fix it:**
Define a consistent `inputDecorationTheme` inside both your `lightTheme` and `darkTheme` definitions in `app_theme.dart`.

```dart
// Example of configuring InputDecorationTheme in AppTheme
inputDecorationTheme: InputDecorationTheme(
  hintStyle: TextStyle(
    color: isDarkMode ? Colors.grey[400] : Colors.grey[600], 
  ),
  filled: true,
  fillColor: isDarkMode ? Colors.grey[800] : Colors.grey[200],
  border: OutlineInputBorder(
    borderRadius: BorderRadius.circular(8.0),
    borderSide: BorderSide.none,
  ),
),
```
By defining this centrally in your theme, **all TextFields across the app (Customer & Worker) will instantly look consistent**.

## 4. Ensuring Customer & Worker Side Consistency

To ensure the UI remains exactly the same and consistent across the whole app:

1. **Centralize the Theme:** All UI styling must come from `lib/app/theme/app_theme.dart`. Do not define separate themes or custom colors inside the Customer or Worker folders.
2. **Use a Shared Color Scheme:** Rely heavily on `ColorScheme`. When building a widget for the worker side or customer side, strictly use:
   - `Theme.of(context).colorScheme.primary` (Main brand color)
   - `Theme.of(context).colorScheme.surface` (Card/Container backgrounds)
   - `Theme.of(context).colorScheme.onSurface` (Default text color)
3. **Use TextThemes:** Instead of explicitly defining `TextStyle` everywhere, define your `textTheme` in `AppTheme` and use it:
   ```dart
   Text("Worker Profile", style: Theme.of(context).textTheme.titleLarge)
   ```

## 5. Action Plan to Fix the Current Bug

1. **Open `lib/app/theme/app_theme.dart`**:
   - Ensure you have a distinct `lightTheme` and `darkTheme` configured.
   - Set up `colorScheme` properly for both. `onSurface` should be black in light mode, and white in dark mode. `surface` should be white in light mode, and dark grey/black in dark mode.

2. **Global Search and Replace**:
   - Search your project for `color: Colors.white` and `color: Colors.black`.
   - Replace them with `color: Theme.of(context).colorScheme.surface` and `color: Theme.of(context).colorScheme.onSurface` as appropriate.
   
3. **Check Custom TextStyles**:
   - Search for `TextStyle(color:` across your app. 
   - Ensure that any text color you define manually responds to the current theme brightness, or simply remove the `color` property so it falls back to the default `TextTheme` which automatically handles dark mode.

By following these rules, your text visibility issues will disappear, and the UI will remain completely uniform across the Customer and Worker modules.
