import './app.css'
import './scripts/reload.js'
import sender from './scripts/sender.js'

if (
  window.matchMedia &&
  window.matchMedia('(prefers-color-scheme: dark)').matches
) {
  document.body.classList.add('dark')
}

sender.init()
