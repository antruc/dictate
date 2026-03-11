const sender = {
  async sendText() {
    const textArea = document.querySelector('#textarea')
    const url = window.location.href

    // Only proceed if there is text in the textarea
    if (textArea.value.length > 0) {
      try {
        await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'text/plain;charset=utf-8'
          },
          body: textArea.value
        })
        // Clear the textarea after successful send
        textArea.value = ''
      } catch {
        alert('Connection lost')
      }
    }
  },
  buttonSend(event) {
    const matchButton = event.target.matches('#send')
    if (matchButton) sender.sendText()
  },
  autoSend(event) {
    const matchText = event.target.matches('#textarea')
    const checkbox = document.querySelector('#checkbox1')
    if (matchText) {
      // Send the text automatically if the checkbox is checked
      if (checkbox.checked) sender.sendText()
    }
  },
  enableButton(event) {
    const matchCheckbox = event.target.matches('#checkbox1')
    const is_disabled = document.querySelector('#send').getAttribute('disabled')
    const sendButton = document.querySelector('#send')
    if (matchCheckbox) {
      is_disabled
        ? sendButton.removeAttribute('disabled')
        : sendButton.setAttribute('disabled', 'true')
    }
  },
  // Initializes the checkbox and disables the send button
  isChecked() {
    const checkbox = document.querySelector('#checkbox1')
    const sendButton = document.querySelector('#send')
    // Check the checkbox by default if it’s unchecked
    if (!checkbox.checked) checkbox.checked = true
    // Disable the send button
    sendButton.setAttribute('disabled', 'true')
  },
  uncaught() {
    window.addEventListener('unhandledrejection', () =>
      alert('Connection lost')
    )
  },
  init() {
    this.isChecked()
    document.addEventListener('click', this.buttonSend)
    document.addEventListener('click', this.enableButton)
    document.addEventListener('input', this.autoSend)
    this.uncaught()
  }
}

export default sender
