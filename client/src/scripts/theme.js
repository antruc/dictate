const theme = {
  init() {
    // Detects if the user prefers dark mode
    const darkMode = window.matchMedia('(prefers-color-scheme: dark)')

    const update = () => {
      const isDark = darkMode.matches
      // Add or remove the dark class
      document.body.classList.toggle('dark', isDark)
    }
    // When the DOM content finishes loading, applies the correct theme
    document.addEventListener('DOMContentLoaded', update)

    // Listen for system theme changes
    darkMode.addEventListener('change', update)
  }
}

export default theme
